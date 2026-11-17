from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from pwdlib import PasswordHash

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.database import settings, get_db
from app.models import User

# JWT Configuration
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password Hashing
password_hash = PasswordHash.recommended()

# Bearer Token Security
security = HTTPBearer()


# Hash password before saving in database
def get_password_hash(password: str):
    return password_hash.hash(password)


# Verify login password
def verify_password(plain_password: str, hashed_password: str):
    return password_hash.verify(plain_password, hashed_password)


# Generate JWT Access Token
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# Verify JWT Token
def verify_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        return email

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

# Get currently logged-in user
def get_current_user(
    credentials = Depends(security),
    db: Session = Depends(get_db)
):
    email = verify_access_token(credentials.credentials)

    user = db.query(User).filter(
        User.email == email
    ).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user