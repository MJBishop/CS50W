from django import forms
from django.forms import ModelForm
from django.utils import timezone
from datetime import date

from stocklist.models import Store, List

class StoreNameForm(ModelForm):
    class Meta:
        model=Store
        fields=['name']
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control mx-auto my-1'},),
        }
        labels = {
            'name':''
        }
