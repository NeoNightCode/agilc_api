from fastapi import APIRouter, HTTPException, status
from config.db import database
from models.usuario import User, LoginUser
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os

ACCESS_TOKEN_DURATION =30
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

router = APIRouter(tags=["Autentificación"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "Not found"}})


@router.post('/login')
async def auth_login(login: LoginUser):
    '''
    Ruta de login de usuarios
    {
        'username' : 'username/email',
        'password' : 'hashedPassword',
    }
    '''
    user = await database.users.find_one({'email': login.email})

    if user is not None and login.password == user['password']:
        to_encode = {"sub": user['email']}
        refresh_expire = datetime.utcnow() + timedelta(days=30)
        refresh_token = jwt.encode({**to_encode, "exp": refresh_expire}, SECRET_KEY, algorithm=ALGORITHM)
        return {"refresh_token": refresh_token}

    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña incorrecta o usuario no encontrado")


@router.post('/register')
async def register_user(user: User):
    '''
    Ruta de registro de usuarios
    {
        'name' : 'name',
        'surname' : 'surname',
        'email' : 'email',
        'password' : 'hashedPassword',
    }
    '''
    new_user = dict(user)
    del new_user['id']

    id = await database.users.insert_one(new_user).inserted_id
    user = await database.users.find_one({'_id': id})
    to_encode = {"sub": user['email']}
    refresh_expire = datetime.utcnow() + timedelta(days=30)
    refresh_token = jwt.encode({**to_encode, "exp": refresh_expire}, SECRET_KEY, algorithm=ALGORITHM)
    return {"refresh_token": refresh_token}


@router.post('/access_token')
async def get_access_token(refresh_token: str):
    '''
    Ruta para obtener token de acceso
    {
        'refresh_token' : 'refresh_token'
    }
    '''
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        # Convertir el valor 'exp' en un objeto datetime
        exp_datetime = datetime.fromtimestamp(payload["exp"])

        if exp_datetime < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de actualización expirado")

        user = await database.users.find_one({'email': payload["sub"]})
        access_token = create_access_token({"sub": user['email']})

        return access_token;
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de actualización inválido")


@router.get("/account")
async def get_account(access_token: str):
    '''
    Ruta para obtener datos basicos del usuario
    {
    'access_token' : 'access_token'
    }
    '''
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user = await database.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
        return {"id": str(user["_id"]), "name": user["name"], "email": user["email"]}
    except jwt.DecodeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")


@router.get("/account/favorites")
async def get_favorites(access_token: str):
    '''
    Ruta para obtener datos basicos del usuario
    {
       'access_token' : 'access_token',
    }
    '''
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user = await database.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")

        user_favorites = await database.user_favorites.find_one({"user_id": user["_id"]})
        if not user_favorites:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo recuperar la lista de favoritos del usuario")

        favorites = {
            'competitions' : user_favorites['competiciones'],
            'teams' : user_favorites['equipos'],
        }

        return favorites


    except jwt.DecodeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")

### Funciones Complementarias
def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_DURATION):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token}
