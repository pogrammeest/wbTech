from django.contrib import admin
from django.contrib.auth.models import User
from image_cropping import ImageCroppingMixin

from .models import Profile

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(ImageCroppingMixin,UserAdmin):
    fieldsets = UserAdmin.fieldsets
    fieldsets[1][1]['fields'] += ('avatar', 'cropping', 'bio', 'subs', 'slug')


admin.site.register(Profile, CustomUserAdmin)
