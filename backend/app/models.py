
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(200), nullable=False)
    event_date = Column(DateTime, nullable=False)
    available_seats = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

from sqlalchemy import ForeignKey


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)

    event_id = Column(
        Integer,
        ForeignKey("events.id"),
        nullable=False
    )

    attendee_name = Column(String(100), nullable=False)

    attendee_email = Column(String(150), nullable=False)

    registered_at = Column(
        DateTime,
        server_default=func.now()
    )


# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
