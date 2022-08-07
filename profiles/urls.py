from django.urls import path, include
from .views import *

app_name = 'profiles'

urlpatterns = [

    path('myprofile/', my_profile_view, name='my-profile-view'),
    path('id/<str:slug>/', profile_detail, name='profile-detail'),
    path('id/<str:slug>/subscribe', subscribe_unsubscribe, name='profile-subscribe'),
    path('porfile-all/', profiles_list_view, name='profile-list'),

]
