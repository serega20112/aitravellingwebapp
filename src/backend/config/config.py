import os
from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")
basedir = os.path.abspath(os.path.dirname(__file__))


@dataclass
class Config:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret")

    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "SQLALCHEMY_DATABASE_URI", "postgresql://hub:hubpass@localhost:5432/aitravel"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = (
        os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "true").lower() == "true"
    )

    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")
    LOG_TO_CONSOLE: bool = os.getenv("LOG_TO_CONSOLE", "true").lower() == "true"
    LOG_TO_FILE: bool = os.getenv("LOG_TO_FILE", "true").lower() == "true"
    LOG_TO_ES: bool = os.getenv("LOG_TO_ES", "false").lower() == "true"
    LOG_MAX_BYTES: int = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    LOG_PRETTY_JSON: bool = os.getenv("LOG_PRETTY_JSON", "true").lower() == "true"
    LOG_ERRORS_PER_FILE: bool = os.getenv("LOG_ERRORS_PER_FILE", "true").lower() == "true"
    LOG_ERRORS_DIR: str = os.getenv("LOG_ERRORS_DIR", "logs/errors")
    LOG_CONSOLE_LEVEL: str = os.getenv("LOG_CONSOLE_LEVEL", LOG_LEVEL)
    LOG_FILE_LEVEL: str = os.getenv("LOG_FILE_LEVEL", LOG_LEVEL)
    LOG_ES_LEVEL: str = os.getenv("LOG_ES_LEVEL", "ERROR")

    # Elasticsearch configuration
    ELASTICSEARCH_HOST: str = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
    ES_INDEX_NAME: str = os.getenv("ES_INDEX_NAME", "logs-app")
    ES_USERNAME: str | None = os.getenv("ES_USERNAME")
    ES_PASSWORD: str | None = os.getenv("ES_PASSWORD")
    ES_VERIFY_CERTS: bool = os.getenv("ES_VERIFY_CERTS", "false").lower() == "true"
    ES_CA_CERTS: str | None = os.getenv("ES_CA_CERTS")
    ES_REQUEST_TIMEOUT: int = int(os.getenv("ES_REQUEST_TIMEOUT", "5"))

    # OpenStreetMap Nominatim settings
    NOMINATIM_BASE_URL: str = os.getenv(
        "NOMINATIM_BASE_URL", "https://nominatim.openstreetmap.org"
    )
    NOMINATIM_USER_AGENT: str = os.getenv(
        "NOMINATIM_USER_AGENT", "aitravel-app/1.0"
    )
    NOMINATIM_EMAIL: str | None = os.getenv("NOMINATIM_EMAIL")

    # Feature flags / visibility
    SHOW_LOGS_LINK: bool = os.getenv("SHOW_LOGS_LINK", "false").lower() == "true"

    # Hugging Face Inference settings
    HF_TOKEN: str | None = os.getenv("HF_TOKEN")
    HF_PROVIDER: str = os.getenv("HF_PROVIDER", "fireworks-ai")
    HF_MODEL: str = os.getenv("HF_MODEL", "openai/gpt-oss-120b")


_config = Config()