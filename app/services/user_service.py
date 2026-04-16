from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.users import User


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.name == username).first()


def create_user(db: Session, username: str, password: str, email: str | None = None) -> User:
    existing_user = get_user_by_username(db, username)
    if existing_user:
        raise ValueError("Username already exists")

    if email:
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            raise ValueError("Email already exists")

    user = User(name=username, email=email, password_hash="")
    user.set_password(password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(db, username)
    if not user:
        return None

    if not user.check_password(password):
        return None

    return user

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def get_all_users(db: Session) -> list[User]:
    return db.query(User).all()

def delete_user(db: Session, user_id: int) -> None:
    user = get_user_by_id(db, user_id)
    if user:
        db.delete(user)
        db.commit()
