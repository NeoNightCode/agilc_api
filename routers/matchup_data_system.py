from fastapi import APIRouter, status
from config.db import database
from global_funcs import global_func
from asyncio import gather
from datetime import datetime

router = APIRouter(tags=["Datos Ultimos Enfrentamientos"], responses={status.HTTP_404_NOT_FOUND: {"message": "Not found"}})

# Obtener los últimos enfrentamientos
@router.get("/ultimos_enfrentamientos")
async def get_recent_matchups():
    current_date = datetime.now()

    matchups = await database.matchups.find({"date": {"$lt": current_date}}).sort("date", -1).limit(10).to_list(length=10)

    json_matchups = []

    for matchup in matchups:
        matchup_data = await global_func.get_matchup(str(matchup['_id']))

        json_matchups.append(matchup_data)

    return json_matchups
