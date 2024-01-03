from stocklist.tests.page_object_model.base_page import BasePage

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import text_to_be_present_in_element, presence_of_element_located, invisibility_of_element


class StorePage(BasePage):

    # Elements
    STORE_NAME_ELEMENT_ID = 'store-name-heading'
    IMPORT_CSV_FORM_ID = 'import-csv-form'

    def __init__(self, driver, live_server_url, url="/store/1", navigate=False):
        super().__init__(driver, live_server_url, navigate=False)
        self.url = url
        if (navigate):
            self.navigate()

    def get_store_page_heading_text(self):
        return self.driver.find_element(By.ID, self.STORE_NAME_ELEMENT_ID).text

    def get_import_items_form(self):
        return self.driver.find_element(By.ID, self.IMPORT_CSV_FORM_ID)


class IndexPage(BasePage):
    url = "/"

    # Elements
    STORE_FORM_ELEMENT_ID = 'store-form'
    STORE_NAME_ELEMENT_NAME = 'name'
    ERROR_ELEMENT_ID = 'error-message'
    INPUT_ELEMENT_XPATH = '//input[@value="Save"]'

    
    def set_store_name(self, store_name):
        self.fill_form_by_name(self.STORE_NAME_ELEMENT_NAME, store_name)

    def get_errors(self):
        return self.driver.find_element(By.ID, self.ERROR_ELEMENT_ID)
    
    def get_store_name_form(self):
        return self.driver.find_element(By.ID, self.STORE_FORM_ELEMENT_ID)
    
    # success:

    def submit(self):
        self.driver.find_element(By.XPATH, self.INPUT_ELEMENT_XPATH).click()
        return StorePage(self.driver, self.live_server_url)

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
    

    