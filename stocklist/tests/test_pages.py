from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.firefox.options import Options
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
        # print(cls.driver.get_window_size())

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


class BaseImportTests(BaseTests):

    # Test Files
    TEST_FILE_FOLDER = '/csv_test_files/'
    STRINGS_AND_NUMBERS_FILE = 'strings_and_numbers.csv'
    NO_STRINGS_FILE = 'no_strings.csv'
    NO_HEADERS_FILE = 'no_headers.csv'
    MULTIPLE_NAME_COLUMNS_FILE = 'multiple_name_columns.csv'

    def setUp(self):
        super().setUp()

        self.login_page = LoginPage(self.driver, self.live_server_url, navigate=True)
        self.index_page = self.login_page.login_as(self.USERNAME, self.PASSWORD)
        self.load_file_component = self.index_page.create_store_named_as(self.TEST_STORE_NAME)
        self.dir_path = os.path.dirname(os.path.abspath(__file__))  # print(dir_path)


class LoadFileTests(BaseImportTests):

    def setUp(self):
        super().setUp()

        # wait for form
        form_locator = self.load_file_component.get_csv_load_form_locator()
        WebDriverWait(self.driver, timeout=10).until(
            expected_conditions.presence_of_element_located(form_locator)
        )

    def test_load_file_success(self):
        file_to_test = self.TEST_FILE_FOLDER + self.STRINGS_AND_NUMBERS_FILE
        local_file_path = self.dir_path + file_to_test
        self.import_items_component = self.load_file_component.load_file_with_path(local_file_path)

        # wait for import items button
        import_items_button_locator = self.import_items_component.get_import_items_button_locator()
        WebDriverWait(self.driver, timeout=10).until(
            expected_conditions.presence_of_element_located(import_items_button_locator)
        )
        self.assertTrue(self.import_items_component.get_csv_table_column_select_elements())

    def test_load_file_error_no_column_of_strings_detected(self):
        file_to_test = self.TEST_FILE_FOLDER + self.NO_STRINGS_FILE
        local_file_path = self.dir_path + file_to_test
        self.load_file_component = self.load_file_component.expect_failure_to_load_file_with_path(local_file_path)

        # wait for error message
        load_file_error_message_locator = self.load_file_component.get_csv_load_error_message_locator()
        WebDriverWait(self.driver, timeout=10).until(
            expected_conditions.presence_of_element_located(load_file_error_message_locator)
        )
        self.assertEqual(self.load_file_component.get_csv_load_error_message_text(), self.load_file_component.LOAD_FILE_COLUMN_ERROR_MESSAGE)

    def test_load_file_fail_no_header_row(self):
        file_to_test = self.TEST_FILE_FOLDER + self.NO_HEADERS_FILE
        local_file_path = self.dir_path + file_to_test
        self.load_file_component = self.load_file_component.expect_failure_to_load_file_with_path(local_file_path)

        # wait for error message
        load_file_error_message_locator = self.load_file_component.get_csv_load_error_message_locator()
        WebDriverWait(self.driver, timeout=10).until(
            expected_conditions.presence_of_element_located(load_file_error_message_locator)
        )
        self.assertEqual(self.load_file_component.get_csv_load_error_message_text(), self.load_file_component.LOAD_FILE_HEADER_ERROR_MESSAGE)
        

class BaseSelectColumnTests(BaseImportTests):

    def setUp(self):
        super().setUp()

        file_to_test = self.TEST_FILE_FOLDER + self.MULTIPLE_NAME_COLUMNS_FILE
        local_file_path = self.dir_path + file_to_test
        self.import_items_component = self.load_file_component.load_file_with_path(local_file_path)

        # wait for import items button
        import_items_button_locator = self.import_items_component.get_import_items_button_locator()
        WebDriverWait(self.driver, timeout=10).until(
            expected_conditions.presence_of_element_located(import_items_button_locator)
        )


