from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base
from .associations import impliquer

if TYPE_CHECKING:
    from .result import Result


class Treatment(Base):
    __tablename__ = "treatment"

    id_treatment: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    advice: Mapped[str] = mapped_column(String(255))

    results: Mapped[List["Result"]] = relationship(secondary=impliquer, back_populates="treatments")