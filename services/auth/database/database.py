from services.database import client
from os import getenv

db = client[getenv("AUTH_SERVICE_MONGO_DATABASE_NAME")]
