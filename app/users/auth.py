from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from jose import jwt
from pydantic import EmailStr

from app.config import settings
from app.users.dao import UsersDAO

pwd_context = PasswordHasher(time_cost=3, memory_cost=256, parallelism=2)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to verify against
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(hashed_password, plain_password)
    except Exception:
        return False

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    # JWT exp должен быть числом (timestamp), jose автоматически преобразует datetime
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, settings.ALGORITHM
    )
    return encoded_jwt

async def authenticate_user(email: EmailStr, password: str):
    user = await UsersDAO.find_one_or_none(email=email)
    if user and verify_password(password, user.hashed_password):
        return user
    return None