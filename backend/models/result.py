from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base

if TYPE_CHECKING:
    from .analysis import Analysis
    from .disease import Disease


class Result(Base):
    __tablename__ = "result"

    id_result: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # État de la plante affiché à l'utilisateur : « Sain », « Attention » ou « Malade »
    label: Mapped[str] = mapped_column(String(255))

    id_disease: Mapped[int] = mapped_column(ForeignKey("disease.id_disease", ondelete="RESTRICT"))

    disease: Mapped["Disease"] = relationship(back_populates="results")
    analyses: Mapped[List["Analysis"]] = relationship(back_populates="result")
