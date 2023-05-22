from datetime import datetime, date, time
from bson import ObjectId
from config.db import database
from models import competition_model, fighter_model, management_personnel_model, team_model
from dateutil.relativedelta import relativedelta
from faker import Faker
import random
import json

fake = Faker('es_ES')

Fighter = fighter_model.Fighter
ManagementPersonnel = management_personnel_model.ManagementPersonnel
Team = team_model.Team
Competition = competition_model.Competition
Fixture = competition_model.Fixture
Matchup = competition_model.Matchup
MatchResult = competition_model.MatchResult

positions = {
    'Presidente': "645d3f4d0d2f7f11f1cadfff",
    'Vicepresidente': "645d3f4d0d2f7f11f1cae000",
    'Secretario': "645d3f4d0d2f7f11f1cae001",
    'Tesorero': "645d3f4d0d2f7f11f1cae002",
    'Vocal': "645d3f4d0d2f7f11f1cae003",
    'Coordinador Deportivo': "645d3f4d0d2f7f11f1cae004",
    'Entrenador': "645d3f4d0d2f7f11f1cae005",
    'Preparador Fisico': "645d3f4d0d2f7f11f1cae006",
    'Monitor de Base': "645d3f4d0d2f7f11f1cae007"
}

classifications = {
    'Puntal A': "645e9d9b1b5d0c26ccb1bef2",
    'Puntal B': "645e9d9b1b5d0c26ccb1bef3",
    'Puntal C': "645e9d9b1b5d0c26ccb1bef4",
    'Destacado A': "645e9d9b1b5d0c26ccb1bef5",
    'Destacado B': "645e9d9b1b5d0c26ccb1bef6",
    'Destacado C': "645e9d9b1b5d0c26ccb1bef7",
    'No Clasificado': "645e9d9b1b5d0c26ccb1bef8"
}

classification_points = {
    'Puntal A': 0,
    'Puntal B': 0,
    'Puntal C': 0,
    'Destacado A': 6,
    'Destacado B': 4,
    'Destacado C': 2,
    'No Clasificado': 0
}

async def generate_fighter(category: str, classification: str) -> Fighter:
    birth_date = fake.date_of_birth(minimum_age=18, maximum_age=40)
    birth_datetime = datetime.combine(birth_date, time())
    return Fighter(
        _id=str(ObjectId()),
        name=fake.first_name(),
        surnames=f"{fake.last_name()} {fake.last_name()}",
        registration_number=fake.unique.random_number(digits=9, fix_len=True),
        birthdate=birth_datetime,
        category="645e9d2a1b5d0c26ccb1beec",
        classification=classifications[classification],
        image="https://guanxemc.net/img/default.png",
        dni=fake.unique.random_number(digits=9, fix_len=True)
    )

async def generate_and_insert_fighters():
    fighters = []
    points = 0
    option = random.randint(1, 3)

    if option == 1:
        fighters.append(await generate_fighter('Category 1', 'Puntal A'))
        fighters.append(await generate_fighter('Category 1', 'Puntal C'))
        points = 12
    elif option == 2:
        fighters.append(await generate_fighter('Category 1', 'Puntal B'))
        fighters.append(await generate_fighter('Category 1', 'Puntal C'))
        points = 16
    elif option == 3:
        fighters.append(await generate_fighter('Category 1', 'Puntal C'))
        fighters.append(await generate_fighter('Category 1', 'Puntal C'))
        points = 20

    remaining_classifications = ['Destacado A', 'Destacado B', 'Destacado C', 'No Clasificado']

    while len(fighters) < 12:
        for classification in remaining_classifications:
            if classification_points[classification] <= points:
                fighters.append(await generate_fighter('Category 1', classification))
                points -= classification_points[classification]
                break
        else:
            fighters.append(await generate_fighter('Category 1', 'No Clasificado'))

    fighters_ids = []
    for i, fighter in enumerate(fighters, start=1):
        new_fighter = fighter.dict()
        fighter_id = await database.fighters.insert_one(new_fighter)
        fighters_ids.append(str(fighter_id.inserted_id))

    return fighters_ids

