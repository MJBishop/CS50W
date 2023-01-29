from django import forms
from django.forms import ModelForm

from stocklist.models import Store, StockPeriod, Stocktake, MAX_STORE_NAME_LENGTH

class StoreNameModelForm(ModelForm):
    class Meta:
        model=Store
        exclude=['user']

class StockPeriodModelForm(ModelForm):
    class Meta:
        model=StockPeriod
        exclude=['store']

class StocktakeModelForm(ModelForm):
    class Meta:
        model=Stocktake
        exclude=['stock_period']