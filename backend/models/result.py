from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base
from .associations import impliquer

if TYPE_CHECKING:
    from .analysis import Analysis
    from .treatment import Treatment


class Result(Base):
    __tablename__ = "result"

    id_result: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    label: Mapped[str] = mapped_column(String(255))

    analyses: Mapped[List["Analysis"]] = relationship(back_populates="result")
    treatments: Mapped[List["Treatment"]] = relationship(secondary=impliquer, back_populates="results")
    