from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base
from .associations import traiter

if TYPE_CHECKING:
    from .result import Result
    from .treatment import Treatment


class Disease(Base):
    __tablename__ = "disease"

    id_disease: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    results: Mapped[List["Result"]] = relationship(back_populates="disease")
    treatments: Mapped[List["Treatment"]] = relationship(secondary=traiter, back_populates="diseases")
