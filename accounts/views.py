from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from profiles.models import Profile


class SignUpForm(UserCreationForm):
    class Meta:
        model = Profile
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')


class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
