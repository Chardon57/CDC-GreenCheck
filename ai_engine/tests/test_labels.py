"""Vérifie la liste des diagnostics du moteur (labels.py)."""

import re
from pathlib import Path

import pytest

from labels import DIAGNOSTICS

SEED_SQL = Path(__file__).resolve().parents[2] / "seed_diagnostics.sql"


def test_douze_diagnostics():
    assert len(DIAGNOSTICS) == 12


def test_chaque_diagnostic_a_au_moins_deux_phrases():
    for nom, phrases in DIAGNOSTICS.items():
        assert len(phrases) >= 2, nom
        assert all(isinstance(p, str) and p.strip() for p in phrases), nom


def test_aucune_phrase_en_double():
    toutes = [p for phrases in DIAGNOSTICS.values() for p in phrases]
    assert len(toutes) == len(set(toutes))


def _noms_du_seed() -> list[str]:
    """Extrait les noms de maladies du bloc INSERT INTO seed_disease de seed_diagnostics.sql."""
    texte = SEED_SQL.read_text(encoding="utf-8")
    bloc = re.search(r"INSERT INTO seed_disease.*?;", texte, re.S).group(0)
    # Chaque ligne ressemble à : ('Excès d''arrosage', 'Attention')
    noms = re.findall(r"\('((?:[^']|'')*)',\s*'", bloc)
    return [n.replace("''", "'") for n in noms]


@pytest.mark.skipif(not SEED_SQL.exists(), reason="seed_diagnostics.sql introuvable (hors dépôt)")
def test_labels_identiques_a_la_table_disease_du_seed():
    """Le moteur doit renvoyer EXACTEMENT les noms que le backend retrouvera en base."""
    assert sorted(DIAGNOSTICS) == sorted(_noms_du_seed())
