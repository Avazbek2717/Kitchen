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
    MEAL_TYPE_CHOICES = (
        ("lunch", "Abed"),
        ("dinner", "Kechki ovqat"),
    )

    STATUS_CHOICES = (
        ("pending", "Kutilmoqda"),
        ("active", "Faol"),
        ("ended", "Tugagan"),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="media/", blank=True, null=True, verbose_name="Rasm")  
    date = models.DateField()
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)

    start_time = models.TimeField(verbose_name="So‘rovnoma boshlanish vaqti")
    end_time = models.TimeField(verbose_name="So‘rovnoma tugash vaqti")

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"{self.get_meal_type_display()} - {self.title} ({self.date})"

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
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name="responses")
    response = models.CharField(max_length=10, choices=RESPONSE_CHOICES)
    responded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "meal") 

    def __str__(self):
        return f"{self.user.full_name} - {self.meal.title} - {self.response}"
    




