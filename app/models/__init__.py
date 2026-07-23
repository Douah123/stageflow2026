# app/models/__init__.py

from app.models.role import Role
from app.models.user import User
from app.models.offre import Offre
from app.models.candidature import Candidature

__all__ = ["Role", "User", "Offre", "Candidature"]