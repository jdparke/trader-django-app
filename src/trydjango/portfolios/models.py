from django.db import models

# Create your models here.

class Portfolio(models.Model):
    UserID = models.IntegerField()
    Ticker = models.TextField()
    Percentage = models.FloatField()

