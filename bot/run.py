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
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton , InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import CallbackQuery
from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Count, Q
from django.conf import settings
from aiogram.types import FSInputFile




TOKEN = os.getenv("TOKEN")
start_router = Router()
admin_id = 5167032738

class CreateMeal(StatesGroup):
    waiting_for_title = State()
    waiting_for_image = State()


class CreateWeeklyMenu(StatesGroup):
    waiting_for_day = State()
    waiting_for_lunch = State()
    waiting_for_dinner = State()

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ℹ️ Bot haqida")],
        [KeyboardButton(text="🍽️ Haftalik menyuni ko‘rish")],
    ],
    resize_keyboard=True
)

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Haftalik menu yaratish"), KeyboardButton(text="✏️ Haftalik menu tahrirlash")],
        [KeyboardButton(text="➕ Ovqat yaratish"), KeyboardButton(text="🗑️ Ovqatni o‘chirish")],
        [KeyboardButton(text="🍽 Ovqatlar ro‘yxati"), KeyboardButton(text="🍽️ Haftalik menyuni ko‘rish")],  # ⬅️ eng pastda alohida tugma
    ],
    resize_keyboard=True
)

async def get_meal_buttons():
    meals = await sync_to_async(list)(Meal.objects.all())

    buttons = [KeyboardButton(text=meal.title) for meal in meals]

    keyboard_rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]

    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_rows,
        resize_keyboard=True
    )
    return keyboard


class Registration(StatesGroup):
    waiting_for_name = State()

@start_router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    user = await get_user_by_id(str(message.from_user.id))
    if user:
        if message.from_user.id == admin_id:
            await message.answer(f"Salom 👋 Admin {user.full_name}", reply_markup=admin_menu)
        else:
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


@start_router.message(F.text == "🍽 Ovqatlar ro‘yxati")
async def show_meals(message: Message):
    meals = await sync_to_async(lambda: list(Meal.objects.all()))()

    if not meals:
        await message.answer("❌ Hozircha ovqatlar mavjud emas!")
        return

    for idx, meal in enumerate(meals, start=1):
        caption = f"<b>{idx}. {meal.title}</b>"

        if meal.image:
            await message.answer_photo(
                photo=FSInputFile(meal.image.path),
                caption=caption,
                parse_mode="HTML"
            )
        else:
            await message.answer(caption, parse_mode="HTML")

UZ_WEEKDAYS = {
    "Monday": "Dushanba",
    "Tuesday": "Seshanba",
    "Wednesday": "Chorshanba",
    "Thursday": "Payshanba",
    "Friday": "Juma",
    "Saturday": "Shanba",
    "Sunday": "Yakshanba",
}

@start_router.message(F.text == "🍽️ Haftalik menyuni ko‘rish")
async def show_weekly_menu(message: Message):
    today = date.today()

    menus = await sync_to_async(lambda: list(
        WeeklyMenu.objects.filter(date__gte=today)
        .select_related("meal")
        .order_by("date")
    ))()

    if not menus:
        await message.answer("❌ Hozircha menyu mavjud emas!")
        return

    weekly_data = {}
    for menu in menus:
        if menu.date not in weekly_data:
            weekly_data[menu.date] = {}
        weekly_data[menu.date][menu.meal_type] = menu.meal

    text = "📅 <b>Haftalik menyu</b>\n\n"
    for menu_date, meals in weekly_data.items():
        weekday_en = menu_date.strftime('%A')  # inglizcha
        weekday_uz = UZ_WEEKDAYS.get(weekday_en, weekday_en)  # o‘zbekcha

        text += (
            f"🗓 <b>{menu_date.strftime('%d-%m-%Y')} ({weekday_uz})</b>\n\n"
            f"🥗 <b>Tushlik:</b>\n👉 {meals.get('lunch').title if meals.get('lunch') else '❌ Belgilanmagan'}\n\n"
            f"🍖 <b>Kechki ovqat:</b>\n👉 {meals.get('dinner').title if meals.get('dinner') else '❌ Belgilanmagan'}\n\n"
            f"{'—'*20}\n\n"
        )

    await message.answer(text, parse_mode="HTML")


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



