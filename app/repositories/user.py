# app/repositories/user_repository.py

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy.orm import selectinload

from app.models.user import User  # adapte selon ton arborescence
from app.schemas.auth import UserRegister  # ton schéma de création
from app.repositories.base import BaseRepository


class UserUpdate(BaseModel):
    """
    Schéma minimal pour les mises à jour partielles de User.
    Ajoute/retire des champs selon ce que ton API autorise
    à modifier (ex: pas de changement de role sans passer
    par une route dédiée).
    """
    username: Optional[str] = None
    is_active: Optional[bool] = None


class UserRepository(BaseRepository[User, UserRegister, UserUpdate]):
    """
    Repository dédié à User : hérite du CRUD générique et
    ajoute les requêtes spécifiques (recherche par email,
    par username, avec la relation role chargée).
    """

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_with_role(self, id: int) -> Optional[User]:
        """
        Surcharge de get() qui précharge la relation role,
        nécessaire pour sérialiser UserResponse (qui contient
        un RoleResponse imbriqué).
        """
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        return await self.get_by_email(email) is not None

    async def username_exists(self, username: str) -> bool:
        return await self.get_by_username(username) is not None
    
    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> list[User]:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())