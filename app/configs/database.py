from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
import ssl
from sqlalchemy.sql import text

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "gateway01.ap-southeast-1.prod.aws.tidbcloud.com")
DB_PORT = os.getenv("DB_PORT", "4000")
DB_USER = os.getenv("DB_USER", "4YeW7yoXjiqC5uP.root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "xYlUfJutBf3wvcyM")
DB_NAME = os.getenv("DB_NAME", "palee_elite_training_center")
DATABASE_URL = os.getenv("DATABASE_URL")
DB_SSL_ENABLED = os.getenv("DB_SSL_ENABLED", "").lower()
DB_SSL_CA = os.getenv("DB_SSL_CA")
DEFAULT_CA_BUNDLE_PATHS = (
    os.getenv("SSL_CERT_FILE"),
    "/etc/ssl/certs/ca-certificates.crt",
    "/etc/ssl/cert.pem",
)


def _is_truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _should_use_ssl() -> bool:
    if DB_SSL_ENABLED:
        return _is_truthy(DB_SSL_ENABLED)
    return DB_HOST not in {"localhost", "127.0.0.1"}


def _build_database_url() -> str:
    if DATABASE_URL:
        return DATABASE_URL

    return (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        "?charset=utf8mb4"
    )


def _resolve_ssl_ca() -> str | None:
    if DB_SSL_CA:
        return DB_SSL_CA

    for candidate in DEFAULT_CA_BUNDLE_PATHS:
        if candidate and os.path.exists(candidate):
            return candidate

    return None


def _build_connect_args() -> dict:
    if not _should_use_ssl():
        return {}

    ca_path = _resolve_ssl_ca()
    ssl_context = (
        ssl.create_default_context(cafile=ca_path)
        if ca_path
        else ssl.create_default_context()
    )

    return {"ssl": ssl_context}

DATABASE_URL = _build_database_url()

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args=_build_connect_args(),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("ເຊື່ອມຕໍ່ຖານຂໍ້ມູນສຳເລັດ!")
    except Exception as e:
        print(f"ການເຊື່ອມຕໍ່ຖານຂໍ້ມູນລົ້ມເຫຼວ: {e}")
