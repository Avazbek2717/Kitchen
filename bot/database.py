

import os
import django
from asgiref.sync import sync_to_async
from datetime import datetime
from apps.models import *  


@sync_to_async
def get_user_by_id(user_id: str):
    return User.objects.filter(user_id=user_id).first()


@sync_to_async
def create_or_update_user(user_id: str, full_name: str):
    created = User.objects.create(
        user_id=user_id,
        full_name = full_name
    )
@sync_to_async
def get_meal(date):
    return list(Meal.objects.filter(date=date, status__in=["pending", "active", "ended"]))

@sync_to_async
def get_today_menus(date):
    return list(WeeklyMenu.objects.filter(date=date, status__in=["pending", "active", "ended"]).select_related("meal"))


@sync_to_async
def get_user_all():
    return list(User.objects.all())

# @sync_to_async
# def status_change(meal, new_status):
#     meal.status = new_status
#     meal.save()

@sync_to_async
def create_meal_response(user, meal, response_value):
    MealResponse.objects.create(
        user=user,
        menu=meal,
        response=response_value,
    )

@sync_to_async
def get_meal_responses_count(meal_id):
    meal = WeeklyMenu.objects.filter(id=meal_id).first()
    yes_count = MealResponse.objects.filter(menu=meal, response="yes").count()
    no_count = MealResponse.objects.filter(menu=meal, response="no").count()
    return yes_count, no_count

@sync_to_async
def get_meal_image(meal_id):
    try:
        meal = Meal.objects.get(id=meal_id)
        if meal.image and hasattr(meal.image, "path"):  # rasm mavjudligini tekshirish
            return meal.image.path  # faylning absolute yo‘li
        return None
    except Meal.DoesNotExist:
        return None
    
@sync_to_async
def get_weekly_menu(date):
    return WeeklyMenu.objects.filter(
            date=date,
        ).first()


def update_menu_status(menu_id, meal_type, status):
    """
    menu_id: WeeklyMenu ID
    meal_type: "lunch" yoki "dinner"
    status: "pending", "active", "ended"
    """
    try:
        menu = WeeklyMenu.objects.get(id=menu_id)

        if meal_type == "lunch":
            menu.lunch_status = status
        elif meal_type == "dinner":
            menu.dinner_status = status
        else:
            return "Noto‘g‘ri meal_type"

        menu.save()
        return f"{meal_type} status yangilandi → {status}"

    except WeeklyMenu.DoesNotExist:
        return "Menu topilmadi"