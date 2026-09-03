from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base

if TYPE_CHECKING:
    from .analysis import Analysis


class User(Base):
    __tablename__ = "user"

    id_user: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    surname: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))

    analyses: Mapped[List["Analysis"]] = relationship(back_populates="user")