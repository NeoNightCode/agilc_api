from fastapi import APIRouter, status
from config.db import database
from global_funcs import global_func
from asyncio import gather

router = APIRouter(tags=["Datos Equipos"], responses={status.HTTP_404_NOT_FOUND: {"message": "Not found"}})

# Get all teams
@router.get("/equipos/{id_isla}")
async def get_teams(id_isla: str):
    teams = await database.teams.find().to_list(length=1000)
    json_teams = []

    for i, team in enumerate(teams, start=1):
        if team['island'] == id_isla or id_isla == 'all':
            wrestlers_tasks = [global_func.get_fighter(fighter_id) for fighter_id in team['fighters']]
            executives_tasks = [global_func.get_management_personnel(executive_id) for executive_id in team['personnel']]

            luchadores_results, directivos_results, isla = await gather(
                gather(*wrestlers_tasks),
                gather(*executives_tasks),
                global_func.get_island(team['island'])
            )

            luchadores = list(luchadores_results)
            directivos = list(directivos_results)

            team_data = {
                "_id": str(team['_id']),
                "name": "C.L. " + team['name'],
                "island": isla,
                "fighters": luchadores,
                "personnel": directivos,
                "image": team['logo']
            }

            json_teams.append(team_data)

    return await global_func.return_response('team', json_teams)


# Get data for a specific team
@router.get("/equipos/{id_isla}/{id_equipo}")
async def get_team(id_equipo: str):
    return await global_func.get_team(id_equipo)
