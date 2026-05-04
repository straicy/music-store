from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    phone: Optional[str] = Field(None, pattern=r"^\+?\d{10,15}$")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    phone: Optional[str] = Field(None, pattern=r"^\+?\d{10,15}$")
    bio: Optional[str] = Field(None, max_length=300)
    city: Optional[str] = Field(None, max_length=100)


class UserPublic(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    bio: Optional[str] = None
    city: Optional[str] = None
    role: str
    avatar: Optional[str] = None
    created_at: datetime
    listings_count: Optional[int] = 0

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserPublic


class RefreshRequest(BaseModel):
    refresh_token: str
