from datetime import datetime, timedelta, timezone
import jwt
from jwt import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .config import get_settings
from .database import get_db
from .models import User

# Argon2 password hashing via passlib, as requested. Never store raw passwords.
password_context = CryptContext(schemes=['argon2'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_context.verify(password, hashed)


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        'sub': str(user_id),
        'iat': now,
        'exp': now + timedelta(minutes=settings.access_token_minutes),
        'iss': settings.jwt_issuer,
        'aud': settings.jwt_audience,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm='HS256')


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    unauthorised = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid or expired authentication token',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    settings = get_settings()
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=['HS256'],
            issuer=settings.jwt_issuer, audience=settings.jwt_audience,
            options={'require': ['exp', 'iat', 'sub', 'iss', 'aud']},
        )
        user_id = int(payload['sub'])
    except (InvalidTokenError, TypeError, ValueError, KeyError):
        raise unauthorised from None
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise unauthorised
    return user
