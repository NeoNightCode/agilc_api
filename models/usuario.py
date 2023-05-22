from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    _id: Optional[str]
    name: str
    surname: str
    username: str
    email: str
    password: str

class LoginUser(BaseModel):
    email: str
    password: str
