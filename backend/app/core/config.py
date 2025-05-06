import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    DEBUG = os.getenv("DEBUG", True)
    ALGORITHM = "HS256"

settings = Settings()
