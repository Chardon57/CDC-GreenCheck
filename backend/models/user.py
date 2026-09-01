from typing import TYPE_CHECKING, List, Optional
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .analysis import Analysis


class User(SQLModel, table=True):
    __tablename__ = "user"

    id_user: Optional[int] = Field(default=None, primary_key=True)
    surname: str = Field(max_length=255)
    name: str = Field(max_length=255)
    email: str = Field(max_length=255, unique=True)
    password: str = Field(max_length=255)

    analyses: List["Analysis"] = Relationship(back_populates="user")