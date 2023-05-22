from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Competition(BaseModel):
    _id: Optional[str]
    name: str
    edition: str
    category: str
    classification: str
    teams: List         # Lista con los ID de los equipos participantes
    fixtures: List      # Lista con los ID de los fixtures de la competicion

class Fixture(BaseModel):
    _id: Optional[str]
    name: str
    matchups: List      # Agrupación de los 3 enfrentamientos semanales

class Matchup(BaseModel):
    _id: Optional[str]
    home_team: str      # ID del equipo local
    away_team: str      # ID del equipo visitante
    date: datetime

class MatchResult(BaseModel):
    _id: str
    matchup: str
    points_home_team: str
    points_away_team: str
