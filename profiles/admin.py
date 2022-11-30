from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django import forms
from image_cropping import ImageCroppingMixin
from django.contrib import messages

from .models import Profile

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin





class CustomUserAdmin(ImageCroppingMixin, UserAdmin):
    fieldsets = UserAdmin.fieldsets
    fieldsets[1][1]['fields'] += ('role', 'boss', 'avatar', 'cropping', 'bio', 'subs', 'slug')

    def get_form(self, request, obj, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['boss'] = forms.ModelChoiceField(queryset=Profile.objects.exclude(id=obj.id).filter(role="HOD"),
                                                              required=False, label="Начальник")
        return form


admin.site.register(Profile, CustomUserAdmin)
