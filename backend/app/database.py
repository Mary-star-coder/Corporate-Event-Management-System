
# Import BaseSettings to read configuration values from environment variables.
# SettingsConfigDict is used to configure the environment file.
from pydantic_settings import BaseSettings, SettingsConfigDict

# Import create_engine to establish a connection with the database.
from sqlalchemy import create_engine

# Import URL to safely construct the PostgreSQL connection URL.
from sqlalchemy.engine import URL

# Import sessionmaker to create database sessions.
from sqlalchemy.orm import sessionmaker


# ==========================================
# DATABASE AND APPLICATION SETTINGS
# ==========================================

# This class stores the database credentials and JWT secret key.
# Values are automatically loaded from the backend .env file.
class Settings(BaseSettings):

    # PostgreSQL database server address.
    DB_HOST: str

    # PostgreSQL server port number.
    DB_PORT: int

    # Name of the database used by the application.
    DB_NAME: str

    # PostgreSQL username.
    DB_USER: str

    # PostgreSQL password.
    DB_PASSWORD: str

    # Secret key used for creating and verifying JWT tokens.
    JWT_SECRET_KEY: str

    # Configure Pydantic to read settings from the .env file.
    model_config = SettingsConfigDict(
        env_file=".env"
    )


# Create an instance of Settings to load configuration values.
settings = Settings()


# ==========================================
# DATABASE CONNECTION URL
# ==========================================

# Build the PostgreSQL connection URL using the loaded settings.
# Psycopg is used as the PostgreSQL database driver.
# URL.create safely handles special characters in credentials.
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME,
)


# ==========================================
# SQLALCHEMY DATABASE ENGINE
# ==========================================

# Create the SQLAlchemy engine to manage database connections.
# pool_pre_ping checks connections before using them.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


# ==========================================
# DATABASE SESSION FACTORY
# ==========================================

# Create a session factory for handling database operations.
SessionLocal = sessionmaker(
    autocommit=False,  # Changes are committed manually.
    autoflush=False,   # Changes are not automatically flushed.
    bind=engine        # Connect sessions to the PostgreSQL engine.
)


# ==========================================
# DATABASE SESSION DEPENDENCY
# ==========================================

# This function provides a database session to API endpoints.
def get_db():

    # Create a new database session.
    db = SessionLocal()

    try:
        # Yield the session so the API endpoint can use it.
        yield db

    finally:
        # Always close the session after the request is completed.
        # This helps release database connection resources.
        db.close()
