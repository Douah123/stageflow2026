from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.role import Role
from app.utils.time import utcnow
from typing import TYPE_CHECKING
import datetime

if TYPE_CHECKING:
    from app.models.offre import Offre
    from app.models.user import User
class Candidature(Base):
    __tablename__ = "candidatures"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    statut: Mapped[str] = mapped_column(String(20), default="pending")
    offre_id: Mapped[int] = mapped_column(ForeignKey("offres.id"))
    etudiant_id: Mapped[int] = mapped_column(ForeignKey("utilisateurs.id"))
    created_at : Mapped[datetime.datetime] = mapped_column(default = utcnow)
    updated_at : Mapped[datetime.datetime | None ] = mapped_column(nullable = True )

    offre: Mapped["Offre"] = relationship(back_populates="candidatures")
    etudiant: Mapped["User"] = relationship(back_populates="candidatures")