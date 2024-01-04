from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.chrome.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.common.by import By
import os

from stocklist.models import User
from stocklist.tests.page_object_model.user_pages import RegisterPage, LoginPage
from stocklist.tests.page_object_model.pages import IndexPage



class SeleniumTests(StaticLiveServerTestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        #  Set Up Driver
        cls.driver = webdriver.Firefox()
        cls.driver.maximize_window()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()


class BaseTests(SeleniumTests):

    # testuser 
    USERNAME = 'testuser'
    PASSWORD = '12345'
    EMAIL = 'testuser@test.com'
    TEST_STORE_NAME = 'Test Store'

    def setUp(self):
        super().setUp()

        self.user = User.objects.create_user(
            username=self.USERNAME, email=self.EMAIL, password=self.PASSWORD)
        
    def tearDown(self):
        super().tearDown()


class RegisterTests(BaseTests):

    def setUp(self):
        super().setUp()

        self.register_page = RegisterPage(self.driver, self.live_server_url, navigate=True)

    def test_register_success(self):
        index_page = self.register_page.register_as('foo', 'foo@bar.com', 'bar', 'bar')
        self.assertTrue(index_page.get_store_name_form())

    def test_register_fail_username_exists(self):
        register_page = self.register_page.expect_failure_to_register_as(self.USERNAME, self.EMAIL, self.PASSWORD, self.PASSWORD)
        self.assertIn("Username", register_page.get_errors().text)

    def test_register_fail_unmatched_passwords(self):
        register_page = self.register_page.expect_failure_to_register_as('foo', 'foo@bar.com', 'foo', 'bar')
        self.assertIn("Passwords", register_page.get_errors().text)


class LoginTests(BaseTests):

    def setUp(self):
        super().setUp()

        self.login_page = LoginPage(self.driver, self.live_server_url, navigate=True)

    def test_login_success(self):
        index_page = self.login_page.login_as(self.USERNAME, self.PASSWORD)
        self.assertTrue(index_page.get_store_name_form())

    def test_login_fail(self):
        login_page = self.login_page.expect_failure_to_login_as('foo', 'bar')
        self.assertIn("Invalid", login_page.get_errors().text)

    
class IndexTests(BaseTests):

    def setUp(self):
        super().setUp()

        self.login_page = LoginPage(self.driver, self.live_server_url, navigate=True)
        self.index_page = self.login_page.login_as(self.USERNAME, self.PASSWORD)

    def test_index(self):
        self.assertTrue(self.index_page.get_store_name_form())

    def test_set_store_name_success(self):
        store_page = self.index_page.create_store_named_as(self.TEST_STORE_NAME)
        self.assertEqual(store_page.get_store_page_heading_text(), self.TEST_STORE_NAME)

    def test_set_store_name_fail_store_name_exists(self):
        pass
        # only one store per user


class ImportItemsTests(BaseTests):

    def setUp(self):
        super().setUp()

        self.login_page = LoginPage(self.driver, self.live_server_url, navigate=True)
        self.index_page = self.login_page.login_as(self.USERNAME, self.PASSWORD)
        self.store_page = self.index_page.create_store_named_as(self.TEST_STORE_NAME)

    def test_store_page_store_name(self):
        heading_text = self.store_page.get_store_page_heading_text()
        self.assertTrue(heading_text, self.TEST_STORE_NAME)

    def test_store_page_file_form(self):
        WebDriverWait(self.driver, timeout=10).until(
            EC.text_to_be_present_in_element((By.ID, "form-label"), "Select a CSV File:")
        )
        self.assertTrue(self.store_page.get_import_items_form())

    def test_load_file_success(self):
        WebDriverWait(self.driver, timeout=10).until(
            EC.presence_of_element_located((By.ID, 'import-csv-form'))
        )

        file_to_test = '/csv_test_files/item_amount.csv'
        dir_path = os.path.dirname(os.path.abspath(__file__))  # print(dir_path)
        local_file_path = dir_path + file_to_test
        self.store_page = self.store_page.load_file_with_path(local_file_path)

        WebDriverWait(self.driver, timeout=10).until(
            EC.presence_of_element_located((By.ID, 'import-csv-table-column-select'))
        )
        self.assertTrue(self.store_page.get_csv_table_selects())

        


class BaseStoreTests(BaseTests):
    fixtures = ['test_data.json']

    def setUp(self):
        super().setUp()
        
        self.login_page = LoginPage(self.driver, self.live_server_url, navigate=True)
        self.index_page = self.login_page.login_as(self.USERNAME, self.PASSWORD)
        # self.store_page = 


# class StoreTests(BaseStoreTests):

#     def setUp(self):
#         super().setUp()
        