import json
import datetime
from decimal import Decimal
from django.test import Client, TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from stocklist.models import User, Store, Session, List, ListItem, Item


class BaseTestCase(TestCase):

    TEST_USER = 'testuser'
    PASSWORD = '12345'

    @classmethod 
    def setUpTestData(cls):

        cls.user1 = User.objects.create_user(
            username=cls.TEST_USER, email='testuser@test.com', password=cls.PASSWORD)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()


class HomeTestCase(BaseTestCase):
    def test_home_path_redirects_to_login_if_not_logged_in(self):
        response = self.client.get("/home")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/home") 

    def test_home_path_returns_status_200_when_logged_in(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        response = self.client.get("/home")
        self.assertEqual(response.status_code, 200)

    def test_home_path_creates_default_store_if_no_stores_exist(self):
        stores = Store.objects.filter(owner=self.user1)
        self.assertEqual(stores.count(), 0)

        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        response = self.client.get("/home")
        stores = Store.objects.filter(owner=self.user1)
        self.assertEqual(stores.count(), 1)
        self.assertEqual(stores[0].name, 'Stocklist')
        



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
        store = Store.objects.create(name='Test Store', owner=self.user1)
        path = "/store/{}".format(store.pk)
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)

class IndexTestCase(BaseTestCase):
    def test_index_path(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_index_GET_renders_index_html(self):
        logged_in = self.client.login(username=self.TEST_USER, password=self.PASSWORD)
        response = self.client.get("/")
        self.assertEquals(response.templates[0].name, 'stocklist/index.html')

    def test_index_GET_redirects_to_login_when_not_signed_in(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login") 
    

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