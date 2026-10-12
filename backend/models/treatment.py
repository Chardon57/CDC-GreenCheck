from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base
from .associations import traiter

if TYPE_CHECKING:
    from .disease import Disease


class Treatment(Base):
    __tablename__ = "treatment"

    id_treatment: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    advice: Mapped[str] = mapped_column(String(255))

    diseases: Mapped[List["Disease"]] = relationship(secondary=traiter, back_populates="treatments")
