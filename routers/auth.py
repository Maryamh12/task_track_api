from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


from app import models, schemas
from app.database import get_db
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=201
)
def register_user(
        user: schemas.UserCreate,
        db: Session = Depends(get_db)
):
    existing_email = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_email:
        print(existing_email)
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    existing_username = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if existing_username:
        print(existing_username)
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )

    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post(
    "/login",
    response_model=schemas.Token
)
def login_user(
        login_data: schemas.UserLogin,
        db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.email == login_data.email
    ).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
            login_data.password,
            user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    access_token = create_access_token(
        {
            "sub": str(user.id)
        }
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get(
    "/me",
    response_model=schemas.UserResponse
)
def get_me(
        current_user: models.User = Depends(get_current_user)
):

    return current_user