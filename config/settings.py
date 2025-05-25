import os

class Settings:
    TIKTOK_API_KEY = os.getenv("TIKTOK_API_KEY", "")
    MAX_VIEWS_PER_HOUR = int(os.getenv("MAX_VIEWS_PER_HOUR", "50"))
    DB_PATH = os.getenv("DB_PATH", "~/storage/shared/tiktok-bot/db/accounts.db")