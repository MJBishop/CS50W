import json
import datetime
from django.test import Client, TestCase
from django.core.exceptions import ValidationError


from stocklist.models import User, Store, Session, List


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
        self.assertEqual(sessions[0].start_date, datetime.date.today())
        self.assertEqual(sessions[0].end_date, datetime.date.today())

    def test_create_session_raises_validation_error_for_end_date_before_start_date(self):
        with self.assertRaises(ValidationError):
            Session.objects.create( store=self.store1,
                                    name=self.session_name, 
                                    start_date=datetime.date(year=2023, month=1, day=14), 
                                    end_date=datetime.date(year=2023, month=1, day=13) )

    def test_session_string_start_date_equals_end_date(self):
        session = Session.objects.create(   store=self.store1, 
                                            name=self.session_name, 
                                            start_date=datetime.date.today(), 
                                            end_date=datetime.date.today() )

        expected_string = "{} Session: {}".format(self.session_name, datetime.date.today())
        self.assertEqual(expected_string, session.__str__())

    def test_session_string_start_date_before_end_date(self):
        start_date = datetime.date(year=2023, month=1, day=14)
        end_date = datetime.date(year=2023, month=1, day=15)
        session = Session.objects.create(   store=self.store1, 
                                            name=self.session_name, 
                                            start_date=start_date, 
                                            end_date=end_date )

        expected_string = "{} Session - starts: {}, ends: {}".format(self.session_name, start_date, end_date)
        self.assertEqual(expected_string, session.__str__())


class ListTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:

        cls.store_name = "Test Store"
        cls.session_name = "Wednesday"

        # Create User, Store
        cls.user1 = User.objects.create_user('Mike')
        store1 = Store.objects.create(owner=cls.user1, name=cls.store_name)

        start_date = datetime.date(year=2023, month=1, day=14)
        end_date = datetime.date(year=2023, month=1, day=15)
        cls.session = Session.objects.create(   store=store1, 
                                                name=cls.session_name, 
                                                start_date=start_date, 
                                                end_date=end_date )

        cls.list_name = 'Starting Stock'

        return super().setUpTestData()

    def test_create_list(self):
        self.lists = List.objects.create(
            session=self.session, 
            owner=self.user1, 
            name=self.list_name, 
        )
        lists = List.objects.all()
        self.assertEqual(lists.count(), 1)
        self.assertEqual(lists[0].name, self.list_name)
        self.assertEqual(lists[0].list_type, List.ADDITION)

    def test_create_addition_list(self):
        lists = List.objects.create(
            session=self.session, 
            owner=self.user1, 
            name=self.list_name, 
            list_type=List.ADDITION
        )
        additions = List.additions.all()
        self.assertEqual(additions.count(), 1)
        self.assertEqual(additions[0].list_type, List.ADDITION)

        counts = List.counts.all()
        self.assertEqual(counts.count(), 0)

    def test_create_count_list(self):
        list_name = 'Final Count'
        lists = List.objects.create(
            session=self.session, 
            owner=self.user1, 
            name=list_name, 
            list_type=List.COUNT
        )
        additions = List.additions.all()
        self.assertEqual(additions.count(), 0)

        counts = List.counts.all()
        self.assertEqual(counts.count(), 1)
        self.assertEqual(counts[0].list_type, List.COUNT)
