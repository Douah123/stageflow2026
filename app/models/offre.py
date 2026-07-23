from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.db.types import JSONEncodedList
import datetime
from app.utils.time import utcnow
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.models.user import User
    from app.models.candidature import Candidature
class Offre(Base):
    __tablename__ = "offres"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    titre: Mapped[str] = mapped_column(String(200))
    mission: Mapped[str] = mapped_column(Text)
    competences: Mapped[list[str]] = mapped_column(JSONEncodedList)
    statut: Mapped[str] = mapped_column(String(20), default="draft")
    entreprise_id: Mapped[int] = mapped_column(ForeignKey("utilisateurs.id"))
    created_at : Mapped[datetime.datetime] = mapped_column(default = utcnow)
    updated_at : Mapped[datetime.datetime | None ] = mapped_column(nullable = True )

    entreprise: Mapped["User"] = relationship(back_populates="offres")
    candidatures: Mapped[list["Candidature"]] = relationship(
        back_populates="offre",
        lazy="selectin",
    )