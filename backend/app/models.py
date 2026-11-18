
# Import DeclarativeBase to create the base class for SQLAlchemy models.
from sqlalchemy.orm import DeclarativeBase

# Import column types and database column definitions.
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)

# Import func to use database functions such as the current timestamp.
from sqlalchemy.sql import func


# ==========================================
# SQLALCHEMY BASE CLASS
# ==========================================

# Base class for all database models.
# All model classes inherit from this class.
class Base(DeclarativeBase):
    pass


# ==========================================
# EVENT MODEL
# ==========================================

# Event model represents the events table in PostgreSQL.
class Event(Base):

    # Name of the database table.
    __tablename__ = "events"

    # Unique ID for every event (Primary Key).
    id = Column(Integer, primary_key=True, index=True)

    # Event title is required and can contain up to 200 characters.
    title = Column(String(200), nullable=False)

    # Event description is optional and supports longer text.
    description = Column(Text, nullable=True)

    # Location where the event will take place.
    location = Column(String(200), nullable=False)

    # Date and time scheduled for the event.
    event_date = Column(DateTime, nullable=False)

    # Number of seats available for the event.
    available_seats = Column(Integer, nullable=False)

    # Automatically stores the creation date and time.
    created_at = Column(DateTime, server_default=func.now())


# ==========================================
# REGISTRATION MODEL
# ==========================================

# Registration model represents the registrations table.
class Registration(Base):

    # Name of the database table.
    __tablename__ = "registrations"

    # Unique ID for every registration (Primary Key).
    id = Column(Integer, primary_key=True, index=True)

    # Event ID connects this registration to an existing event.
    # ForeignKey ensures that the referenced event exists.
    event_id = Column(
        Integer,
        ForeignKey("events.id"),
        nullable=False
    )

    # Name of the person registering for the event.
    attendee_name = Column(String(100), nullable=False)

    # Email address of the attendee.
    attendee_email = Column(String(150), nullable=False)

    # Automatically stores the registration date and time.
    registered_at = Column(
        DateTime,
        server_default=func.now()
    )


# ==========================================
# USER MODEL
# ==========================================

# User model represents the users table.
# It stores account information and securely hashed passwords.
class User(Base):

    # Name of the database table.
    __tablename__ = "users"

    # Unique ID for every user (Primary Key).
    id = Column(Integer, primary_key=True, index=True)

    # Full name of the registered user.
    full_name = Column(String(100), nullable=False)

    # Email must be unique so duplicate accounts cannot be created.
    email = Column(String(150), unique=True, nullable=False, index=True)

    # Stores the hashed password, never the original plain-text password.
    hashed_password = Column(String(255), nullable=False)

    # Automatically records when the user account was created.
    created_at = Column(DateTime, server_default=func.now())
