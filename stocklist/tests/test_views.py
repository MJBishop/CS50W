import json
# import datetime
from decimal import Decimal
from django.test import Client, TestCase

from stocklist.models import User, Store, List, ListItem, Item, MAX_STORE_NAME_LENGTH 


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
    
    json_data = [ 
        {
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
                    'amount':''
                },
            ]
        }
    ]


class ItemsTestCase(ImportTestCase):

    @classmethod
    def setUpTestData(cls):
        sup = super().setUpTestData()
        cls.store = Store.objects.create(name='Test Store', user=cls.user1)
        return sup

    def test_GET_items_redirects_to_login_if_not_logged_in(self):
        path = "/items/{}".format(self.store.pk)
        response = self.client.get(path)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/items/1") 

    def test_GET_items_returns_404_for_invalid_store(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        response = self.client.get("/items/2")
        self.assertEqual(response.status_code, 404)

    def test_POST_items_returns_400_for_user_logged_in(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        
        path = "/items/{}".format(self.store.pk)
        response = self.client.post(path)
        self.assertEqual(response.status_code, 400)


    # failing when all test cases running

    def test_GET_items_returns_items(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        import_path = "/import_items/{}".format(self.store.pk)
        self.client.generic('POST', import_path, json.dumps(self.json_data))

        path = "/items/{}".format(self.store.pk)
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        data = response.json() 
        print(data)
        items = data['items']
        self.assertEqual(items[0]['name'], 'Absolut Vodka 70CL BTL')

    def test_GET_items_returns_lists(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        import_path = "/import_items/{}".format(self.store.pk)
        self.client.generic('POST', import_path, json.dumps(self.json_data))

        path = "/items/{}".format(self.store.pk)
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        data = response.json() 
        lists = data['lists']
        self.assertEqual(lists[0]['name'], 'Stock')


class ImportItemsTestCase(ImportTestCase):

    @classmethod
    def setUpTestData(cls):
        sup = super().setUpTestData()
        cls.store = Store.objects.create(name='Test Store', user=cls.user1)
        return sup
    
    def test_POST_import_items_redirects_to_login_if_not_logged_in(self):
        response = self.client.post("/import_items/1")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/import_items/1") 

    def test_POST_import_items_returns_404_for_invalid_store(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        response = self.client.post("/import_items/2")
        self.assertEqual(response.status_code, 404)

    def test_GET_import_items_returns_400_for_user_logged_in(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        
        path = "/import_items/{}".format(self.store.pk)
        response = self.client.get(path)
        self.assertEqual(response.status_code, 400)

    def test_POST_import_items_creates_list(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        path = "/import_items/{}".format(self.store.pk)
        response = self.client.generic('POST', path, json.dumps(self.json_data))
        lists = List.objects.filter(store=self.store)
        self.assertEqual(lists.count(), 1)
        self.assertEqual(response.status_code, 201)

    def test_POST_import_items_returns_400_for_invalid_list_name_length(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        self.json_data[0]['name'] = 'A'*(20 + 1)
        path = "/import_items/{}".format(self.store.pk)
        response = self.client.generic('POST', path, json.dumps(self.json_data))

        lists = List.objects.filter(store=self.store)
        self.assertEqual(lists.count(), 0)
        self.assertEqual(response.status_code, 400)

    def test_POST_import_items_returns_400_for_invalid_list_type(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        self.json_data[0]['type'] = 'ZZ'
        path = "/import_items/{}".format(self.store.pk)
        response = self.client.generic('POST', path, json.dumps(self.json_data))
        
        lists = List.objects.filter(store=self.store)
        self.assertEqual(lists.count(), 0)
        self.assertEqual(response.status_code, 400)

    def test_POST_import_items_creates_items(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        path = "/import_items/{}".format(self.store.pk)
        response = self.client.generic('POST', path, json.dumps(self.json_data))
        
        items = Item.objects.filter(store=self.store)
        self.assertEqual(items.count(), 3)

    def test_POST_import_items_returns_400_for_invalid_item_name_length(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        items = list(self.json_data[0]["items"])
        items.append({
            'name':'A'*(80+1),
            'amount':'6'
        })
        json_data = self.json_data.copy()
        json_data[0]['items'] = items

        path = "/import_items/{}".format(self.store.pk)
        response = self.client.generic('POST', path, json.dumps(json_data))
        
        lists = List.objects.filter(store=self.store)
        self.assertEqual(lists.count(), 1)
        items = Item.objects.filter(store=self.store)
        self.assertEqual(items.count(), 3)
        self.assertEqual(response.status_code, 400)

    def test_POST_import_items_handles_missing_item_name(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        items = list(self.json_data[0]["items"])
        items.append({
            'name':'',
            'amount':'6'
        })
        json_data = self.json_data.copy()
        json_data[0]['items'] = items

        path = "/import_items/{}".format(self.store.pk)
        response = self.client.generic('POST', path, json.dumps(json_data))
        
        lists = List.objects.filter(store=self.store)
        self.assertEqual(lists.count(), 1)
        items = Item.objects.filter(store=self.store)
        self.assertEqual(items.count(), 3)
        self.assertEqual(response.status_code, 201)

    def test_POST_import_items_creates_list_items(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        path = "/import_items/{}".format(self.store.pk)
        response = self.client.generic('POST', path, json.dumps(self.json_data))
        
        lists = List.objects.filter(store=self.store)
        self.assertEqual(lists.count(), 1)
        list_items = ListItem.objects.filter(list=lists[0].pk)
        self.assertEqual(list_items.count(), 3)
        self.assertEqual(response.status_code, 201)

    def test_POST_import_items_returns_400_for_invalid_list_items_amount(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        items = list(self.json_data[0]["items"])
        items.append({
            'name':'Test Fail for negative number',
            'amount':'-1'
        })
        json_data = self.json_data.copy()
        json_data[0]['items'] = items

        path = "/import_items/{}".format(self.store.pk)
        response = self.client.generic('POST', path, json.dumps(json_data))
        
        lists = List.objects.filter(store=self.store)
        self.assertEqual(lists.count(), 1)
        list_items = ListItem.objects.filter(list=lists[0].pk)
        self.assertEqual(list_items.count(), 3)
        self.assertEqual(response.status_code, 400)

    def test_POST_import_items_returns_400_for_invalid_list_items_amount2(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        items = list(self.json_data[0]["items"])
        items.append({
            'name':'Test Fail for large number',
            'amount':'1000001'
        })
        json_data = self.json_data.copy()
        json_data[0]['items'] = items
        # print(json_data)

        path = "/import_items/{}".format(self.store.pk)
        response = self.client.generic('POST', path, json.dumps(json_data))
        
        lists = List.objects.filter(store=self.store)
        self.assertEqual(lists.count(), 1)
        list_items = ListItem.objects.filter(list=lists[0].pk)
        self.assertEqual(list_items.count(), 3)
        self.assertEqual(response.status_code, 400)

    def test_POST_import_items_creates_listitem_for_missing_item_amount(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        items = list(self.json_data[0]["items"])
        items.append({
            'name':'Test Pass for missing amount'
        })
        json_data = self.json_data.copy()
        json_data[0]['items'] = items

        path = "/import_items/{}".format(self.store.pk)
        response = self.client.generic('POST', path, json.dumps(json_data))
        
        lists = List.objects.filter(store=self.store)
        self.assertEqual(lists.count(), 1)
        list_items = ListItem.objects.filter(list=lists[0].pk)
        self.assertEqual(list_items.count(), 4)
        self.assertEqual(response.status_code, 201)

    def test_POST_import_items_doesnt_create_new_item_if_item_already_in_store(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        items = list(self.json_data[0]["items"])
        items.append({
            'name':'Absolut Vodka 70CL BTL'
        })
        json_data = self.json_data.copy()
        json_data[0]['items'] = items

        path = "/import_items/{}".format(self.store.pk)
        response = self.client.generic('POST', path, json.dumps(json_data))
        
        lists = List.objects.filter(store=self.store)
        self.assertEqual(lists.count(), 1)
        list_items = ListItem.objects.filter(list=lists[0].pk)
        self.assertEqual(list_items.count(), 4)
        items = Item.objects.filter(store=self.store.pk)
        self.assertEqual(items.count(), 3)
        self.assertEqual(response.status_code, 201)


class CreateListTestCase(ImportTestCase):

    @classmethod
    def setUpTestData(cls):
        sup = super().setUpTestData()
        cls.store = Store.objects.create(name='Test Store', user=cls.user1)
        return sup

    def test_POST_create_list_redirects_to_login_if_not_logged_in(self):
        response = self.client.generic('POST', "/create_lists/1", json.dumps([{'name':'Test List', 'type':'AD'}]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/create_lists/1") 

    def test_GET_create_list_returns_400_for_user_logged_in(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        response = self.client.generic('GET', "/create_lists/1", json.dumps([{'name':'Test List', 'type':'AD'}]))
        self.assertEqual(response.status_code, 400)

    def test_POST_create_list_returns_404_for_invalid_store(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        response = self.client.generic('POST', "/create_lists/2", json.dumps([{'name':'Test List', 'type':'AD'}]))
        self.assertEqual(response.status_code, 404)

    def test_POST_create_list_returns_201_for_valid_list_type(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        response = self.client.generic('POST', "/create_lists/1", json.dumps([{'name':'Test List', 'type':'AD'}]))
        self.assertEqual(response.status_code, 201)

    def test_POST_create_list_returns_400_for_invalid_name(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        response = self.client.generic('POST', "/create_lists/1", json.dumps([{'name':'A'*21, 'type':'AD'}]))
        self.assertEqual(response.status_code, 400)

    def test_POST_create_list_returns_400_for_empty_name(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        response = self.client.generic('POST', "/create_lists/1", json.dumps([{'name':'', 'type':'AD'}]))
        self.assertEqual(response.status_code, 400)

    def test_POST_create_list_returns_400_for_invalid_type(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        response = self.client.generic('POST', "/create_lists/1", json.dumps([{'name':'test list', 'type':'ZZ'}]))
        self.assertEqual(response.status_code, 400)

    def test_POST_create_list_returns_201_for_multiple_valid_lists(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        data = [
            {'name':'Import', 'type':'AD'},
            {'name':'Start', 'type':'CO'},
            {'name':'End', 'type':'CO'},
        ]
        response = self.client.generic('POST', "/create_lists/1", json.dumps(data))
        self.assertEqual(response.status_code, 201)

    def test_POST_create_list_returns_201_for_missing_type(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        response = self.client.generic('POST', "/create_lists/1", json.dumps([{'name':'Test List'}]))
        self.assertEqual(response.status_code, 201)
    
    def test_POST_create_list_returns_201_for_empty_type(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        response = self.client.generic('POST', "/create_lists/1", json.dumps([{'name':'test list', 'type':''}]))
        self.assertEqual(response.status_code, 201)
        

class CreateListItemTestCase(ImportTestCase):
    
    def test_POST_create_list_item_redirects_to_login_if_not_logged_in(self):
        response = self.client.generic('POST', "/create_list_item/1/1", json.dumps({'amount':'1'}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/create_list_item/1/1") 

    def test_POST_create_list_item_returns_404_for_invalid_list(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        response = self.client.generic('POST', "/create_list_item/1/1", json.dumps({'amount':'1'}))
        self.assertEqual(response.status_code, 404) 

    def test_POST_create_list_item_returns_404_for_invalid_item(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store = Store.objects.create(name='Test Store', user=self.user1)
        list = List.objects.create(name='Test List', type='CO', store=store)

        path = "/create_list_item/{}/1".format(list.pk)
        response = self.client.generic('POST', path, json.dumps({'amount':'1'}))
        self.assertEqual(response.status_code, 404)

    def test_GET_create_list_item_returns_400_for_user_logged_in(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store = Store.objects.create(name='Test Store', user=self.user1)
        list = List.objects.create(name='Test List', type='CO', store=store)
        item = Item.objects.create(store=store, name="TEST ITEM NAME")

        path = "/create_list_item/{}/{}".format(list.pk, item.pk)
        response = self.client.generic('GET', path, json.dumps({'amount':'1'}))
        self.assertEqual(response.status_code, 400)

    def test_POST_create_list_item_creates_list_item(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store = Store.objects.create(name='Test Store', user=self.user1)
        list = List.objects.create(name='Test List', type='CO', store=store)
        item = Item.objects.create(store=store, name="TEST ITEM NAME")

        path = "/create_list_item/{}/{}".format(list.pk, item.pk)
        response = self.client.generic('POST', path, json.dumps({'amount':'1'}))
        list_items = ListItem.objects.filter(list=list, item=item)
        self.assertTrue(list_items.exists())
        self.assertEqual(list_items[0].amount, 1)
        self.assertEqual(response.status_code, 201)

    def test_POST_create_list_item_creates_list_item_with_decimal_amount(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store = Store.objects.create(name='Test Store', user=self.user1)
        list = List.objects.create(name='Test List', type='CO', store=store)
        item = Item.objects.create(store=store, name="TEST ITEM NAME")

        path = "/create_list_item/{}/{}".format(list.pk, item.pk)
        response = self.client.generic('POST', path, json.dumps({'amount':'1.1'}))
        list_items = ListItem.objects.filter(list=list, item=item)
        self.assertTrue(list_items.exists())
        self.assertEqual(list_items[0].amount, Decimal('1.1'))
        self.assertEqual(response.status_code, 201)

    def test_POST_create_list_item_updates_list_item_if_exists(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store = Store.objects.create(name='Test Store', user=self.user1)
        list = List.objects.create(name='Test List', type='CO', store=store)
        item = Item.objects.create(store=store, name="TEST ITEM NAME")
        list_item = ListItem.objects.create(list=list, item=item, amount='1')

        path = "/create_list_item/{}/{}".format(list.pk, item.pk)
        response = self.client.generic('POST', path, json.dumps({'amount':'11'}))
        list_items = ListItem.objects.filter(list=list, item=item)
        self.assertTrue(list_items.exists())
        self.assertEqual(list_items.count(), 1)
        self.assertEqual(list_items[0].amount, 11)
        self.assertEqual(response.status_code, 201)

    def test_POST_create_list_item_returns_400_for_invalid_list_items_amount_min(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store = Store.objects.create(name='Test Store', user=self.user1)
        list = List.objects.create(name='Test List', type='CO', store=store)
        item = Item.objects.create(store=store, name="TEST ITEM NAME")

        path = "/create_list_item/{}/{}".format(list.pk, item.pk)
        response = self.client.generic('POST', path, json.dumps({'amount':'-1'}))
        list_items = ListItem.objects.filter(list=list, item=item)
        self.assertEqual(response.status_code, 400)

    def test_POST_create_list_item_returns_400_for_invalid_list_items_amount_max(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store = Store.objects.create(name='Test Store', user=self.user1)
        list = List.objects.create(name='Test List', type='CO', store=store)
        item = Item.objects.create(store=store, name="TEST ITEM NAME")

        path = "/create_list_item/{}/{}".format(list.pk, item.pk)
        response = self.client.generic('POST', path, json.dumps({'amount':'1000001'}))
        list_items = ListItem.objects.filter(list=list, item=item)
        self.assertEqual(response.status_code, 400)


class CreateItemTestCase(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        sup = super().setUpTestData()
        cls.store = Store.objects.create(name='Test Store', user=cls.user1)
        return sup

    def test_POST_create_item_redirects_to_login_if_not_logged_in(self):
        response = self.client.generic('POST', "/create_item/1", json.dumps({'name':'Test Item'}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/create_item/1") 

    def test_POST_create_item_returns_404_for_invalid_store(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        response = self.client.generic('POST', "/create_item/2", json.dumps({'name':'Test Item'}))
        self.assertEqual(response.status_code, 404) 

    def test_GET_create_item_returns_400_for_user_logged_in(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        item = Item.objects.create(store=self.store, name="TEST ITEM NAME")

        path = "/create_item/{}".format(self.store.pk)
        response = self.client.generic('GET', path)
        self.assertEqual(response.status_code, 400)

    def test_POST_create_item_returns_400_for_invalid_name(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        response = self.client.generic('POST', "/create_item/1", json.dumps({'name':'A'*81}))
        self.assertEqual(response.status_code, 400)

    def test_POST_create_item_returns_400_for_empty_name(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        response = self.client.generic('POST', "/create_item/1", json.dumps({'name':''}))
        self.assertEqual(response.status_code, 400)

    def test_POST_create_item_name_not_unique_returns_400(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        test_item_name = 'Test Item Name'
        item = Item.objects.create(store=self.store, name=test_item_name)

        response = self.client.generic('POST', "/create_item/1", json.dumps({'name':test_item_name}))
        self.assertEqual(response.status_code, 400)

    def test_POST_create_item_returns_201_for_valid_name_and_store(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)

        response = self.client.generic('POST', "/create_item/1", json.dumps({'name':'New Name'}))
        self.assertEqual(response.status_code, 201)


class UpdateStoreTestCase(BaseTestCase):
    def test_PUT_returns_404_for_invalid_store(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        response = self.client.put("/update_store/1")
        self.assertEqual(response.status_code, 404)

    def test_PUT_returns_201_for_valid_store(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store = Store.objects.create(name='Test Store', user=self.user1)
        test_store_name = 'New Store Name'

        path = "/update_store/{}".format(store.pk)
        response = self.client.generic('PUT', path, json.dumps({"name":test_store_name}))
        self.assertEqual(response.status_code, 201)

    def test_PUT_valid_data_returns_201(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store = Store.objects.create(name='Test Store', user=self.user1)
        test_store_name = 'New Store Name'

        path = "/update_store/{}".format(store.pk)
        response = self.client.generic('PUT', path, json.dumps({"name":test_store_name}))
        self.assertEqual(response.status_code, 201)

    def test_PUT_no_name_change_returns_201(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store = Store.objects.create(name='Test Store', user=self.user1)
        test_store_name = 'Test Store'

        path = "/update_store/{}".format(store.pk)
        response = self.client.generic('PUT', path, json.dumps({"name":test_store_name}))
        self.assertEqual(response.status_code, 201)

    def test_PUT_empty_data_returns_400(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store = Store.objects.create(name='Test Store', user=self.user1)
        test_store_name = ''

        path = "/update_store/{}".format(store.pk)
        response = self.client.generic('PUT', path, json.dumps({"name":test_store_name}))
        self.assertEqual(response.status_code, 400)

    def test_store_name_max_length_returns_400(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store = Store.objects.create(name='Test Store', user=self.user1)
        test_store_name = 'A'*(MAX_STORE_NAME_LENGTH + 1)

        path = "/update_store/{}".format(store.pk)
        response = self.client.generic('PUT', path, json.dumps({"name":test_store_name}))
        self.assertEqual(response.status_code, 400)

    def test_store_name_not_unique_returns_400(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store1 = Store.objects.create(name='Test Store 1', user=self.user1)
        test_store_name = 'Test Store 2'
        store2 = Store.objects.create(name=test_store_name, user=self.user1)

        path = "/update_store/{}".format(store1.pk)
        response = self.client.generic('PUT', path, json.dumps({"name":test_store_name}))
        self.assertEqual(response.status_code, 400)
        # print(response)

# TODO - 2 fail when testing whole page
class StoreTestCase(ImportTestCase):

    @classmethod
    def setUpTestData(cls):
        sup = super().setUpTestData()
        cls.store = Store.objects.create(name='Test Store', user=cls.user1)
        return sup
    
    def test_store_path_redirects_to_login_if_not_logged_in(self):
        path = "/store/{}".format(self.store.pk)
        response = self.client.get(path)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/store/{}".format(self.store.pk)) 

    def test_PUT_returns_302(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        path = "/store/{}".format(self.store.pk)
        response = self.client.put(path)

        self.assertEqual(response.status_code, 302)

    def test_invalid_store(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        path = "/store/{}".format(self.store.pk + 1)
        response = self.client.get(path)

        self.assertEqual(response.status_code, 404)

    def test_valid_store(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        path = "/store/{}".format(self.store.pk)
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['store'])

    def test_delete_store(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        path = "/import_items/{}".format(self.store.pk)
        response = self.client.generic('POST', path, json.dumps(self.json_data))

        path = "/store/{}".format(self.store.pk)
        response = self.client.post(path)

        self.assertEqual(response.status_code, 302)
        items = Item.objects.filter(store=self.store)
        self.assertEqual(items.count(), 0)


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

    def test_GET_redirects_to_store_when_store_exists(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        test_store_name = 'Test Store'
        store = Store.objects.create(name=test_store_name, user=self.user1)
        response = self.client.get("/")

        self.assertEqual(response.status_code, 302)

        path = "/store/{}".format(store.pk)
        self.assertEqual(response.url, path) 

    def test_get_page_title(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_title'], 'Home')

    def test_GET_forms(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['store_name_form'])

    def test_PUT_reverse_to_index(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        response = self.client.put("/")

        self.assertEqual(response.url, "/") 
    
    def test_POST_valid_store_name(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        store_count = Store.objects.count()
        response = self.client.post("/", data={'name':'Test Store'})

        self.assertEqual(response.status_code, 302)

        path = "/store/1"
        self.assertEqual(response.url, path) 
        self.assertEqual(Store.objects.count(), store_count + 1) 

    def test_POST_invalid_store_name(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        test_store_name = 'Test Store'
        store = Store.objects.create(name=test_store_name, user=self.user1)
        store_count = Store.objects.count()
        response = self.client.post("/", data={'name':test_store_name})

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Store.objects.count(), store_count) 
        # check messages!!


    # def test_GET_num_queries_existing_store(self):
    #     logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
    #     store = Store.objects.create(name='Test Store', user=self.user1)
    #     with self.assertNumQueries(3):
    #         response = self.client.get("/")

    # def test_GET_num_queries_no_stores(self):
    #     logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
    #     with self.assertNumQueries(3):
    #         response = self.client.get("/")

   

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