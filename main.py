from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()
from datos_pruebas.generator import create_competition, delete_old_data
from routers import auth_system, directivo_data_system, luchador_data_system, equipo_data_system, competicion_data_system, matchup_data_system
from middlewares import api_keys_middleware

description = """
AGILC API te permite obtener registros actualizados de la Lucha Canaria. 🚀

## Luchadores
- Obtener listado global de luchadores.
- Obtener información de cada luchador.

## Directivos
- Obtener listado global de directivos.
- Obtener información de cada directivo.

## Equipos
- Obtener listado global de equipos.
- Obtener información de cada equipo.
- Obtener listado de luchadores pertenecientes al equipo.
- Obtener listado de directivos pertenecientes al equipo.

## Competiciones
- Obtener listado de competicines.
- Obtener calendario de una competicios especifica.

## Islas
- Obtener listado de islas.
- Obtener competiciones por Isla.
- Obtener equipos por Isla.

## Categorias
- Obtener listado de categorias.

## Clasificaciones
- Obtener listado de clasificaciones.

"""
app = FastAPI(
    title="AGILC API",
    description=description,
    version="1.0.4",
)

### Middlewares ###
app.middleware("http")(api_keys_middleware.api_key_middleware)

### Routers ###
app.include_router(auth_system.router)
app.include_router(directivo_data_system.router)
app.include_router(luchador_data_system.router)
app.include_router(equipo_data_system.router)
app.include_router(competicion_data_system.router)
app.include_router(matchup_data_system.router)


@app.get("/")
async def root():
    #print( await delete_old_data())
    #result = await create_competition("Torneo Fundacion La Caja De Canarias", "XXXVIII", "645e9d2a1b5d0c26ccb1beec", "6469221a2e9ee98457708daa")
    return {'Status':'Running'}
