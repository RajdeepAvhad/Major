from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

# class User(AbstractUser):
#     def __str__(self):
#         return f"{self.id}: {self.first_name} {self.last_name}"

class Food(models.Model):
    name = models.CharField(max_length=50)
    bf = models.IntegerField()
    lu = models.IntegerField()
    di = models.IntegerField()
    cal = models.IntegerField()
    fat = models.IntegerField()
    pro = models.IntegerField()
    sug = models.IntegerField()
    imagepath = models.CharField(default="", max_length=100)
    
    # New fields for enhanced food metadata
    veg = models.BooleanField(default=False, help_text="Is this food vegetarian?")
    glycemic_index = models.FloatField(null=True, blank=True, help_text="Glycemic Index (0-100)")
    gi_category = models.CharField(max_length=10, null=True, blank=True)
    cuisine = models.CharField(max_length=50, default='International', help_text="Cuisine type (e.g., Indian, Chinese, Italian)")
    
    def __str__(self):
        return self.name
class UserList(models.Model):
    Username = models.CharField(max_length=50)
    Password = models.CharField(max_length=50)
    mail_id1 = models.CharField(max_length=100)
    pass


class SavedDiet(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    session_key = models.CharField(max_length=100, blank=True, default="")
    period = models.CharField(max_length=10, default="daily")
    plan_date = models.DateField(null=True, blank=True, default=timezone.localdate)
    target_calories = models.IntegerField(default=0)
    selected_calories = models.IntegerField(default=0)
    selected_items = models.JSONField(default=list, blank=True)
    bmi = models.FloatField(null=True, blank=True)
    bodyfat = models.FloatField(null=True, blank=True)
    bmiinfo = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', 'period']),
            models.Index(fields=['session_key', 'period']),
        ]

    def __str__(self):
        return f"SavedDiet {self.id} ({self.selected_calories}/{self.target_calories})"


class UserPreference(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    session_key = models.CharField(max_length=100, blank=True, default="")
    age = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    bodyfat = models.FloatField(null=True, blank=True)
    goal = models.CharField(max_length=20, default="healthy")
    activity = models.CharField(max_length=20, default="Heavy")
    gender = models.CharField(max_length=10, default="")
    category = models.CharField(max_length=20, default="none")
    plan_period = models.CharField(max_length=10, default="daily")
    plan_date = models.DateField(null=True, blank=True, default=timezone.localdate)
    reminder_time = models.CharField(max_length=5, blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]


class FavoriteFood(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    session_key = models.CharField(max_length=100, blank=True, default="")
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "session_key", "food")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['user', 'food']),
            models.Index(fields=['session_key', 'food']),
        ]


class WaterLog(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    session_key = models.CharField(max_length=100, blank=True, default="")
    log_date = models.DateField(default=timezone.localdate, db_index=True)
    amount_ml = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "session_key", "log_date")
        ordering = ["-log_date"]
        indexes = [
            models.Index(fields=['user', 'log_date']),
            models.Index(fields=['session_key', 'log_date']),
        ]
