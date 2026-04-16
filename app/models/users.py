from datetime import datetime
import base64
import binascii
import hmac
import secrets
from hashlib import pbkdf2_hmac

from sqlalchemy import Column, Integer, String, DateTime

from app.db.base import Base


HASH_ALGORITHM = "sha256"
HASH_ITERATIONS = 200000
SALT_SIZE = 16


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    password_hash = Column(String, nullable=False)

    def set_password(self, password: str) -> None:
        salt = secrets.token_bytes(SALT_SIZE)
        password_hash = pbkdf2_hmac(
            HASH_ALGORITHM,
            password.encode("utf-8"),
            salt,
            HASH_ITERATIONS,
        )
        encoded_salt = base64.b64encode(salt).decode("ascii")
        encoded_hash = base64.b64encode(password_hash).decode("ascii")
        self.password_hash = f"{HASH_ITERATIONS}${encoded_salt}${encoded_hash}"

    def check_password(self, password: str) -> bool:
        try:
            iterations_text, encoded_salt, encoded_hash = self.password_hash.split("$", 2)
            iterations = int(iterations_text)
            salt = base64.b64decode(encoded_salt)
            expected_hash = base64.b64decode(encoded_hash)
        except (ValueError, TypeError, binascii.Error):
            return False

        actual_hash = pbkdf2_hmac(
            HASH_ALGORITHM,
            password.encode("utf-8"),
            salt,
            iterations,
        )
        return hmac.compare_digest(actual_hash, expected_hash)

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"


__all__ = ["User"]