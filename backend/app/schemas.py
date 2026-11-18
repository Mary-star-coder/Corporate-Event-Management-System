
# Import datetime to validate date and time values.
from datetime import datetime

# Import Pydantic tools for data validation and schema configuration.
from pydantic import BaseModel, ConfigDict, Field, EmailStr


# ==========================================
# EVENT SCHEMAS
# ==========================================

# Defines and validates the data required to create a new event.
class EventCreate(BaseModel):

    # Event title must contain between 3 and 200 characters.
    title: str = Field(min_length=3, max_length=200)

    # Event description is optional.
    description: str | None = None

    # Event location must contain between 2 and 200 characters.
    location: str = Field(min_length=2, max_length=200)

    # Event date and time must be in a valid datetime format.
    event_date: datetime

    # Available seats must be greater than zero.
    available_seats: int = Field(gt=0)


# Defines the optional fields that can be updated for an event.
class EventUpdate(BaseModel):

    # New title is optional but must meet length requirements if provided.
    title: str | None = Field(default=None, min_length=3, max_length=200)

    # Description can be updated or left empty.
    description: str | None = None

    # New location is optional but must meet length requirements if provided.
    location: str | None = Field(default=None, min_length=2, max_length=200)

    # New event date and time, if provided, must be valid.
    event_date: datetime | None = None

    # Updated seat count must be greater than zero if provided.
    available_seats: int | None = Field(default=None, gt=0)


# Defines the event data returned by the API.
class EventResponse(BaseModel):

    # Unique event ID.
    id: int

    # Event title.
    title: str

    # Event description.
    description: str | None

    # Event location.
    location: str

    # Scheduled event date and time.
    event_date: datetime

    # Number of available seats.
    available_seats: int

    # Event creation timestamp.
    created_at: datetime

    # Allows Pydantic to read data directly from SQLAlchemy model objects.
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# REGISTRATION SCHEMAS
# ==========================================

# Defines and validates the data required to register for an event.
class RegistrationCreate(BaseModel):

    # ID of the event for which the attendee wants to register.
    event_id: int

    # Attendee name must contain between 3 and 100 characters.
    attendee_name: str = Field(min_length=3, max_length=100)

    # EmailStr checks that the provided email has a valid email format.
    attendee_email: EmailStr


# Defines the registration data returned by the API.
class RegistrationResponse(BaseModel):

    # Unique registration ID.
    id: int

    # ID of the registered event.
    event_id: int

    # Name of the attendee.
    attendee_name: str

    # Validated email address of the attendee.
    attendee_email: EmailStr

    # Date and time when the registration was created.
    registered_at: datetime

    # Allows conversion from SQLAlchemy model objects.
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# USER REGISTRATION SCHEMA
# ==========================================

# Defines and validates the information needed to create a user account.
class UserCreate(BaseModel):

    # User's full name must contain between 3 and 100 characters.
    full_name: str = Field(min_length=3, max_length=100)

    # User must provide a valid email address.
    email: EmailStr

    # Password must contain at least 8 and at most 100 characters.
    password: str = Field(min_length=8, max_length=100)


# ==========================================
# USER RESPONSE SCHEMA
# ==========================================

# Defines the user information returned by the API.
# Password is intentionally excluded from this response.
class UserResponse(BaseModel):

    # Unique user ID.
    id: int

    # User's full name.
    full_name: str

    # User's registered email address.
    email: EmailStr

    # Date and time when the account was created.
    created_at: datetime

    # Allows Pydantic to read values from SQLAlchemy model objects.
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# USER LOGIN SCHEMA
# ==========================================

# Defines and validates the credentials required for login.
class UserLogin(BaseModel):

    # Email address used to identify the user account.
    email: EmailStr

    # Password provided by the user for authentication.
    password: str
