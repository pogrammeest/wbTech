from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets
    fieldsets[1][1]['fields'] += ('bio', 'subs', 'slug')


admin.site.register(Account, CustomUserAdmin)


admin.site.register(Post)
admin.site.register(Like)