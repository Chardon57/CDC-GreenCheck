"""Tests de l'API (POST /diagnose, GET /health) avec un faux diagnostiqueur."""

import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

import app as app_module
from app import app, get_diagnoser
from diagnoser import Diagnosis


class FakeDiagnoser:
    def __init__(self):
        self.received = []

    def diagnose(self, image):
        self.received.append(image)
        return Diagnosis(label="Oïdium", confidence=0.87)


@pytest.fixture
def fake():
    return FakeDiagnoser()


@pytest.fixture
def client(fake):
    app.dependency_overrides[get_diagnoser] = lambda: fake
    # Pas de `with` : le lifespan (qui chargerait le vrai modèle) ne doit pas s'exécuter.
    yield TestClient(app)
    app.dependency_overrides.clear()


def _image_bytes(fmt="PNG", mode="RGB", size=(40, 20), exif_orientation=None) -> bytes:
    buffer = io.BytesIO()
    image = Image.new(mode, size, "green")
    kwargs = {}
    if exif_orientation:
        exif = Image.Exif()
        exif[0x0112] = exif_orientation  # 0x0112 = balise « Orientation »
        kwargs["exif"] = exif
    image.save(buffer, fmt, **kwargs)
    return buffer.getvalue()


def _post(client, data: bytes, content_type="image/png", field="image"):
    return client.post("/diagnose", files={field: ("plante.png", data, content_type)})


def test_diagnose_ok(client, fake):
    response = _post(client, _image_bytes())
    assert response.status_code == 200
    assert response.json() == {"label": "Oïdium", "confidence": 0.87}
    assert len(fake.received) == 1


def test_diagnose_accepte_jpeg_et_webp(client):
    assert _post(client, _image_bytes("JPEG"), "image/jpeg").status_code == 200
    assert _post(client, _image_bytes("WEBP"), "image/webp").status_code == 200


def test_le_modele_recoit_une_image_rgb(client, fake):
    _post(client, _image_bytes(mode="RGBA"))
    assert fake.received[0].mode == "RGB"


def test_l_orientation_exif_est_appliquee(client, fake):
    # Image 40x20 marquée « à pivoter de 90° » (orientation 6) : elle doit arriver en 20x40.
    _post(client, _image_bytes("JPEG", exif_orientation=6), "image/jpeg")
    assert fake.received[0].size == (20, 40)


def test_type_non_supporte_415(client, fake):
    response = _post(client, b"du texte", "text/plain")
    assert response.status_code == 415
    assert fake.received == []


def test_image_trop_volumineuse_413(client, fake, monkeypatch):
    monkeypatch.setattr(app_module.config, "MAX_IMAGE_BYTES", 100)
    response = _post(client, _image_bytes(size=(200, 200)))
    assert response.status_code == 413
    assert fake.received == []


def test_fichier_corrompu_422(client, fake):
    response = _post(client, b"ceci n'est pas une image", "image/png")
    assert response.status_code == 422
    assert fake.received == []


def test_champ_image_manquant_422(client):
    response = _post(client, _image_bytes(), field="autre_nom")
    assert response.status_code == 422


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
