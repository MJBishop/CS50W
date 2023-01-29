import json
from django.test import Client, TestCase
from django.core.exceptions import ValidationError

from stocklist.models import User
from stocklist.forms import StoreNameModelForm

class StoreNameFormTestCase(TestCase):

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


    # def test_blank_store_name_form_data(self):
    #     form = StoreNameForm({
    #         'name': "",
    #     })
    #     self.assertFalse(form.is_valid())
    #     self.assertEqual(form.errors, {
    #         'name': ['This field is required.'],
    #     })