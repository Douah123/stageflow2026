from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidature import Candidature
from app.repositories.base import BaseRepository
from app.schemas.candidature import CandidatureCreate


class CandidatureRepository(
    BaseRepository[
        Candidature, CandidatureCreate, CandidatureCreate
    ]
):
    def __init__(self, db: AsyncSession):
        super().__init__(Candidature, db)

    async def create_candidature(
        self, offre_id: int, etudiant_id: int
    ) -> Candidature:
        candidature = Candidature(
            offre_id=offre_id,
            etudiant_id=etudiant_id,
            statut="pending",
        )
        self.db.add(candidature)
        await self.db.flush()
        await self.db.refresh(candidature)
        return candidature

    async def a_candidature_active(
        self, etudiant_id: int, offre_id: int
    ) -> bool:
        """
        Invariant : une seule candidature active (pending)
        par etudiant et par offre.
        """
        result = await self.db.execute(
            select(Candidature).where(
                Candidature.etudiant_id == etudiant_id,
                Candidature.offre_id == offre_id,
                Candidature.statut == "pending",
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_pour_offre(self, offre_id: int) -> list[Candidature]:
        result = await self.db.execute(
            select(Candidature)
            .where(Candidature.offre_id == offre_id)
            .order_by(Candidature.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_pour_etudiant(
        self, etudiant_id: int, skip: int = 0, limit: int = 20
    ) -> list[Candidature]:
        result = await self.db.execute(
            select(Candidature)
            .where(Candidature.etudiant_id == etudiant_id)
            .order_by(Candidature.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_status(self) -> dict[str, int]:
        result = await self.db.execute(
            select(
                Candidature.statut,
                func.count(Candidature.id).label("count"),
            ).group_by(Candidature.statut)
        )
        return {row.statut: row.count for row in result}