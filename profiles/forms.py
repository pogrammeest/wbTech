from django import forms
from image_cropping import ImageCropWidget

from .models import *


class ProfileModelForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar', 'cropping', 'first_name', 'last_name', 'bio','slug')
        widgets = {
            'avatar': ImageCropWidget,
        }
