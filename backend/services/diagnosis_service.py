# Client du moteur IA de diagnostic (conteneur ai_engine) : état de santé d'une plante à partir d'une photo.
import logging
from dataclasses import dataclass

import httpx2

from config.engine import ENGINE_TIMEOUT, ENGINE_URL

logger = logging.getLogger(__name__)


class DiagnosisError(Exception):
    """Classe de base des erreurs liées au moteur de diagnostic."""


class DiagnosisImageRejectedError(DiagnosisError):
    """Le moteur a refusé l'image (type non supporté, trop volumineuse, illisible)."""


class DiagnosisUnavailableError(DiagnosisError):
    """Le moteur est injoignable, en erreur, ou a renvoyé une réponse inexploitable."""


@dataclass(frozen=True)
class PlantDiagnosis:
    label: str  # nom exact d'une maladie de la table `disease`
    confidence: float  # entre 0 et 1


def diagnose_plant(
        image: bytes,
        filename: str = "image.jpg",
        content_type: str = "image/jpeg",
        *,
        client: httpx2.Client | None = None,
    ) -> PlantDiagnosis:
    """Demande au moteur IA le diagnostic de la plante photographiée.

    `client` permet d'injecter un client HTTP préconfiguré (utilisé par les tests pour
    simuler le moteur sans aucun appel réseau).
    """
    owns_client = client is None
    if client is None:
        client = httpx2.Client(timeout=ENGINE_TIMEOUT)
    try:
        response = _send(client, image, filename, content_type)
    finally:
        if owns_client:
            client.close()
    return _parse(response)


def _send(client: httpx2.Client, image: bytes, filename: str, content_type: str) -> httpx2.Response:
    try:
        return client.post(
            f"{ENGINE_URL}/diagnose",
            files={"image": (filename, image, content_type)},
        )
    except httpx2.RequestError as exc:
        # Couvre moteur éteint, réseau coupé et délai dépassé.
        logger.error("Moteur IA injoignable (%s).", type(exc).__name__)
        raise DiagnosisUnavailableError("Service de diagnostic injoignable.") from None


def _parse(response: httpx2.Response) -> PlantDiagnosis:
    status = response.status_code

    if status in (413, 415, 422):
        # L'image elle-même pose problème : ce n'est pas une panne du moteur.
        logger.warning("Image refusée par le moteur IA (HTTP %s).", status)
        raise DiagnosisImageRejectedError("Image refusée par le service de diagnostic.")
    if status != 200:
        logger.error("Réponse inattendue du moteur IA (HTTP %s).", status)
        raise DiagnosisUnavailableError("Service de diagnostic en erreur.")

    try:
        data = response.json()
        label = data["label"]
        confidence = float(data["confidence"])
        if not isinstance(label, str) or not label.strip() or not 0.0 <= confidence <= 1.0:
            raise ValueError
    except (ValueError, KeyError, TypeError):
        logger.error("Réponse du moteur IA illisible (structure inattendue).")
        raise DiagnosisUnavailableError("Réponse du service de diagnostic illisible.") from None

    return PlantDiagnosis(label=label, confidence=confidence)
