from sqlalchemy import Column, ForeignKey, Table

from config.database import Base

# Association « traiter » : une maladie se soigne avec plusieurs conseils, et un même conseil peut servir pour plusieurs maladies.
traiter = Table(
    "traiter",
    Base.metadata,
    Column("id_disease", ForeignKey("disease.id_disease", ondelete="CASCADE"), primary_key=True),
    Column("id_treatment", ForeignKey("treatment.id_treatment", ondelete="CASCADE"), primary_key=True),
)
