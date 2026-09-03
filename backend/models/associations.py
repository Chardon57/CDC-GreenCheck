from sqlalchemy import Column, ForeignKey, Table

from config.database import Base

impliquer = Table(
    "impliquer",
    Base.metadata,
    Column("id_result", ForeignKey("result.id_result", ondelete="CASCADE"), primary_key=True),
    Column("id_treatment", ForeignKey("treatment.id_treatment", ondelete="CASCADE"), primary_key=True),
)