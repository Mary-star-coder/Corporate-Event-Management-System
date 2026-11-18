
# Import FastAPI tools for creating APIs, handling dependencies,
# raising HTTP errors, and defining HTTP status codes.
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import Response

# Import SQLAlchemy Session to communicate with the database.
from sqlalchemy.orm import Session

# Import CORS middleware to allow frontend-backend communication.
from fastapi.middleware.cors import CORSMiddleware

# Import database engine and database session dependency.
from app.database import engine, get_db

# Import database models (tables).
from app.models import Base, Event, Registration, User

# Import Pydantic schemas for request validation and response formatting.
from app.schemas import (
    EventCreate,
    EventUpdate,
    EventResponse,
    RegistrationCreate,
    RegistrationResponse,
    UserCreate,
    UserResponse,
    UserLogin
)

# Import authentication functions for password security and JWT.
from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user
)


# ==========================================
# FASTAPI APPLICATION INITIALIZATION
# ==========================================

# Create the main FastAPI application.
app = FastAPI(
    title="Corporate Event Management System",
    description="API for managing corporate events and registrations",
    version="1.0.0"
)


# ==========================================
# CORS CONFIGURATION
# ==========================================

# Allow the frontend to communicate with the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# DATABASE TABLE CREATION
# ==========================================

# Create database tables defined in SQLAlchemy models.
Base.metadata.create_all(bind=engine)


# ==========================================
# HOME API
# ==========================================

# Check whether the API is running.
@app.get("/")
def home():
    return {
        "message": "Welcome to Corporate Event Management System!"
    }


# ==========================================
# CREATE EVENT API
# JWT AUTHENTICATION REQUIRED
# ==========================================

# Only authenticated users can create events.
@app.post(
    "/events",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED
)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Convert validated Pydantic data into an Event object.
    new_event = Event(**event.model_dump())

    # Add and save the event in the database.
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event


# ==========================================
# GET ALL EVENTS API
# PAGINATION, SEARCH AND FILTERING
# ==========================================

# Retrieve events with optional pagination and filters.
@app.get("/events", response_model=list[EventResponse])
def get_events(
    skip: int = 0,
    limit: int = 5,
    search: str | None = None,
    location: str | None = None,
    db: Session = Depends(get_db)
):
    # Start a query for all events.
    query = db.query(Event)

    # Search event titles without case sensitivity.
    if search:
        query = query.filter(Event.title.ilike(f"%{search}%"))

    # Filter events by location.
    if location:
        query = query.filter(Event.location.ilike(f"%{location}%"))

    # Apply pagination.
    events = query.offset(skip).limit(limit).all()

    return events


# ==========================================
# GET SINGLE EVENT API
# ==========================================

