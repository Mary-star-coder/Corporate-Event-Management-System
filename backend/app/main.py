
# Import FastAPI tools for creating APIs, handling dependencies,
# raising HTTP errors, and defining HTTP status codes.
from fastapi import FastAPI, Depends, HTTPException, status

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
# Title, description, and version appear in Swagger documentation.
app = FastAPI(
    title="Corporate Event Management System",
    description="API for managing corporate events and registrations",
    version="1.0.0"
)


# ==========================================
# CORS CONFIGURATION
# ==========================================

# CORS allows the frontend running on another origin
# to send HTTP requests to this backend.
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

# Create all database tables defined in the SQLAlchemy models.
# Existing tables are not recreated or deleted.
Base.metadata.create_all(bind=engine)


# ==========================================
# HOME API
# ==========================================

# GET endpoint for checking whether the API is running.
@app.get("/")
def home():
    return {
        "message": "Welcome to Corporate Event Management System!"
    }


# ==========================================
# CREATE EVENT API
# ==========================================

# POST endpoint to create a new corporate event.
# EventCreate validates the incoming event information.
# EventResponse defines the structure of the returned data.
@app.post(
    "/events",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED
)
def create_event(event: EventCreate, db: Session = Depends(get_db)):

    # Convert the validated Pydantic data into an Event model object.
    new_event = Event(**event.model_dump())

    # Add the new event to the database session.
    db.add(new_event)

    # Save the new event permanently in the database.
    db.commit()

    # Refresh the object to retrieve database-generated values.
    db.refresh(new_event)

    return new_event


# ==========================================
# GET ALL EVENTS API
# WITH PAGINATION, SEARCH AND FILTERING
# ==========================================

# GET endpoint to retrieve events from the database.
@app.get("/events", response_model=list[EventResponse])
def get_events(
    skip: int = 0,                 # Number of records to skip.
    limit: int = 5,                # Maximum number of events to return.
    search: str | None = None,     # Optional event title search.
    location: str | None = None,   # Optional location filter.
    db: Session = Depends(get_db) # Database session dependency.
):

    # Start building a query for the Event table.
    query = db.query(Event)

    # Search event titles without case sensitivity.
    if search:
        query = query.filter(Event.title.ilike(f"%{search}%"))

    # Filter events according to their location.
    if location:
        query = query.filter(Event.location.ilike(f"%{location}%"))

    # Apply pagination using skip and limit values.
    events = query.offset(skip).limit(limit).all()

    # Return the matching event records.
    return events


# ==========================================
# GET SINGLE EVENT API
# ==========================================

# GET endpoint to retrieve one event using its ID.
@app.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):

    # Find the event whose ID matches the requested ID.
    event = db.query(Event).filter(Event.id == event_id).first()

    # Return 404 if the requested event does not exist.
    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    return event


# ==========================================
# UPDATE EVENT API
# ==========================================

# PUT endpoint to update an existing event.
@app.put("/events/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db)
):

    # Find the event that needs to be updated.
    event = db.query(Event).filter(Event.id == event_id).first()

    # Check whether the event exists.
    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    # Convert only the fields provided by the user into a dictionary.
    update_data = event_data.model_dump(exclude_unset=True)

    # Update each provided field in the existing event object.
    for key, value in update_data.items():
        setattr(event, key, value)

    # Save the updated event in the database.
    db.commit()

    # Refresh the event to get its latest database values.
    db.refresh(event)

    return event


# ==========================================
# DELETE EVENT API
# ==========================================

# DELETE endpoint to remove an event using its ID.
@app.delete("/events/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):

    # Find the event that needs to be deleted.
    event = db.query(Event).filter(Event.id == event_id).first()

    # Return 404 if the event does not exist.
    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    # Remove the event from the database session.
    db.delete(event)

    # Permanently save the deletion.
    db.commit()

    return {
        "message": "Event deleted successfully"
    }


# ==========================================
# CREATE EVENT REGISTRATION API
# ==========================================

# POST endpoint that allows an attendee to register for an event.
@app.post(
    "/registrations",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_registration(
    registration: RegistrationCreate,
    db: Session = Depends(get_db)
):

    # Check whether the requested event exists.
    event = db.query(Event).filter(
        Event.id == registration.event_id
    ).first()

    # Stop registration if the event does not exist.
    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    # Check whether any seats are available for the event.
    if event.available_seats <= 0:
        raise HTTPException(
            status_code=400,
            detail="No seats available"
        )

    # Check whether the same attendee email is already
    # registered for this particular event.
    existing = db.query(Registration).filter(
        Registration.event_id == registration.event_id,
        Registration.attendee_email == registration.attendee_email
    ).first()

    # Prevent duplicate registrations.
    if existing:
        raise HTTPException(
            status_code=400,
            detail="You are already registered for this event"
        )

    # Create a new registration using validated request data.
    new_registration = Registration(
        **registration.model_dump()
    )

    # Decrease the event's available seat count by one.
    event.available_seats -= 1

    # Add the registration to the database session.
    db.add(new_registration)

    # Save the registration and updated seat count.
    db.commit()

    # Refresh the registration to retrieve generated database values.
    db.refresh(new_registration)

    return new_registration


# ==========================================
# GET ALL REGISTRATIONS API
# ==========================================

# GET endpoint to retrieve all event registrations.
@app.get(
    "/registrations",
    response_model=list[RegistrationResponse]
)
def get_registrations(db: Session = Depends(get_db)):

    # Retrieve and return all registration records.
    return db.query(Registration).all()


# ==========================================
# GET SINGLE REGISTRATION API
# ==========================================

# GET endpoint to retrieve a registration using its ID.
@app.get(
    "/registrations/{registration_id}",
    response_model=RegistrationResponse
)
def get_registration(
    registration_id: int,
    db: Session = Depends(get_db)
):

    # Find the registration matching the requested ID.
    registration = db.query(Registration).filter(
        Registration.id == registration_id
    ).first()

    # Return 404 if the registration does not exist.
    if registration is None:
        raise HTTPException(
            status_code=404,
            detail="Registration not found"
        )

    return registration


# ==========================================
# USER SIGNUP API
# ==========================================

# POST endpoint to create a new user account.
@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(user: UserCreate, db: Session = Depends(get_db)):

    # Check whether the email address is already registered.
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    # Prevent multiple accounts using the same email.
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash the user's password before saving it.
    # Plain-text passwords are never stored in the database.
    hashed_password = get_password_hash(user.password)

    # Create a new user database object.
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed_password
    )

    # Add the new user to the database.
    db.add(new_user)

    # Save the new account.
    db.commit()

    # Refresh the object to retrieve generated values.
    db.refresh(new_user)

    return new_user


# ==========================================
# USER LOGIN API
# ==========================================

# POST endpoint to authenticate an existing user.
@app.post("/auth/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):

    # Find the user using the submitted email address.
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    # Verify that the user exists and the submitted password is correct.
    if not existing_user or not verify_password(
        user.password,
        existing_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )

    # Generate a JWT access token containing the user's email.
    access_token = create_access_token(
        data={"sub": existing_user.email}
    )

    # Return the access token and basic user information.
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

# GET endpoint for retrieving the currently authenticated user's profile.
@app.get("/auth/me")
def get_my_profile(
    # get_current_user verifies the JWT token and identifies the user.
    current_user: User = Depends(get_current_user)
):

    # Return the authenticated user's basic profile information.
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email
    }
