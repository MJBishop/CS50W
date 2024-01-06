from stocklist.tests.page_object_model.base_page import BasePage

from selenium.webdriver.common.by import By


class IndexPage(BasePage):
    url = "/"

    # Elements: 
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

    # elements: 

    LOAD_FILE_FORM_ID = 'import-csv-form'
    LOAD_FILE_INPUT_ID = 'input-file'
    LOAD_FILE_INPUT_XPATH = '//input[@value="Load File"]'
    LOAD_FILE_ERROR_MESSAGE_ELEMENT_ID = 'load-csv-error-message'
    LOAD_FILE_COLUMN_ERROR_MESSAGE = 'CSV File should contain a column of text: Choose another file!'
    LOAD_FILE_HEADER_ERROR_MESSAGE = 'CSV File should contain headers with text: Choose another file!'

    # load csv:

    def get_csv_load_form_locator(self):
        return (By.ID, self.LOAD_FILE_FORM_ID)
    
    def get_csv_load_error_message_locator(self):
        return (By.ID, self.LOAD_FILE_ERROR_MESSAGE_ELEMENT_ID)
    
    def get_csv_load_error_message_text(self):
        return self.driver.find_element(By.ID, self.LOAD_FILE_ERROR_MESSAGE_ELEMENT_ID).text
    
    def set_file_path(self, path):
        self.fill_form_by_id(self.LOAD_FILE_INPUT_ID, path)

    # success:

    def submit(self):
        self.driver.find_element(By.XPATH, self.LOAD_FILE_INPUT_XPATH).click()
        return ImportItemsComponent(self.driver, self.live_server_url)

    def load_file_with_path(self, file_local_path):
        self.set_file_path(file_local_path)
        return self.submit()

    # failure:

    def submitExpectingFailure(self):
        self.driver.find_element(By.XPATH, self.LOAD_FILE_INPUT_XPATH).click()
        return LoadFileComponent(self.driver, self.live_server_url)

    def expect_failure_to_load_file_with_path(self, file_local_path):
        self.set_file_path(file_local_path)
        return self.submitExpectingFailure()


class ImportItemsComponent(StorePage):

    # elements:

    IMPORT_CSV_TABLE_DIV_ID = 'import-csv-table-div'
    IMPORT_CSV_TABLE_COL_SELECT_CLASS = 'import-csv-table-column-select'
    IMPORT_CSV_TABLE_COL_SELECT_ID_PREFIX = 'select_'

    IMPORT_ITEMS_BUTTON_ID = 'import-items-button'
    IMPORT_ITEMS_ERROR_MESSAGE_ELEMENT_ID = 'save-items-error-message'
    IMPORT_ITEMS_COLUMN_ERROR_MESSAGE = 'Select an Item Name column!'

    # select columns to import:

    def get_csv_table_column_select_elements(self):
        return self.driver.find_elements(By.CLASS_NAME, self.IMPORT_CSV_TABLE_COL_SELECT_CLASS)
    
    def get_import_items_button_locator(self):
        return (By.ID, self.IMPORT_ITEMS_BUTTON_ID)

    def get_select_at_col_index(self, index):
        return self.driver.find_element(By.ID, self.IMPORT_CSV_TABLE_COL_SELECT_ID_PREFIX + str(index))
    
    def get_option_for_select_with_value(self, select, value):
        return select.find_element(By.CSS_SELECTOR, "option[value='" + value + "']")

    # save items:

    def get_import_items_error_message_locator(self):
        return (By.ID, self.IMPORT_ITEMS_ERROR_MESSAGE_ELEMENT_ID)
    
    def get_import_items_error_message_text(self):
        return self.driver.find_element(By.ID, self.IMPORT_ITEMS_ERROR_MESSAGE_ELEMENT_ID).text

    # save items success:

    def submit(self):
        self.driver.find_element(By.ID, self.IMPORT_ITEMS_BUTTON_ID).click()
        return ItemsTableComponent(self.driver, self.live_server_url)

    def save_items(self):
        return self.submit()

    # save items failure:

    def submitExpectingFailure(self):
        self.driver.find_element(By.ID, self.IMPORT_ITEMS_BUTTON_ID).click()
        return ImportItemsComponent(self.driver, self.live_server_url)

    def expect_failure_to_save_items(self):
        return self.submitExpectingFailure()
    

class ItemsTableComponent(StorePage):
    
    # elements:
    
    ITEMS_TABLE_VIEW = "table-view"
    ITEMS_TABLE_SELECTED_HEADER_CLASS ='selected'
    ITEMS_TABLE_BODY_ROW_CLASS = "items-table-body-row"
    ITEMS_TABLE_BODY_ID = "items-table-body"

    # table:

    def get_items_table_body_rows(self):
        return self.driver.find_elements(By.CLASS_NAME, self.ITEMS_TABLE_BODY_ROW_CLASS)

    def get_selected_table_header_locator(self):
        return (By.CLASS_NAME, self.ITEMS_TABLE_SELECTED_HEADER_CLASS)
    
    def get_table_cell_innerHTML_at_index_in_table_row(self, column_index, table_row):
        return table_row.find_elements(By.XPATH, "//td")[column_index].get_attribute("innerHTML")
    
    def get_table_header_innerHTML_in_table_row(self, table_row):
        return table_row.find_element(By.TAG_NAME, "th").get_attribute("innerHTML")
    
    # count:

    
class ExportFileComponent(ItemsTableComponent):

    # elements:
    
    EXPORT_CSV_BUTTON_ID = "export-csv-button"
    DOWNLOAD_FILE_LINK_ELEMENT_ID = "export-csv-link"

    #  export csv

    def get_export_csv_button_locator(self):
        return (By.ID, self.EXPORT_CSV_BUTTON_ID)

    def get_download_file_link_locator(self):
        return (By.ID, self.DOWNLOAD_FILE_LINK_ELEMENT_ID)

    # export success:

    def submit_export(self):
        self.driver.find_element(By.ID, self.EXPORT_CSV_BUTTON_ID).click()
        return ExportFileComponent(self.driver, self.live_server_url)
    
    def export_items(self):
        return self.submit_export()
    
    #  download success:

    def submit_download(self):
        self.driver.find_element(By.ID, self.DOWNLOAD_FILE_LINK_ELEMENT_ID).click()
        return DeleteStoreComponent(self.driver, self.live_server_url)
    
    def download_file(self):
        return self.submit_download()

    
class DeleteStoreComponent(ItemsTableComponent):
     
    # elements:
    DELETE_STORE_VIEW_ID = "delete-store-view"
    DELETE_STORE_INPUT_ID = "delete-store-input"
    DELETE_STORE_INPUT_XPATH = '//input[@value="Delete Store"]'
     
    # delete store:

    def get_delete_store_view_locator(self):
        return (By.ID, self.DELETE_STORE_VIEW_ID)

    def get_delete_store_input_locator(self):
        return (By.ID, self.DELETE_STORE_INPUT_ID)

    # success:

    def submit(self):
        self.driver.find_element(By.XPATH, self.DELETE_STORE_INPUT_XPATH).click()
        return IndexPage(self.driver, self.live_server_url)

    def delete_store(self):
        return self.submit()