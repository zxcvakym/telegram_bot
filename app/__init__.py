from os import getenv

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.client.default import DefaultBotProperties

from .routers import film_router


# Завантажимо дані середовища з файлу .env(За замовчуванням)
load_dotenv()


# Усі обробники варто закріплювати за Router або Dispatcher
root_router = Router()
root_router.include_router(film_router)

# Обробник для команди /start
@root_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
   await message.answer(f"Вітаю, {hbold(message.from_user.full_name)}!")



# Головна функція пакету
async def main() -> None:
   # Дістанемо токен бота з середовища
   TOKEN = getenv("BOT_API")
   # Створимо об'єкт Bot
   bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


   dp = Dispatcher()
   dp.include_router(root_router)
   # Почнемо обробляти події для бота
   await dp.start_polling(bot)
