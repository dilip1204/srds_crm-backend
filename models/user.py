from enum import Enum
from pydantic import BaseModel, EmailStr

class RoleEnum(str, Enum):
    ADMIN = "Admin"
    INSTRUCTOR = "Instructor"
    STUDENT = "Student"

class User(BaseModel):
    id: str = None
    name: str
    email: EmailStr
    password: str
    role: RoleEnum

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