@start_router.callback_query(F.data.startswith("meal_yes_") | F.data.startswith("meal_no_"))
async def meal_callback_handler(callback: CallbackQuery):
    data = callback.data  
    user_id = callback.from_user.id

    # Callback data parsing
    if data.startswith("meal_yes_"):
        response_value = "yes"
        menu_id = int(data.split("_")[-1])
    elif data.startswith("meal_no_"):
        response_value = "no"
        menu_id = int(data.split("_")[-1])
    else:
        return  

    # 👤 Foydalanuvchi
    user = await sync_to_async(User.objects.get)(user_id=user_id)

    # 🍽 WeeklyMenu
    menu = await sync_to_async(WeeklyMenu.objects.select_related("meal").get)(id=menu_id)

    if menu.status == "ended":
        await callback.answer(
            text=f"❌ {menu.meal.title} uchun ovoz berish tugagan!",
            show_alert=True
        )
        return

    # ✅ Javobni saqlaymiz
    await create_meal_response(user, menu, response_value)

    
    await callback.message.delete()

    # ✅ Keyin oddiy notification yuboramiz
    await callback.message.answer(
        text=f"Siz hozirgi so‘rovnomaga {menu.meal.title} uchun "
             f"{'✅ yeyman' if response_value == 'yes' else '❌ yemayman'} deb javob berdingiz!"
    )


@start_router.message(F.text == "🗑️ Ovqatni o‘chirish")
async def delete_meal_menu(message: Message):
    meals = await sync_to_async(lambda: list(Meal.objects.all()))()

    if not meals:
        await message.answer("❌ Ovqatlar mavjud emas!")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for meal in meals:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"🗑️ {meal.title}",
                callback_data=f"delete_meal:{meal.id}"
            )
        ])

    await message.answer("🗑️ Qaysi ovqatni o‘chirmoqchisiz?", reply_markup=keyboard)

@start_router.callback_query(F.data.startswith("delete_meal:"))
async def confirm_delete_meal(callback: CallbackQuery):
    meal_id = int(callback.data.split(":")[1])

    meal = await sync_to_async(lambda: Meal.objects.filter(id=meal_id).first())()

    if not meal:
        await callback.answer("❌ Ovqat topilmadi!", show_alert=True)
        return

    # Ovqatni o‘chirish
    await sync_to_async(meal.delete)()

    await callback.message.edit_text(f"✅ <b>{meal.title}</b> muvaffaqiyatli o‘chirildi!", parse_mode="HTML")
    await callback.answer("✅ O‘chirildi")



@start_router.message(F.text == "➕ Ovqat yaratish")
async def create_meal_start(message: Message, state: FSMContext):
    await message.answer("🍲 Ovqat nomini kiriting:")
    await state.set_state(CreateMeal.waiting_for_title)


@start_router.message(CreateMeal.waiting_for_title)
async def create_meal_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await message.answer("Rasm yuboring (majburiy emas, agar yo‘q bo‘lsa /skip buyrug‘ini yuboring):")
    await state.set_state(CreateMeal.waiting_for_image)


@start_router.message(CreateMeal.waiting_for_image)
async def create_meal_image(message: Message, state: FSMContext):
    data = await state.get_data()
    title = data.get("title")

    if message.text == "/skip":
        meal = await sync_to_async(Meal.objects.create)(title=title)
    else:
        if message.photo:
            photo = message.photo[-1]
            file = await message.bot.get_file(photo.file_id)
            file_path = f"{settings.MEDIA_ROOT}/media/{photo.file_id}.jpg"
            
            await message.bot.download_file(file.file_path, file_path)

            relative_path = f"media/{photo.file_id}.jpg"
            meal = await sync_to_async(Meal.objects.create)(title=title, image=relative_path)
        else:
            meal = await sync_to_async(Meal.objects.create)(title=title)

    await message.answer(f"✅ Ovqat '{meal.title}' yaratildi!", reply_markup=admin_menu)
    await state.clear()

