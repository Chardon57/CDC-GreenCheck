"""Cœur du moteur : transforme « une image » en « un diagnostic + une confiance ».

Ce fichier ne contient AUCUNE dépendance à PyTorch ni à Hugging Face : il reçoit un « embedder »
(voir siglip_embedder.py) qui sait convertir du texte et des images en vecteurs de nombres.
Grâce à cela, la logique de décision se teste avec de faux vecteurs, sans télécharger de modèle.

Rappel du principe (zero-shot) :
  1. au démarrage, chaque phrase de labels.py est convertie en vecteur (une seule fois) ;
  2. pour chaque photo reçue, on la convertit en vecteur et on mesure sa ressemblance avec
     chaque phrase (produit scalaire de vecteurs normalisés = similarité cosinus) ;
  3. on fait la moyenne des ressemblances des phrases de chaque diagnostic ;
  4. un softmax transforme les 12 scores en pourcentages qui totalisent 100 % ;
     le diagnostic au pourcentage le plus élevé gagne, et ce pourcentage est la `confidence`.
"""

from dataclasses import dataclass
from threading import Lock
from typing import Protocol

import numpy as np
from PIL import Image


class Embedder(Protocol):
    """Ce qu'on attend d'un modèle : convertir texte et image en vecteurs normalisés."""

    # Facteur multiplicateur appris par le modèle (« température » inverse). Il rend les
    # écarts de similarité plus nets avant le softmax. Le biais, lui aussi appris, est le même
    # pour tous les diagnostics : il s'annule dans le softmax, on l'ignore.
    logit_scale: float

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """Renvoie un tableau (nombre_de_textes, dimension), chaque ligne de norme 1."""
        ...

    def embed_image(self, image: Image.Image) -> np.ndarray:
        """Renvoie un vecteur (dimension,) de norme 1."""
        ...


@dataclass(frozen=True)
class Diagnosis:
    label: str  # nom exact d'une maladie de la table `disease`
    confidence: float  # part (0 à 1) de ce diagnostic parmi les 12 possibles


class Diagnoser:
    def __init__(self, embedder: Embedder, diagnostics: dict[str, list[str]]) -> None:
        if not diagnostics:
            raise ValueError("Aucun diagnostic fourni.")

        prompts: list[str] = []
        owner: list[int] = []  # owner[i] = indice du diagnostic auquel appartient la phrase i
        for index, (name, phrases) in enumerate(diagnostics.items()):
            if not phrases:
                raise ValueError(f"Le diagnostic {name!r} n'a aucune phrase de description.")
            prompts.extend(phrases)
            owner.extend([index] * len(phrases))

        self._embedder = embedder
        self._labels = list(diagnostics)
        self._owner = np.array(owner)
        # Calculé UNE fois au démarrage : le texte ne change pas d'une photo à l'autre.
        self._text_embeds = embedder.embed_texts(prompts)
        # Un seul calcul à la fois sur le modèle (projet de petite taille, GPU/CPU unique).
        self._lock = Lock()

    def diagnose(self, image: Image.Image) -> Diagnosis:
        with self._lock:
            image_embed = self._embedder.embed_image(image)

        similarities = self._text_embeds @ image_embed  # une valeur par phrase
        logits = self._embedder.logit_scale * similarities

        per_label = np.array(
            [logits[self._owner == i].mean() for i in range(len(self._labels))]
        )

        # Softmax (en retirant le max avant exp() pour éviter les débordements numériques)
        exp = np.exp(per_label - per_label.max())
        probabilities = exp / exp.sum()

        best = int(probabilities.argmax())
        return Diagnosis(label=self._labels[best], confidence=float(probabilities[best]))
