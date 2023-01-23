from datetime import date
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

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

    def test_default_store_returns_users_first_store(self):
        first_store = Store.objects.create(owner=self.user1, name="Test Store 1")
        other_store = Store.objects.create(owner=self.user1, name="Test Store 2")
        default_store = self.user1.default_store()
        self.assertEqual(first_store, default_store)
    
    def test_default_store_created_if_no_user_stores(self):
        default_store = self.user1.default_store()
        self.assertEqual(default_store.name, 'Stocklist')


class StoreTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        
        # create User
        cls.user1 = User.objects.create_user('Mike')

        # create Store
        cls.store_name = "Test Store"
        cls.store = Store.objects.create(owner=cls.user1, name=cls.store_name)

        return super().setUpTestData()

    def test_create_store_fails_for_no_store_name(self):
        with self.assertRaises(ValidationError):
            store = Store.objects.create(owner=self.user1)
            store.full_clean()

    def test_create_store(self):
        stores = Store.objects.all()
        self.assertEqual(stores.count(), 1)
        self.assertEqual(stores[0].name, self.store_name)
        self.assertEqual(self.store.owner, self.user1)

    def test_unique_store_name_for_owner(self):
        with self.assertRaises(IntegrityError):
            store = Store.objects.create(owner=self.user1, name=self.store_name)
            store.full_clean()

    def test_store_string(self):
        self.assertEqual(self.store_name, self.store.__str__())

    # edit store.name?

    def test_max_store_name_length(self):
        long_store_name = (20 + 1)*'A'
        with self.assertRaises(ValidationError):
            store = Store.objects.create(owner=self.user1, name=long_store_name)
            store.full_clean()

    def test_current_session_returns_stores_last_session(self):
        default_store = self.user1.default_store()
        session1 = Session.objects.create( store=default_store, name='Sesion 1')
        session2 = Session.objects.create( store=default_store, name='Sesion 2', previous_session=session1)
        current_session = default_store.current_session()
        self.assertEqual(session2, current_session)

    def test_current_session_created_if_no_store_sessions(self):
        user2 = User.objects.create_user('James')
        current_session = user2.default_store().current_session()
        self.assertEqual('Session', current_session.name)


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
                                            start_date=date.today(), 
                                            end_date=date.today() )
        sessions = Session.objects.all()
        self.assertEqual(sessions.count(), 1)
        self.assertEqual(sessions[0].name, self.session_name)
        self.assertEqual(sessions[0].start_date, date.today())
        self.assertEqual(sessions[0].end_date, date.today())
        self.assertEqual(sessions[0].store, self.store1)

    def test_create_session_raises_validation_error_for_end_date_before_start_date(self):
        with self.assertRaises(ValidationError):
            Session.objects.create( store=self.store1,
                                    name=self.session_name, 
                                    start_date=date(year=2023, month=1, day=14), 
                                    end_date=date(year=2023, month=1, day=13) )

    def test_session_string_start_date_equals_end_date(self):
        session = Session.objects.create(   store=self.store1, 
                                            name=self.session_name, 
                                            start_date=date.today(), 
                                            end_date=date.today() )

        expected_string = "{} Session: {}".format(self.session_name, date.today())
        self.assertEqual(expected_string, session.__str__())

    def test_session_string_start_date_before_end_date(self):
        start_date = date(year=2023, month=1, day=14)
        end_date = date(year=2023, month=1, day=15)
        session = Session.objects.create(   store=self.store1, 
                                            name=self.session_name, 
                                            start_date=start_date, 
                                            end_date=end_date )

        expected_string = "{} Session - starts: {}, ends: {}".format(self.session_name, start_date, end_date)
        self.assertEqual(expected_string, session.__str__())

    # def test_session_string_no_end_date(self):

    # edit session name, start & end date?

    def test_max_session_name_length(self):
        long_session_name = (10 + 1)*'A'
        with self.assertRaises(ValidationError):
            session = Session.objects.create(   store=self.store1, 
                                                name=long_session_name, 
                                                start_date=date.today(), 
                                                end_date=date.today() )
            session.full_clean()

    def test_create_session_with_previous_session(self):
        start_date = date(year=2023, month=1, day=14)
        end_date = date(year=2023, month=1, day=15)
        session = Session.objects.create(   store=self.store1, 
                                            name=self.session_name, 
                                            start_date=date(year=2023, month=1, day=14), 
                                            end_date=date(year=2023, month=1, day=15))
        session2 = Session.objects.create(  store=self.store1, 
                                            name=self.session_name, 
                                            start_date=date(year=2023, month=1, day=15), 
                                            end_date=date(year=2023, month=1, day=16), 
                                            previous_session=session)
        self.assertEqual(session2.previous_session, session)
        # self.assertEqual(session.next_session, session2) ??fails??    


class ListTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:

        cls.store_name = "Test Store"
        cls.session_name = "Wednesday"

        # Create User, Store
        cls.user1 = User.objects.create_user('Mike')
        store1 = Store.objects.create(owner=cls.user1, name=cls.store_name)

        start_date = date(year=2023, month=1, day=14)
        end_date = date(year=2023, month=1, day=15)
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
        self.assertEqual(lists[0].type, List.ADDITION)

    def test_create_addition_list(self):
        list = List.objects.create(
            session=self.session, 
            owner=self.user1, 
            name=self.list_name, 
            type=List.ADDITION
        )
        additions = List.additions.all()
        self.assertEqual(additions.count(), 1)
        self.assertEqual(additions[0].type, List.ADDITION)

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
            type=List.COUNT
        )
        additions = List.additions.all()
        self.assertEqual(additions.count(), 0)

        subtractions = List.subtractions.all()
        self.assertEqual(subtractions.count(), 0)

        counts = List.counts.all()
        self.assertEqual(counts.count(), 1)
        self.assertEqual(counts[0].type, List.COUNT)

    def test_create_subtraction_list(self):
        list_name = 'Sales'
        list = List.objects.create(
            session=self.session, 
            owner=self.user1, 
            name=list_name, 
            type=List.SUBTRACTION
        )
        additions = List.additions.all()
        self.assertEqual(additions.count(), 0)

        subtractions = List.subtractions.all()
        self.assertEqual(subtractions.count(), 1)
        self.assertEqual(subtractions[0].type, List.SUBTRACTION)

        counts = List.counts.all()
        self.assertEqual(counts.count(), 0)

    def test_list_string(self):
        list = List.objects.create(
            session=self.session, 
            owner=self.user1, 
            name=self.list_name, 
            type=List.ADDITION
        )
        self.assertEqual(list.__str__(), '{} List - {} {}'.format(self.list_name, self.session.name, list.get_type_display()))

    # edit list name?

    def test_max_list_name_length(self):
        long_list_name = (20 + 1)*'A'
        with self.assertRaises(ValidationError):
            list = List.objects.create(
                session=self.session, 
                owner=self.user1, 
                name=long_list_name, 
                type=List.ADDITION
        )
            list.full_clean()

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

    def test_duplicate_item_name_raises_integrity_error(self):
        with self.assertRaises(IntegrityError):
            item2 = Item.objects.create(store=self.store1, name=self.item_name)

    def test_duplicate_item_name_for_seperate_stores(self):
        store_name2 = 'Test Store2'
        store2 = Store.objects.create(owner=self.user1, name=store_name2)
        item2 = Item.objects.create(store=store2, name=self.item_name)
        self.assertEqual(item2.name, self.item.name)

    def test_item_string(self):
        self.assertEqual(self.item.__str__(), self.item_name)

    def test_max_item_name_length(self):
        long_item_name = (40 + 1)*'A'
        with self.assertRaises(ValidationError):
            item = Item.objects.create(store=self.store1, name=long_item_name)
            item.full_clean()

    def test_max_item_origin_length(self):
        long_origin_name = (30 + 1)*'A'
        with self.assertRaises(ValidationError):
            item = Item.objects.create(store=self.store1, name='test', origin=long_origin_name)
            item.full_clean()

    def test_max_item_department_length(self):
        long_department_name = (10 + 1)*'A'
        with self.assertRaises(ValidationError):
            item = Item.objects.create(store=self.store1, name='test', department=long_department_name)
            item.full_clean()

class SessionItemsManagerTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:

        # Create User, Store, Item
        cls.user1 = User.objects.create_user('Mike')
        cls.store_name = "Test Store"
        cls.store1 = Store.objects.create(owner=cls.user1, name=cls.store_name)
        cls.item_name = "Bacardi Superior 70CL BTL"
        cls.item = Item.objects.create(store=cls.store1, name=cls.item_name)

        # Session1
        cls.session1 = Session.objects.create(  store=cls.store1, 
                                                name="Tuesday", 
                                                start_date=date(year=2023, month=1, day=13), 
                                                end_date=date(year=2023, month=1, day=14) 
        )
        # List1, ListItem1
        cls.list = List.objects.create(
            session=cls.session1, 
            owner=cls.user1, 
            name='Closing Stock', 
            type=List.COUNT
        )
        list_item = ListItem.objects.create(list=cls.list, item=cls.item, amount='4.5')


        # Session2
        cls.session2 = Session.objects.create(  store=cls.store1, 
                                                name="Wednesday", 
                                                start_date=date(year=2023, month=1, day=14), 
                                                end_date=date(year=2023, month=1, day=15),
                                                previous_session=cls.session1,
        )

        # List1, ListItem1
        cls.list1 = List.objects.create(
            session=cls.session2, 
            owner=cls.user1, 
            name='Starting Stock', 
            type=List.ADDITION
        )
        list_item1 = ListItem.objects.create(list=cls.list1, item=cls.item, amount='12.7')

        # List2, ListItem2
        cls.list2 = List.objects.create(
            session=cls.session2, 
            owner=cls.user1, 
            name='Delivery', 
            type=List.ADDITION
        )
        list_item2 = ListItem.objects.create(list=cls.list2, item=cls.item, amount='10')

        # List3, ListItem3
        cls.list3 = List.objects.create(
            session=cls.session2, 
            owner=cls.user1, 
            name='Sales', 
            type=List.SUBTRACTION
        )
        list_item3 = ListItem.objects.create(list=cls.list3, item=cls.item, amount='3.7')

        return super().setUpTestData()

    def test_session_items_manager(self):
        items = Item.objects.session_items(self.session2)
        self.assertEqual(items[0].total_previous, Decimal('4.5'))
        self.assertEqual(items[0].total_added, Decimal('22.7'))
        self.assertEqual(items[0].total_subtracted, Decimal('3.7'))
        self.assertEqual(items[0].total_counted, Decimal('0'))

    def test_serialize_session_items_manager(self):
        serialized_items = Item.objects.serialized_session_items(self.session2)
        dict = serialized_items[0]
        self.assertEqual(dict['total_previous'], '4.5')
        self.assertEqual(dict['total_added'], '22.7')
        self.assertEqual(dict['total_subtracted'], '3.7')
        self.assertEqual(dict['total_counted'], '0.0')

class ListItemTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:


        # Create User, Store, Session, List, Item
        cls.user1 = User.objects.create_user('Mike')
        cls.store_name = "Test Store"
        cls.store1 = Store.objects.create(owner=cls.user1, name=cls.store_name)
        cls.session_name = "Wednesday"
        start_date = date(year=2023, month=1, day=14)
        end_date = date(year=2023, month=1, day=15)
        cls.session = Session.objects.create(   store=cls.store1, 
                                                name=cls.session_name, 
                                                start_date=start_date, 
                                                end_date=end_date )
        cls.list_name = 'Starting Stock'
        cls.list = List.objects.create(
            session=cls.session, 
            owner=cls.user1, 
            name=cls.list_name, 
            type=List.ADDITION
        )
        cls.item_name = "Bacardi Superior 70CL BTL"
        cls.item = Item.objects.create(store=cls.store1, name=cls.item_name)

        cls.list_item_amount = '12.7'
        cls.list_item = ListItem.objects.create(list=cls.list, item=cls.item, amount=cls.list_item_amount)

        return super().setUpTestData()

    def test_create_list_item(self):

        list_items = ListItem.objects.all()
        self.assertEqual(list_items[0].list, self.list)
        self.assertEqual(list_items[0].item, self.item)
        self.assertEqual(list_items[0].amount, Decimal(self.list_item_amount))

    def test_list_item_string(self):
        self.assertEqual(self.list_item.__str__(), '{} {}'.format(self.list_item_amount, self.item_name))

    def test_min_list_item_amount(self):
        negative_amount = '-1'
        with self.assertRaises(ValidationError):
            list_item = ListItem.objects.create(list=self.list, item=self.item, amount=negative_amount)
            list_item.full_clean()

    def test_max_list_item_amount(self):
        v_large_amount = '100001'
        with self.assertRaises(ValidationError):
            list_item = ListItem.objects.create(list=self.list, item=self.item, amount=v_large_amount)
            list_item.full_clean()