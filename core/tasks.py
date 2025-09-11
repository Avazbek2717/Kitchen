

from celery import shared_task
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from datetime import datetime
from datetime import datetime ,time
import logging
from celery import shared_task
from bot.database import *


admin_id = 5167032738


@shared_task
def check_meals():
    import asyncio
    from aiogram import Bot

    async def main():
        bot = Bot(token="6952901446:AAHrX_x7B4O6IOtUl4_SLvpUDKi43dgrzrA")
        result = await process(bot)
        await bot.session.close()
        return result

    return asyncio.run(main())


async def process(bot):
    current_time = datetime.now().time()
    today = datetime.now().date()

    # 🥘 Hozirgi kun uchun menyularni olamiz
    menus = await get_today_menus(today)

    for menu in menus:
        # 🍽 Ovqat turiga qarab vaqt belgilaymiz
        if menu.meal_type == "lunch":
            start_time = time(20, 29)
            end_time = time(20, 31)
        # elif menu.meal_type == "dinner":
        #     start_time = time(18, 0)
        #     end_time = time(20, 0)
        else:
            continue

        # ✅ Agar hali boshlanmagan bo‘lsa
        if start_time <= current_time < end_time and menu.status == "pending":
            await status_change(menu, "active")

            buttons = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Yeyman", callback_data=f"meal_yes_{menu.id}")],
                [InlineKeyboardButton(text="❌ Yemayman", callback_data=f"meal_no_{menu.id}")],
            ])
            meal_title = await sync_to_async(lambda: menu.meal.title if menu.meal else "Noma’lum")()
            text = (
                f"📌 {meal_title}\n\n"
                f"🕒 So'rov {start_time.strftime('%H:%M')} dan "
                f"{end_time.strftime('%H:%M')} gacha faol bo'ladi."
            )

            users = await get_user_all()
            for user in users:
                try:
                    if menu.meal and menu.meal.image:
                        photo = FSInputFile(menu.meal.image.path) 
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
        elif current_time >= end_time and menu.status == "active":
            await status_change(menu, "ended")
            meal_title = await sync_to_async(lambda: menu.meal.title if menu.meal else "Noma’lum")()

            # ✅ Barcha javoblarni olish
            responses = await sync_to_async(
                lambda: list(MealResponse.objects.filter(menu=menu).select_related("user"))
            )()

            yes_users = [r.user.full_name for r in responses if r.response == "yes"]
            no_users = [r.user.full_name for r in responses if r.response == "no"]

            yes_count = len(yes_users)
            no_count = len(no_users)

            # 📋 Statistikaga ro‘yxatlarni qo‘shish
            result_text = (
                f"🍽 {meal_title} yakunlandi!\n\n"
                f"✅ Yeyman: {yes_count} ta\n"
                f"❌ Yemayman: {no_count} ta\n"
                f"📊 Jami: {yes_count + no_count} ta javob\n\n"
                f"👥 Yeymanlar:\n" +
                ("\n".join(f"- {name}" for name in yes_users) if yes_users else "—") + "\n\n"
                f"🚫 Yemaymanlar:\n" +
                ("\n".join(f"- {name}" for name in no_users) if no_users else "—")
            )

            try:
                await bot.send_message(chat_id=int(admin_id), text=result_text)
            except Exception as e:
                logging.error(f"Failed to send admin message: {e}")

    return f"{len(menus)} menu tekshirildi"



@sync_to_async
def status_change(menu: WeeklyMenu, new_status: str):
    """
    WeeklyMenu statusini yangilash
    """
    if new_status not in dict(WeeklyMenu.STATUS_CHOICES):
        raise ValueError(f"Noto‘g‘ri status: {new_status}")

    menu.status = new_status
    menu.save(update_fields=["status"])
    return menu