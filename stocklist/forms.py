from django import forms
from django.forms import ModelForm

from stocklist.models import Store, StockPeriod, Stocktake, List

class StoreNameForm(ModelForm):
    class Meta:
        model=Store
        exclude=['user']

class StockPeriodForm(ModelForm):
    class Meta:
        model=StockPeriod
        # exclude=['store']
        fields=['frequency']

class StocktakeForm(ModelForm):
    class Meta:
        model=Stocktake
        exclude=['stock_period']

class ListForm(ModelForm):
    class Meta:
        model=List
        exclude=['store', 'type', 'date_added']