from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    role = models.CharField(
        max_length=5,
        choices=(('user', 'User'), ('admin', 'Admin')),
        default='user'
    )

    def __str__(self):
        return self.username

class DataSheet(models.Model):
    SHEET_CHOICES = [
        ('MACD', 'MACD'),
        ('BREAK', 'BREAK'),
        ('MA10', 'MA10'),
        ('MA20', 'MA20'),
        ('MA50', 'MA50'),
    ]

    sheet_name = models.CharField(max_length=50, choices=SHEET_CHOICES)
    symbol = models.CharField(max_length=100)
    volume = models.IntegerField()
    signal = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)  # Set default to the current date and time


    def __str__(self):
        return f"{self.sheet_name} - {self.symbol}"
