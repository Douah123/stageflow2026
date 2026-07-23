# app/core/permissions.py

from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import get_db
from app.models.candidature import Candidature
from app.models.offre import Offre
from app.models.user import User
from app.repositories.candidature import CandidatureRepository
from app.repositories.offre import OffreRepository
from app.repositories.user import UserRepository

DBSession = Annotated[AsyncSession, Depends(get_db)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DBSession,
) -> User:
    payload = decode_token(token)
    user_id = payload.get("sub")
    repo = UserRepository(db)
    user = await repo.get(int(user_id))
    if not user or not user.is_active:
        raise HTTPException(401, "Utilisateur introuvable ou inactif")
    return user


def require_role(*allowed_roles: str):
    """Fabrique de dépendance : centralise toute la logique RBAC."""

    async def checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role.nom not in allowed_roles:
            raise HTTPException(403, f"Rôle requis parmi {allowed_roles}")
        return current_user

    return checker


CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentStudent = Annotated[User, Depends(require_role("student"))]
CurrentCompany = Annotated[User, Depends(require_role("company"))]
CurrentManager = Annotated[
    User, Depends(require_role("program_manager"))
]
CurrentAdmin = Annotated[User, Depends(require_role("admin"))]


async def get_offre_possedee(
    offre_id: int,
    entreprise: CurrentCompany,
    db: DBSession,
) -> Offre:
    """Garantit qu'une entreprise n'accède jamais à une offre
    qui n'est pas la sienne."""
    repo = OffreRepository(db)
    offre = await repo.get(offre_id)
    if not offre or offre.entreprise_id != entreprise.id:
        raise HTTPException(404, "Offre introuvable")
    return offre


OffrePossedee = Annotated[Offre, Depends(get_offre_possedee)]


async def get_candidature_possedee(
    candidature_id: int,
    etudiant: CurrentStudent,
    db: DBSession,
) -> Candidature:
    """Même principe que get_offre_possedee, appliqué à la
    candidature."""
    repo = CandidatureRepository(db)
    candidature = await repo.get(candidature_id)
    if not candidature or candidature.etudiant_id != etudiant.id:
        raise HTTPException(404, "Candidature introuvable")
    return candidature


CandidaturePossedee = Annotated[
    Candidature, Depends(get_candidature_possedee)
]

async def get_offre_visible_pour_gestion(
    offre_id: int,
    current_user: CurrentUser,
    db: DBSession,
) -> Offre:
    """
    Autorise soit l'entreprise propriétaire de l'offre,
    soit un program_manager, à consulter ses candidatures.
    """
    repo = OffreRepository(db)
    offre = await repo.get(offre_id)
    if not offre:
        raise HTTPException(404, "Offre introuvable")

    est_proprietaire = (
        current_user.role.nom == "company"
        and offre.entreprise_id == current_user.id
    )
    est_manager = current_user.role.nom == "program_manager"

    if not (est_proprietaire or est_manager):
        raise HTTPException(404, "Offre introuvable")

    return offre


OffreVisiblePourGestion = Annotated[
    Offre, Depends(get_offre_visible_pour_gestion)
]