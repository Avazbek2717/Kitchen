from aiogram import Bot, types, F, Router
import os
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.database import *
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import CallbackQuery


TOKEN = os.getenv("TOKEN")
start_router = Router()



main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ℹ️ Bot haqida")],
    ],
    resize_keyboard=True
)


class Registration(StatesGroup):
    waiting_for_name = State()

@start_router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    user = await get_user_by_id(str(message.from_user.id))
    if user:
        await message.answer(f"Salom 👋 {user.full_name}, siz allaqachon ro'yxatdan o'tgansiz ✅", reply_markup=main_menu)
    else:
        await message.answer(
            "🌟 <b>Salom va xush kelibsiz!</b> 👋\n\n"
            "Sizni botimizda ko‘rib turganimizdan juda xursandmiz. 🤗\n\n"
            "📌 Iltimos, quyida <b>ismingizni</b> kiriting.\n"
            "Bu bizga siz bilan yanada qulay aloqa qilishga yordam beradi. 🙌",
            parse_mode="HTML"
        )
        await state.set_state(Registration.waiting_for_name)


# Ism qabul qilish
@start_router.message(Registration.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    full_name = message.text.strip()
    created = await create_or_update_user(
        user_id=str(message.from_user.id),
        full_name=full_name
    )


    await message.answer(f"Xush kelibsiz, {full_name}! 🎉", reply_markup=main_menu)
    await state.clear()



@start_router.message(F.text == "ℹ️ Bot haqida")
async def bot_info(message: Message):
    text = (
        "🤖 Bu bot oshxona uchun mo‘ljallangan.\n\n"
        "🍲 Admin ovqat menyusini qo‘shadi\n"
        "✅ Siz ovqatni yeyman yoki ❌ yemayman deb javob berasiz\n"
        "📊 Admin esa statistikani ko‘radi\n\n"
        "👉 Bot sizning ovqatlanishingizni yengillashtirish uchun ishlaydi."
    )
    await message.answer(text, reply_markup=main_menu)



@start_router.callback_query(F.data.startswith("meal_yes_"))
async def meal_callback_handler(callback: CallbackQuery):
    data = callback.data  
    user_id = callback.from_user.id

    # Callback data parsing
    if data.startswith("meal_yes_"):
        response_value = "yes"
        meal_id = int(data.split("_")[-1])
    else:
        return  

    user = await sync_to_async(User.objects.get)(user_id=user_id)
    meal = await sync_to_async(Meal.objects.get)(id=meal_id)

    if meal.status == "ended":
        await callback.answer(
            text=f"❌ {meal.title} uchun ovoz berish tugagan!",
            show_alert=True
        )
        return

    await create_meal_response(user, meal, response_value)

    await callback.message.delete()

    await callback.answer(text=f"Siz {meal.title} uchun '{response_value}' deb javob berdingiz!", show_alert=True)


@start_router.callback_query(F.data.startswith("meal_no_"))
async def meal_callback_handler(callback: CallbackQuery):
    data = callback.data  
    user_id = callback.from_user.id


    if data.startswith("meal_no_"):
        response_value = "no"
        meal_id = int(data.split("_")[-1])
    else:
        return  

    user = await sync_to_async(User.objects.get)(user_id=user_id)
    meal = await sync_to_async(Meal.objects.get)(id=meal_id)

    if meal.status == "ended":
        await callback.answer(
            text=f"❌ {meal.title} uchun ovoz berish tugagan!",
            show_alert=True
        )
        return

    await create_meal_response(user, meal, response_value)

    await callback.message.delete()

    await callback.answer(text=f"Siz {meal.title} uchun '{response_value}' deb javob berdingiz!", show_alert=True)