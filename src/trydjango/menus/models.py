from django.db import models

# Create your models here.

class Menu(models.Model):
    Title = models.TextField()
    Href = models.TextField()
    isActive = models.BooleanField(default=False)
    iOrder = models.IntegerField(blank=True, null=True)