from pydantic import BaseModel, EmailStr
import datetime
from app.schemas.role import RoleResponse
from typing import Optional

class UserCreate(BaseModel):
    """
    Champs exacts du modèle User, utilisés par
    repo.create(). Ne vient jamais du body brut du
    client : role_id et hashed_password sont calculés
    dans la route avant construction de ce schéma.
    """

    username: str
    email: EmailStr
    hashed_password: str
    role_id: int

class UserResponse(BaseModel):
    """
    Profil public renvoyé par GET /users/me.
    Ne contient jamais mot_de_passe_hache.
    """

    id: int
    username: str
    email: EmailStr
    is_active: bool
    role: RoleResponse
    created_at: datetime.datetime

    model_config = {"from_attributes": True}

class UserUpdate(BaseModel):
    """Réservé à l'admin : changement de rôle ou d'activation."""

    role_id: Optional[int] = None
    is_active: Optional[bool] = None