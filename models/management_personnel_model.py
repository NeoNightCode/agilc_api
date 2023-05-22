from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ManagementPersonnel(BaseModel):
    _id: Optional[str]
    name: str
    surnames: str
    position: str
    birthdate: datetime
    image: str
    dni: str

class ManagementPosition(BaseModel):
    _id: Optional[str]
    name: str
