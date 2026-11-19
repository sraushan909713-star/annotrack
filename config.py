import os
from dotenv import load_dotenv

load_dotenv() # reads .env and puts the values in environment variables

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-fallback")  # Default value for development
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///annotrack.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # In-memory database for testing