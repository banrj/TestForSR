import os
from datetime import date
from dotenv import load_dotenv
from envparse import Env


load_dotenv()
env = Env()

# DB configuration
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")

REAL_DATABASE_URL = env.str(
    "REAL_DATABASE_URL",
    default=f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

# here limit years_publication
MAX_DATA = date.today().year
MIN_DATA = 300

# url for loading books from other api
LOAD_BOOKS_URL = os.environ.get("LOAD_BOOKS_URL")

# type columns for check in xlsx file
COLUMNS = {
    'title': str,
    'publication_year': int,
    'genre': str,
    'price': int | None,
    'author': str | None,
    'description': str | None,
    'cover_image': str | None
}