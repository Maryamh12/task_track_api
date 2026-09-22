from http.client import HTTPException

from fastapi.params import Depends
from pwdlib import PasswordHash
import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session
from database import  get_db
import models


password_hash = PasswordHash.recommended()
bearer_scheme = HTTPBearer()

SECRET_KEY = "Temporary-deve;opment-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
        plain_password: str,
        hashed_password: str
) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt


def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        db: Session = Depends(get_db)
):

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise  HTTPException(
                status_code=401,
                detail="Invalid"
            )

        user = db.query(models.User).filter(
            models.User.id == int(user_id)
        )

        if user is None:
            raise  HTTPException(
                status_code=401,
                detail= "User not found"
            )

        return user

    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
