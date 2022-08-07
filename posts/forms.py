from django import forms
from .models import *
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget


class PostModelForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content')
        widgets = {

            'content': SummernoteWidget(),
        }


class CommentModelForm(forms.ModelForm):
    body = forms.CharField(label='Comment:', widget=forms.TextInput(attrs={'placeholder': 'Add a comment '}))

    class Meta:
        model = Comment
        fields = ('body',)
