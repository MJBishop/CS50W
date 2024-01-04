from stocklist.tests.page_object_model.base_page import BasePage

from selenium.webdriver.common.by import By


class StorePage(BasePage):

    # Elements
    STORE_NAME_ELEMENT_ID = 'store-name-heading'

    def __init__(self, driver, live_server_url, url="/store/1", navigate=False):
        super().__init__(driver, live_server_url, navigate=False)
        self.url = url
        if (navigate):
            self.navigate()

    def get_store_page_heading_text(self):
        return self.driver.find_element(By.ID, self.STORE_NAME_ELEMENT_ID).text
    

class LoadFileComponent(StorePage):

    # Elements: 
    LOAD_FILE_FORM_ID = 'import-csv-form'
    LOAD_FILE_INPUT_ID = 'input-file'
    LOAD_FILE_INPUT_SUBMIT_XPATH = '//input[@value="Load File"]'
    LOAD_FILE_ERROR_MESSAGE_ELEMENT_ID = 'load-csv-error-message'

    # load csv:

    def get_load_csv_form_locator(self):
        return (By.ID, self.LOAD_FILE_FORM_ID)
    
    def get_load_CSV_error_message_text(self):
        return self.driver.find_element(By.ID, self.LOAD_FILE_ERROR_MESSAGE_ELEMENT_ID).text
    
    def set_file_path(self, path):
        self.fill_form_by_id(self.LOAD_FILE_INPUT_ID, path)

    # success:

    def submit(self):
        self.driver.find_element(By.XPATH, self.LOAD_FILE_INPUT_SUBMIT_XPATH).click()
        return ImportItemsComponent(self.driver, self.live_server_url)

    def load_file_with_path(self, file_local_path):
        self.set_file_path(file_local_path)
        return self.submit()

    # failure:

    def submitExpectingFailure(self):
        self.driver.find_element(By.XPATH, self.LOAD_FILE_INPUT_SUBMIT_XPATH).click()
        return LoadFileComponent(self.driver, self.live_server_url)

    def expect_failure_to_load_file_with_path(self, file_local_path):
        self.set_file_path(file_local_path)
        return self.submitExpectingFailure()


class ImportItemsComponent(StorePage):

    # Elements
    IMPORT_CSV_TABLE_DIV_ID = 'import-csv-table-div'
    IMPORT_CSV_TABLE_COL_SELECT_ID = 'import-csv-table-column-select'
    IMPORT_ITEMS_BUTTON_ID = 'import-items-button'


    # select Table columns
    def get_csv_table_column_select_elements(self):
        return self.driver.find_element(By.ID, self.IMPORT_CSV_TABLE_COL_SELECT_ID)
    
    def get_import_items_button_locator(self):
        return (By.ID, self.IMPORT_ITEMS_BUTTON_ID)


class IndexPage(BasePage):
    url = "/"

    # Elements
    STORE_FORM_ELEMENT_ID = 'store-form'
    STORE_NAME_ELEMENT_NAME = 'name'
    ERROR_ELEMENT_ID = 'error-message'
    INPUT_ELEMENT_XPATH = '//input[@value="Save"]'

    def get_errors(self):
        return self.driver.find_element(By.ID, self.ERROR_ELEMENT_ID)
    
    def get_store_name_form(self):
        return self.driver.find_element(By.ID, self.STORE_FORM_ELEMENT_ID)

    def set_store_name(self, store_name):
        self.fill_form_by_name(self.STORE_NAME_ELEMENT_NAME, store_name)

    
    # success:

    def submit(self):
        self.driver.find_element(By.XPATH, self.INPUT_ELEMENT_XPATH).click()
        return LoadFileComponent(self.driver, self.live_server_url)

    def create_store_named_as(self, store_name):
        self.set_store_name(store_name)
        return self.submit()

    # failure:

    def submitExpectingFailure(self):
        self.driver.find_element(By.XPATH, self.INPUT_ELEMENT_XPATH).click()
        return IndexPage(self.driver, self.live_server_url)

    def expect_failure_to_create_store_named_as(self, store_name):
        self.set_store_name(store_name)
        return self.submitExpectingFailure()
    

    