from django.urls import path, include
from api import views

from rest_framework.routers import DefaultRouter

app_name = 'api'

router = DefaultRouter()
router.register(r'profile', views.ProfileViewSet)
router.register(r'post', views.PostViewSet, basename='post')
router.register(r'feed', views.FeedViewSet, basename='feed')
urlpatterns = [
    path('', include(router.urls)),
]
