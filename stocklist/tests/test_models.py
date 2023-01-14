import json
import datetime
import decimal
from django.test import Client, TestCase
from django.core.exceptions import ValidationError


from stocklist.models import User, Store, Session, List, ListItem, Item


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

        # create Store
        cls.store_name = "Test Store"
        cls.store = Store.objects.create(owner=cls.user1, name=cls.store_name)

        return super().setUpTestData()

    def test_create_store(self):
        stores = Store.objects.all()
        self.assertEqual(stores.count(), 1)
        self.assertEqual(stores[0].name, self.store_name)

    def test_store_string(self):
        self.assertEqual(self.store_name, self.store.__str__())

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
        list = List.objects.create(
            session=self.session, 
            owner=self.user1, 
            name=self.list_name, 
            list_type=List.ADDITION
        )
        additions = List.additions.all()
        self.assertEqual(additions.count(), 1)
        self.assertEqual(additions[0].list_type, List.ADDITION)

        subtractions = List.subtractions.all()
        self.assertEqual(subtractions.count(), 0)

        counts = List.counts.all()
        self.assertEqual(counts.count(), 0)

    def test_create_count_list(self):
        list_name = 'Final Count'
        list = List.objects.create(
            session=self.session, 
            owner=self.user1, 
            name=list_name, 
            list_type=List.COUNT
        )
        additions = List.additions.all()
        self.assertEqual(additions.count(), 0)

        subtractions = List.subtractions.all()
        self.assertEqual(subtractions.count(), 0)

        counts = List.counts.all()
        self.assertEqual(counts.count(), 1)
        self.assertEqual(counts[0].list_type, List.COUNT)

    def test_create_subtraction_list(self):
        list_name = 'Sales'
        list = List.objects.create(
            session=self.session, 
            owner=self.user1, 
            name=list_name, 
            list_type=List.SUBTRACTION
        )
        additions = List.additions.all()
        self.assertEqual(additions.count(), 0)

        subtractions = List.subtractions.all()
        self.assertEqual(subtractions.count(), 1)
        self.assertEqual(subtractions[0].list_type, List.SUBTRACTION)

        counts = List.counts.all()
        self.assertEqual(counts.count(), 0)


class ItemTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:

        # Create User, Store, Item
        cls.user1 = User.objects.create_user('Mike')
        cls.store_name = "Test Store"
        cls.store1 = Store.objects.create(owner=cls.user1, name=cls.store_name)
        cls.item_name = "Bacardi Superior 70CL BTL"
        cls.item = Item.objects.create(store=cls.store1, name=cls.item_name)

        return super().setUpTestData()

    def test_create_item(self):
        items = Item.objects.all()
        self.assertEqual(items[0].name, self.item_name)
        self.assertEqual(items[0].store, self.store1)


class AnnotatedItemManagerTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:

        # Create User, Store, Item, Session
        cls.user1 = User.objects.create_user('Mike')
        cls.store_name = "Test Store"
        cls.store1 = Store.objects.create(owner=cls.user1, name=cls.store_name)
        cls.item_name = "Bacardi Superior 70CL BTL"
        cls.item = Item.objects.create(store=cls.store1, name=cls.item_name)
        cls.session_name = "Wednesday"
        start_date = datetime.date(year=2023, month=1, day=14)
        end_date = datetime.date(year=2023, month=1, day=15)
        cls.session = Session.objects.create(   store=cls.store1, 
                                                name=cls.session_name, 
                                                start_date=start_date, 
                                                end_date=end_date )
        
        # List1, ListItem1
        cls.list_name1 = 'Starting Stock'
        cls.list1 = List.objects.create(
            session=cls.session, 
            owner=cls.user1, 
            name=cls.list_name1, 
            list_type=List.ADDITION
        )
        list_item_amount = '12.7'
        list_item1 = ListItem.objects.create(list=cls.list1, item=cls.item, amount=list_item_amount)

        # List2, ListItem2
        cls.list_name2 = 'Delivery'
        cls.list2 = List.objects.create(
            session=cls.session, 
            owner=cls.user1, 
            name=cls.list_name2, 
            list_type=List.ADDITION
        )
        list_item_amount = '10'
        list_item1 = ListItem.objects.create(list=cls.list2, item=cls.item, amount=list_item_amount)

        return super().setUpTestData()

    def test_annotated_item_manager_additions(self):
        items = Item.objects.annotated_items_for_session(self.session).all()
        self.assertEqual(items[0].total_added, decimal.Decimal('22.7'))
        self.assertEqual(items[0].total_subtracted, decimal.Decimal('0'))
        self.assertEqual(items[0].total_counted, decimal.Decimal('0'))
        # None returned when none counted


class ListItemTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:


        # Create User, Store, Session, List, Item
        cls.user1 = User.objects.create_user('Mike')
        cls.store_name = "Test Store"
        cls.store1 = Store.objects.create(owner=cls.user1, name=cls.store_name)
        cls.session_name = "Wednesday"
        start_date = datetime.date(year=2023, month=1, day=14)
        end_date = datetime.date(year=2023, month=1, day=15)
        cls.session = Session.objects.create(   store=cls.store1, 
                                                name=cls.session_name, 
                                                start_date=start_date, 
                                                end_date=end_date )
        cls.list_name = 'Starting Stock'
        cls.list = List.objects.create(
            session=cls.session, 
            owner=cls.user1, 
            name=cls.list_name, 
            list_type=List.ADDITION
        )
        cls.item_name = "Bacardi Superior 70CL BTL"
        cls.item = Item.objects.create(store=cls.store1, name=cls.item_name)

        return super().setUpTestData()

    def test_create_list_item(self):
        list_item_amount = '12.7'
        list_item = ListItem.objects.create(list=self.list, item=self.item, amount=list_item_amount)

        list_items = ListItem.objects.all()
        self.assertEqual(list_items[0].list, self.list)
        self.assertEqual(list_items[0].item, self.item)
        self.assertEqual(list_items[0].amount, decimal.Decimal(list_item_amount))


        # test item.name is unique