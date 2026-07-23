from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.permissions import CurrentUser
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.db.session import get_db
from app.repositories.role import RoleRepository
from app.repositories.user import UserRepository
from app.schemas.auth import Token, TokenRefresh, UserRegister
from app.schemas.user import UserCreate, UserResponse
from app.utils.hashing import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentification"])

DBSession = Annotated[AsyncSession, Depends(get_db)]


@router.post("/register", status_code=201)
async def register(data: UserRegister, db: DBSession):
    """Inscription d'un nouvel utilisateur."""
    repo = UserRepository(db)

    if await repo.get_by_email(data.email):
        raise HTTPException(409, "Email déjà utilisé")
    if await repo.get_by_username(data.username):
        raise HTTPException(409, "Nom d'utilisateur déjà pris")

    role_repo = RoleRepository(db)
    role = await role_repo.get_by_name(data.role)
    if role is None:
        raise HTTPException(400, "Rôle invalide")

    hashed_pw = hash_password(data.password)
    user_data = UserCreate(
        username=data.username,
        email=data.email,
        hashed_password=hashed_pw,
        role_id=role.id,
    )
    user = await repo.create(user_data)
    return {"message": "Compte créé avec succès", "user_id": user.id}


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DBSession,
):
    """Connexion - retourne un token JWT (compatible OAuth2)."""
    repo = UserRepository(db)
    user = await repo.get_by_username(form_data.username)

    # IMPORTANT : ne pas révéler si c'est le username ou le password qui est faux
    if not user or not verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(400, "Compte désactivé")

    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=Token)
async def refresh(data: TokenRefresh, db: DBSession):
    """Renouveler un token d'accès via le refresh token."""
    payload = decode_token(data.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(401, "Token de rafraîchissement invalide")

    user_id = payload["sub"]
    repo = UserRepository(db)
    user = await repo.get(int(user_id))
    if not user or not user.est_actif:
        raise HTTPException(401, "Utilisateur introuvable ou inactif")

    new_access = create_access_token(subject=user.id)
    new_refresh = create_refresh_token(subject=user.id)
    return Token(
        access_token=new_access,
        refresh_token=new_refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


router_users = APIRouter(tags=["Users"])


@router_users.get("/users/me", response_model=UserResponse)
async def read_me(current_user: CurrentUser):
    """Profil de l'utilisateur authentifié."""
    return current_user