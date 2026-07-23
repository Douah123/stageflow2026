from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)


from app.core.config import settings


async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    pool_pre_ping=True,
    max_overflow=20
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)




#---- Dépendance FastAPI (fournit une session par requête) ----#
async def get_db() -> AsyncGenerator[AsyncSession, None]:
 """Générateur de session de base de données."""
 async with AsyncSessionLocal() as session:
    try:
       yield session
       await session.commit()
    except Exception:
       await session.rollback()
       raise