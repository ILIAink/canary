from django.db import models

# Create your models here.
# TODO extend allauth user model
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    def __str__(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.username