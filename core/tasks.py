

from celery import shared_task
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from datetime import datetime
from datetime import datetime
import logging
from celery import shared_task
from bot.database import *


admin_id = 5167032738


@shared_task
def check_meals():
    import asyncio
    from aiogram import Bot, types

    async def main():
        bot = Bot(token="8395669472:AAHjXTgl_o7MlaxE1dhdoL1RHY8_xNk_lXk")
        result = await process(bot)
        await bot.session.close()
        return result

    return asyncio.run(main())

async def process(bot):
    current_time = datetime.now().time()
    today = datetime.now().date()

    meals = await get_meal(today)

    for meal in meals:
        if meal.start_time and meal.end_time and meal.status == "pending":
            if meal.start_time <= current_time < meal.end_time:
                await status_change(meal, "active")

                buttons = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Yeyman", callback_data=f"meal_yes_{meal.id}")],
                    [InlineKeyboardButton(text="❌ Yemayman", callback_data=f"meal_no_{meal.id}")],
                ])

                text = (
                    f"📌 {meal.title}\n\n"
                    f"🕒 So'rov {meal.start_time.strftime('%H:%M')} dan "
                    f"{meal.end_time.strftime('%H:%M')} gacha faol bo'ladi."
                )
                
                users = await get_user_all()
                for user in users:
                    try:
                        meal_image = await get_meal_image(meal.id)
                        if meal_image and os.path.exists(meal_image):
                            photo = FSInputFile(meal_image)
                            await bot.send_photo(
                                chat_id=int(user.user_id),
                                photo=photo,
                                caption=text,
                                reply_markup=buttons
                            )
                        else:
                            await bot.send_message(
                                chat_id=int(user.user_id),
                                text=text,
                                reply_markup=buttons
                            )
                    except Exception as e:
                        logging.error(f"Failed to send message to user {user.user_id}: {e}")
                        continue

        elif meal.end_time and current_time >= meal.end_time and meal.status == "active":
            await status_change(meal, "ended")

            yes_count, no_count = await get_meal_responses_count(meal.id)

            result_text = (
                f"🍽 {meal.title} yakunlandi!\n\n"
                f"✅ Yeyman: {yes_count} ta\n"
                f"❌ Yemayman: {no_count} ta\n"
                f"📊 Jami: {yes_count + no_count} ta javob"
            )
            
            try:
                await bot.send_message(chat_id=int(admin_id), text=result_text)
            except Exception as e:
                logging.error(f"Failed to send admin message: {e}")

    return f"{len(meals)} meal tekshirildi"