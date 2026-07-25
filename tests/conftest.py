import pytest_asyncio
from typing import AsyncGenerator
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

import app.models  # noqa: F401 — force l'enregistrement des modèles
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.repositories.role import RoleRepository
from app.repositories.user import UserRepository
from app.utils.hashing import hash_password

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    TestSessionLocal = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def db_session_with_roles(db_session: AsyncSession):
    """Peuple les 4 rôles avant chaque test (table vide sinon)."""
    from app.models.role import Role

    for nom in ["student", "company", "program_manager", "admin"]:
        db_session.add(Role(nom=nom))
    await db_session.flush()
    return db_session


@pytest_asyncio.fixture
async def _db_override(db_session_with_roles: AsyncSession):
    """Enregistre l'override de session DB, partagé par tous les clients
    HTTP d'un même test (anonyme ou authentifiés)."""

    async def override_get_db():
        yield db_session_with_roles

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(_db_override):
    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as ac:
        yield ac


async def _authenticated_client(
    db_session, username, email, password, role_nom
):
    """Crée un utilisateur et renvoie un AsyncClient qui lui est propre
    (chaque rôle doit avoir son propre client : ils sont utilisés
    ensemble dans les mêmes tests et ne doivent pas partager d'en-têtes)."""
    role_repo = RoleRepository(db_session)
    role = await role_repo.get_by_name(role_nom)

    user_repo = UserRepository(db_session)
    from app.schemas.user import UserCreate

    user_data = UserCreate(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role_id=role.id,
    )
    await user_repo.create(user_data)

    ac = AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    )
    resp = await ac.post(
        "/auth/login",
        data={"username": username, "password": password},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    ac.headers["Authorization"] = f"Bearer {token}"
    return ac


@pytest_asyncio.fixture
async def student_client(_db_override, db_session_with_roles):
    ac = await _authenticated_client(
        db_session_with_roles,
        "etudiant_test",
        "etudiant@test.com",
        "pass1234",
        "student",
    )
    yield ac
    await ac.aclose()


@pytest_asyncio.fixture
async def student_client_2(_db_override, db_session_with_roles):
    """Deuxième étudiant, pour les tests d'isolation."""
    ac = await _authenticated_client(
        db_session_with_roles,
        "etudiant_test_2",
        "etudiant2@test.com",
        "pass1234",
        "student",
    )
    yield ac
    await ac.aclose()


@pytest_asyncio.fixture
async def company_client(_db_override, db_session_with_roles):
    ac = await _authenticated_client(
        db_session_with_roles,
        "entreprise_test",
        "entreprise@test.com",
        "pass1234",
        "company",
    )
    yield ac
    await ac.aclose()


@pytest_asyncio.fixture
async def company_client_2(_db_override, db_session_with_roles):
    """Deuxième entreprise, pour le test d'isolation."""
    ac = await _authenticated_client(
        db_session_with_roles,
        "entreprise_test_2",
        "entreprise2@test.com",
        "pass1234",
        "company",
    )
    yield ac
    await ac.aclose()


@pytest_asyncio.fixture
async def manager_client(_db_override, db_session_with_roles):
    ac = await _authenticated_client(
        db_session_with_roles,
        "manager_test",
        "manager@test.com",
        "pass1234",
        "program_manager",
    )
    yield ac
    await ac.aclose()


@pytest_asyncio.fixture
async def admin_client(_db_override, db_session_with_roles):
    ac = await _authenticated_client(
        db_session_with_roles,
        "admin_test",
        "admin@test.com",
        "pass1234",
        "admin",
    )
    yield ac
    await ac.aclose()