async def generate_management_personnel(position: str) -> ManagementPersonnel:
    birth_date = fake.date_of_birth(minimum_age=25, maximum_age=60)
    birth_datetime = datetime.combine(birth_date, time())
    return ManagementPersonnel(
        _id=str(ObjectId()),
        name=fake.first_name(),
        surnames=f"{fake.last_name()} {fake.last_name()}",
        position=positions[position],
        birthdate=birth_datetime,
        image="https://guanxemc.net/img/default.png",
        dni=fake.unique.random_number(digits=9, fix_len=True)
    )

async def generate_and_insert_management_personnel():
    personnel = []

    for position in ['Presidente', 'Vicepresidente', 'Secretario', 'Tesorero', 'Coordinador Deportivo', 'Entrenador', 'Preparador Fisico', 'Monitor de Base']:
        personnel.append(await generate_management_personnel(position))

    for _ in range(3):
        personnel.insert(4, await generate_management_personnel('Vocal'))

    personnel_ids = []
    for i, person in enumerate(personnel, start=1):
        new_person = person.dict()
        person_id = await database.management_personnel.insert_one(new_person)
        personnel_ids.append(str(person_id.inserted_id))  # Aquí se añade el ID del personal a la lista.

    return personnel_ids

async def generate_team(fighters, personnel):
    return Team(
        _id=str(ObjectId()),
        name=fake.company(),
        island="645ed6c42ad793b33666718d",
        municipality=fake.city(),
        classification='Clasificación Desconocida',
        fighters=fighters,
        personnel=personnel,
        logo=fake.image_url(),
        email=fake.company_email()
    )


islands = [
    "645ed6c42ad793b33666718d",
    "645ed6c42ad793b336667191"
]

async def generate_and_insert_teams():
    teams = []

    for i in range(1, 7):
        fighters_data = await generate_and_insert_fighters()
        personnel_data = await generate_and_insert_management_personnel()

        team = await generate_team(fighters_data, personnel_data)
        new_team = team.dict()
        team_id = await database.teams.insert_one(new_team)
        teams.append(str(team_id.inserted_id))

    return teams


async def generate_and_insert_match_results(matchups):
    match_results = []

    current_date = datetime.now()

    for matchup_id in matchups:
        matchup = await database.matchups.find_one({"_id": ObjectId(matchup_id)})

        if matchup["date"] < current_date:
            points_home_team = random.randint(0, 12)
            points_away_team = random.randint(0, 12)

            while points_home_team < 12 and points_away_team < 12:
                points_home_team = random.randint(0, 12)
                points_away_team = random.randint(0, 12)

            result = MatchResult(
                _id=str(ObjectId()),
                matchup=matchup_id,
                points_home_team=str(points_home_team),
                points_away_team=str(points_away_team)
            )

            new_result = result.dict()
            result_id = await database.match_results.insert_one(new_result)
            match_results.append(str(result_id.inserted_id))

    return match_results

