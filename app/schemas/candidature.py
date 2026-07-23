import datetime
from typing import Literal

from pydantic import BaseModel


class CandidatureCreate(BaseModel):
    pass  # offre_id vient de l'URL, etudiant_id du token


class CandidatureDecision(BaseModel):
    decision: Literal["accepted", "rejected"]


class CandidatureResponse(BaseModel):
    id: int
    statut: str
    offre_id: int
    etudiant_id: int
    created_at: datetime.datetime

    model_config = {"from_attributes": True}