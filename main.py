import os
import sys
import django
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

# Django setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

from bot.run import start_router   

async def main():
    dp.include_router(start_router)   
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