class SelectTableColumnTests(BaseSelectColumnTests):

    def setUp(self):
        super().setUp()

    def test_table_column_select_options_for_type_string(self):
        select_element = self.import_items_component.get_select_at_col_index(0)
        ignore_element = self.import_items_component.get_option_for_select_with_value(select_element, '0')
        item_name_element = self.import_items_component.get_option_for_select_with_value(select_element, '1')

        select = Select(select_element)
        option_list = select.options
        expected_options = [ignore_element, item_name_element]
        self.assertEqual(option_list, expected_options)

        selected_option_list = select.all_selected_options
        expected_selection = [ignore_element]
        self.assertEqual(selected_option_list, expected_selection)

        select.select_by_index(1)
        self.assertTrue(item_name_element.is_selected)

        select.select_by_index(0)
        self.assertTrue(ignore_element.is_selected)

    def test_table_column_select_options_for_type_number(self):
        select_element = self.import_items_component.get_select_at_col_index(2)
        ignore_element = self.import_items_component.get_option_for_select_with_value(select_element, '0')
        item_name_element = self.import_items_component.get_option_for_select_with_value(select_element, '1')
        item_quantity_element = self.import_items_component.get_option_for_select_with_value(select_element, '2')

        select = Select(select_element)
        option_list = select.options
        expected_options = [ignore_element, item_name_element, item_quantity_element]
        self.assertEqual(option_list, expected_options)

        selected_option_list = select.all_selected_options
        expected_selection = [ignore_element]
        self.assertEqual(selected_option_list, expected_selection)

        select.select_by_index(1)
        self.assertTrue(item_name_element.is_selected)

        select.select_by_index(0)
        self.assertTrue(ignore_element.is_selected)

        select.select_by_index(1)
        self.assertTrue(item_quantity_element.is_selected)

    def test_table_column_select_options_for_type_other(self):
        select_element = self.import_items_component.get_select_at_col_index(4)
        ignore_element = self.import_items_component.get_option_for_select_with_value(select_element, '0')

        select = Select(select_element)
        option_list = select.options
        expected_options = [ignore_element]
        self.assertEqual(option_list, expected_options)

        selected_option_list = select.all_selected_options
        expected_selection = [ignore_element]
        self.assertEqual(selected_option_list, expected_selection)

    def test_table_column_select_options_for_multiple_type_number(self):
        first_select_element = self.import_items_component.get_select_at_col_index(2)
        first_item_quantity_element = self.import_items_component.get_option_for_select_with_value(first_select_element, '2')
        second_select_element = self.import_items_component.get_select_at_col_index(3)
        second_item_quantity_element = self.import_items_component.get_option_for_select_with_value(second_select_element, '2')
        second_ignore_element = self.import_items_component.get_option_for_select_with_value(second_select_element, '0')

        first_select = Select(first_select_element)
        second_select = Select(second_select_element)

        # select first item quantity
        first_select.select_by_index(2)
        self.assertTrue(first_item_quantity_element.is_selected)
        # second item quantity is disabled - no change
        second_select.select_by_index(2)
        second_selected_option_list = second_select.all_selected_options
        expected_selection = [second_ignore_element]
        self.assertEqual(second_selected_option_list, expected_selection)

        # deselect first item quantity
        first_select.select_by_index(0)
        # second item quantity can be selected
        second_select.select_by_index(2)
        second_selected_option_list = second_select.all_selected_options
        expected_selection = [second_item_quantity_element]
        self.assertEqual(second_selected_option_list, expected_selection)

    def test_table_column_select_options_for_multiple_type_string(self):
        first_select_element = self.import_items_component.get_select_at_col_index(0)
        first_item_name_element = self.import_items_component.get_option_for_select_with_value(first_select_element, '1')
        second_select_element = self.import_items_component.get_select_at_col_index(1)
        second_item_name_element = self.import_items_component.get_option_for_select_with_value(second_select_element, '1')

        first_select = Select(first_select_element)
        second_select = Select(second_select_element)

        # select first item name
        first_select.select_by_index(1)
        self.assertTrue(first_item_name_element.is_selected)
        # second item quantity is disabled - no change
        second_select.select_by_index(1)
        self.assertTrue(second_item_name_element.is_selected)


