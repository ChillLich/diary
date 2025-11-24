from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class MyUser(AbstractUser):
    bio = models.TextField("Биография", blank=True)

    def get_absolute_url(self):

        return reverse("blog:profile", kwargs={"username": self.username})
