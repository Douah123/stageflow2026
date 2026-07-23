# app/core/security.py

from datetime import datetime, timedelta, timezone
from typing import Any
from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.core.config import settings

ALGORITHM = "HS256"


def create_access_token(
    subject: str | int,
    extra_data: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Génère un JWT d'accès."""
    if expires_delta is None:
        expires_delta = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    expire = datetime.now(timezone.utc) + expires_delta

    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    if extra_data:
        payload.update(extra_data)
    return jwt.encode(
        payload, settings.SECRET_KEY, algorithm=ALGORITHM
    )


def create_refresh_token(subject: str | int) -> str:
    """Génère un JWT de rafraîchissement (durée longue)."""
    expires_delta = timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(
        payload, settings.SECRET_KEY, algorithm=ALGORITHM
    )


def decode_token(token: str) -> dict[str, Any]:
    """Décode et valide un JWT. Lève une exception si invalide."""
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token invalide: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )