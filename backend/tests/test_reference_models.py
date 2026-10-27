"""Tests des tables de référence : disease, treatment, result et leurs relations."""
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models.disease import Disease
from models.result import Result
from models.treatment import Treatment


def test_une_maladie_a_plusieurs_conseils(session):
    disease = Disease(
        name="Oïdium",
        treatments=[Treatment(advice="Conseil A"), Treatment(advice="Conseil B")],
    )
    session.add(disease)
    session.commit()

    assert {t.advice for t in disease.treatments} == {"Conseil A", "Conseil B"}


def test_un_meme_conseil_peut_servir_a_plusieurs_maladies(session):
    isoler = Treatment(advice="Isoler la plante des autres.")
    rouille = Disease(name="Rouille", treatments=[isoler])
    oidium = Disease(name="Oïdium", treatments=[isoler])
    session.add_all([rouille, oidium])
    session.commit()

    assert session.scalars(select(Treatment)).all() == [isoler]  # une seule ligne en base
    assert {d.name for d in isoler.diseases} == {"Rouille", "Oïdium"}


def test_le_nom_dune_maladie_est_unique(session):
    session.add(Disease(name="Rouille"))
    session.commit()

    session.add(Disease(name="Rouille"))
    with pytest.raises(IntegrityError):
        session.commit()


def test_un_resultat_porte_un_etat_et_une_maladie(session):
    disease = Disease(name="Oïdium")
    result = Result(label="Malade", disease=disease)
    session.add(result)
    session.commit()

    assert result.id_disease == disease.id_disease
    assert disease.results == [result]


def test_un_resultat_sans_maladie_est_refuse(session):
    session.add(Result(label="Sain"))  # id_disease est obligatoire

    with pytest.raises(IntegrityError):
        session.commit()
