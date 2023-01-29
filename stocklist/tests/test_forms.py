from datetime import date
from django.test import Client, TestCase
from django.core.exceptions import ValidationError

from stocklist.models import StockPeriod
from stocklist.forms import StoreNameModelForm, StockPeriodModelForm, StocktakeModelForm

class StoreNameFormTestCase(TestCase):

    def test_empty_model_form(self):
        form = StoreNameModelForm()
        self.assertIn("name", form.fields)

    def test_valid_store_name_model_form_data(self):
        test_store_name = 'Test Store name'
        form = StoreNameModelForm({
            'name':test_store_name,
        })
        self.assertTrue(form.is_valid())
        store_name = form.cleaned_data["name"]
        self.assertEqual(store_name, test_store_name)

    def test_blank_store_name_model_form_data(self):
        form = StoreNameModelForm({
            'name': "",
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'name': ['This field is required.'],
        })

    def test_invalid_store_name_length_model_form_data(self):
        test_store_name = 'A'*(20 + 1)
        form = StoreNameModelForm({
            'name':test_store_name,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'name': ['Ensure this value has at most 20 characters (it has 21).'],
        })

class StockPeriodModelFormTestCase(TestCase):

    def test_empty_model_form(self):
        form = StockPeriodModelForm()
        self.assertIn("frequency", form.fields)

    def test_valid_stock_period_frequency_model_form_data(self):
        form = StockPeriodModelForm({
            'frequency':StockPeriod.MONTHLY,
        })
        self.assertTrue(form.is_valid())
        frequency = form.cleaned_data["frequency"]
        self.assertEqual(frequency, StockPeriod.MONTHLY)

    def test_blank_stock_period_frequency_model_form_data(self):
        form = StockPeriodModelForm({
            'frequency':''
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'frequency': ['This field is required.'],
        })

    def test_invalid_stock_period_frequency_model_form_data(self):
        form = StockPeriodModelForm({
            'frequency':'ZZ',
        })
        self.assertFalse(form.is_valid())
        # self.assertEqual(form.errors, {
        #     'name': ['Ensure this value has at most 20 characters (it has 21).'],
        # })

class StocktakeModelFormTestCase(TestCase):

    def test_empty_model_form(self):
        form = StocktakeModelForm()
        self.assertIn("end_date", form.fields)
        self.assertFalse(form.is_valid())

    def test_valid_model_form_data(self):
        test_end_date = date(year=2023, month=1, day=31)
        form = StocktakeModelForm({
            'end_date':test_end_date,
        })
        self.assertTrue(form.is_valid())
        cleaned_end_date = form.cleaned_data["end_date"]
        self.assertEqual(cleaned_end_date, test_end_date)

    def test_blank_model_form_data(self):
        form = StocktakeModelForm({
            'end_date':''
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'end_date': ['This field is required.'],
        })

    def test_invalid_model_form_data(self):
        pass
    # Dates!! TODO 