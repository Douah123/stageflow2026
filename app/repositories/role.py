# app/repositories/role_repository.py
from os import name
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.models.role import Role  # adapte selon ton arborescence
from app.repositories.base import BaseRepository


class RoleCreate(BaseModel):
    nom: str


class RoleUpdate(BaseModel):
    nom: Optional[str] = None


class RoleRepository(BaseRepository[Role, RoleCreate, RoleUpdate]):
    """Repository pour Role, utilisé pour résoudre role_id à l'inscription."""

    def __init__(self, db: AsyncSession):
        super().__init__(Role, db)

    async def get_by_name(self, nom: str) -> Optional[Role]:
        result = await self.db.execute(
            select(Role).where(Role.nom == nom)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, id: int) -> Role | None:
        result = await self.db.execute(
            select(Role).where(Role.id == id)
        )
        return result.scalar_one_or_none()