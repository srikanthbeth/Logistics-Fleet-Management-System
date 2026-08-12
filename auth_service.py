from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import (
    create_user,
    get_user_by_email,
    get_user_by_username
)

from schemas import UserRegister
from utils import hash_password, verify_password


ALLOWED_ROLES = {
    "Admin",
    "Fleet Manager",
    "Driver"
}


# ==========================================
# Register User
# ==========================================

def register_user(
    db: Session,
    user_data: UserRegister
):
    # Check username
    existing_username = get_user_by_username(
        db,
        user_data.username
    )

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    # Check email
    existing_email = get_user_by_email(
        db,
        user_data.email
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    # Check role
    if user_data.role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid role. Allowed roles: "
                "Admin, Fleet Manager, Driver"
            )
        )

    hashed_password = hash_password(
        user_data.password
    )

    return create_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role
    )


# ==========================================
# Authenticate User
# ==========================================

def authenticate_user(
    db: Session,
    username: str,
    password: str
):
    user = get_user_by_username(
        db,
        username
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(
        password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )

    return user