class CreateWeeklyMenu(StatesGroup):
    current_day = State()
    waiting_for_lunch = State()
    waiting_for_dinner = State()


WEEKDAYS = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba"]


@start_router.message(F.text == "📅 Haftalik menu yaratish")
async def start_weekly_menu(message: Message, state: FSMContext):
    menus = await sync_to_async(lambda: list(
        WeeklyMenu.objects.filter(date__week=date.today().isocalendar()[1])
    ))()
    if menus:
        await message.answer("❌ Bu hafta uchun menu allaqachon yaratilgan!")
        return

    await state.update_data(day_index=0, menu_data=[])
    await message.answer(f"📅 {WEEKDAYS[0]} uchun Tushlikni tanlang:", reply_markup=await get_meal_buttons())
    await state.set_state(CreateWeeklyMenu.waiting_for_lunch)


@start_router.message(CreateWeeklyMenu.waiting_for_lunch)
async def select_lunch(message: Message, state: FSMContext):
    selected_meal = message.text.strip()
    meal = await sync_to_async(Meal.objects.get)(title=selected_meal)
    await state.update_data(lunch_id=meal.id)
    data = await state.get_data()
    await message.answer(
        f"🍽️ {WEEKDAYS[data['day_index']]} kechki ovqatni tanlang:",
        reply_markup=await get_meal_buttons()
    )
    await state.set_state(CreateWeeklyMenu.waiting_for_dinner)


@start_router.message(CreateWeeklyMenu.waiting_for_dinner)
async def select_dinner(message: Message, state: FSMContext):
    data = await state.get_data()
    day_index = data['day_index']
    lunch = await sync_to_async(Meal.objects.get)(id=data['lunch_id'])
    dinner = await sync_to_async(Meal.objects.get)(title=message.text.strip())

    menu_data = data['menu_data']
    menu_data.append({
        'day_index': day_index,
        'lunch': lunch.id,
        'dinner': dinner.id
    })

    day_index += 1

    if day_index < len(WEEKDAYS):
        await state.update_data(day_index=day_index, menu_data=menu_data)
        await message.answer(
            f"📅 {WEEKDAYS[day_index]} uchun Tushlikni tanlang:",
            reply_markup=await get_meal_buttons()
        )
        await state.set_state(CreateWeeklyMenu.waiting_for_lunch)
    else:
        # Haftaning dushanbasini topish
        today = date.today()
        weekday = today.weekday()  # Dushanba=0 ... Yakshanba=6
        if weekday == 6:  # Yakshanba
            start_of_week = today + timedelta(days=1)
        else:
            start_of_week = today - timedelta(days=weekday)

        # Har bir kun uchun alohida lunch va dinner yozuvlarini yaratamiz
        for day_menu in menu_data:
            lunch_meal = await sync_to_async(Meal.objects.get)(id=day_menu['lunch'])
            dinner_meal = await sync_to_async(Meal.objects.get)(id=day_menu['dinner'])
            menu_date = start_of_week + timedelta(days=day_menu['day_index'])

            await sync_to_async(WeeklyMenu.objects.create)(
                date=menu_date,
                meal=lunch_meal,
                meal_type="lunch",
                status="pending"
            )
            await sync_to_async(WeeklyMenu.objects.create)(
                date=menu_date,
                meal=dinner_meal,
                meal_type="dinner",
                status="pending"
            )

        await message.answer("✅ Haftalik menu saqlandi!", reply_markup=admin_menu)
        await state.clear()


class EditWeeklyMenu(StatesGroup):
    choosing_day = State()
    editing_lunch = State()
    editing_dinner = State()


def _next_or_same_date_for_weekday(day_index: int) -> date:
    """
    Haftaning kerakli kuniga to‘g‘ri keladigan sanani topadi.
    day_index: 0 = Dushanba ... 6 = Yakshanba
    """
    today = date.today()
    today_index = today.weekday()
    days_ahead = (day_index - today_index) % 7
    return today + timedelta(days=days_ahead)


