# Client de l'API Pl@ntNet : identification de l'espèce d'une plante à partir d'une photo.
import logging
from dataclasses import dataclass

import httpx2

from config.plantnet import (
    PLANTNET_API_KEY,
    PLANTNET_BASE_URL,
    PLANTNET_MIN_SCORE,
    PLANTNET_TIMEOUT,
)

logger = logging.getLogger(__name__)

# Pl@ntNet reçoit la clé API dans l'URL (?api-key=...). httpx2 journalise l'URL complète de chaque requête au niveau INFO : on le limite à WARNING pour que la clé n'atterrisse jamais dans les logs.
logging.getLogger("httpx2").setLevel(logging.WARNING)
logging.getLogger("httpcore2").setLevel(logging.WARNING)


class PlantNetError(Exception):
    """Classe de base des erreurs liées à Pl@ntNet."""


class PlantNotRecognizedError(PlantNetError):
    """Aucune plante identifiable sur l'image (ou identification trop peu fiable)."""


class PlantNetUnavailableError(PlantNetError):
    """Pl@ntNet est injoignable, en erreur, ou a refusé la requête (clé invalide, quota dépassé...)."""


@dataclass(frozen=True)
class PlantIdentification:
    vernacular_name: str
    official_name: str
    score: float
    family: str | None = None  # famille botanique (latin), absente de certaines réponses


def identify_plant(
        image: bytes,
        filename: str = "image.jpg",
        content_type: str = "image/jpeg",
        *,
        client: httpx2.Client | None = None,
    ) -> PlantIdentification:
    """Identifie l'espèce de la plante photographiée.

    `client` permet d'injecter un client HTTP préconfiguré (utilisé par les tests pour
    simuler Pl@ntNet sans aucun appel réseau).
    """
    owns_client = client is None
    if client is None:
        client = httpx2.Client(timeout=PLANTNET_TIMEOUT)
    try:
        response = _send(client, image, filename, content_type)
    finally:
        if owns_client:
            client.close()
    return _parse(response)


def _send(client: httpx2.Client, image: bytes, filename: str, content_type: str) -> httpx2.Response:
    try:
        return client.post(
            f"{PLANTNET_BASE_URL}/v2/identify/all",
            params={"api-key": PLANTNET_API_KEY, "lang": "fr", "nb-results": 1},
            files={"images": (filename, image, content_type)},
        )
    except httpx2.RequestError as exc:
        # On ne journalise que le type de l'erreur : son message pourrait contenir l'URL, donc la clé API.
        logger.error("Pl@ntNet injoignable (%s).", type(exc).__name__)
        raise PlantNetUnavailableError("Service d'identification injoignable.") from None


def _parse(response: httpx2.Response) -> PlantIdentification:
    status = response.status_code

    if status == 404:
        raise PlantNotRecognizedError("Aucune plante identifiable sur cette image.")
    if status in (401, 403):
        logger.error("Pl@ntNet a refusé la clé API (HTTP %s).", status)
        raise PlantNetUnavailableError("Service d'identification mal configuré.")
    if status == 429:
        logger.warning("Quota Pl@ntNet dépassé (HTTP 429).")
        raise PlantNetUnavailableError("Quota d'identification dépassé.")
    if status != 200:
        logger.error("Réponse inattendue de Pl@ntNet (HTTP %s).", status)
        raise PlantNetUnavailableError("Service d'identification en erreur.")

    try:
        results = response.json()["results"]
        if not results:
            raise PlantNotRecognizedError("Aucune plante identifiable sur cette image.")
        best = results[0]
        score = float(best["score"])
        species = best["species"]
        official_name = species["scientificNameWithoutAuthor"]
        common_names = species.get("commonNames") or []
        family = (species.get("family") or {}).get("scientificNameWithoutAuthor")
    except PlantNotRecognizedError:
        raise
    except (ValueError, KeyError, TypeError, IndexError):
        logger.error("Réponse Pl@ntNet illisible (structure inattendue).")
        raise PlantNetUnavailableError("Réponse du service d'identification illisible.") from None

    if score < PLANTNET_MIN_SCORE:
        raise PlantNotRecognizedError("Identification trop peu fiable.")

    return PlantIdentification(
        # Pas de nom courant connu : on retombe sur le nom scientifique plutôt que de laisser le champ vide.
        vernacular_name=common_names[0] if common_names else official_name,
        official_name=official_name,
        score=score,
        family=family,
    )
