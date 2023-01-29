from django import forms
from django.forms import ModelForm

from stocklist.models import Store, StockPeriod, Stocktake, MAX_STORE_NAME_LENGTH

class StoreNameModelForm(ModelForm):
    class Meta:
        model=Store
        exclude= ['user']


class StoreNameForm(forms.Form):
    pass