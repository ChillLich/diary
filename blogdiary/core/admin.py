from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()

# регистрацтя модель в админке
admin.site.register(User, UserAdmin)
