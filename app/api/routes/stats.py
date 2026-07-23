from fastapi import APIRouter

from app.core.permissions import CurrentManager, DBSession
from app.repositories.candidature import (
    CandidatureRepository,
)
from app.repositories.offre import OffreRepository

router = APIRouter(tags=["Stats"])


@router.get("/stats")
async def get_stats(manager: CurrentManager, db: DBSession):
    """
    Réservé au program_manager : nombre d'offres et de
    candidatures, regroupées par statut.
    """
    offre_repo = OffreRepository(db)
    candidature_repo = CandidatureRepository(db)
    return {
        "offres_par_statut": await offre_repo.count_by_status(),
        "candidatures_par_statut": (
            await candidature_repo.count_by_status()
        ),
    }