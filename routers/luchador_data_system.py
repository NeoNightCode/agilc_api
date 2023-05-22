from fastapi import APIRouter, status
from config.db import database
from global_funcs import global_func
from asyncio import gather

router = APIRouter(tags=["Datos Luchadores"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "Not found"}})

# Get all fighters
@router.get("/luchadores")
async def get_fighters():
    fighters = await database.fighters.find().to_list(length=1000)
    json_fighters = []

    for i, fighter in enumerate(fighters, start=1):
        category, classification, age = await gather(
            global_func.get_fighter_category(fighter['category']),
            global_func.get_fighter_classification(fighter['classification']),
            global_func.get_age(fighter['birthdate']),
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

        json_fighters.append(fighter_data)

    return await global_func.return_response('fighter', json_fighters)


# Get data for a specific fighter
@router.get("/luchadores/{id}")
async def get_fighter(id: str):
    return await global_func.get_fighter(id)
