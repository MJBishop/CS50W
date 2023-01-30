from django import forms
from django.forms import ModelForm
from django.utils import timezone
from datetime import date

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

    def clean(self):
        '''End date cannot be in the past.'''
        cleaned_data = super(StocktakeForm, self).clean()
        end_date = cleaned_data.get('end_date')
        if end_date and end_date < date.today():
            raise forms.ValidationError(
                {'end_date':'End date cannot be in the past!'}
            )

class StockListForm(ModelForm):
    class Meta:
        model=List
        fields=['name']
        # TODO Add email field for invites

# class ListForm(ModelForm):
#     class Meta:
#         model=List
#         fields=['name', 'type', 'date_added']

