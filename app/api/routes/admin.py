
import logging

from fastapi import APIRouter, HTTPException, Request
from app.utils.time import utcnow
from app.core.permissions import CurrentAdmin, DBSession
from app.repositories.role import RoleRepository
from app.repositories.user import UserRepository
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = logging.getLogger(__name__)


@router.get(
    "/users",
    response_model=list[UserResponse],
    summary="Lister les utilisateurs",
    description="Réservé au rôle `admin`.",
    responses={403: {"description": "Réservé au rôle admin"}},
)
async def list_users(admin: CurrentAdmin, db: DBSession):
    repo = UserRepository(db)
    return await repo.get_all()


@router.patch(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Modifier le rôle ou l'activation d'un compte",
    description=(
        "Réservé au rôle `admin`. Permet de changer le rôle "
        "(`role_id`) et/ou de désactiver un compte (`is_active`). "
        "L'action est tracée dans les logs applicatifs."
    ),
    responses={
        403: {"description": "Réservé au rôle admin"},
        404: {"description": "Utilisateur introuvable"},
        400: {
            "description": "Aucune modification fournie, ou "
            "`role_id` invalide"
        },
    },
)
async def update_user(
    user_id: int,
    data: UserUpdate,
    admin: CurrentAdmin,
    db: DBSession,
    request: Request,
):
    """
    Change le rôle et/ou l'activation d'un compte.
    Trace l'action dans les logs applicatifs.
    """
    repo = UserRepository(db)
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(404, "Utilisateur introuvable")

    updates = data.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(400, "Aucune modification fournie")

    if "role_id" in updates:
        role_repo = RoleRepository(db)
        role = await role_repo.get_by_id(updates["role_id"])
        if role is None:
            raise HTTPException(400, "role_id invalide")

    for champ, valeur in updates.items():
        setattr(user, champ, valeur)
    user.updated_at = utcnow()

    await db.flush()
    await db.refresh(user)

    logger.info(
        "Modification utilisateur par admin",
        extra={
            "request_id": getattr(
                request.state, "request_id", None
            ),
            "acteur_id": admin.id,
            "cible_id": user.id,
            "modifications": updates,
        },
    )
    return user