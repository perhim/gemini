import asyncio
from aiogram import Bot
from config import Config

async def test_connection():
    bot = Bot(token=Config.TOKEN)
    try:
        await bot.get_me()
        print("✅ اتصال به سرورهای تلگرام موفقیت‌آمیز بود.")
    except Exception as e:
        print(f"❌ خطا در اتصال به سرورهای تلگرام: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
