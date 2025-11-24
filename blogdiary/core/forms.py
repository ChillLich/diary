from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

# получить модель пользователя:
User = get_user_model()


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        # поля для пароля в атрибуте fields перечислять не надо, они выводятся в форму
        # автоматически, это от родительского класса
        fields = ("username", "bio")
