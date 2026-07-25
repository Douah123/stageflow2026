from app.utils.time import utcnow
from app.utils.pagination import LimitParam, SkipParam
from fastapi import APIRouter, HTTPException

from app.core.permissions import (
    CurrentCompany,
    CurrentManager,
    DBSession,
    OffrePossedee,
)
from app.repositories.offre import OffreRepository
from app.schemas.offre import (
    OffreCreate,
    OffreResponse,
    OffreReview,
    OffreUpdate,
)

router = APIRouter(prefix="/offres", tags=["Offres"])


@router.post("", response_model=OffreResponse, status_code=201)
async def create_offer(
    data: OffreCreate,
    entreprise: CurrentCompany,
    db: DBSession,
):
    repo = OffreRepository(db)
    return await repo.create_offre(data, entreprise_id=entreprise.id)


@router.get("", response_model=list[OffreResponse])
async def list_offers(
    db: DBSession, skip: SkipParam = 0, limit: LimitParam = 20
):
    """Liste publique : uniquement les offres publiées."""
    repo = OffreRepository(db)
    return await repo.get_published(skip, limit)


@router.get("/{offre_id}", response_model=OffreResponse)
async def get_offer(offre_id: int, db: DBSession):
    repo = OffreRepository(db)
    offre = await repo.get(offre_id)
    if not offre or offre.statut != "published":
        raise HTTPException(404, "Offre introuvable")
    return offre


@router.patch("/{offre_id}", response_model=OffreResponse)
async def update_offer(
    data: OffreUpdate, offre: OffrePossedee, db: DBSession
):
    """Édition d'une offre tant qu'elle est en brouillon."""
    if offre.statut != "draft":
        raise HTTPException(
            400, "Seule une offre en brouillon peut être modifiée"
        )
    repo = OffreRepository(db)
    offre_maj = await repo.update(offre.id, data)
    offre_maj.updated_at = utcnow()
    return offre_maj


@router.patch(
    "/{offre_id}/submit",
    response_model=OffreResponse,
    summary="Soumettre une offre pour validation",
    description=(
        "Réservé à l'entreprise propriétaire de l'offre. Fait "
        "passer l'offre de `draft` à `submitted`, uniquement si "
        "titre, mission et compétences sont renseignés."
    ),
    responses={
        400: {
            "description": "Offre déjà soumise, ou incomplète "
            "(titre/mission/compétences manquants)"
        },
        404: {"description": "Offre introuvable ou n'appartenant pas "
              "à l'entreprise authentifiée"},
    },
)
async def submit_offer(offre: OffrePossedee, db: DBSession):
    if offre.statut != "draft":
        raise HTTPException(
            400, "Seule une offre en brouillon peut être soumise"
        )
    repo = OffreRepository(db)
    if not repo.est_complete(offre):
        raise HTTPException(
            400,
            "Titre, mission, compétences et entreprise "
            "requis avant soumission",
        )
    offre.statut = "submitted"
    offre.updated_at = utcnow()
    await db.flush()
    return offre


@router.patch(
    "/{offre_id}/review",
    response_model=OffreResponse,
    summary="Valider ou refuser une offre soumise",
    description=(
        "Réservé au `program_manager`. Fait passer une offre "
        "`submitted` vers `published` ou `rejected` selon la "
        "décision."
    ),
    responses={
        403: {"description": "Réservé au rôle program_manager"},
        404: {"description": "Offre introuvable"},
        400: {
            "description": "L'offre n'est pas au statut `submitted`"
        },
    },
)
async def review_offer(
    offre_id: int,
    data: OffreReview,
    manager: CurrentManager,
    db: DBSession,
):
    repo = OffreRepository(db)
    offre = await repo.get(offre_id)
    if not offre:
        raise HTTPException(404, "Offre introuvable")
    if offre.statut != "submitted":
        raise HTTPException(
            400, "Seule une offre soumise peut être revue"
        )
    offre.statut = (
        "published" if data.decision == "publish" else "rejected"
    )
    offre.updated_at = utcnow()
    await db.flush()
    return offre