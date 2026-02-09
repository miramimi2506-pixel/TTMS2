import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MySQL Database Configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "timetable_db4")
}

# Flask Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Application Environment
FLASK_ENV = os.getenv("FLASK_ENV", "production")
DEBUG = FLASK_ENV == "development"