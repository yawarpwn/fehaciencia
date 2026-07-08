import os
from pathlib import Path

DATA_PATH = Path(os.getenv("DATA_PATH", Path(__file__).parent.parent / "tmp"))

STORAGE_PATH = DATA_PATH / "COMPROBANTES"
DATABASE_PATH = DATA_PATH / "db" / "fehaciencia_tell.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Tamaño máximo por archivo en (bytes). 20 MB por defecto
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "20")) * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".webp", ".heic"}

STORAGE_PATH.mkdir(parents=True, exist_ok=True)
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

BASE_URL = "http://localhost:7780"

# JWT & Authentication settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key-for-tell-docs-development-123456789")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # 24 hours
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")

