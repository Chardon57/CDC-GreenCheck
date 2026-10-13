"""Tests de la logique de décision, avec un faux modèle (aucun téléchargement)."""

import numpy as np
import pytest

from diagnoser import Diagnoser


class FakeEmbedder:
    """Un « modèle » à 3 dimensions où chaque phrase est un vecteur choisi à la main."""

    def __init__(self, text_vectors: dict[str, list[float]], image_vector: list[float], scale=1.0):
        self._text_vectors = text_vectors
        self._image_vector = np.array(image_vector, dtype=np.float32)
        self.logit_scale = scale

    @staticmethod
    def _unit(v):
        v = np.array(v, dtype=np.float32)
        return v / np.linalg.norm(v)

    def embed_texts(self, texts):
        return np.stack([self._unit(self._text_vectors[t]) for t in texts])

    def embed_image(self, image):
        return self._unit(self._image_vector)


DIAGNOSTICS = {
    "A": ["phrase a1", "phrase a2"],
    "B": ["phrase b1", "phrase b2"],
    "C": ["phrase c1", "phrase c2"],
}

VECTORS = {
    "phrase a1": [1, 0, 0], "phrase a2": [1, 0.1, 0],
    "phrase b1": [0, 1, 0], "phrase b2": [0.1, 1, 0],
    "phrase c1": [0, 0, 1], "phrase c2": [0, 0.1, 1],
}


def test_choisit_le_diagnostic_le_plus_proche_de_l_image():
    embedder = FakeEmbedder(VECTORS, image_vector=[0, 1, 0.1], scale=10.0)
    result = Diagnoser(embedder, DIAGNOSTICS).diagnose(image=None)
    assert result.label == "B"


def test_confiance_entre_0_et_1_et_plus_nette_si_la_photo_est_sans_ambiguite():
    clair = Diagnoser(FakeEmbedder(VECTORS, [0, 1, 0], scale=10.0), DIAGNOSTICS).diagnose(None)
    ambigu = Diagnoser(FakeEmbedder(VECTORS, [0, 1, 0.9], scale=10.0), DIAGNOSTICS).diagnose(None)
    assert 0.0 <= ambigu.confidence <= clair.confidence <= 1.0
    assert clair.confidence > ambigu.confidence


def test_confiance_egale_a_un_sur_n_quand_rien_ne_distingue_les_diagnostics():
    # Image équidistante des trois diagnostics -> 3 diagnostics équiprobables.
    embedder = FakeEmbedder(VECTORS, [1, 1, 1], scale=10.0)
    result = Diagnoser(embedder, DIAGNOSTICS).diagnose(None)
    assert result.confidence == pytest.approx(1 / 3, abs=0.01)


def test_les_phrases_d_un_diagnostic_sont_moyennees():
    # A a une phrase très proche de l'image et une très éloignée ; B a deux phrases moyennes.
    # En moyenne, B doit l'emporter : une seule bonne phrase ne suffit pas.
    vectors = {
        "a-proche": [1, 0, 0], "a-loin": [-1, 0, 0],
        "b1": [1, 1, 0], "b2": [1, 1, 0],
    }
    diagnostics = {"A": ["a-proche", "a-loin"], "B": ["b1", "b2"]}
    embedder = FakeEmbedder(vectors, image_vector=[1, 0, 0], scale=5.0)
    assert Diagnoser(embedder, diagnostics).diagnose(None).label == "B"


def test_le_facteur_d_echelle_rend_la_decision_plus_tranchee():
    peu = Diagnoser(FakeEmbedder(VECTORS, [0, 1, 0.5], scale=1.0), DIAGNOSTICS).diagnose(None)
    beaucoup = Diagnoser(FakeEmbedder(VECTORS, [0, 1, 0.5], scale=50.0), DIAGNOSTICS).diagnose(None)
    assert beaucoup.confidence > peu.confidence


def test_pas_de_debordement_avec_de_tres_grands_scores():
    result = Diagnoser(FakeEmbedder(VECTORS, [0, 1, 0], scale=1e4), DIAGNOSTICS).diagnose(None)
    assert result.label == "B"
    assert result.confidence == pytest.approx(1.0)


def test_diagnostics_vides_refuses():
    embedder = FakeEmbedder(VECTORS, [1, 0, 0])
    with pytest.raises(ValueError):
        Diagnoser(embedder, {})
    with pytest.raises(ValueError):
        Diagnoser(embedder, {"A": []})
