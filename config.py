import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv() # reads .env and puts the values in environment variables

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-fallback")  # Default value for development
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///annotrack.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # key used to sign tokens; anyone who has it can create valid tokens
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-fallback")
    # tokens stop working after 1 hour, which limits damage if one is stolen
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # In-memory database for testing