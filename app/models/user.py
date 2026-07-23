from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.role import Role
import datetime
from app.utils.time import utcnow
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.offre import Offre
    from app.models.candidature import Candidature


class User(Base):
    __tablename__ = "utilisateurs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password : Mapped[str] = mapped_column(String(255))
    is_active : Mapped[bool] = mapped_column(Boolean , default=True)
    created_at : Mapped[datetime.datetime] = mapped_column(default = utcnow)
    updated_at : Mapped[datetime.datetime | None ] = mapped_column(nullable = True )
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    role: Mapped["Role"] = relationship(lazy="selectin")

    offres: Mapped[list["Offre"]] = relationship(
        back_populates="entreprise",
        lazy="selectin",
    )

    candidatures: Mapped[list["Candidature"]] = relationship(
        back_populates="etudiant",
        lazy="selectin",
    )