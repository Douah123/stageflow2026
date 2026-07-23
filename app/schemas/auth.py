# app.schemas.auth.py

from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    """Ce que le client envoie : mot de passe en clair."""

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    role: Literal["student", "company"]

    @field_validator("username")
    @classmethod
    def username_sans_espaces(cls, v: str) -> str:
        """
        Un username avec des espaces casserait les
        mentions/URLs côté frontend plus tard.
        """
        v = v.strip()
        if " " in v:
            raise ValueError(
                "Le nom d'utilisateur ne peut pas contenir d'espaces"
            )
        return v

    @field_validator("password")
    @classmethod
    def password_pas_trivial(cls, v: str) -> str:
        """
        Validation minimale de robustesse, dans l'esprit
        de la séance 3 (field_validator), sans aller vers
        une politique de mots de passe complexe hors-sujet.
        """
        if v.lower() in {"password", "12345678"}:
            raise ValueError("Ce mot de passe est trop courant")
        return v


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int # Secondes

class TokenRefresh(BaseModel):
    refresh_token: str