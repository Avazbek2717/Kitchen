

import os
import django
from asgiref.sync import sync_to_async

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
def get_user_all():
    return list(User.objects.all())

@sync_to_async
def status_change(meal, new_status):
    meal.status = new_status
    meal.save()

@sync_to_async
def create_meal_response(user, meal, response_value):
    MealResponse.objects.create(
        user=user,
        meal=meal,
        response=response_value,
    )

@sync_to_async
def get_meal_responses_count(meal_id):
    meal = Meal.objects.filter(id=meal_id).first()
    yes_count = MealResponse.objects.filter(meal=meal, response="yes").count()
    no_count = MealResponse.objects.filter(meal=meal, response="no").count()
    return yes_count, no_count

@sync_to_async
def get_meal_image(meal_id):
    try:
        meal = Meal.objects.get(id=meal_id)
        return meal.image.path  # faylning absolute yo‘li
        # return meal.image.url  # agar URL kerak bo‘lsa
    except Meal.DoesNotExist:
        return None