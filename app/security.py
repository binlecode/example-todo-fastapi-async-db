from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .models import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    print(f"authenticate user: {user}")
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
