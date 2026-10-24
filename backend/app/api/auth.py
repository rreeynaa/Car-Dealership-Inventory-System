from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import EmailAlreadyRegisteredError
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserOut
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
