from fastapi import HTTPException, status
from dateutil.relativedelta import relativedelta
from config.db import database
from datetime import date, datetime
from bson import ObjectId
from asyncio import gather


### Data Retrieval by ID ###

async def get_island(island_id):
    island = await database.islands.find_one({"_id": ObjectId(island_id)})
    island_name = island['name'] if island else None
    return island_name

async def get_age(birthdate):
    age = relativedelta(date.today(), birthdate).years
    return age

async def get_fighter_category(category_id):
    category = await database.categories_fighters.find_one({"_id": ObjectId(category_id)})
    category_name = category['name'] if category else None
    return category_name

async def get_fighter_classification(classification_id):
    classification = await database.rankings_fighters.find_one({"_id": ObjectId(classification_id)})
    classification_name = classification['name'] if classification else None
    return classification_name

async def get_competition_category(category_id):
    category = await database.categories_competitions.find_one({"_id": ObjectId(category_id)})
    category_name = category['name'] if category else None
    return category_name

async def get_competition_classification(classification_id):
    classification = await database.rankings_competitions.find_one({"_id": ObjectId(classification_id)})
    classification_name = classification['name'] if classification else None
    return classification_name

async def get_management_position(position_id):
    position = await database.managerial_positions.find_one({"_id": ObjectId(position_id)})
    position_name = position.get('name') if position else None
    return position_name


### Fighter ###
async def get_fighter(fighter_id):
    fighter = await database.fighters.find_one({"_id": ObjectId(fighter_id)})
    if fighter is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fighter not found")

    category, classification, age = await gather(
        get_fighter_category(fighter['category']),
        get_fighter_classification(fighter['classification']),
        get_age(fighter['birthdate'])
    )

    fighter_data = {
        "_id": str(fighter['_id']),
        "name": f"{fighter['name']} {fighter['surnames']}",
        "registration_number": fighter['registration_number'],
        "category": category,
        "classification": classification,
        "image": fighter['image'],
        "age": age,
    }

    return fighter_data


### Management Personnel ###
async def get_management_personnel(personnel_id):
    personnel = await database.management_personnel.find_one({"_id": ObjectId(personnel_id)})
    if personnel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Management personnel not found")

    position, age = await gather(
        get_management_position(personnel['position']),
        get_age(personnel['birthdate'])
    )

    personnel_data = {
        "_id": str(personnel['_id']),
        "name": f"{personnel['name']} {personnel['surnames']}",
        "position": position,
        "image": personnel['image'],
        "age": age,
    }

    return personnel_data


### Team ###
async def get_team(team_id):
    team = await database.teams.find_one({"_id": ObjectId(team_id)})

    wrestlers_tasks = [get_fighter(fighter_id) for fighter_id in team['fighters']]
    executives_tasks = [get_management_personnel(executive_id) for executive_id in team['personnel']]

    luchadores_results, directivos_results, island = await gather(
        gather(*wrestlers_tasks),
        gather(*executives_tasks),
        get_island(team['island'])
    )

    fighters = list(luchadores_results)
    personnel = list(directivos_results)

    team_data = {
        "_id": str(team['_id']),
        "name": team['name'],
        "island": island,
        "fighters": fighters,
        "personnel": personnel,
        "image": team['logo']
    }
    return team_data

async def get_island_teams(island_id):
    teams = await database.teams.find().to_list(length=1000)
    json_teams = []

    for i, team in enumerate(teams, start=1):
        if team['island'] == island_id:
            fighters_coroutines = [
                get_fighter(fighter_id)
                for fighter_id in team['fighters'].values()
            ]
            personnel_coroutines = [
                get_management_personnel(personnel_id)
                for personnel_id in team['personnel'].values()
            ]

            fighters_results, personnel_results, island = await gather(
                gather(*fighters_coroutines),
                gather(*personnel_coroutines),
                get_island(team['island'])
            )

            fighters = list(fighters_results)
            personnel = list(personnel_results)

            team_data = {
                "_id": str(team['_id']),
                "name": team['name'],
                "island": island,
                "fighters": fighters,
                "personnel": personnel,
                "image": team['logo']
            }

            json_teams.append(team_data)

    return json_teams


async def get_team_name(team_id):
    team = await database.teams.find_one({"_id": ObjectId(team_id)})

    return f"C.L. {team['name']}"


async def get_team_image(team_id):
    team = await database.teams.find_one({"_id": ObjectId(team_id)})

    return team['logo']


### Competitions ###
async def get_competition(competition_id):

    competition = await database.competitions.find_one({"_id": ObjectId(competition_id)})
    teams_coroutines = [
        get_team_name(team_id)
        for team_id in competition['teams'].values()
    ]
    fixtures_coroutines = [
        get_fixture(fixture_id)
        for fixture_id in competition['fixtures'].values()
    ]

    teams_results, fixtures_results = await gather(
        gather(*teams_coroutines),
        gather(*fixtures_coroutines),
    )

    teams = {
        team: result
        for team, result in zip(competition['teams'].keys(), teams_results)
    }
    fixtures = {
        fixture: result
        for fixture, result in zip(competition['fixtures'].keys(), fixtures_results)
    }

    competition_data = {
        "_id": str(competition['_id']),
        "name": competition['name'],
        "edition": competition['edition'],
        "category": competition['category'],
        "teams": teams,
        "fixtures": fixtures
    }

    return competition_data

async def get_fixture(fixture_id):
    fixture = await database.fixtures.find_one({"_id": ObjectId(fixture_id)})

    matchups_coroutines = [get_matchup(matchup_id) for matchup_id in fixture['matchups']]

    matchups = await gather(*matchups_coroutines)

    fixture_data = {
        "_id": str(fixture['_id']),
        "name": fixture['name'],
        "matchups": matchups
    }
    return fixture_data

async def get_matchup(matchup_id):
    matchup = await database.matchups.find_one({"_id": ObjectId(matchup_id)})

    if 'date' in matchup and matchup['date'] < datetime.now():
        home_team, home_team_image, away_team, away_team_image, match_result = await gather(
            get_team_name(matchup['home_team']),
            get_team_image(matchup['home_team']),
            get_team_name(matchup['away_team']),
            get_team_image(matchup['away_team']),
            get_match_result(matchup_id)
        )
        results = {
            'done' : True,
            'points_home_team' : match_result['points_home_team'],
            'points_away_team' : match_result['points_away_team'],
            }

    else:
        home_team, home_team_image, away_team, away_team_image = await gather(
            get_team_name(matchup['home_team']),
            get_team_image(matchup['home_team']),
            get_team_name(matchup['away_team']),
            get_team_image(matchup['away_team'])
        )
        results = {'done' : False}

    matchup_data = {
        "home_team": home_team,
        "home_team_image" : home_team_image,
        "away_team": away_team,
        "away_team_image" : away_team_image,
        'results' : results,
        "date": str(matchup['date'])
    }

    return matchup_data

async def get_match_result(matchup_id):
    match_result = await database.match_results.find_one({"matchup": matchup_id})

    match_result_data = {
        "points_home_team": match_result['points_home_team'],
        "points_away_team": match_result['points_away_team']
    }
    return match_result_data


### Prepared Responses ###
async def return_response(response_type, data_list):
    if len(data_list) == 0:
        error_types = {
            'team': {'Not Found': 'No teams found that match the filters.'},
            'fighter': {'Not Found': 'No fighters found that match the filters.'},
            'management_personnel': {'Not Found': 'No management personnel found that match the filters.'},
        }
        return error_types[response_type]
    return data_list
