from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.exceptions import EmailAlreadyRegisteredError, InvalidCredentialsError
from app.core.limiter import limiter
from app.db.session import get_db
from app.models import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import LoginRequest, TokenOut, UserCreate, UserOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


# Decorator order matters: @router.post must be outermost, so FastAPI registers
# the rate-limited wrapper. slowapi also requires a parameter named "request".
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@limiter.limit(lambda: settings.register_rate_limit)
def register(
    request: Request,
    data: UserCreate,
    service: AuthService = Depends(get_auth_service),
):
    """Register a new (non-admin) user."""
    try:
        return service.register(data)
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="Email already registered"
        ) from None


@router.post("/login", response_model=TokenOut)
@limiter.limit(lambda: settings.login_rate_limit)
def login(
    request: Request,
    data: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    """Exchange email and password for a JWT access token."""
    try:
        user, token = service.login(data.email, data.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    return TokenOut(access_token=token, user=user)


@router.get("/me", response_model=UserOut)
def read_current_user(user: Annotated[User, Depends(get_current_user)]):
    """Return the authenticated user (used by the frontend to restore a session)."""
    return user