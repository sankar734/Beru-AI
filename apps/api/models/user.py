from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class UserBase(BaseModel):
    email: str = Field(..., pattern=r"^[\w\.\+\-]+@[\w\.\-]+\.\w+$", description="User email address")
    name: str = Field(..., min_length=1, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)

class UserLogin(BaseModel):
    email: str = Field(..., pattern=r"^[\w\.\+\-]+@[\w\.\-]+\.\w+$")
    password: str = Field(..., min_length=1)

class UserResponse(UserBase):
    id: str
    role: str = "user"
    created_at: str
    preferences: Optional[Dict[str, Any]] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenPayload(BaseModel):
    sub: str
    email: str
    role: str
    exp: int
