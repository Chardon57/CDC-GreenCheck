import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.engine import URL

load_dotenv()

REQUIRED_ENV_VARS = ("DB_USER", "DB_PASSWORD")
missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
if missing:
    raise RuntimeError(
        f"Variables d'environnement manquantes : {', '.join(missing)}. "
        "Merci de se référer au fichier .env.example."
    )

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "greencheck")
DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"

try:
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
except ValueError:
    raise RuntimeError(
        "DB_PORT invalide : doit être un nombre entier. "
        "Merci de se référer au fichier .env.example."
    )

DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)


class Base(DeclarativeBase):
    pass


class Database:
    def __init__(self, url: URL = DATABASE_URL, echo: bool = DB_ECHO) -> None:
        self.engine = create_engine(url, echo=echo)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self) -> None:
        Base.metadata.create_all(self.engine)

    def get_session(self):
        with self.SessionLocal() as session:
            yield session


db = Database()