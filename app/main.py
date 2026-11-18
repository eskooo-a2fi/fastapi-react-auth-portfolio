from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .auth import create_access_token, get_current_user, hash_password, verify_password
from .config import get_settings
from .database import get_db
from .models import User
from .schemas import TokenResponse, UserLogin, UserPublic, UserRegister

settings = get_settings()
app = FastAPI(title='Portfolio Auth API', version='1.0.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # Specific origins, never '*'+credentials in production
    allow_credentials=False,  # Bearer token in Authorization header, not cookie credentials
    allow_methods=['GET', 'POST'],
    allow_headers=['Authorization', 'Content-Type'],
)


@app.get('/health', tags=['Operations'])
def health() -> dict[str, str]:
    return {'status': 'ok'}


@app.post('/auth/register', response_model=UserPublic, status_code=status.HTTP_201_CREATED, tags=['Auth'])
def register(payload: UserRegister, db: Session = Depends(get_db)) -> User:
    if db.scalar(select(User.id).where(User.email == str(payload.email))):
        raise HTTPException(status_code=409, detail='Email already registered')
    user = User(email=str(payload.email), hashed_password=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:  # Race-safe unique constraint check
        db.rollback()
        raise HTTPException(status_code=409, detail='Email already registered') from None
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    if not user or not verify_password(password, user.hashed_password) or not user.is_active:
        raise HTTPException(status_code=401, detail='Invalid email or password', headers={'WWW-Authenticate': 'Bearer'})
    return user


def token_for(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user.id),
        expires_in=settings.access_token_minutes * 60,
    )


@app.post('/auth/login', response_model=TokenResponse, tags=['Auth'])
def login(payload: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    return token_for(authenticate(db, str(payload.email), payload.password))


@app.post('/auth/token', response_model=TokenResponse, tags=['Auth'])
def oauth2_token(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> TokenResponse:
    # Supports FastAPI's /docs Authorize flow; username field contains email.
    return token_for(authenticate(db, form.username, form.password))


@app.get('/auth/me', response_model=UserPublic, tags=['Auth'])
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user

# Claude Code review exercise:
#   'Review register/login/me for auth bypass, token validation, SQL injection,
#    race conditions, Pydantic validation, CORS and sensitive error handling.
#    Suggest pytest cases, run the tests, and show a diff before editing.'
# The detailed copyable prompts and manual endpoint tests live in CLAUDE_CODE_REVIEW.md.
