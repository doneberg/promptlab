from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.config import settings

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(subject: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

        payload = {
            "sub": subject,
            "exp": expire,
        }

        return jwt.encode(
            payload,
            settings.secret_key,
            algorithm="HS256",
        )    @staticmethod
    def create_access_token(subject: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

        payload = {
            "sub": subject,
            "exp": expire,
        }

        return jwt.encode(
            payload,
            settings.secret_key,
            algorithm="HS256",
        )