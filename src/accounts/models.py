import uuid
from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # class tutorial: https://docs.djangoproject.com/en/5.0/topics/auth/customizing/#auth-custom-user

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # all fields that will be prompted when creating a user
    #date_of_birth = models.DateField(blank=True, null=True)
    #REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def __str__(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.username