# Retrieve one event using its ID.
@app.get("/events/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    # Find the requested event.
    event = db.query(Event).filter(Event.id == event_id).first()

    # Return 404 if the event does not exist.
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    return event


# ==========================================
# UPDATE EVENT API
# JWT AUTHENTICATION REQUIRED
# ==========================================

# Only authenticated users can update events.
@app.put("/events/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find the event that needs updating.
    event = db.query(Event).filter(Event.id == event_id).first()

    # Check whether the event exists.
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    # Get only the fields supplied in the request.
    update_data = event_data.model_dump(exclude_unset=True)

    # Update the supplied event fields.
    for key, value in update_data.items():
        setattr(event, key, value)

    # Save the changes.
    db.commit()
    db.refresh(event)

    return event


# ==========================================
# DELETE EVENT API
# JWT AUTHENTICATION REQUIRED
# ==========================================

# Only authenticated users can delete events.
@app.delete(
    "/events/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find the event that needs deleting.
    event = db.query(Event).filter(Event.id == event_id).first()

    # Return 404 if the event does not exist.
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    # Delete the event and save the change.
    db.delete(event)
    db.commit()

    # Return an empty 204 No Content response.
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ==========================================
# REGISTRATION HELPER FUNCTION
# ==========================================

# This function contains the shared business rules for registration.
# Both registration POST endpoints use this function.
def create_registration_record(
    event_id: int,
    registration: RegistrationCreate,
    db: Session
):
    # Check whether the requested event exists.
    event = db.query(Event).filter(Event.id == event_id).first()

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    # Prevent registration when no seats are available.
    if event.available_seats <= 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No seats available for this event"
        )

    # Check whether this attendee is already registered.
    existing = db.query(Registration).filter(
        Registration.event_id == event_id,
        Registration.attendee_email == registration.attendee_email
    ).first()

    # Prevent duplicate registrations.
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are already registered for this event"
        )

    # Convert validated request data into a dictionary.
    # The event ID from the URL is used as the authoritative ID.
    registration_data = registration.model_dump(exclude={"event_id"})

    # Create a new registration record.
    new_registration = Registration(
        event_id=event_id,
        **registration_data
    )

    # Decrease the number of available seats.
    event.available_seats -= 1

    # Save the registration and updated seat count.
    db.add(new_registration)
    db.commit()
    db.refresh(new_registration)

    return new_registration


# ==========================================
# CREATE REGISTRATION FOR A SPECIFIC EVENT
# PDF REQUIRED ENDPOINT
# ==========================================

# Register an attendee for the event specified in the URL.
@app.post(
    "/events/{event_id}/registrations",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED
)
def register_for_event(
    event_id: int,
    registration: RegistrationCreate,
    db: Session = Depends(get_db)
):
    # Apply event existence, capacity and duplicate checks.
    return create_registration_record(
        event_id,
        registration,
        db
    )


# ==========================================
# LEGACY CREATE REGISTRATION API
# KEPT FOR FRONTEND COMPATIBILITY
# ==========================================

# Existing frontend can continue using POST /registrations.
@app.post(
    "/registrations",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_registration(
    registration: RegistrationCreate,
    db: Session = Depends(get_db)
):
    # Use the event ID supplied in the request body.
    return create_registration_record(
        registration.event_id,
        registration,
        db
    )


# ==========================================
# GET REGISTRATIONS FOR A SPECIFIC EVENT
# PDF REQUIRED ENDPOINT
# ==========================================

# Retrieve all registrations belonging to one event.
@app.get(
    "/events/{event_id}/registrations",
    response_model=list[RegistrationResponse]
)
def get_event_registrations(
    event_id: int,
    db: Session = Depends(get_db)
):
    # First check whether the event exists.
    event = db.query(Event).filter(Event.id == event_id).first()

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    # Retrieve registrations for the requested event.
    registrations = db.query(Registration).filter(
        Registration.event_id == event_id
    ).all()

    return registrations


# ==========================================
# GET ALL REGISTRATIONS API
# ==========================================

# Retrieve every registration in the database.
@app.get(
    "/registrations",
    response_model=list[RegistrationResponse]
)
def get_registrations(db: Session = Depends(get_db)):
    return db.query(Registration).all()


# ==========================================
# GET SINGLE REGISTRATION API
# ==========================================

# Retrieve one registration using its ID.
@app.get(
    "/registrations/{registration_id}",
    response_model=RegistrationResponse
)
def get_registration(
    registration_id: int,
    db: Session = Depends(get_db)
):
    # Find the requested registration.
    registration = db.query(Registration).filter(
        Registration.id == registration_id
    ).first()

    # Return 404 if the registration does not exist.
    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )

    return registration


# ==========================================
# CANCEL REGISTRATION API
# PDF REQUIRED ENDPOINT
# ==========================================

# Cancel a registration and restore one available seat.
@app.delete(
    "/registrations/{registration_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def cancel_registration(
    registration_id: int,
    db: Session = Depends(get_db)
):
    # Find the registration that needs cancelling.
    registration = db.query(Registration).filter(
        Registration.id == registration_id
    ).first()

    # Return 404 if the registration does not exist.
    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )

    # Find the event associated with this registration.
    event = db.query(Event).filter(
        Event.id == registration.event_id
    ).first()

    # Restore one available seat if the event still exists.
    if event is not None:
        event.available_seats += 1

    # Delete the registration.
    db.delete(registration)
    db.commit()

    # Return an empty 204 No Content response.
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ==========================================
# USER SIGNUP API
# ==========================================

# Create a new user account.
@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    # Check whether the email is already registered.
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Hash the password before storing it.
    hashed_password = get_password_hash(user.password)

    # Create the new user.
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed_password
    )

    # Save the user in the database.
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ==========================================
# USER LOGIN API
# ==========================================

# Authenticate a user and return a JWT access token.
@app.post("/auth/login")
def login_user(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    # Find the user by email.
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    # Check the submitted password.
    if not existing_user or not verify_password(
        user.password,
        existing_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Generate a JWT access token.
    access_token = create_access_token(
        data={"sub": existing_user.email}
    )

    # Return the token and basic user information.
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": existing_user.id,
            "full_name": existing_user.full_name,
            "email": existing_user.email
        }
    }


# ==========================================
# PROTECTED USER PROFILE API
# ==========================================

# Retrieve the profile of the currently authenticated user.
@app.get("/auth/me")
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email
    }
