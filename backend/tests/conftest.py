"""Configuration commune des tests.

Principe : les tests ne touchent JAMAIS à la vraie base MariaDB ni au vrai .env.
- Les variables d'environnement sont fixées ici AVANT l'import de l'application
  (config/database.py et config/security.py les lisent à l'import).
- La dépendance `db.get_session` est remplacée par une session SQLite en mémoire.
- TestClient est utilisé SANS `with` : le `lifespan` (qui appelle db.create_tables()
  sur MariaDB) n'est ainsi jamais exécuté. Les tables sont créées sur SQLite ici.
"""
import os

# Variables factices, fixées avant tout import du projet (load_dotenv() ne
# remplace pas une variable déjà définie).
os.environ["DB_USER"] = "test_user"
os.environ["DB_PASSWORD"] = "test_password"
os.environ["JWT_SECRET_KEY"] = "cle-secrete-uniquement-pour-les-tests"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_EXPIRE_MINUTES"] = "30"
os.environ["PLANTNET_API_KEY"] = "cle-plantnet-uniquement-pour-les-tests"
os.environ["ENGINE_URL"] = "http://moteur-ia.test:8001"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models  # noqa: F401 — enregistre tous les modèles dans Base.metadata
from config.database import Base, db
from main import app

USER_PAYLOAD = {
    "surname": "Dupont",
    "name": "Jean",
    "email": "jean.dupont@example.com",
    "password": "motdepasse123",
}


@pytest.fixture()
def engine():
    """Base SQLite en mémoire, neuve pour chaque test (isolation totale)."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # une seule connexion partagée, sinon chaque connexion aurait sa propre base vide
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def session(engine):
    """Session SQLAlchemy directe, pour tester les services ou préparer des données."""
    with sessionmaker(bind=engine)() as session:
        yield session


@pytest.fixture()
def client(engine):
    """Client HTTP de test, branché sur la base SQLite à la place de MariaDB."""
    test_session_factory = sessionmaker(bind=engine)

    def override_get_session():
        with test_session_factory() as session:
            yield session

    app.dependency_overrides[db.get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def user_payload():
    return dict(USER_PAYLOAD)


@pytest.fixture()
def make_auth_headers(client):
    """Fabrique un utilisateur (inscription + connexion) et renvoie son header Authorization."""

    def _make(email: str = USER_PAYLOAD["email"]):
        payload = {**USER_PAYLOAD, "email": email}
        assert client.post("/auth/register", json=payload).status_code == 201
        response = client.post(
            "/auth/login", json={"email": email, "password": payload["password"]}
        )
        assert response.status_code == 200
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    return _make
