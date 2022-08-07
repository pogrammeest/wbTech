from django.urls import path

from .views import SignUpView

app_name = 'reg'

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
]