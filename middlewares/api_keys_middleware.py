import random
import string
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from config.db import database

collection = database['api_keys']


rutas_excluidas = ["/docs", "/openapi.json"]
async def api_key_middleware(request: Request, call_next):
    if request.url.path not in rutas_excluidas:
        if "Authorization" not in request.headers:
            return JSONResponse(content={"error": "Falta la clave de API"}, status_code=status.HTTP_400_BAD_REQUEST)
        api_key = request.headers["Authorization"]
        api_key_document = await collection.find_one({"api_key": api_key})
        if not api_key_document :
            return JSONResponse(content={"error": "Clave de API inválida"}, status_code=status.HTTP_401_UNAUTHORIZED)
        if not api_key_document.get("status", False) :
            return JSONResponse(content={"error": "Clave de API inactiva"}, status_code=status.HTTP_401_UNAUTHORIZED)
    response = await call_next(request)
    return response

async def create_api_key(user_id: int, status: bool=True):
    api_key = '-'.join([''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(6)])  # Genera API key aleatoria

    while(await collection.count_documents({"api_key": api_key}) > 0):
        api_key = '-'.join([''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(6)])

    new_api = {"api_key": api_key, "user_id": user_id, 'status': status}
    await collection.insert_one(new_api)

    return api_key
