import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_PORT = os.environ.get('DB_PORT')

if DB_HOST and DB_USER and DB_PASSWORD and DB_PORT and DB_NAME:
    ENGINE = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
else:
    ENGINE = "sqlite+aiosqlite:///./database/database.db"

WEBAPP_URL = 'https://yrugi.spac'
BOT_TOKEN = '7091456940:AAH_E9UxyThodpMBXSgtJ0crq_wOPZsUaV0'
WEBHOOK_HOST = 'https://yrugi.spac'
WEBHOOK_PATH = '/webhook'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'h56xW32'