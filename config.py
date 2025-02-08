import os
import sys
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

class Config:
    TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN') or sys.exit("خطا: توکن تلگرام تنظیم نشده است.")
    DB_FILE: str = os.getenv('DB_FILE', 'users.db')
    BASE_URL: str = os.getenv('BASE_URL', 'https://divar.ir/s/tehran/real-estate')
    REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB: int = int(os.getenv('REDIS_DB', 0))
    MAX_WORKERS: int = int(os.getenv('MAX_WORKERS', 10))
    SCRAPING_TIMEOUT: int = int(os.getenv("SCRAPING_TIMEOUT", 10))
    RATE_LIMIT: int = int(os.getenv("RATE_LIMIT", 5))
    TELEGRAM_RATE_LIMIT: int = int(os.getenv("TELEGRAM_RATE_LIMIT", 3))
    PROXY_URL: str = os.getenv('PROXY_URL')  # آدرس پروکسی
    PROXY_SECRET: str = os.getenv('PROXY_SECRET')  # رمز پروکسی
