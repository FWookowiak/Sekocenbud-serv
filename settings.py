import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_USER = os.getenv("DATABASE_USER", "default_user")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "default_password")
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_NAME = os.getenv("DATABASE_NAME", "default_db")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///./{DATABASE_NAME}.db"
)
