from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import CustomUserCreationForm


class CreateUserView(CreateView):
    template_name = "registration/registration_form.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("blog:index")
