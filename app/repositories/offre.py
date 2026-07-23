from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.offre import Offre
from app.repositories.base import BaseRepository
from app.schemas.offre import OffreCreate, OffreUpdate


class OffreRepository(
    BaseRepository[Offre, OffreCreate, OffreUpdate]
):
    def __init__(self, db: AsyncSession):
        super().__init__(Offre, db)

    async def create_offre(
        self, data: OffreCreate, entreprise_id: int
    ) -> Offre:
        offre = Offre(
            **data.model_dump(),
            entreprise_id=entreprise_id,
            statut="draft",
        )
        self.db.add(offre)
        await self.db.flush()
        await self.db.refresh(offre)
        return offre

    async def get_published(
        self, skip: int = 0, limit: int = 20
    ) -> list[Offre]:
        result = await self.db.execute(
            select(Offre)
            .where(Offre.statut == "published")
            .order_by(Offre.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_entreprise(self, entreprise_id: int) -> list[Offre]:
        result = await self.db.execute(
            select(Offre)
            .where(Offre.entreprise_id == entreprise_id)
            .order_by(Offre.created_at.desc())
        )
        return list(result.scalars().all())

    def est_complete(self, offre: Offre) -> bool:
        """
        Invariant : titre, mission, competences et
        entreprise renseignes avant publication.
        """
        return bool(
            offre.titre
            and offre.mission
            and offre.competences
            and offre.entreprise_id
        )

    async def count_by_status(self) -> dict[str, int]:
        result = await self.db.execute(
            select(
                Offre.statut,
                func.count(Offre.id).label("count"),
            ).group_by(Offre.statut)
        )
        return {row.statut: row.count for row in result}