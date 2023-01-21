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
        cls.user1.save()

    def setUp(self):
        # Every test needs a client.
        self.client = Client()


class IndexTestCase(BaseTestCase):
    def test_index_path(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_index_GET_renders_index_html(self):
        response = self.client.get("/")
        self.assertEquals(response.templates[0].name, 'stocklist/index.html')
    


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