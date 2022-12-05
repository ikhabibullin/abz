import datetime
from typing import Optional

from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel, Field, UUID4, validator

import service


class Employee(BaseModel):
    full_name: str = Field(min_length=1, max_length=128)
    job_title: str = Field(min_length=1, max_length=128)
    employment_date: datetime.date
    salary: int = Field(ge=1)
    manager_id: UUID4 = None

    class Config:
        orm_mode = True


class PatchEmployee(BaseModel):
    full_name: Optional[str] = Field(min_length=1, max_length=128)
    job_title: Optional[str] = Field(min_length=1, max_length=128)
    employment_date: Optional[datetime.date]
    salary: Optional[int] = Field(ge=1)
    manager_id: Optional[UUID4]


class Login(BaseModel):
    email: str
    password: str


class Register(BaseModel):
    email: str
    password: str

    @validator('password')
    def hash_password(cls, pw: str) -> str:
        password_hash = service.get_password_hash(pw)
        return password_hash


class RegisterOut(BaseModel):
    id: UUID4
    email: str
    access_token: str = None
    refresh_token: str = None

    @validator('access_token', always=True)
    def set_access_token(cls, token, values) -> str:
        token = AuthJWT().create_access_token(subject=values.get('email'))
        return token

    @validator('refresh_token', always=True)
    def set_refresh_token(cls, token, values) -> str:
        token = AuthJWT().create_refresh_token(subject=values.get('email'))
        return token


class Token(BaseModel):
    access_token: str = None
    refresh_token: str = None
