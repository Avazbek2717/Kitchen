import os
import sys
import django
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

# Django settings ulash
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

# Bot sozlamalari
load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Routers import qilish


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
import os
import sys
import django
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

# Django settings ulash
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

# Bot sozlamalari
load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Routers import qilish


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())