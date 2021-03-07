import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.UUIDField(auto_created=True,
                          primary_key=True,
                          serialize=False,
                          verbose_name='ID',
                          default=uuid.uuid4,
                          editable=False)
    username = None
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=30)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
