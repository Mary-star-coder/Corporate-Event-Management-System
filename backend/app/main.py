

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, get_db
from app.models import Base, Event, Registration, User
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

from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user
)




app = FastAPI(
    title="Corporate Event Management System",
    description="API for managing corporate events and registrations",
    version="1.0.0"
)


# Allow frontend to communicate with backend
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

# Create database tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {
        "message": "Welcome to Corporate Event Management System!"
    }


# CREATE EVENT
@app.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    new_event = Event(**event.model_dump())

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event




# GET ALL EVENTS WITH PAGINATION, SEARCH AND FILTERING
@app.get("/events", response_model=list[EventResponse])
def get_events(
    skip: int = 0,
    limit: int = 5,
    search: str | None = None,
    location: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Event)

    # Search events by title
    if search:
        query = query.filter(Event.title.ilike(f"%{search}%"))

    # Filter events by location
    if location:
        query = query.filter(Event.location.ilike(f"%{location}%"))

    # Apply pagination
    events = query.offset(skip).limit(limit).all()

    return events




# GET SINGLE EVENT
@app.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    return event


# UPDATE EVENT
@app.put("/events/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db)
):
    event = db.query(Event).filter(Event.id == event_id).first()

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    update_data = event_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(event, key, value)

    db.commit()
    db.refresh(event)

    return event


# DELETE EVENT
@app.delete("/events/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    db.delete(event)
    db.commit()

    return {
        "message": "Event deleted successfully"
    }


# CREATE EVENT REGISTRATION
@app.post(
    "/registrations",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_registration(
    registration: RegistrationCreate,
    db: Session = Depends(get_db)
):
    # Check if event exists
    event = db.query(Event).filter(
        Event.id == registration.event_id
    ).first()

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    # Check available seats
    if event.available_seats <= 0:
        raise HTTPException(
            status_code=400,
            detail="No seats available"
        )

    # Check duplicate registration
    existing = db.query(Registration).filter(
        Registration.event_id == registration.event_id,
        Registration.attendee_email == registration.attendee_email
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="You are already registered for this event"
        )

    # Create registration
    new_registration = Registration(
        **registration.model_dump()
    )

    event.available_seats -= 1

    db.add(new_registration)
    db.commit()
    db.refresh(new_registration)

    return new_registration


# GET ALL REGISTRATIONS
@app.get(
    "/registrations",
    response_model=list[RegistrationResponse]
)
def get_registrations(db: Session = Depends(get_db)):
    return db.query(Registration).all()


# GET SINGLE REGISTRATION
@app.get(
    "/registrations/{registration_id}",
    response_model=RegistrationResponse
)
def get_registration(
    registration_id: int,
    db: Session = Depends(get_db)
):
    registration = db.query(Registration).filter(
        Registration.id == registration_id
    ).first()

    if registration is None:
        raise HTTPException(
            status_code=404,
            detail="Registration not found"
        )

    return registration


# ==============================
# USER SIGNUP API
# ==============================

@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(user.password)

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ==============================
# USER LOGIN API
# ==============================

@app.post("/auth/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing_user or not verify_password(
        user.password,
        existing_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )

    access_token = create_access_token(
        data={"sub": existing_user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": existing_user.id,
            "full_name": existing_user.full_name,
            "email": existing_user.email
        }
    }

# ==============================
# PROTECTED USER PROFILE API
# ==============================

@app.get("/auth/me")
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email
    }