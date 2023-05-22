from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class Fighter(BaseModel):
    _id: Optional[str]
    name: str
    surnames: str
    registration_number: str
    birthdate: datetime
    category: str
    classification: str
    image: str
    dni: str

class Category(BaseModel):
    _id: str
    name: str

class Classification(BaseModel):
    _id: str
    name: str
