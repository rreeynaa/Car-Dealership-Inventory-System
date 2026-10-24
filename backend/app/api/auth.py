from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import EmailAlreadyRegisteredError, InvalidCredentialsError
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user import LoginRequest, TokenOut, UserCreate, UserOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, service: AuthService = Depends(get_auth_service)):
    """Register a new (non-admin) user."""
    try:
        return service.register(data)
    except EmailAlreadyRegisteredError:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")


@router.post("/login", response_model=TokenOut)
def login(data: LoginRequest, service: AuthService = Depends(get_auth_service)):
    """Exchange email and password for a JWT access token."""
    try:
        user, token = service.login(data.email, data.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenOut(access_token=token, user=user)
