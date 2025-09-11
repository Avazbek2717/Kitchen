from django.contrib import admin
from .models import User, Meal, MealResponse, WeeklyMenu


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "user_id", "created_at")
    search_fields = ("full_name", "user_id")
    ordering = ("-created_at",)


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    ordering = ("-created_at",)



@admin.register(MealResponse)
class MealResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "get_meal_type", "get_meal_title", "response", "responded_at")
    list_filter = ("response", "responded_at", "menu__meal_type", "menu__status")
    search_fields = ("user__full_name", "menu__meal__title")
    ordering = ("-responded_at",)

    def get_meal_type(self, obj):
        return obj.menu.get_meal_type_display()
    get_meal_type.short_description = "Ovqat turi"

    def get_meal_title(self, obj):
        return obj.menu.meal.title if obj.menu and obj.menu.meal else "Noma’lum"
    get_meal_title.short_description = "Ovqat nomi"

@admin.register(WeeklyMenu)
class WeeklyMenuAdmin(admin.ModelAdmin):
    list_display = ('id', 'date' , "status", "meal_type")