from typing import Optional

from pydantic import BaseModel


class UserRequest(BaseModel):
    username:str
    email:str
    first_name:str
    last_name: str
    password:str
    role:str


class UserPublic(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    role: str

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        orm_mode = True


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str