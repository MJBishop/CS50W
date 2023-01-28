from datetime import date
# from django.utils import timezone
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from stocklist.models import User, Store, Count, List, StockList, ListItem, Item


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

    def test_create_store_fails_for_no_store_name(self):
        with self.assertRaises(ValidationError):
            store = Store.objects.create(user=self.user1)
            store.full_clean()

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


class CountTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:

        cls.store_name = "Test Store"

        # Create User, Store
        cls.user1 = User.objects.create_user('Mike')
        cls.store1 = Store.objects.create(user=cls.user1, name=cls.store_name)

        return super().setUpTestData()


    def test_create_count(self):
        count = Count.objects.create(   
            store=self.store1, 
        )
        counts = Count.objects.all()
        self.assertEqual(counts.count(), 1)
        self.assertEqual(counts[0].end_date, date.today())
        self.assertEqual(counts[0].store, self.store1)
        self.assertEqual(counts[0].frequency, Count.DAILY)
        self.assertEqual(counts[0].previous_count, None)

    def test_daily_count_string(self):
        count = Count.objects.create(   
            store=self.store1, 
            end_date = date(year=2023, month=1, day=27),
        )
        
        expected_string = "Friday 27 Jan 2023"
        self.assertEqual(expected_string, count.__str__())

    def test_weeky_count_string(self):
        count = Count.objects.create(   
            store=self.store1, 
            end_date = date(year=2023, month=1, day=29),
            frequency = Count.WEEKLY,
        )
        
        expected_string = "Week Ending Sunday 29 Jan 2023"
        self.assertEqual(expected_string, count.__str__())

    def test_monthy_count_string(self):
        count = Count.objects.create(   
            store=self.store1, 
            end_date = date(year=2023, month=1, day=31),
            frequency = Count.MONTHLY,
        )
        
        expected_string = "January 2023"
        self.assertEqual(expected_string, count.__str__())


    # def test_create_count_raises_validation_error_for_end_date_before_start_date(self):
    #     with self.assertRaises(ValidationError):
    #         Count.objects.create( store=self.store1,
    #                                 name=self.count_name, 
    #                                 start_date=date(year=2023, month=1, day=14), 
    #                                 end_date=date(year=2023, month=1, day=13) )



    # edit count name, start & end date?

    # test for next count dates!
    def test_create_count_with_previous_count(self):
        start_date = date(year=2023, month=1, day=14)
        end_date = date(year=2023, month=1, day=15)
        count = Count.objects.create(   
            store=self.store1,  
            end_date=end_date
        )
        count2 = Count.objects.create(  
            store=self.store1, 
            end_date=date(year=2023, month=1, day=16), 
            previous_count=count
        )
        self.assertEqual(count2.previous_count, count)
        # self.assertEqual(count.next_count, count2) ??fails??    

    def test_count_next_date_month_end_of_year(self):
        previous_date = date(year=2022, month=12, day=31)
        next_date = date(year=2023, month=1, day=31)
        
        count = Count.objects.create(   
            store=self.store1, 
            end_date = previous_date,
            frequency = Count.MONTHLY,
        )
        self.assertEqual(next_date, count.next_date())

    def test_count_next_date_month_leap_year(self):
        previous_date = date(year=2023, month=2, day=28)
        next_date = date(year=2023, month=3, day=31)
        
        count = Count.objects.create(   
            store=self.store1, 
            end_date = previous_date,
            frequency = Count.MONTHLY,
        )
        self.assertEqual(next_date, count.next_date())

class CountManagerTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:

        # Create User, Store
        cls.store_name = "Test Store"
        cls.user1 = User.objects.create_user('Mike')
        cls.store1 = Store.objects.create(user=cls.user1, name=cls.store_name)

        cls.end_date1 = date(year=2023, month=1, day=31)
        cls.end_date2 = date(year=2023, month=2, day=28)
        cls.count1 = Count.objects.create(
            store=cls.store1,  
            end_date=cls.end_date1,
            frequency = Count.MONTHLY,
        )

        return super().setUpTestData()

    def test_monthly_create_next_count(self):
        next_count = Count.objects.create_next_count(self.count1)
        self.assertEqual(self.end_date2, next_count.end_date)


class ListTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:

        cls.store_name = "Test Store"

        # Create User, Store
        cls.user1 = User.objects.create_user('Mike')
        cls.store1 = Store.objects.create(user=cls.user1, name=cls.store_name)

        start_date = date(year=2023, month=1, day=14)
        end_date = date(year=2023, month=1, day=15)
        cls.count = Count.objects.create(   
            store=cls.store1, 
            end_date=end_date 
        )
        cls.list_name = 'Starting Stock'

        return super().setUpTestData()

    def test_create_list(self):
        self.lists = List.objects.create(
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
        self.assertEqual(list.__str__(), '{} List - {} {}'.format(self.list_name, self.store1.name, list.get_type_display()))

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

    def test_max_item_origin_length(self):
        long_origin_name = (30 + 1)*'A'
        with self.assertRaises(ValidationError):
            item = Item.objects.create(store=self.store1, name='test', origin=long_origin_name)
            item.full_clean()

class CountItemsManagerTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:

        # Create User, Store, Item
        cls.user1 = User.objects.create_user('Mike')
        cls.store_name = "Test Store"
        cls.store = Store.objects.create(user=cls.user1, name=cls.store_name)
        cls.item_name = "Bacardi Superior 70CL BTL"
        cls.item = Item.objects.create(store=cls.store, name=cls.item_name)

        # 1
        cls.count1 = Count.objects.create(  
            store=cls.store, 
            end_date=date(year=2023, month=1, day=14) 
        )
        cls.list1 = List.objects.create(
            store=cls.store, 
            name='Closing Stock', 
            type=List.COUNT
        )
        count_list1 = StockList.objects.create(  
            list = cls.list1,
            count = cls.count1,
            user=cls.user1
        )
        list_item1 = ListItem.objects.create(
            list=cls.list1, 
            item=cls.item, 
            amount='4.5'
            )


        # 2
        cls.count2 = Count.objects.create(  
            store=cls.store,  
            end_date=date(year=2023, month=1, day=15),
            previous_count=cls.count1,
        )
        cls.list2 = List.objects.create(
            store=cls.store, 
            name="Gerry's Delivery", 
            type=List.ADDITION
        )
        count_list2 = StockList.objects.create(  
            list = cls.list2,
            count = cls.count2,
            user=cls.user1
        )
        list_item2 = ListItem.objects.create(
            list=cls.list2, 
            item=cls.item, 
            amount='12.7')

        # 3
        cls.list3 = List.objects.create(
            store=cls.store, 
            name='Amathus Delivery', 
            type=List.ADDITION
        )
        count_list3 = StockList.objects.create(  
            list = cls.list3,
            count = cls.count2,
            user=cls.user1
        )
        list_item3 = ListItem.objects.create(
            list=cls.list3, 
            item=cls.item, 
            amount='10'
        )

        # 4
        cls.list4 = List.objects.create(
            store=cls.store, 
            name='Sales', 
            type=List.SUBTRACTION
        )
        count_list4 = StockList.objects.create(  
            list = cls.list4,
            count = cls.count2,
            user=cls.user1
        )
        list_item4 = ListItem.objects.create(
            list=cls.list4, 
            item=cls.item, 
            amount='3.7'
        )

        return super().setUpTestData()

    def test_count_items_manager(self):
        items = Item.objects.count_items(self.count2)
        self.assertEqual(items[0].total_added, Decimal('22.7'))
        self.assertEqual(items[0].total_subtracted, Decimal('3.7'))
        self.assertEqual(items[0].total_counted, Decimal('0'))
        self.assertEqual(items[0].total_previous, Decimal('4.5'))

    def test_serialize_count_items_manager(self):
        serialized_items = Item.objects.serialized_count_items(self.count2)
        dict = serialized_items[0]
        self.assertEqual(dict['total_previous'], '4.5')
        self.assertEqual(dict['total_added'], '22.7')
        self.assertEqual(dict['total_subtracted'], '3.7')
        self.assertEqual(dict['total_counted'], '0.0')

class ListItemTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:


        # Create User, Store, count, List, Item
        cls.user1 = User.objects.create_user('Mike')
        cls.store_name = "Test Store"
        cls.store1 = Store.objects.create(user=cls.user1, name=cls.store_name)
        cls.count_name = "Wednesday"
        start_date = date(year=2023, month=1, day=14)
        end_date = date(year=2023, month=1, day=15)
        cls.count = Count.objects.create(   
            store=cls.store1, 
            end_date=end_date 
        )
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