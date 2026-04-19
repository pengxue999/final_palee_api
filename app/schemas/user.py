from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    user_name: str
    user_password: str
    role: str

class UserUpdate(BaseModel):
    user_name: Optional[str] = None
    user_password: Optional[str] = None
    role: Optional[str] = None

class UserResponse(BaseModel):
    user_id: int
    user_name: str
    role: str
    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    user_name: str
    user_password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    user_name: str
    role: str
    teacher_id: Optional[str] = None
