from datetime import date
# from django.utils import timezone
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from stocklist.models import User, Store, List, ListItem, Item, StockPeriod, StockList, Stocktake


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

    def test_create_store_default_store_name(self):
        store = Store.objects.create(user=self.user1)
        store.full_clean()
        self.assertEqual(store.name, 'Store')

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


class StockPeriodTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:

        cls.store_name = "Test Store"

        # Create User, Store
        cls.user1 = User.objects.create_user('Mike')
        cls.store1 = Store.objects.create(user=cls.user1, name=cls.store_name)

        return super().setUpTestData()

    def test_create_default_stockperiod(self):
        stock_period = StockPeriod.objects.create(
            store=self.store1,
        )
        stockperiods = StockPeriod.objects.all()
        self.assertEqual(stockperiods.count(), 1)
        self.assertEqual(stockperiods[0].store, self.store1)
        self.assertEqual(stockperiods[0].frequency, StockPeriod.DAILY)

    def test_stockperiod_default_string(self):
        stock_period = StockPeriod.objects.create(
            store=self.store1,
        )
        stockperiods = StockPeriod.objects.all()
        self.assertEqual(stockperiods.count(), 1)
        self.assertEqual(stockperiods[0].__str__(), 'Test Store Daily Count')

    def test_stockperiod_monthly_string(self):
        stock_period = StockPeriod.objects.create(
            store=self.store1,
            frequency=StockPeriod.MONTHLY,
        )
        stockperiods = StockPeriod.objects.all()
        self.assertEqual(stockperiods.count(), 1)
        self.assertEqual(stockperiods[0].__str__(), 'Test Store Monthly Count')

    def test_stockperiod_weekly_string(self):
        stock_period = StockPeriod.objects.create(
            store=self.store1,
            frequency=StockPeriod.WEEKLY,
        )
        stockperiods = StockPeriod.objects.all()
        self.assertEqual(stockperiods.count(), 1)
        self.assertEqual(stockperiods[0].__str__(), 'Test Store Weekly Count')

    def test_monthly_stock_period_next_date_end_of_year(self):
        stock_period = StockPeriod.objects.create(
            store=self.store1,
            frequency=StockPeriod.MONTHLY,
        )
        previous_date = date(year=2022, month=12, day=31)
        next_date = date(year=2023, month=1, day=31)

        self.assertEqual(next_date, stock_period.next_date(previous_date))

    def test_monthly_stock_period_next_date_leap_year(self):
        stock_period = StockPeriod.objects.create(
            store=self.store1,
            frequency=StockPeriod.MONTHLY,
        )
        previous_date = date(year=2023, month=2, day=28)
        next_date = date(year=2023, month=3, day=31)
        
        self.assertEqual(next_date, stock_period.next_date(previous_date))

    def test_weekly_stock_period_next_date(self):
        stock_period = StockPeriod.objects.create(
            store=self.store1,
            frequency=StockPeriod.WEEKLY,
        )
        previous_date = date(year=2022, month=12, day=26)
        next_date = date(year=2023, month=1, day=2)
        
        self.assertEqual(next_date, stock_period.next_date(previous_date))

    def test_daily_stock_period_next_date(self):
        stock_period = StockPeriod.objects.create(
            store=self.store1,
        )
        previous_date = date(year=2022, month=12, day=31)
        next_date = date(year=2023, month=1, day=1)
        
        self.assertEqual(next_date, stock_period.next_date(previous_date))

    def test_monthly_frequency_unique_for_store(self):
        monthly_period = StockPeriod.objects.create(
            store=self.store1,
            frequency=StockPeriod.MONTHLY,
        )
        with self.assertRaises(IntegrityError):
            StockPeriod.objects.create(
            store=self.store1,
            frequency=StockPeriod.MONTHLY,
        )

    def test_weeky_frequency_unique_for_store(self):
        weeky_period = StockPeriod.objects.create(
            store=self.store1,
            frequency=StockPeriod.WEEKLY,
        )
        with self.assertRaises(IntegrityError):
            StockPeriod.objects.create(
            store=self.store1,
            frequency=StockPeriod.WEEKLY,
        )

    def test_daily_frequency_not_unique_for_store(self):
        daily_period = StockPeriod.objects.create(
            store=self.store1,
        )
        StockPeriod.objects.create(
            store=self.store1,
        )
        stock_periods = StockPeriod.objects.all()
        self.assertEqual(stock_periods.count(), 2)


class StocktakeTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:

        cls.store_name = "Test Store"

        # Create User, Store
        cls.user1 = User.objects.create_user('Mike')
        cls.store1 = Store.objects.create(user=cls.user1, name=cls.store_name)

        cls.daily_period = StockPeriod.objects.create(
            store=cls.store1,
        )
        cls.weekly_period = StockPeriod.objects.create(
            store=cls.store1,
            frequency=StockPeriod.WEEKLY
        )
        cls.monthly_period = StockPeriod.objects.create(
            store=cls.store1,
            frequency=StockPeriod.MONTHLY
        )

        return super().setUpTestData()

    def test_create_stocktake(self):
        stocktake = Stocktake.objects.create(   
            stock_period=self.daily_period
        )
        stocktakes = Stocktake.objects.all()
        self.assertEqual(stocktakes.count(), 1)
        self.assertEqual(stocktakes[0].end_date, date.today())
        self.assertEqual(stocktakes[0].stock_period.store, self.store1)
        self.assertEqual(stocktakes[0].stock_period.frequency, StockPeriod.DAILY)

    def test_daily_stocktake_string(self):
        stocktake = Stocktake.objects.create(
            stock_period=self.daily_period, 
            end_date = date(year=2023, month=1, day=27),
        )
        
        expected_string = "Friday 27 Jan 2023"
        self.assertEqual(expected_string, stocktake.__str__())

    def test_weeky_stocktake_string(self):
        stocktake = Stocktake.objects.create(
            stock_period=self.weekly_period, 
            end_date = date(year=2023, month=1, day=29),
        )
        
        expected_string = "Week Ending Sunday 29 Jan 2023"
        self.assertEqual(expected_string, stocktake.__str__())

    def test_monthy_stocktake_string(self):
        stocktake = Stocktake.objects.create(   
            stock_period=self.monthly_period, 
            end_date = date(year=2023, month=1, day=31),
        )
        
        expected_string = "January 2023"
        self.assertEqual(expected_string, stocktake.__str__())

    # def test_end_date_unique_for_monthly_period(self):
    #     end_date = date(year=2023, month=1, day=31)
    #     Stocktake.objects.create(   
    #         stock_period=self.monthly_period, 
    #         end_date = end_date,
    #     )
    #     with self.assertRaises(IntegrityError):
    #         stocktake = Stocktake.objects.create(   
    #         stock_period=self.monthly_period, 
    #         end_date = end_date,
    #     )


    # def test_create_count_raises_validation_error_for_end_date_before_start_date(self):
    #     with self.assertRaises(ValidationError):
    #         Stocktake.objects.create( store=self.store1,
    #                                 name=self.count_name, 
    #                                 start_date=date(year=2023, month=1, day=14), 
    #                                 end_date=date(year=2023, month=1, day=13) )



    # edit count name, start & end date?
   

class StockListTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:

        # Create User, Store
        cls.store_name = "My Store"
        cls.user1 = User.objects.create_user('Mike')
        cls.store1 = Store.objects.create(
            user=cls.user1, 
            name=cls.store_name
        )

        # create StockPeriod, StockTake, List
        cls.stock_period = StockPeriod.objects.create(
            store=cls.store1,
        )
        cls.stocktake = Stocktake.objects.create(   
            stock_period=cls.stock_period, 
            end_date=date(year=2023, month=1, day=15)
        )
        cls.list = List.objects.create(
            store=cls.store1, 
            name='BoH Count', 
            type=List.COUNT,
            date_added=date(year=2023, month=1, day=28)
        )

        return super().setUpTestData()

    def test_create_stocklist(self):
        stocklist = StockList.objects.create(
            stocktake=self.stocktake,
            list=self.list,
            user=self.user1
        )
        stocklists = StockList.objects.all()
        self.assertEqual(stocklists.count(), 1)

    def test_stocklist__str__(self):
        stocklist = StockList.objects.create(
            stocktake=self.stocktake,
            list=self.list,
            user=self.user1
        )
        stocklists = StockList.objects.all()
        self.assertEqual(stocklists.count(), 1)
        self.assertEqual(stocklists[0].__str__(), 'BoH Count on Saturday 28 Jan 2023')

    # def test_list_type_must_be_count_constraint(self):
    #     list2 = List.objects.create(
    #         store=self.store1, 
    #         name='BoH Count', 
    #         type=List.ADDITION,
    #     )
    #     with self.assertRaises(ValidationError):
    #         stocklist = StockList.objects.create(
    #         stocktake=self.stocktake,
    #         list=list2,
    #         user=self.user1,
    #     )



class ListTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:

        cls.store_name = "Test Store"

        # Create User, Store
        cls.user1 = User.objects.create_user('Mike')
        cls.store1 = Store.objects.create(user=cls.user1, name=cls.store_name)


        cls.stock_period = StockPeriod.objects.create(
            store=cls.store1,
        )

        start_date = date(year=2023, month=1, day=14)
        end_date = date(year=2023, month=1, day=15)
        cls.stocktake = Stocktake.objects.create(   
            stock_period=cls.stock_period, 
            end_date=end_date 
        )
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


        cls.stock_period = StockPeriod.objects.create(
            store=cls.store1,
        )

        cls.count = Stocktake.objects.create(   
            stock_period=cls.stock_period,
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

    def test_item_unique_for_list(self):
        with self.assertRaises(IntegrityError):
            list_item2 = ListItem.objects.create(list=self.list, item=self.item, amount=self.list_item_amount)
            list_item2.full_clean()