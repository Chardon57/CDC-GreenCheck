"""Tests de services/image_service.py : normalisation des photos et stockage sur disque."""
import io
import os

import pytest
from PIL import Image

from config import storage
from services.image_service import (
    InvalidImageError,
    UnsupportedImageFormatError,
    delete_image,
    image_path,
    normalize_image,
    save_image,
)

ORIENTATION = 0x0112  # balise EXIF « Orientation »
GPS_IFD = 0x8825  # balise EXIF « position GPS »


def make_image(fmt="PNG", mode="RGB", size=(40, 20), color="green", exif=None) -> bytes:
    buffer = io.BytesIO()
    kwargs = {"exif": exif} if exif is not None else {}
    Image.new(mode, size, color).save(buffer, fmt, **kwargs)
    return buffer.getvalue()


def open_result(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data))


# --- normalize_image : cas acceptés -------------------------------------------------

@pytest.mark.parametrize("fmt", ["PNG", "JPEG", "WEBP"])
def test_formats_acceptes_deviennent_un_jpeg_rgb(fmt):
    result = open_result(normalize_image(make_image(fmt)))

    assert result.format == "JPEG"
    assert result.mode == "RGB"


def test_la_transparence_devient_blanche_et_non_noire():
    transparent = make_image("PNG", mode="RGBA", color=(0, 0, 0, 0))  # noir totalement transparent

    pixel = open_result(normalize_image(transparent)).getpixel((5, 5))

    assert all(canal > 240 for canal in pixel)


def test_l_orientation_exif_est_appliquee_aux_pixels():
    exif = Image.Exif()
    exif[ORIENTATION] = 6  # « à pivoter de 90° »
    data = make_image("JPEG", size=(40, 20), exif=exif)

    assert open_result(normalize_image(data)).size == (20, 40)


def test_les_metadonnees_exif_dont_le_gps_sont_supprimees():
    exif = Image.Exif()
    exif[0x010F] = "Fabricant secret"  # balise « Make »
    exif.get_ifd(GPS_IFD)[2] = (48.0, 35.0, 0.0)  # latitude
    data = make_image("JPEG", exif=exif)
    assert open_result(data).getexif()  # contrôle : l'EXIF était bien présent à l'entrée

    result = open_result(normalize_image(data))

    assert len(result.getexif()) == 0
    assert b"Fabricant secret" not in normalize_image(data)


def test_une_grande_image_est_reduite_en_conservant_les_proportions(monkeypatch):
    monkeypatch.setattr(storage, "IMAGE_MAX_SIDE", 100)

    result = open_result(normalize_image(make_image(size=(400, 200))))

    assert result.size == (100, 50)


def test_une_petite_image_n_est_jamais_agrandie(monkeypatch):
    monkeypatch.setattr(storage, "IMAGE_MAX_SIDE", 100)

    assert open_result(normalize_image(make_image(size=(40, 20)))).size == (40, 20)


# --- normalize_image : cas refusés --------------------------------------------------

@pytest.mark.parametrize(
    "data",
    [b"", b"du texte", b"%PDF-1.4 faux pdf", make_image("PNG")[:30]],
    ids=["vide", "texte", "pdf", "png-tronque"],
)
def test_fichier_illisible(data):
    with pytest.raises(InvalidImageError):
        normalize_image(data)


def test_png_dont_les_donnees_sont_corrompues():
    # Image « bruitée » : ses données ne se compressent pas en quelques octets, la corruption
    # tombe donc bien au milieu du flux de pixels.
    buffer = io.BytesIO()
    Image.frombytes("RGB", (100, 100), os.urandom(100 * 100 * 3)).save(buffer, "PNG")
    data = bytearray(buffer.getvalue())
    milieu = len(data) // 2
    data[milieu : milieu + 200] = b"\x00" * 200

    with pytest.raises(InvalidImageError):
        normalize_image(bytes(data))


@pytest.mark.parametrize("fmt", ["GIF", "BMP"])
def test_format_valide_mais_non_accepte(fmt):
    with pytest.raises(UnsupportedImageFormatError):
        normalize_image(make_image(fmt))


# --- Stockage -----------------------------------------------------------------------

@pytest.fixture()
def uploads(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "UPLOADS_DIR", tmp_path / "uploads")
    return tmp_path / "uploads"


def test_chemin_reconstruit_a_partir_des_identifiants(uploads):
    assert image_path(7, 42) == uploads / "7" / "42.jpg"


def test_les_identifiants_sont_convertis_en_entiers(uploads):
    """Garde-fou : un identifiant n'est jamais traité comme du texte (pas de « ../ »)."""
    with pytest.raises((ValueError, TypeError)):
        image_path("../../etc", 1)


def test_enregistrement_puis_suppression(uploads):
    path = save_image(b"contenu", 7, 42)

    assert path == uploads / "7" / "42.jpg"
    assert path.read_bytes() == b"contenu"

    delete_image(7, 42)
    assert not path.exists()


def test_suppression_d_une_image_absente_sans_erreur(uploads):
    delete_image(7, 999)  # ne doit pas lever d'exception
