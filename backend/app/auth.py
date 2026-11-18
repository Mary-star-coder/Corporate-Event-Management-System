
# Import datetime utilities to create token expiration times.
from datetime import datetime, timedelta, timezone

# Import JWT tools to create and verify authentication tokens.
from jose import jwt, JWTError

# Import PasswordHash to securely hash and verify user passwords.
from pwdlib import PasswordHash

# Import FastAPI tools for errors, status codes, and dependencies.
from fastapi import HTTPException, status, Depends

# Import HTTPBearer to receive JWT tokens through the Authorization header.
from fastapi.security import HTTPBearer

# Import SQLAlchemy Session for database operations.
from sqlalchemy.orm import Session

# Import application settings and database session dependency.
from app.database import settings, get_db

# Import the User database model.
from app.models import User


# ==========================================
# JWT CONFIGURATION
# ==========================================

# Load the secret key from the backend .env file.
# Keep this key private and never upload it to GitHub.
SECRET_KEY = settings.JWT_SECRET_KEY

# Algorithm used to sign and verify JWT tokens.
ALGORITHM = "HS256"

# JWT access tokens expire after 30 minutes.
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ==========================================
# PASSWORD HASHING CONFIGURATION
# ==========================================

# Select a recommended secure password hashing algorithm.
password_hash = PasswordHash.recommended()


# ==========================================
# BEARER TOKEN SECURITY
# ==========================================

# Configure FastAPI to receive tokens using Bearer authentication.
security = HTTPBearer()


# ==========================================
# HASH USER PASSWORD
# ==========================================

# Convert a plain-text password into a secure hash before storing it.
def get_password_hash(password: str):

    # Return the hashed password.
    return password_hash.hash(password)


# ==========================================
# VERIFY USER PASSWORD
# ==========================================

# Compare the entered password with the stored password hash.
def verify_password(plain_password: str, hashed_password: str):

    # Return True if the password matches; otherwise return False.
    return password_hash.verify(plain_password, hashed_password)


# ==========================================
# CREATE JWT ACCESS TOKEN
# ==========================================

# Generate a signed JWT token containing the supplied user information.
def create_access_token(data: dict):

    # Copy the original data so it is not modified directly.
    to_encode = data.copy()

    # Calculate the token expiration date and time in UTC.
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Add the expiration time to the token payload.
    to_encode.update({"exp": expire})

    # Encode and digitally sign the JWT token.
    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    # Return the generated access token.
    return token


# ==========================================
# VERIFY JWT ACCESS TOKEN
# ==========================================

# Decode the token and verify its signature and expiration.
def verify_access_token(token: str):

    try:
        # Decode the JWT token using the secret key and allowed algorithm.
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        # Extract the user's email from the token subject field.
        email = payload.get("sub")

        # Reject the token if it does not contain a user identity.
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # Return the verified user's email address.
        return email

    # Handle invalid, expired, or incorrectly signed JWT tokens.
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


# ==========================================
# GET CURRENTLY LOGGED-IN USER
# ==========================================

# Identify the authenticated user using the supplied JWT token.
def get_current_user(
    # Receive the Bearer token from the Authorization header.
    credentials=Depends(security),

    # Get a database session for looking up the user.
    db: Session = Depends(get_db)
):

    # Verify the token and extract the user's email.
    email = verify_access_token(credentials.credentials)

    # Search the database for the user with the verified email.
    user = db.query(User).filter(
        User.email == email
    ).first()

    # Reject the request if the user no longer exists.
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # Return the authenticated user.
    return user
