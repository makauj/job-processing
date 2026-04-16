from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=4)
    password: str = Field(min_length=8)
    email: str | None = None


class UserLogin(BaseModel):
    username: str = Field(min_length=4)
    password: str = Field(min_length=8)
    
class UserResponse(BaseModel):
    id: int
    username: str
    email: str | None = None
    created_at: str

    class Config:
        orm_mode = True

__all__ = ["UserCreate", "UserLogin", "UserResponse"]