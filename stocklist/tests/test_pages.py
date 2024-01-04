from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
import os

from stocklist.models import User
from stocklist.tests.page_object_model.user_pages import RegisterPage, LoginPage
from stocklist.tests.page_object_model.pages import *



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


class LoadCSVFileTests(BaseTests):
    
    # Test Files
    TEST_FILE_FOLDER = '/csv_test_files/'
    STRINGS_AND_NUMBERS_FILE = 'strings_and_numbers.csv'
    NO_STRINGS_FILE = 'no_strings.csv'


    def setUp(self):
        super().setUp()

        self.login_page = LoginPage(self.driver, self.live_server_url, navigate=True)
        self.index_page = self.login_page.login_as(self.USERNAME, self.PASSWORD)
        self.store_page = self.index_page.create_store_named_as(self.TEST_STORE_NAME)

    def test_store_page_store_name(self):
        heading_text = self.store_page.get_store_page_heading_text()
        self.assertTrue(heading_text, self.TEST_STORE_NAME)

    def test_load_file_success(self):
        form_locator = self.store_page.get_csv_load_form_locator()
        WebDriverWait(self.driver, timeout=10).until(
            expected_conditions.presence_of_element_located(form_locator)
        )

        # load local file
        file_to_test = self.TEST_FILE_FOLDER + self.STRINGS_AND_NUMBERS_FILE
        dir_path = os.path.dirname(os.path.abspath(__file__))  # print(dir_path)
        local_file_path = dir_path + file_to_test
        self.store_page = self.store_page.load_file_with_path(local_file_path)

        # wait for 
        import_items_button_locator = self.store_page.get_import_items_button_locator()
        WebDriverWait(self.driver, timeout=10).until(
            expected_conditions.presence_of_element_located(import_items_button_locator)
        )
        self.assertTrue(self.store_page.get_csv_table_column_select_elements())


    # test_load_file_error_no_column_of_strings_detected(self):
    # test_load_file_fail_no_header_row(self):
        

# class ImportItemsTests(LoadCSVFileTests):
    # test_table_column_select_options_for_type_string(self):
    # test_table_column_select_options_for_type_ynumber(self):
    # test_table_column_select_options_for_type_other(self):
        
    # test_save_items_fail_no_columns_selected(self):
    # test_save_items_success_item_name_column(self):
    # test_save_items_succes_item_name_and_amount(self);
    # test_save_items_succes_item_name_from_multiple_columns(self);
    


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
        