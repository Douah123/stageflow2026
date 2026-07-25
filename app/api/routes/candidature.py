from fastapi import APIRouter, HTTPException
from app.utils.pagination import LimitParam, SkipParam
from app.core.permissions import (
    CandidaturePossedee,
    CurrentManager,
    CurrentStudent,
    DBSession,
    OffreVisiblePourGestion,
    OffreVisiblePourGestion,
)
from app.repositories.candidature import (
    CandidatureRepository,
)
from app.repositories.offre import OffreRepository
from app.schemas.candidature import (
    CandidatureDecision,
    CandidatureResponse,
)

router = APIRouter(tags=["Candidatures"])


@router.post(
    "/offres/{offre_id}/candidatures",
    response_model=CandidatureResponse,
    status_code=201,
    summary="Postuler à une offre",
    description=(
        "Réservé au rôle `student`. Crée une candidature `pending` "
        "sur une offre publiée. Refusée si l'étudiant a déjà une "
        "candidature active sur cette offre."
    ),
    responses={
        403: {"description": "Réservé au rôle student"},
        404: {"description": "Offre introuvable ou non publiée"},
        400: {
            "description": "Candidature déjà active sur cette offre"
        },
    },
)
async def apply(
    offre_id: int, etudiant: CurrentStudent, db: DBSession
):
    offre_repo = OffreRepository(db)
    offre = await offre_repo.get(offre_id)
    if not offre or offre.statut != "published":
        raise HTTPException(404, "Offre introuvable")

    candidature_repo = CandidatureRepository(db)
    if await candidature_repo.a_candidature_active(
        etudiant.id, offre_id
    ):
        raise HTTPException(
            400, "Candidature déjà active sur cette offre"
        )

    return await candidature_repo.create_candidature(
        offre_id=offre_id, etudiant_id=etudiant.id
    )


@router.get(
    "/candidatures/me", response_model=list[CandidatureResponse]
)
async def my_candidatures(
    etudiant: CurrentStudent,
    db: DBSession,
    skip: SkipParam = 0,
    limit: LimitParam = 20,
):
    repo = CandidatureRepository(db)
    return await repo.get_pour_etudiant(etudiant.id)


@router.get(
    "/offres/{offre_id}/candidatures",
    response_model=list[CandidatureResponse],
)
async def offer_candidatures(
    offre: OffreVisiblePourGestion,
    db: DBSession,
    skip: SkipParam = 0,
    limit: LimitParam = 20,
):
    repo = CandidatureRepository(db)
    return await repo.get_pour_offre(offre.id)


@router.patch(
    "/candidatures/{candidature_id}/decision",
    response_model=CandidatureResponse,
    summary="Accepter ou refuser une candidature",
    description="Réservé au `program_manager`.",
    responses={
        403: {"description": "Réservé au rôle program_manager"},
        404: {"description": "Candidature introuvable"},
    },
)
async def decide_candidature(
    candidature_id: int,
    data: CandidatureDecision,
    manager: CurrentManager,
    db: DBSession,
):
    repo = CandidatureRepository(db)
    candidature = await repo.get(candidature_id)
    if not candidature:
        raise HTTPException(404, "Candidature introuvable")
    candidature.statut = data.decision
    await db.flush()
    return candidature


@router.delete(
    "/candidatures/{candidature_id}",
    status_code=204,
    summary="Retirer sa candidature",
    description=(
        "Réservé à l'étudiant propriétaire de la candidature. "
        "Impossible si elle a déjà été acceptée."
    ),
    responses={
        404: {
            "description": "Candidature introuvable ou n'appartenant "
            "pas à l'étudiant authentifié"
        },
        400: {
            "description": "La candidature est déjà acceptée, elle "
            "ne peut plus être retirée"
        },
    },
)
async def withdraw_candidature(
    candidature: CandidaturePossedee, db: DBSession
):
    """CandidaturePossedee a déjà vérifié l'ownership."""
    if candidature.statut == "accepted":
        raise HTTPException(
            400,
            "Une candidature acceptée ne peut plus être retirée",
        )
    repo = CandidatureRepository(db)
    await repo.delete(candidature.id)