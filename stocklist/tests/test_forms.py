from datetime import date
from django.utils import timezone
from django.test import Client, TestCase
from django.core.exceptions import ValidationError

from stocklist.models import User, Store, StockPeriod, MAX_STORE_NAME_LENGTH, MAX_LIST_NAME_LENGTH
from stocklist.forms import StoreNameForm, StockPeriodForm, StocktakeForm, StockListForm#, StockListInviteForm


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
        self.assertIn("user", form.fields)

    def test_blank_form_data(self):
        form = StoreNameForm({
            'name': "",
            'user':self.user,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'name': ['This field is required.'],
        })

    def test_valid_form_data(self):
        test_store_name = 'Test Store name'
        form = StoreNameForm({
            'name':test_store_name,
            'user':self.user,
        })
        self.assertTrue(form.is_valid())
        store_name = form.cleaned_data["name"]
        self.assertEqual(store_name, test_store_name)

    def test_invalid_form_data(self):
        test_store_name = 'A'*(MAX_STORE_NAME_LENGTH + 1)
        form = StoreNameForm({
            'name':test_store_name,
            'user':self.user,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'name': ['Ensure this value has at most 20 characters (it has 21).'],
        })

    def test_unique_form_data(self):
        test_store_name = 'Test Store name'
        store = Store.objects.create(name=test_store_name, user=self.user)
        form = StoreNameForm({
            'name':test_store_name,
            'user':self.user,
        })
        self.assertFalse(form.is_valid())


class StockPeriodFormTestCase(TestCase):

    def test_empty_form(self):
        form = StockPeriodForm()
        self.assertIn("frequency", form.fields)

    def test_blank_form_data(self):
        form = StockPeriodForm({
            'frequency':''
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'frequency': ['This field is required.'],
        })

    def test_valid_form_data(self):
        form = StockPeriodForm({
            'frequency':StockPeriod.MONTHLY,
        })
        self.assertTrue(form.is_valid())
        frequency = form.cleaned_data["frequency"]
        self.assertEqual(frequency, StockPeriod.MONTHLY)

    def test_invalid_form_data(self):
        form = StockPeriodForm({
            'frequency':'ZZ',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'frequency': ['Select a valid choice. ZZ is not one of the available choices.'],
        })


class StocktakeFormTestCase(TestCase):

    def test_empty_form(self):
        form = StocktakeForm()
        self.assertIn("end_date", form.fields)
        self.assertFalse(form.is_valid())

    def test_blank_form_data(self):
        form = StocktakeForm({
            'end_date':''
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'end_date': ['This field is required.'],
        })

    def test_valid_form_data(self):
        test_end_date = date.today()
        form = StocktakeForm({
            'end_date':test_end_date,
        })
        self.assertTrue(form.is_valid())
        cleaned_end_date = form.cleaned_data["end_date"]
        self.assertEqual(cleaned_end_date, test_end_date)

    def test_invalid_form_data(self):
        test_end_date = date(year=2022, month=1, day=29)
        form = StocktakeForm({
            'end_date':test_end_date,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'end_date': ['End date cannot be in the past!'],
        })


class StockListFormTestCase(TestCase):

    def test_empty_form(self):
        form = StockListForm()
        self.assertIn("name", form.fields)

    def test_blank_form_data(self):
        form = StockListForm({
            'name':'',
        })
        self.assertFalse(form.is_valid())

    def test_valid_form_data(self):
        test_list_name = 'Test List Name'
        form = StockListForm({
            'name':test_list_name,
        })
        self.assertTrue(form.is_valid())
        cleaned_list_name = form.cleaned_data['name']
        self.assertEqual(cleaned_list_name, test_list_name)

    def test_invalid_form_data(self):
        test_list_name = 'A'*(MAX_LIST_NAME_LENGTH + 1)
        form = StockListForm({
            'name':test_list_name,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'name': ['Ensure this value has at most 20 characters (it has 21).'],
        })

# class StockListInviteFormTestCase(TestCase):

#     def test_empty_form(self):
#         form = StockListInviteForm()

# class ListFormTestCase(TestCase):
#     pass