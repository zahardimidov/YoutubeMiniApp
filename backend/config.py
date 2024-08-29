import os
from dotenv import load_dotenv
import pathlib

load_dotenv()

BASE_DIR = pathlib.Path(__file__).parent.parent.resolve()

DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_PORT = os.environ.get('DB_PORT')
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')

if DB_HOST and DB_USER and DB_PASSWORD and DB_PORT and DB_NAME:
    ENGINE = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
else:
    ENGINE = "sqlite+aiosqlite:///./database/database.db"

WEBAPP_URL = 'https://yrugi.space'
BOT_TOKEN = '6953647393:AAGDj91ag-iUjB0Rck80HWw3KNUX1iLIHgc'
WEBHOOK_HOST = 'https://yrugi.space'
WEBHOOK_PATH = '/webhook'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'h56xW32'