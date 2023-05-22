from fastapi import APIRouter, HTTPException, status
from dateutil.relativedelta import relativedelta
from config.db import database
from global_funcs import global_func
from datetime import date
from bson import ObjectId

router = APIRouter(tags=["Datos Directivos"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "Not found"}})

# Obtener todos los directivos
@router.get("/directivos")
async def get_directivos():
    directivos = await database.directivos.find().to_list(length=1000)
    json_directivos = {}

    for i, directivo in enumerate(directivos, start=1):
        datos_directivo = {
            "_id" : str(directivo['_id']),
            "nombre" : f"{directivo['name']} {directivo['surnames']}",
            "cargo": await global_func.get_cargo_directivo(directivo['cargo']),
            "image": directivo['image'],
            "edad": await global_func.get_edad(directivo['birthdate']),
        }

        json_directivos[i] = datos_directivo

    return json_directivos


# Obtener datos de un directivo en especifico
@router.get("/directivos/{id}")
async def get_directivo(id: str):
    return await global_func.get_directivo(id)
