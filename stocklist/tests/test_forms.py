from datetime import date
from django.utils import timezone
from django.test import TestCase

from stocklist.models import User, MAX_STORE_NAME_LENGTH, MAX_LIST_NAME_LENGTH 
from stocklist.forms import StoreNameForm 


class StoreNameFormTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        # create User
        TEST_USER = 'testuser'
        PASSWORD = '12345'
        cls.user = User.objects.create_user(
            username=TEST_USER, email='testuser@test.com', password=PASSWORD
        )

        return super().setUpTestData()

    def test_empty_form(self):
        form = StoreNameForm()
        self.assertIn("name", form.fields)

    def test_blank_form_data(self):
        form = StoreNameForm({
            'name': "",
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'name': ['This field is required.'],
        })

    def test_valid_form_data(self):
        test_store_name = 'Test Store name'
        form = StoreNameForm({
            'name':test_store_name,
        })
        self.assertTrue(form.is_valid())
        store_name = form.cleaned_data["name"]
        self.assertEqual(store_name, test_store_name)

    def test_invalid_form_data(self):
        test_store_name = 'A'*(MAX_STORE_NAME_LENGTH + 1)
        form = StoreNameForm({
            'name':test_store_name,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'name': ['Ensure this value has at most 20 characters (it has 21).'],
        })


