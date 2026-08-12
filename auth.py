from fastapi import (
    APIRouter,
    Depends,
    status
)

from sqlalchemy.orm import Session

from database import get_db

from fastapi.security import OAuth2PasswordRequestForm

from oauth2 import (
    create_access_token,
    get_current_user
)

from schemas import (
    Token,
    UserLogin,
    UserOut,
    UserRegister
)

from services.auth_service import (
    authenticate_user,
    register_user
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ==========================================
# Register
# ==========================================

@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    return register_user(
        db,
        user_data
    )


# ==========================================
# Login
# ==========================================

@router.post(
    "/login",
    response_model=Token
)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    user = authenticate_user(
        db=db,
        username=login_data.username,
        password=login_data.password
    )

    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }



# ==========================================
# OAuth2 Token Login - Swagger Authorize
# ==========================================

@router.post(
    "/token",
    response_model=Token
)
def login_for_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(
        db=db,
        username=form_data.username,
        password=form_data.password
    )

    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ==========================================
# Current User
# ==========================================

@router.get(
    "/me",
    response_model=UserOut
)
def get_me(
    current_user=Depends(
        get_current_user
    )
):
    return current_user