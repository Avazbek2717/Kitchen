from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan sana")

    objects = models.Manager()

    class Meta:
        abstract = True


class User(BaseModel):
    user_id = models.CharField(max_length=255, unique=True) 
    full_name = models.CharField(max_length=255)
    

    def __str__(self):
        return self.full_name


class Meal(BaseModel):
    

    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="media/", blank=True, null=True, verbose_name="Rasm")  


    def __str__(self):
        return f"{self.title})"





class WeeklyMenu(BaseModel):
    STATUS_CHOICES = (
        ("pending", "Kutilmoqda"),
        ("active", "Faol"),
        ("ended", "Yakunlangan"),
    )
    MEAL_TYPE = (
        ("lunch", "Abed"),
        ("dinner", "Kechki")
    )

    
    date = models.DateField()  # Har bir kun uchun aniq
    meal = models.ForeignKey(Meal, on_delete=models.SET_NULL, null=True, blank=True, related_name="lunch_menus")
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default="pending"
    )

    def __str__(self):
        return f"Menu"
    
    @property
    def yes_count(self):
        return self.responses.filter(response="yes").count()

    @property
    def no_count(self):
        return self.responses.filter(response="no").count()

    



class MealResponse(BaseModel):
    RESPONSE_CHOICES = (
        ("yes", "Yeyman"),
        ("no", "Yemayman"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meal_responses")
    menu = models.ForeignKey(WeeklyMenu, on_delete=models.CASCADE, related_name="responses")
    response = models.CharField(max_length=10, choices=RESPONSE_CHOICES)
    responded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "menu") 


    def __str__(self):
        meal_title = self.menu.meal.title if self.menu and self.menu.meal else "Noma’lum ovqat"
        return f"{self.user.full_name} - {meal_title} - {self.response}"

