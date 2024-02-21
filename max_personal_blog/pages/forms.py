from django import forms
from . import models


class PageForm(forms.ModelForm):    
    class Meta:
        model = models.Page
        fields = ('name', 'category', 'description', 'is_published' )