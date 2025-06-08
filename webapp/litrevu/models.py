from django.db import models


class CustomUser(models.Model):  # Renommé de User à CustomUser
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
