# app/schemas/offre.py

import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class OffreBase(BaseModel):
    titre: str = Field(min_length=3, max_length=200)
    mission: str = Field(min_length=10)
    competences: list[str] = Field(min_length=1)

    @field_validator("competences")
    @classmethod
    def nettoyer_competences(cls, v: list[str]) -> list[str]:
        """Normalise la casse et supprime les doublons."""
        nettoyees = sorted({c.strip().lower() for c in v if c.strip()})
        if not nettoyees:
            raise ValueError("Au moins une compétence valide est requise")
        return nettoyees


class OffreCreate(OffreBase):
    pass  # entreprise_id vient du token JWT, jamais du body


class OffreUpdate(BaseModel):
    """Mise à jour partielle d'une offre en brouillon."""

    titre: Optional[str] = Field(None, min_length=3, max_length=200)
    mission: Optional[str] = Field(None, min_length=10)
    competences: Optional[list[str]] = Field(None, min_length=1)


class OffreReview(BaseModel):
    decision: Literal["publish", "reject"]


class OffreResponse(OffreBase):
    id: int
    statut: str
    entreprise_id: int
    created_at: datetime.datetime

    model_config = {"from_attributes": True}