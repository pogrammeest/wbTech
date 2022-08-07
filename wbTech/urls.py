from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from wbTech import settings
from .views import *
from posts.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('', home_view, name='home-view'),
    path('profile/', include('profiles.urls', namespace='profile')),
    path('posts/', include('posts.urls', namespace='posts')),
    path('api/', include('api.urls', namespace='api')),
    path('__debug__/', include('debug_toolbar.urls')),
    path('summernote/', include('django_summernote.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
