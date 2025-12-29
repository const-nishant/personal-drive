"""Configuration management for the Python service."""

import os
import logging
from typing import Optional
from pathlib import Path

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        logging.info(f"Loaded environment variables from {env_path}")
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass

logger = logging.getLogger(__name__)


class Config:
    """Application configuration loaded from environment variables."""

    # API Key Configuration
    API_KEY: str = os.getenv("API_KEY") or os.getenv("SEMANTIC_SERVICE_API_KEY") or ""
    if not API_KEY:
        import secrets
        API_KEY = secrets.token_hex(32)
        logger.warning(
            f"⚠️  No API_KEY environment variable set. Generated API key for this session: {API_KEY}"
        )
        logger.warning(
            "⚠️  Set API_KEY or SEMANTIC_SERVICE_API_KEY environment variable for production!"
        )

    # Appwrite Configuration
    APPWRITE_ENDPOINT: str = os.getenv("APPWRITE_ENDPOINT", "https://sgp.cloud.appwrite.io/v1")
    APPWRITE_PROJECT_ID: str = os.getenv("APPWRITE_PROJECT_ID", "")
    APPWRITE_API_KEY: str = os.getenv("APPWRITE_API_KEY", "")
    APPWRITE_DATABASE_ID: str = os.getenv("APPWRITE_DATABASE_ID", "")
    APPWRITE_TABLE_ID: str = os.getenv("APPWRITE_TABLE_ID", "")

    # S3 Configuration
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "")
    S3_ACCESS_KEY_ID: str = os.getenv("S3_ACCESS_KEY_ID", "")
    S3_SECRET_ACCESS_KEY: str = os.getenv("S3_SECRET_ACCESS_KEY", "")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")

    # Service Configuration
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "104857600"))  # 100MB default
    ALLOWED_MIME_TYPES: list[str] = (
        os.getenv(
            "ALLOWED_MIME_TYPES",
            "application/pdf,text/plain,image/jpeg,image/png,image/webp,"
            "application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ).split(",")
    )

    # Index Configuration
    INDEX_DIR: str = os.getenv("INDEX_DIR", "./index")
    MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384  # Dimension for all-MiniLM-L6-v2

    # Presigned URL Expiration
    PRESIGNED_UPLOAD_EXPIRES_IN: int = int(os.getenv("PRESIGNED_UPLOAD_EXPIRES_IN", "900"))  # 15 minutes
    PRESIGNED_DOWNLOAD_EXPIRES_IN: int = int(os.getenv("PRESIGNED_DOWNLOAD_EXPIRES_IN", "3600"))  # 1 hour

    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present."""
        required_vars = [
            ("APPWRITE_ENDPOINT", cls.APPWRITE_ENDPOINT),
            ("APPWRITE_PROJECT_ID", cls.APPWRITE_PROJECT_ID),
            ("APPWRITE_API_KEY", cls.APPWRITE_API_KEY),
            ("APPWRITE_DATABASE_ID", cls.APPWRITE_DATABASE_ID),
            ("APPWRITE_TABLE_ID", cls.APPWRITE_TABLE_ID),
            ("S3_ENDPOINT", cls.S3_ENDPOINT),
            ("S3_ACCESS_KEY_ID", cls.S3_ACCESS_KEY_ID),
            ("S3_SECRET_ACCESS_KEY", cls.S3_SECRET_ACCESS_KEY),
            ("S3_BUCKET_NAME", cls.S3_BUCKET_NAME),
        ]

        missing = [var for var, value in required_vars if not value]
        if missing:
            logger.error(f"Missing required environment variables: {', '.join(missing)}")
            return False

        return True

    @classmethod
    def get_index_path(cls) -> str:
        """Get the full path to the FAISS index file."""
        return os.path.join(cls.INDEX_DIR, "faiss.index")

    @classmethod
    def get_meta_path(cls) -> str:
        """Get the full path to the metadata pickle file."""
        return os.path.join(cls.INDEX_DIR, "meta.pkl")

