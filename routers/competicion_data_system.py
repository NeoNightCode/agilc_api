from fastapi import APIRouter, status
from config.db import database
from global_funcs import global_func
from asyncio import gather

router = APIRouter(tags=["Competition Data"], responses={status.HTTP_404_NOT_FOUND: {"message": "Not found"}})

# Get all competitions
@router.get("/competiciones/{clasificacion}")
async def get_competitions(clasificacion: str):
    competitions = await database.competitions.find().to_list(length=1000)
    json_competitions = []

    for i, competition in enumerate(competitions, start=1):
        if competition['classification'] == clasificacion or clasificacion == 'all':
            teams_coroutines = [global_func.get_team(team_id) for team_id in competition['teams']]
            fixtures_coroutines = [global_func.get_fixture(fixture_id) for fixture_id in competition['fixtures']]

            teams_results, fixtures_results, category, classification = await gather(
                gather(*teams_coroutines),
                gather(*fixtures_coroutines),
                global_func.get_competition_category(competition['category']),
                global_func.get_competition_classification(competition['classification'])
            )

            teams = list(teams_results)
            fixtures = list(fixtures_results)

            competition_data = {
                "_id": str(competition['_id']),
                "name": competition['name'],
                "edition": competition['edition'],
                "category": category,
                "classification": classification,
                "teams": teams,
                "fixtures": fixtures
            }

            json_competitions.append(competition_data)

    return json_competitions


# Get data for a specific competition
@router.get("/Competiciones/{id}")
async def get_competition(id: str):
    return await global_func.get_competition(id)
