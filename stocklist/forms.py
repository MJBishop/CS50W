from django import forms
from django.forms import ModelForm
from django.utils import timezone
from datetime import date

from stocklist.models import Store, List#, StockPeriod, Stocktake

class StoreNameForm(ModelForm):
    class Meta:
        model=Store
        fields=['name', 'user']
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control mx-auto my-1'},),
            'user':forms.HiddenInput,
        }
        labels = {
            'name':'Store Name'
        }

# class StockPeriodForm(ModelForm):
#     class Meta:
#         model=StockPeriod
#         fields=['frequency']
#         widgets = {
#             'frequency':forms.Select(attrs={'class':'form-control mx-auto my-1'},),
#         }
#         labels = {
#             'frequency':'Stocktake Frequency'
#         }

# class StocktakeForm(ModelForm):
#     class Meta:
#         model=Stocktake
#         fields=['end_date']
#         widgets = {
#             'end_date': forms.SelectDateWidget(attrs={'class':'form-control mx-auto my-1'},),
#         }
#         labels = {
#             'end_date':'Stocktake Date'
#         }

#     def clean(self):
#         '''End date cannot be in the past.'''
#         cleaned_data = super(StocktakeForm, self).clean()
#         end_date = cleaned_data.get('end_date')
#         if end_date and end_date < date.today():
#             raise forms.ValidationError(
#                 {'end_date':'End date cannot be in the past!'}
#             )

# class StockListForm(ModelForm):
#     class Meta:
#         model=List
#         fields=['name']

# # class StockListInviteForm(StockListForm):
# #     # TODO Add email field for invites
# #     pass

# # class ListForm(ModelForm):
# #     class Meta:
# #         model=List
# #         fields=['name', 'type', 'date_added']
# # inheritance for forms!
