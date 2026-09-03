from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base

if TYPE_CHECKING:
    from .analysis import Analysis


class Plant(Base):
    __tablename__ = "plant"

    id_plant: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vernacular_name: Mapped[str] = mapped_column(String(255))
    official_name: Mapped[Optional[str]] = mapped_column(String(255))

    analyses: Mapped[List["Analysis"]] = relationship(back_populates="plant")