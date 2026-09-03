from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base

if TYPE_CHECKING:
    from .user import User
    from .plant import Plant
    from .result import Result


class Analysis(Base):
    __tablename__ = "analysis"

    id_analysis: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[datetime]
    plant_location: Mapped[Optional[str]] = mapped_column(String(255))
    plant_exposition: Mapped[Optional[str]] = mapped_column(String(255))
    confidence: Mapped[float] = mapped_column(Float)

    id_user: Mapped[int] = mapped_column(ForeignKey("user.id_user", ondelete="CASCADE"))
    id_plant: Mapped[int] = mapped_column(ForeignKey("plant.id_plant", ondelete="RESTRICT"))
    id_result: Mapped[int] = mapped_column(ForeignKey("result.id_result", ondelete="RESTRICT"))

    user: Mapped["User"] = relationship(back_populates="analyses")
    plant: Mapped["Plant"] = relationship(back_populates="analyses")
    result: Mapped["Result"] = relationship(back_populates="analyses")