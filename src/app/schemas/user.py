from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str
