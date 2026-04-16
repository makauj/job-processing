from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.base import Base



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    password_hash = Column(String, nullable=False, default="hashed_password_placeholder")
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"
    
__all__ = ["User"]