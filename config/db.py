from motor.motor_asyncio import AsyncIOMotorClient
import os
import urllib.parse

mongo_user = urllib.parse.quote_plus(os.getenv('MONGO_USER'))
mongo_pass = urllib.parse.quote_plus(os.getenv('MONGO_PASS'))
mongo_host = os.getenv('MONGO_HOST')
mongo_port = os.getenv('MONGO_PORT')
mongo_url = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}/agilc?authSource=agilc"

client = AsyncIOMotorClient(mongo_url)
database = client['agilc']
