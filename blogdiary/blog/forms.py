from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Post, PostComments

User = get_user_model()


class PostForm(forms.ModelForm):
    pub_date = forms.DateTimeField(
        # required=False, # для текущего времени по умолчанию если не указано
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),  # , format="%Y-%m-%dT%H:%M"
    )

    class Meta:
        model = Post
        exclude = ("author", "is_published")

    # def clean_pub_date(self):
    #   dt = self.cleaned_data.get("pub_date")
    #   return timezone.now().replace(microsecond=0) if dt is None else dt


class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class CommentForm(forms.ModelForm):
    class Meta:
        model = PostComments
        fields = ("text",)
