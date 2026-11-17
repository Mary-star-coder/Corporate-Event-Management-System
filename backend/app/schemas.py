
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


# Data required to create an event
class EventCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str | None = None
    location: str = Field(min_length=2, max_length=200)
    event_date: datetime
    available_seats: int = Field(gt=0)


# Data required to update an event
class EventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = None
    location: str | None = Field(default=None, min_length=2, max_length=200)
    event_date: datetime | None = None
    available_seats: int | None = Field(default=None, gt=0)


# Data returned by the API
class EventResponse(BaseModel):
    id: int
    title: str
    description: str | None
    location: str
    event_date: datetime
    available_seats: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

from pydantic import EmailStr


class RegistrationCreate(BaseModel):
    event_id: int
    attendee_name: str = Field(min_length=3, max_length=100)
    attendee_email: EmailStr


class RegistrationResponse(BaseModel):
    id: int
    event_id: int
    attendee_name: str
    attendee_email: EmailStr
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True)


# User Registration Schema
class UserCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)


# User Response Schema
class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# User Login Schema
class UserLogin(BaseModel):
    email: EmailStr
    password: str
