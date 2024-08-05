from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.markdown import hbold

from ..data import get_films, get_film, save_film,del_film
from ..keyboards import build_films_keyboard,build_film_details_keyboard
from ..fsm import FilmCreateForm

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


@film_router.callback_query(F.data.startswith("film_"))
async def show_film_details(callback: CallbackQuery, state: FSMContext) -> None:
   film_id = int(callback.data.split("_")[-1])
   film = get_film(film_id)
   text = f"Назва:{hbold(film.get('title'))}\nОпис:{hbold(film.get('desc'))}\nРейтинг:{hbold(film.get('rating'))}"
   photo_id = film.get('photo')
   url = film.get('url')
   await callback.message.answer_photo(photo_id)
   await edit_or_answer(callback.message, text, build_film_details_keyboard(url,film_id))


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


@film_router.callback_query(F.data.startswith("remove_"))
async def remove_film(callback: CallbackQuery, state: FSMContext) -> None:
   film_id = int(callback.data.split("_")[-1])
   del_film(film_id)

   await callback.message.answer(text="Успішно видаленно",)
