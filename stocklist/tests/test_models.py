# from datetime import date
from django.utils import timezone
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from stocklist.models import User, Store, List, ListItem, Item#, StockPeriod, StockList, Stocktake


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
        cls.store = Store.objects.create(user=cls.user1, name=cls.store_name)

        return super().setUpTestData()

    def test_create_store_missing_store_name(self):
        with self.assertRaises(ValidationError):
            store = Store.objects.create(user=self.user1)
            store.full_clean()
        
        # self.assertEqual(store.name, 'Store')

    def test_create_store(self):
        stores = Store.objects.all()
        self.assertEqual(stores.count(), 1)
        self.assertEqual(stores[0].name, self.store_name)
        self.assertEqual(self.store.user, self.user1)

    def test_unique_store_name_for_owner(self):
        with self.assertRaises(IntegrityError):
            store = Store.objects.create(user=self.user1, name=self.store_name)
            store.full_clean()

    def test_store_string(self):
        self.assertEqual(self.store_name, self.store.__str__())

    # edit store.name?

    def test_max_store_name_length(self):
        long_store_name = (20 + 1)*'A'
        with self.assertRaises(ValidationError):
            store = Store.objects.create(user=self.user1, name=long_store_name)
            store.full_clean()

    # def test_store_queryset_only_returns_stores_from_ownwer(self):
    #     # create stores
    #     store1 = Store.objects.create(user=self.user1, name=self.store_name)
    #     store2 = Store.objects.create(user=self.user2, name=self.store_name)

    #     stores = Store.objects.all()
    #     self.assertEqual(stores.count(), 1)


class ListTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:

        cls.store_name = "Test Store"

        # Create User, Store
        cls.user1 = User.objects.create_user('Mike')
        cls.store1 = Store.objects.create(user=cls.user1, name=cls.store_name)

        cls.list_name = 'Starting Stock'

        return super().setUpTestData()

    def test_create_list(self):
        self.list = List.objects.create(
            store=self.store1, 
            name=self.list_name, 
        )
        lists = List.objects.all()
        self.assertEqual(lists.count(), 1)
        self.assertEqual(lists[0].name, self.list_name)
        self.assertEqual(lists[0].type, List.ADDITION)

    def test_create_addition_list(self):
        list = List.objects.create(
            store=self.store1, 
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
            store=self.store1, 
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
            store=self.store1, 
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
            store=self.store1, 
            name=self.list_name, 
            type=List.ADDITION
        )
        self.assertEqual(list.__str__(), self.list_name)
        # self.assertEqual(list.__str__(), '{} List - {} {}'.format(self.list_name, self.store1.name, list.get_type_display()))

    # edit list name?

    def test_max_list_name_length(self):
        long_list_name = (20 + 1)*'A'
        with self.assertRaises(ValidationError):
            list = List.objects.create(
                store=self.store1, 
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
        cls.store1 = Store.objects.create(user=cls.user1, name=cls.store_name)
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
        store2 = Store.objects.create(user=self.user1, name=store_name2)
        item2 = Item.objects.create(store=store2, name=self.item_name)
        self.assertEqual(item2.name, self.item.name)

    def test_item_string(self):
        self.assertEqual(self.item.__str__(), self.item_name)

    def test_max_item_name_length(self):
        long_item_name = (80 + 1)*'A'
        with self.assertRaises(ValidationError):
            item = Item.objects.create(store=self.store1, name=long_item_name)
            item.full_clean()


    # serializer
    def test_item_serializer_item_id(self):
        serialized_item = self.item.serialize()
        self.assertEqual(self.item.id, serialized_item['id'])
    
    def test_item_serializer_item_name(self):
        serialized_item = self.item.serialize()
        self.assertEqual(self.item.name, serialized_item['name'])
    
    def test_item_serializer_item_list_item_list_id(self):
        list = List.objects.create(store=self.store1, name="Test List", type=List.COUNT)
        list_item = ListItem.objects.create(item=self.item, list=list, amount=11)

        serialized_item = self.item.serialize()
        list_item_to_test = serialized_item["list_items"][0]
        self.assertEqual(list.id, list_item_to_test["list_id"])

    def test_item_serializer_item_list_item_amount(self):
        list = List.objects.create(store=self.store1, name="Test List", type=List.COUNT)
        list_item = ListItem.objects.create(item=self.item, list=list, amount=11)

        serialized_item = self.item.serialize()
        list_item_to_test = serialized_item["list_items"][0]
        self.assertEqual(list_item.amount, list_item_to_test['amount'])
   
    def test_item_serializer_item_list_items_length(self):
        list = List.objects.create(store=self.store1, name="Test List", type=List.COUNT)
        list_item = ListItem.objects.create(item=self.item, list=list, amount=11)

        list2 = List.objects.create(store=self.store1, name="Test List 2", type=List.COUNT)
        list_item2 = ListItem.objects.create(item=self.item, list=list2, amount=22)

        serialized_item = self.item.serialize()
        self.assertEqual(2, len(serialized_item['list_items']))



class ListItemTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:


        # Create User, Store, count, List, Item
        cls.user1 = User.objects.create_user('Mike')
        cls.store_name = "Test Store"
        cls.store1 = Store.objects.create(user=cls.user1, name=cls.store_name)
        cls.count_name = "Wednesday"
        cls.list_name = 'Starting Stock'
        cls.list = List.objects.create(
            store=cls.store1, 
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
        list_item = list_items[0]
        self.assertEqual(list_item.list, self.list)
        self.assertEqual(list_item.item, self.item)
        self.assertEqual(list_item.amount, Decimal(self.list_item_amount))
        self.assertEqual(list_item.name, self.item_name)

    def test_list_item_string(self):
        self.assertEqual(self.list_item.__str__(), '{} {}'.format(self.list_item_amount, self.item_name))

    def test_min_list_item_amount(self):
        item = Item.objects.create(store=self.store1, name='Another Item')
        negative_amount = '-1'
        with self.assertRaises(ValidationError):
            list_item = ListItem.objects.create(list=self.list, item=item, amount=negative_amount)
            list_item.full_clean()

    def test_max_list_item_amount(self):
        item = Item.objects.create(store=self.store1, name='And Another Item')
        v_large_amount = '100001'
        with self.assertRaises(ValidationError):
            list_item = ListItem.objects.create(list=self.list, item=item, amount=v_large_amount)
            list_item.full_clean()


