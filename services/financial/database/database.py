from services.database import client
from os import getenv

db = client[getenv("FINANCIAL_ADVISOR_SERVICE_MONGO_DATABASE_NAME")]
