from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove


from ..data import get_films
from ..keyboards import build_films_keyboard


film_router = Router()


#Обробник для команди /films та повідомлення із текстом films
@film_router.message(Command("films"))
@film_router.message(F.text.casefold() == "films")
async def show_films_command(message: Message, state: FSMContext) -> None:
   films = get_films()
   keyboard = build_films_keyboard(films)
   await message.answer(
       text="Виберіть будь-який фільм",
       reply_markup=keyboard,
   )
from ..data import get_films, get_film, save_film
from ..fsm import FilmCreateForm

...

@film_router.message(Command("filmcreate"))
@film_router.message(F.text.casefold() == "filmcreate")
@film_router.message(F.text.casefold() == "create film")
async def create_film_command(message: Message, state: FSMContext) -> None:
   await state.clear()
   await state.set_state(FilmCreateForm.title)
   await edit_or_answer(message, "Яка назва фільму?", ReplyKeyboardRemove())




@film_router.message(FilmCreateForm.title)
async def procees_title(message: Message, state: FSMContext) -> None:
   await state.update_data(title=message.text)
   await state.set_state(FilmCreateForm.desc)
   await edit_or_answer(message, "Який опис фільму?", ReplyKeyboardRemove())




@film_router.message(FilmCreateForm.desc)
async def procees_desctription(message: Message, state: FSMContext) -> None:
   data = await state.update_data(desc=message.text)
   await state.set_state(FilmCreateForm.url)
   await edit_or_answer(
       message,
       f"Введіть посилання на фільм: {hbold(data.get('title'))}",
       ReplyKeyboardRemove(),
   )


@film_router.message(FilmCreateForm.url)
@film_router.message(F.text.contains('http'))
async def procees_url(message: Message, state: FSMContext) -> None:
   data = await state.update_data(url=message.text)
   await state.set_state(FilmCreateForm.photo)
   await edit_or_answer(
       message,
       f"Надайте фото для афіші фільму: {hbold(data.get('title'))}",
       ReplyKeyboardRemove(),
   )


@film_router.message(FilmCreateForm.photo)
@film_router.message(F.photo)
async def procees_photo_binary(message: Message, state: FSMContext) -> None:
   photo = message.photo[-1]
   photo_id = photo.file_id


   data = await state.update_data(photo=photo_id)
   await state.set_state(FilmCreateForm.rating)
   await edit_or_answer(
       message,
       f"Надайте рейтинг фільму: {hbold(data.get('title'))}",
       ReplyKeyboardRemove(),
   )


@film_router.message(FilmCreateForm.rating)
async def procees_rating(message: Message, state: FSMContext) -> None:
   data = await state.update_data(rating=message.text)
   await state.clear()
   save_film(data)
   return await show_films_command(message, state)

@film_router.callback_query(F.data == "back")
async def back_handler(callback: CallbackQuery, state: FSMContext) -> None:
   return await show_films_command(callback.message, state)

async def edit_or_answer(message: Message, text: str, keyboard, *args, **kwargs):
   if message.from_user.is_bot:
       await message.edit_text(text=text, reply_markup=keyboard, **kwargs)
   else:
       await message.answer(text=text, reply_markup=keyboard, **kwargs)


from dotenv import load_dotenv
from os import getenv


from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.client.default import DefaultBotProperties
