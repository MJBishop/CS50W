import json
import datetime
from decimal import Decimal
from django.test import Client, TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from stocklist.models import User, Store, List, ListItem, Item, Stocktake, StockPeriod, StockList


class BaseTestCase(TestCase):

    TEST_USER = 'testuser'
    PASSWORD = '12345'
    
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username=cls.TEST_USER, email='testuser@test.com', password=cls.PASSWORD
        )
        return super().setUpTestData()

    def setUp(self):
        # Every test needs a client.
        self.client = Client()


class ImportTestCase(BaseTestCase):
    json_data = {
        'origin':'test_data.csv',
        'name':'Stock',
        'type':'AD',
        'items':[
            {
                'name':'Absolut Vodka 70CL BTL',
                'amount':'12'
            },
            {
                'name':'Bacardi Superior Rum 70CL BTL',
                'amount':'9'
            },
            {
                'name':'Cazadores Reposado Tequila Vodka 70CL BTL',
                'amount':'6'
            },
        ]
    }

class ImportItemsTestCase(ImportTestCase):

    @classmethod
    def setUpTestData(cls):
        sup = super().setUpTestData()
        cls.store = Store.objects.create(name='Test Store', user=cls.user1)
        cls.stock_period = StockPeriod.objects.create(store=cls.store)
        cls.stocktake = Stocktake.objects.create(stock_period=cls.stock_period)
        return sup
    
    def test_POST_import_items_redirects_to_login_if_not_logged_in(self):
        response = self.client.post("/import_items/1")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/import_items/1") 

    def test_POST_import_items_returns_404_for_invalid_stocktake(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        response = self.client.post("/import_items/2")
        self.assertEqual(response.status_code, 404)

    def test_GET_import_items_returns_400_for_user_logged_in(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        
        path = "/import_items/{}".format(self.stocktake.pk)
        response = self.client.get(path)
        self.assertEqual(response.status_code, 400)

    def test_POST_import_items_creates_list(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        path = "/import_items/{}".format(self.stocktake.pk)
        response = self.client.generic('POST', path, json.dumps(self.json_data))
        lists = List.objects.filter(store=self.store)
        self.assertEqual(lists.count(), 1)
        self.assertEqual(response.status_code, 201)

    def test_POST_import_items_returns_400_for_invalid_list_name_length(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        self.json_data['name'] = 'A'*(20 + 1)
        path = "/import_items/{}".format(self.stocktake.pk)
        response = self.client.generic('POST', path, json.dumps(self.json_data))

        lists = List.objects.filter(store=self.store)
        self.assertEqual(lists.count(), 0)
        self.assertEqual(response.status_code, 400)

    def test_POST_import_items_returns_400_for_invalid_list_type(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        self.json_data['type'] = 'ZZ'
        path = "/import_items/{}".format(self.stocktake.pk)
        response = self.client.generic('POST', path, json.dumps(self.json_data))
        
        lists = List.objects.filter(store=self.store)
        self.assertEqual(lists.count(), 0)
        self.assertEqual(response.status_code, 400)

    def test_POST_import_items_creates_items(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        path = "/import_items/{}".format(self.stocktake.pk)
        response = self.client.generic('POST', path, json.dumps(self.json_data))
        
        items = Item.objects.filter(store=self.stocktake.stock_period.store)
        self.assertEqual(items.count(), 3)

    def test_POST_import_items_returns_400_for_invalid_item_name_length(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        items = list(self.json_data["items"])
        items.append({
            'name':'A'*(80+1),
            'amount':'6'
        })
        self.json_data['items'] = items

        path = "/import_items/{}".format(self.stocktake.pk)
        response = self.client.generic('POST', path, json.dumps(self.json_data))
        
        lists = List.objects.filter(store=self.store)
        self.assertEqual(lists.count(), 1)
        items = Item.objects.filter(store=self.stocktake.stock_period.store)
        self.assertEqual(items.count(), 3)
        self.assertEqual(response.status_code, 400)

    def test_POST_import_items_creates_list_items(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        path = "/import_items/{}".format(self.stocktake.pk)
        response = self.client.generic('POST', path, json.dumps(self.json_data))
        
        lists = List.objects.filter(store=self.store)
        self.assertEqual(lists.count(), 1)
        list_items = ListItem.objects.filter(list=lists[0].pk)
        self.assertEqual(list_items.count(), 3)
        self.assertEqual(response.status_code, 201)

    def test_POST_import_items_returns_400_for_invalid_list_items_amount(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        items = list(self.json_data["items"])
        items.append({
            'name':'Test Fail for negative number',
            'amount':'-1'
        })
        self.json_data['items'] = items

        path = "/import_items/{}".format(self.stocktake.pk)
        response = self.client.generic('POST', path, json.dumps(self.json_data))
        
        lists = List.objects.filter(store=self.store)
        self.assertEqual(lists.count(), 1)
        list_items = ListItem.objects.filter(list=lists[0].pk)
        self.assertEqual(list_items.count(), 3)
        self.assertEqual(response.status_code, 400)

    def test_POST_import_items_returns_400_for_invalid_list_items_amount2(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        items = list(self.json_data["items"])
        items.append({
            'name':'Test Fail for large number',
            'amount':'1000001'
        })
        self.json_data['items'] = items

        path = "/import_items/{}".format(self.stocktake.pk)
        response = self.client.generic('POST', path, json.dumps(self.json_data))
        
        lists = List.objects.filter(store=self.store)
        self.assertEqual(lists.count(), 1)
        list_items = ListItem.objects.filter(list=lists[0].pk)
        self.assertEqual(list_items.count(), 3)
        self.assertEqual(response.status_code, 400)


class CountItemTestCase(ImportTestCase):
    
    def test_POST_count_item_redirects_to_login_if_not_logged_in(self):
        response = self.client.generic('POST', "/count_item/1/1", json.dumps({'amount':'1'}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/count_item/1/1") 

    def test_POST_count_item_returns_404_for_invalid_list(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        response = self.client.generic('POST', "/count_item/1/1", json.dumps({'amount':'1'}))
        self.assertEqual(response.status_code, 404) 

    def test_POST_count_item_returns_404_for_invalid_item(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store = Store.objects.create(name='Test Store', user=self.user1)
        list = List.objects.create(name='Test List', type='CO', store=store)

        path = "/count_item/{}/1".format(list.pk)
        response = self.client.generic('POST', path, json.dumps({'amount':'1'}))
        self.assertEqual(response.status_code, 404)

    def test_GET_count_item_returns_400_for_user_logged_in(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store = Store.objects.create(name='Test Store', user=self.user1)
        list = List.objects.create(name='Test List', type='CO', store=store)
        item = Item.objects.create(store=store, name="TEST ITEM NAME")

        path = "/count_item/{}/{}".format(list.pk, item.pk)
        response = self.client.generic('GET', path, json.dumps({'amount':'1'}))
        self.assertEqual(response.status_code, 400)

    def test_POST_count_item_creates_list_item(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store = Store.objects.create(name='Test Store', user=self.user1)
        list = List.objects.create(name='Test List', type='CO', store=store)
        item = Item.objects.create(store=store, name="TEST ITEM NAME")

        path = "/count_item/{}/{}".format(list.pk, item.pk)
        response = self.client.generic('POST', path, json.dumps({'amount':'1'}))
        list_items = ListItem.objects.filter(list=list, item=item)
        self.assertTrue(list_items.exists())
        self.assertEqual(list_items[0].amount, 1)
        self.assertEqual(response.status_code, 201)

    def test_POST_count_item_returns_400_for_invalid_list_items_amount_min(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store = Store.objects.create(name='Test Store', user=self.user1)
        list = List.objects.create(name='Test List', type='CO', store=store)
        item = Item.objects.create(store=store, name="TEST ITEM NAME")

        path = "/count_item/{}/{}".format(list.pk, item.pk)
        response = self.client.generic('POST', path, json.dumps({'amount':'-1'}))
        list_items = ListItem.objects.filter(list=list, item=item)
        self.assertEqual(response.status_code, 400)

    def test_POST_count_item_returns_400_for_invalid_list_items_amount_max(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store = Store.objects.create(name='Test Store', user=self.user1)
        list = List.objects.create(name='Test List', type='CO', store=store)
        item = Item.objects.create(store=store, name="TEST ITEM NAME")

        path = "/count_item/{}/{}".format(list.pk, item.pk)
        response = self.client.generic('POST', path, json.dumps({'amount':'1000001'}))
        list_items = ListItem.objects.filter(list=list, item=item)
        self.assertEqual(response.status_code, 400)


class StocktakeTestCase(BaseTestCase):
    def test_GET_count_redirects_to_login_if_not_logged_in(self):
        response = self.client.get("/count/1")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/count/1") 
    
    def test_GET_count_returns_404_for_invalid_count(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        response = self.client.get("/count/1")
        self.assertEqual(response.status_code, 404)

    def test_GET_count_returns_200_for_valid_count(self):
        store = Store.objects.create(name='Test Store', user=self.user1)
        stock_period = StockPeriod.objects.create(store=store)
        stocktake = Stocktake.objects.create(stock_period=stock_period)

        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        path = "/count/{}".format(stocktake.pk)
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)

    def test_POST_count_returns_400(self):
        store = Store.objects.create(name='Test Store', user=self.user1)
        stock_period = StockPeriod.objects.create(store=store)
        stocktake = Stocktake.objects.create(stock_period=stock_period)
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        path = "/count/{}".format(stocktake.pk)
        response = self.client.post(path)
        self.assertEqual(response.status_code, 400)

    def test_PUT_count_returns_400(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store = Store.objects.create(name='Test Store', user=self.user1)
        stock_period = StockPeriod.objects.create(store=store)
        stocktake = Stocktake.objects.create(stock_period=stock_period)

        path = "/count/{}".format(stocktake.pk)
        new_count_name = "New Stocktake Name"*3
        response = self.client.generic('PUT', path, json.dumps({"name":new_count_name}))
        self.assertEqual(response.status_code, 400)


class StoreTestCase(BaseTestCase):
    def test_store_path_redirects_to_login_if_not_logged_in(self):
        response = self.client.get("/store/1")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/store/1") 

    def test_store_path_returns_404_for_invalid_store(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        response = self.client.get("/store/1")
        self.assertEqual(response.status_code, 404)

    def test_store_path_returns_200_for_valid_store(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store = Store.objects.create(name='Test Store', user=self.user1)
        path = "/store/{}".format(store.pk)
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)

    def test_POST_store_returns_400(self):
        store = Store.objects.create(name='Test Store', user=self.user1)
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        path = "/store/{}".format(store.pk)
        response = self.client.post(path)
        self.assertEqual(response.status_code, 400)


class IndexTestCase(BaseTestCase):
    def test_index_path(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_GET_renders_index_html(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        response = self.client.get("/")
        self.assertEquals(response.templates[0].name, 'stocklist/index.html')

    def test_GET_redirects_to_login_when_not_signed_in(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login") 

    def test_GET_no_stores(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['stores_or_None'], None)

    def test_GET_stores(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        test_store_name = 'Test Store'
        Store.objects.create(name=test_store_name, user=self.user1)

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        store = response.context['stores_or_None'][0]
        self.assertEqual(store.name, test_store_name)

    def test_GET_oldest_store_first(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        Store.objects.create(name='Test Store 1', user=self.user1)
        Store.objects.create(name='Test Store 2', user=self.user1)

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['stores_or_None'][0].name, "Test Store 1")

    def test_GET_stock_takes(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store = Store.objects.create(name='Test Store', user=self.user1)
        stock_period = StockPeriod.objects.create(store=store)
        stocktake = Stocktake.objects.create(stock_period=stock_period)
        list = List.objects.create(store=store, type=List.COUNT)
        StockList.objects.create(stocktake=stocktake, list=list, user=self.user1)

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        stocktakes = response.context['stock_takes_or_None']
        self.assertEqual(stocktakes.count(), 1)

        test_stocktake = stocktakes[0]
        self.assertEqual(test_stocktake.frequency, StockPeriod.DAILY)

        test_stocklist = test_stocktake.stocklists.first()
        self.assertEqual(test_stocklist.list_id, list.pk)

    def test_GET_newest_stock_takes_first(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store = Store.objects.create(name='Test Store', user=self.user1)
        stock_period = StockPeriod.objects.create(store=store)
        Stocktake.objects.create(stock_period=stock_period)
        newest_stocktake = Stocktake.objects.create(stock_period=stock_period)

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        stocktakes = response.context['stock_takes_or_None']
        self.assertEqual(stocktakes.count(), 2)
        self.assertEqual(stocktakes[0], newest_stocktake)

    def test_GET_num_queries_existing_store(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store = Store.objects.create(name='Test Store', user=self.user1)
        with self.assertNumQueries(3):
            response = self.client.get("/")

    def test_GET_num_queries_no_stores(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        with self.assertNumQueries(3):
            response = self.client.get("/")

    def test_GET_forms(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['store_name_form'])
        self.assertTrue(response.context['stock_period_form'])
        self.assertTrue(response.context['stocktake_form'])
        self.assertTrue(response.context['stock_list_form'])

    def test_POST_reverse_to_index(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        response = self.client.post("/")
        self.assertEqual(response.url, "/") 
        

    # def test POST PUT


class LoginTestCase(BaseTestCase):
    def test_user_login(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user1.pk)

    def test_login_view(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)

    def test_login_view_GET_renders_login_html(self):
        response = self.client.get("/login")
        self.assertEquals(response.templates[0].name, 'stocklist/login.html')

    def test_login_view_POST_displays_error_message_for_invalid_username_and_or_password(self):
        response = self.client.post("/login", {'username':'someone', 'password':'something'})
        self.assertContains(response, "Invalid username and/or password.")

    def test_login_view_POST_success_reverse_to_index(self):
        response = self.client.post("/login", {'username':self.TEST_USER, 'password':self.PASSWORD})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/") 


class LogoutTestCase(BaseTestCase):
    def test_user_logout(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        response = self.client.get("/logout")
        self.assertEqual(response.url, "/") 


class RegisterTestCase(BaseTestCase):
    def test_register_view(self):
        response = self.client.get("/register")
        self.assertEqual(response.status_code, 200)
    
    def test_register_view_GET_renders_register_html(self):
        response = self.client.get("/register")
        self.assertEquals(response.templates[0].name, 'stocklist/register.html')

    def test_register_view_POST_displays_error_message_for_unmatching_password_confirmation(self):
        response = self.client.post("/register", {'username':'someone', 'confirmation':'other', 'password':'something', 'email':'test@test.com'})
        self.assertContains(response, "Passwords must match.")
    
    def test_register_view_POST_displays_error_message_for_username_taken(self):
        response = self.client.post("/register", {'username':self.TEST_USER, 'confirmation':'something', 'password':'something', 'email':'test@test.com'})
        self.assertContains(response, "Username already taken.")

    def test_register_view_POST_success_reverse_to_index(self):
        response = self.client.post("/register", {'username':'someone', 'confirmation':'something', 'password':'something', 'email':'test@test.com'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/") 