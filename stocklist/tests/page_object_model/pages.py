from stocklist.tests.page_object_model.base_page import BasePage

class IndexPage(BasePage):
    url = "/"

    # Elements
    STORE_FORM_ELEMENT_ID = 'store-form'

    # 
    def get_store_form(self):
        return self.driver.find_element_by_id(self.STORE_FORM_ELEMENT_ID)