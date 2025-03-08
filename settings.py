import os
from dotenv import load_dotenv

load_dotenv()

# Environment
ENVIRONMENT = os.environ.get("ENVIRONMENT")

# Fast API Root Path
ROOT_PATH = os.environ.get("ROOT_PATH", "")

# Connect to PostgreSQL
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")

# JWT Config
JWT_PREFIX = os.environ.get("JWT_PREFIX", "Bearer")
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

TZ = os.environ.get("TIMEZONE", "Asia/Jakarta")

SEED_EMAIL = os.environ.get("SEED_EMAIL")
SEED_PASS = os.environ.get("SEED_PASS")

LAT_OF_CENTER = float(os.environ.get("LAT_OF_CENTER"))
LONG_OF_CENTER = float(os.environ.get("LONG_OF_CENTER"))
# Value dalam bentuk Kilometer
CHECK_RADIUS= float(os.environ.get("CHECK_RADIUS", 5.00))