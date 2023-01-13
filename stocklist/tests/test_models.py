import json
import datetime
from django.test import Client, TestCase
from django.core.exceptions import ValidationError


from stocklist.models import User, Store, Session


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

        # create Users
        cls.user1 = User.objects.create_user('Mike')
        # cls.user2 = User.objects.create_user('James')

        cls.store_name = "Test Store"

        return super().setUpTestData()

    def test_create_store(self):
        store = Store.objects.create(owner=self.user1, name=self.store_name)

        stores = Store.objects.all()
        self.assertEqual(stores.count(), 1)
        self.assertEqual(stores[0].name, self.store_name)

    def test_store_string(self):
        store = Store.objects.create(owner=self.user1, name=self.store_name)

        self.assertEqual(self.store_name, store.__str__())

    # def test_store_queryset_only_returns_stores_from_ownwer(self):
    #     # create stores
    #     store1 = Store.objects.create(owner=self.user1, name=self.store_name)
    #     store2 = Store.objects.create(owner=self.user2, name=self.store_name)

    #     stores = Store.objects.all()
    #     self.assertEqual(stores.count(), 1)


class SessionTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:

        cls.store_name = "Test Store"
        cls.session_name = "Wednesday"

        # Create User, Store
        cls.user1 = User.objects.create_user('Mike')
        cls.store1 = Store.objects.create(owner=cls.user1, name=cls.store_name)

        return super().setUpTestData()


    def test_create_session(self):
        session = Session.objects.create(   store=self.store1, 
                                            name=self.session_name, 
                                            start_date=datetime.date.today(), 
                                            end_date=datetime.date.today() )
        sessions = Session.objects.all()
        self.assertEqual(sessions.count(), 1)
        self.assertEqual(sessions[0].name, self.session_name)

    def test_create_session_raises_validation_error_for_end_date_before_start_date(self):
        with self.assertRaises(ValidationError):
            Session.objects.create( store=self.store1,
                                    name=self.session_name, 
                                    start_date=datetime.date(year=2023, month=1, day=14), 
                                    end_date=datetime.date(year=2023, month=1, day=13) )