import json
from django.test import Client, TestCase
from django.core.exceptions import ValidationError

from stocklist.models import User, Store


class UserTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:

        # create User
        cls.user1 = User.objects.create_user('Mike')

        return super().setUpTestData()
    
    def test_user(self):
        users = User.objects.all()
        self.assertEqual(users.count(), 1)
        self.assertEqual(users[0].username, 'Mike')


class StoreTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:

        # create User
        cls.user1 = User.objects.create_user('Mike')
        cls.store_name = "Test Store"

        return super().setUpTestData()

    def test_create_store(self):
        store = Store.objects.create(owner=self.user1, name=self.store_name)

        stores = Store.objects.all()
        self.assertEqual(stores.count(), 1)
        self.assertEqual(stores[0].name, self.store_name)