class ImportItemsTests(BaseSelectColumnTests):

    def setUp(self):
        super().setUp()

    def test_save_items_fail_no_columns_selected(self):
        import_items_component = self.import_items_component.expect_failure_to_save_items()

        # wait for error message
        import_items_error_message_locator = import_items_component.get_import_items_error_message_locator()
        WebDriverWait(self.driver, timeout=10).until(
            expected_conditions.presence_of_element_located(import_items_error_message_locator)
        )
        self.assertEqual(import_items_component.get_import_items_error_message_text(), import_items_component.IMPORT_ITEMS_COLUMN_ERROR_MESSAGE)

    def test_save_items_success_item_name_selected(self):
        select_element = self.import_items_component.get_select_at_col_index(0)

        # select an item name column 
        select = Select(select_element)
        select.select_by_index(1)
        items_table_component = self.import_items_component.save_items()

        # wait for items table selected header
        selected_table_header_locator = items_table_component.get_selected_table_header_locator()
        WebDriverWait(self.driver, timeout=10).until(
            expected_conditions.presence_of_element_located(selected_table_header_locator)
        )
        self.assertTrue(items_table_component.get_items_table_body_rows())

    def test_save_items_success_item_name_and_amount(self):
        name_select_element = self.import_items_component.get_select_at_col_index(0)
        amount_select_element = self.import_items_component.get_select_at_col_index(2)

        # select an item name column 
        name_select = Select(name_select_element)
        name_select.select_by_index(1)
        # select an item amount column 
        amount_select = Select(amount_select_element)
        amount_select.select_by_index(2)

        items_table_component = self.import_items_component.save_items()

        # wait for items table selected header
        selected_table_header_locator = items_table_component.get_selected_table_header_locator()
        WebDriverWait(self.driver, timeout=10).until(
            expected_conditions.presence_of_element_located(selected_table_header_locator)
        )
        table_body_row_elements = items_table_component.get_items_table_body_rows()
        first_table_row = table_body_row_elements[0]
        first_cell_innerHTML = items_table_component.get_table_cell_innerHTML_at_index_in_table_row(0, first_table_row)
        self.assertEqual(first_cell_innerHTML, '10')

    def test_save_items_success_item_name_from_multiple_columns(self):
        name_select_element_1 = self.import_items_component.get_select_at_col_index(0)
        name_select_element_2 = self.import_items_component.get_select_at_col_index(1)

        # select an item name column 
        name_select = Select(name_select_element_1)
        name_select.select_by_index(1)
        # select an item amount column 
        amount_select = Select(name_select_element_2)
        amount_select.select_by_index(1)

        items_table_component = self.import_items_component.save_items()

        # wait for items table selected header
        selected_table_header_locator = items_table_component.get_selected_table_header_locator()
        WebDriverWait(self.driver, timeout=10).until(
            expected_conditions.presence_of_element_located(selected_table_header_locator)
        )
        table_body_row_elements = items_table_component.get_items_table_body_rows()
        first_table_row = table_body_row_elements[0]
        row_header_innerHTML = items_table_component.get_table_header_innerHTML_in_table_row(first_table_row)
        self.assertEqual(row_header_innerHTML, 'Vodka 70cl')
    


class BaseFixtureTests(SeleniumTests):
    fixtures = ['db.json']

    USERNAME = "bishop"
    PASSWORD = "36tnJ.PO"

    def setUp(self):
        super().setUp()

        self.login_page = LoginPage(self.driver, self.live_server_url, navigate=True)
        self.index_page = self.login_page.login_as(self.USERNAME, self.PASSWORD)
        

class CountItemsTests(BaseFixtureTests):

    def setUp(self):
        super().setUp()
        
        self.items_table_component = ItemsTableComponent(self.driver, self.live_server_url)

        # wait for items table selected header
        selected_table_header_locator = self.items_table_component.get_selected_table_header_locator()
        WebDriverWait(self.driver, timeout=10).until(
            expected_conditions.presence_of_element_located(selected_table_header_locator)
        )

    def test_fixtures_ok(self):
        pass
        self.assertTrue(self.items_table_component.get_items_table_body_rows())


class ExportFileTests(BaseFixtureTests):

    def setUp(self):
        super().setUp()

        self.export_file_component = ExportFileComponent(self.driver, self.live_server_url)

        # wait for export button
        export_csv_button_locator = self.export_file_component.get_export_csv_button_locator()
        export_csv_button = WebDriverWait(self.driver, timeout=10).until(
            expected_conditions.element_to_be_clickable(export_csv_button_locator)
        )

    def test_export_file(self):
        self.export_file_component = self.export_file_component.export_items()

        # wait for download link
        download_file_link_locator = self.export_file_component.get_download_file_link_locator()
        WebDriverWait(self.driver, timeout=10).until(
            expected_conditions.presence_of_element_located(download_file_link_locator)
        )
        delete_store_component = self.export_file_component.download_file()

        # wait for delete store view
        delete_store_view_locator = delete_store_component.get_delete_store_view_locator()
        WebDriverWait(self.driver, timeout=10).until(
            expected_conditions.presence_of_element_located(delete_store_view_locator)
        )
        self.assertTrue(delete_store_component.get_delete_store_input_locator())


class DeleteStoreTests(BaseFixtureTests):

    def setUp(self):
        super().setUp()

        self.delete_store_component = DeleteStoreComponent(self.driver, self.live_server_url)

        # wait for delete store view
        delete_store_view_locator = self.delete_store_component.get_delete_store_view_locator()
        WebDriverWait(self.driver, timeout=10).until(
            expected_conditions.element_to_be_clickable(delete_store_view_locator)
        )

    def test_delete_store(self):
        index_page = self.delete_store_component.delete_store()
        self.assertTrue(index_page.get_store_name_form())

