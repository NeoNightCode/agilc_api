from typing import List, Optional
from pydantic import BaseModel

class Team(BaseModel):
    _id: Optional[str]
    name: str
    island: str
    classification: str
    fighters: List
    personnel: List
    email: str
    logo: str
