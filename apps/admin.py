from django.contrib import admin
from .models import User, Meal, MealResponse


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "user_id", "created_at")
    search_fields = ("full_name", "user_id")
    ordering = ("-created_at",)


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "meal_type", "date", "yes_count", "no_count")
    list_filter = ("meal_type", "date")
    search_fields = ("title", "description")
    ordering = ("-date",)

    readonly_fields = ("yes_count", "no_count")  # faqat o‘qish mumkin


@admin.register(MealResponse)
class MealResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "meal", "response", "responded_at")
    list_filter = ("response", "responded_at")
    search_fields = ("user__full_name", "meal__title")
    ordering = ("-responded_at",)
