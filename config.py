import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "replace-this-with-a-random-secret")
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB
    ALLOWED_EXTENSIONS = {"doc", "docx", "pdf"}

    UPLOAD_FOLDER = Path(os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "uploads")))
    PROCESSED_FOLDER = Path(os.getenv("PROCESSED_FOLDER", str(BASE_DIR / "processed")))

    @classmethod
    def ensure_directories(cls) -> None:
        cls.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)
