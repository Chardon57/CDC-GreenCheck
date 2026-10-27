# Traitement et stockage des photos envoyées par les utilisateurs.
#
# Toute photo reçue est « normalisée » : décodée, remise à l'endroit, réduite si elle est trop
# grande, et ré-encodée en JPEG sans métadonnées (EXIF). C'est cette version qui est envoyée à
# Pl@ntNet et au moteur IA, puis stockée sur disque.
import io
import logging
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from config import storage

logger = logging.getLogger(__name__)

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


class ImageError(Exception):
    """Classe de base des erreurs liées aux photos."""


class InvalidImageError(ImageError):
    """Le fichier n'est pas une image lisible (vide, corrompu, tronqué, autre type de fichier)."""


class UnsupportedImageFormatError(ImageError):
    """Image valide, mais dans un format non accepté (par exemple GIF ou BMP)."""


def normalize_image(raw: bytes) -> bytes:
    """Renvoie la photo sous forme d'un JPEG RGB, orienté correctement, sans métadonnées."""
    try:
        with Image.open(io.BytesIO(raw)) as source:
            if source.format not in ALLOWED_FORMATS:
                raise UnsupportedImageFormatError(f"Format {source.format!r} non accepté.")
            # Les photos de téléphone sont souvent stockées « couchées » avec une indication
            # d'orientation dans l'EXIF : on l'applique réellement aux pixels.
            image = ImageOps.exif_transpose(source)
            # La conversion lit tous les pixels : une image tronquée ou corrompue échoue ici.
            image = _to_rgb(image)
    except ImageError:
        raise
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise InvalidImageError("Fichier image illisible ou corrompu.") from None

    # Seul le dessous de la limite est conservé : une photo plus petite n'est jamais agrandie.
    image.thumbnail((storage.IMAGE_MAX_SIDE, storage.IMAGE_MAX_SIDE), Image.Resampling.LANCZOS)

    buffer = io.BytesIO()
    # On ne passe volontairement pas `exif=` : les métadonnées (dont la position GPS) sont perdues.
    image.save(buffer, "JPEG", quality=storage.JPEG_QUALITY, optimize=True)
    return buffer.getvalue()


def _to_rgb(image: Image.Image) -> Image.Image:
    """Convertit en RGB ; les zones transparentes (PNG, WebP) deviennent blanches, pas noires."""
    if image.mode in ("RGBA", "LA") or "transparency" in image.info:
        rgba = image.convert("RGBA")
        fond = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        return Image.alpha_composite(fond, rgba).convert("RGB")
    return image.convert("RGB")


# --- Stockage -----------------------------------------------------------------------
# Le chemin est reconstruit à partir de deux entiers (jamais d'un nom fourni par l'utilisateur) :
# aucun risque de sortir du dossier d'envoi.

def image_path(id_user: int, id_analysis: int) -> Path:
    return storage.UPLOADS_DIR / str(int(id_user)) / f"{int(id_analysis)}.jpg"


def save_image(jpeg: bytes, id_user: int, id_analysis: int) -> Path:
    path = image_path(id_user, id_analysis)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(jpeg)
    return path


def delete_image(id_user: int, id_analysis: int) -> None:
    """Supprime la photo si elle existe (sans erreur dans le cas contraire)."""
    image_path(id_user, id_analysis).unlink(missing_ok=True)