def get_weekday_buttons():
    buttons = []
    for i in range(0, len(WEEKDAYS), 2):
        row = [KeyboardButton(text=day) for day in WEEKDAYS[i:i + 2]]
        buttons.append(row)

    buttons.append([KeyboardButton(text="🔙 Bosh menu")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


@start_router.message(F.text == "✏️ Haftalik menu tahrirlash")
async def start_edit_menu(message: Message, state: FSMContext):
    menus = await sync_to_async(lambda: list(WeeklyMenu.objects.all()))()
    if not menus:
        await message.answer("❌ Hozircha menu mavjud emas!")
        return

    await message.answer("📅 Qaysi kunni tahrirlashni xohlaysiz?", reply_markup=get_weekday_buttons())
    await state.set_state(EditWeeklyMenu.choosing_day)


@start_router.message(EditWeeklyMenu.choosing_day)
async def choose_day(message: Message, state: FSMContext):
    if message.text == "🔙 Bosh menu":
        await message.answer("🔙 Asosiy menyuga qaytdingiz", reply_markup=admin_menu)
        await state.clear()
        return

    if message.text not in WEEKDAYS:
        await message.answer("❌ Iltimos, faqat berilgan kunlardan birini tanlang!")
        return

    day_index = WEEKDAYS.index(message.text)
    await state.update_data(day_index=day_index)

    await message.answer(f"📅 {WEEKDAYS[day_index]} uchun Lunchni tanlang:", reply_markup=await get_meal_buttons())
    await state.set_state(EditWeeklyMenu.editing_lunch)


@start_router.message(EditWeeklyMenu.editing_lunch)
async def edit_lunch(message: Message, state: FSMContext):
    selected_meal = message.text.strip()
    if selected_meal == "🔙 Bosh menu":
        await message.answer("🔙 Asosiy menyuga qaytdingiz", reply_markup=admin_menu)
        await state.clear()
        return

    try:
        meal = await sync_to_async(Meal.objects.get)(title=selected_meal)
    except Meal.DoesNotExist:
        await message.answer("❌ Bunday taom mavjud emas, qayta tanlang!")
        return

    data = await state.get_data()
    day_index = data["day_index"]
    date_str = _next_or_same_date_for_weekday(day_index)

    weekly_menu = await sync_to_async(
        lambda: WeeklyMenu.objects.filter(date=date_str, meal_type="lunch").last()
    )()
    if weekly_menu:
        weekly_menu.meal = meal
        await sync_to_async(weekly_menu.save)()

    await message.answer(f"🍽️ {WEEKDAYS[day_index]} Lunch yangilandi!")
    await message.answer(f"🍽️ {WEEKDAYS[day_index]} Kechki ovqatni tanlang:", reply_markup=await get_meal_buttons())
    await state.set_state(EditWeeklyMenu.editing_dinner)


@start_router.message(EditWeeklyMenu.editing_dinner)
async def edit_dinner(message: Message, state: FSMContext):
    selected_meal = message.text.strip()
    if selected_meal == "🔙 Bosh menu":
        await message.answer("🔙 Asosiy menyuga qaytdingiz", reply_markup=admin_menu)
        await state.clear()
        return

    try:
        meal = await sync_to_async(Meal.objects.get)(title=selected_meal)
    except Meal.DoesNotExist:
        await message.answer("❌ Bunday taom mavjud emas, qayta tanlang!")
        return

    data = await state.get_data()
    day_index = data["day_index"]
    date_str = _next_or_same_date_for_weekday(day_index)

    weekly_menu = await sync_to_async(
        lambda: WeeklyMenu.objects.filter(date=date_str, meal_type="dinner").last()
    )()
    if weekly_menu:
        weekly_menu.meal = meal
        await sync_to_async(weekly_menu.save)()

    await message.answer(f"✅ {WEEKDAYS[day_index]} kuni uchun menu yangilandi!", reply_markup=admin_menu)
    await state.clear()
