from django.db import models

# Create your models here.
# TODO extend allauth user model
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # class tutorial: https://docs.djangoproject.com/en/5.0/topics/auth/customizing/#auth-custom-user

    # a string describing which field will be used as the unique identifier
    # does not need to be modified until we allow anonymous users
    # USERNAME_FIELD = 'email'

    # all fields that will be prompted when creating a user
    #date_of_birth = models.DateField(blank=True, null=True)
    #REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def __str__(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.username