async def generate_and_insert_matchups(teams):
    matchups = []

    matchup_data = [
        {"_id": ObjectId("645fc2a6d165a84b35d5eda7"), "home_team": teams[0], "away_team": teams[1], "date": datetime(2023, 5, 4, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5eda8"), "home_team": teams[2], "away_team": teams[3], "date": datetime(2023, 5, 5, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5eda9"), "home_team": teams[4], "away_team": teams[5], "date": datetime(2023, 5, 6, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edaa"), "home_team": teams[3], "away_team": teams[4], "date": datetime(2023, 5, 18, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edab"), "home_team": teams[5], "away_team": teams[0], "date": datetime(2023, 5, 19, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edac"), "home_team": teams[1], "away_team": teams[2], "date": datetime(2023, 5, 20, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edad"), "home_team": teams[2], "away_team": teams[5], "date": datetime(2023, 6, 14, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edae"), "home_team": teams[0], "away_team": teams[4], "date": datetime(2023, 6, 15, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edaf"), "home_team": teams[1], "away_team": teams[3], "date": datetime(2023, 6, 16, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edb0"), "home_team": teams[0], "away_team": teams[3], "date": datetime(2023, 6, 21, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edb1"), "home_team": teams[4], "away_team": teams[2], "date": datetime(2023, 6, 22, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edb2"), "home_team": teams[5], "away_team": teams[1], "date": datetime(2023, 6, 23, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edb3"), "home_team": teams[1], "away_team": teams[4], "date": datetime(2023, 6, 28, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edb4"), "home_team": teams[2], "away_team": teams[0], "date": datetime(2023, 6, 29, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edb5"), "home_team": teams[3], "away_team": teams[5], "date": datetime(2023, 6, 30, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edb6"), "home_team": teams[3], "away_team": teams[2], "date": datetime(2023, 7, 4, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edb7"), "home_team": teams[5], "away_team": teams[4], "date": datetime(2023, 7, 5, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edb8"), "home_team": teams[1], "away_team": teams[0], "date": datetime(2023, 7, 6, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edb9"), "home_team": teams[0], "away_team": teams[5], "date": datetime(2023, 7, 11, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edba"), "home_team": teams[4], "away_team": teams[3], "date": datetime(2023, 7, 12, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edbb"), "home_team": teams[2], "away_team": teams[1], "date": datetime(2023, 7, 13, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edbc"), "home_team": teams[4], "away_team": teams[0], "date": datetime(2023, 7, 18, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edbd"), "home_team": teams[3], "away_team": teams[1], "date": datetime(2023, 7, 19, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edbe"), "home_team": teams[5], "away_team": teams[2], "date": datetime(2023, 7, 20, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edbf"), "home_team": teams[1], "away_team": teams[5], "date": datetime(2023, 8, 2, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edc0"), "home_team": teams[2], "away_team": teams[4], "date": datetime(2023, 8, 3, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edc1"), "home_team": teams[3], "away_team": teams[0], "date": datetime(2023, 8, 4, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edc2"), "home_team": teams[1], "away_team": teams[3], "date": datetime(2023, 8, 9, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edc3"), "home_team": teams[0], "away_team": teams[5], "date": datetime(2023, 8, 10, 21, 0)},
        {"_id": ObjectId("645fc2a6d165a84b35d5edc4"), "home_team": teams[4], "away_team": teams[2], "date": datetime(2023, 8, 11, 21, 0)}
    ]

    for data in matchup_data:
        matchup = Matchup(
            _id=str(data["_id"]),
            home_team=data["home_team"],
            away_team=data["away_team"],
            date=data["date"]
        )

        new_matchup = matchup.dict()
        matchup_id = await database.matchups.insert_one(new_matchup)
        matchups.append(str(matchup_id.inserted_id))

    return matchups

async def generate_and_insert_fixtures(teams):
    fixtures = []
    matchups = await generate_and_insert_matchups(teams)
    matchups_results = await generate_and_insert_match_results (matchups)
    num_matchups_per_fixture = 3

    num_fixtures = len(matchups) // num_matchups_per_fixture

    for i in range(num_fixtures):
        fixture_matchups = matchups[i * num_matchups_per_fixture : (i + 1) * num_matchups_per_fixture]
        fixture_name = f"JO{i+1}"

        fixture = Fixture(
            _id=str(ObjectId()),
            name=fixture_name,
            matchups=fixture_matchups
        )

        new_fixture = fixture.dict()
        fixture_id = await database.fixtures.insert_one(new_fixture)
        fixtures.append(str(fixture_id.inserted_id))

    return fixtures

async def create_competition(name: str, edition: str, category: str, classification: str) -> str:
    teams = await generate_and_insert_teams()
    fixtures = await generate_and_insert_fixtures(teams)

    competition = Competition(
        name=name,
        edition=edition,
        category=category,
        classification=classification,
        teams=teams,
        fixtures=fixtures
    )

    new_competition = competition.dict()
    competition_id = await database.competitions.insert_one(new_competition)

    return {f"Competición con ID: {str(competition_id.inserted_id)} creada correctamente!"}



async def delete_old_data():
    await database.matchups.delete_many({})
    await database.management_personnel.delete_many({})
    await database.fighters.delete_many({})
    await database.fixtures.delete_many({})
    await database.teams.delete_many({})
    await database.match_results.delete_many({})
    await database.competitions.delete_many({})

    return "Old data deleted successfully."
