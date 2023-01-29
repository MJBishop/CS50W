from django import forms
from django.forms import ModelForm

from stocklist.models import Store, StockPeriod, Stocktake, List

class StoreNameForm(ModelForm):
    class Meta:
        model=Store
        fields=['name']

class StockPeriodForm(ModelForm):
    class Meta:
        model=StockPeriod
        fields=['frequency']

class StocktakeForm(ModelForm):
    class Meta:
        model=Stocktake
        fields=['end_date']

class ListForm(ModelForm):
    class Meta:
        model=List
        fields=['name']