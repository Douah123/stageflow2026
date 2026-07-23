# scripts/seed_admin.py
import asyncio

from app.db.session import AsyncSessionLocal
from app.repositories.role import RoleRepository
from app.repositories.user import UserRepository
from app.utils.hashing import hash_password
import app.models  # noqa: F401 — force l'enregistrement de tous les modèles


async def creer_admin():
    async with AsyncSessionLocal() as db:
        role_repo = RoleRepository(db)
        user_repo = UserRepository(db)

        role = await role_repo.get_by_name("admin")
        if await user_repo.get_by_email("admin@gmail.com"):
            print("Admin déjà existant.")
            return

        from app.schemas.user import UserCreate

        user_data = UserCreate(
            username="admin",
            email="admin@gmail.com",
            hashed_password=hash_password("Admin1234#"),
            role_id=role.id,
        )
        await user_repo.create(user_data)
        await db.commit()
        print("Admin créé.")


if __name__ == "__main__":
    asyncio.run(creer_admin())