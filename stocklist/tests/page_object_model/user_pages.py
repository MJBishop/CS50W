from stocklist.tests.page_object_model.base_page import BasePage
from stocklist.tests.page_object_model.pages import IndexPage
    

class LoginPage(BasePage):
    url = "/login"

    # ELEMENTS:
    USERNAME_ELEM_NAME = 'username'
    PASSWORD_ELEM_NAME = "password"
    ERROR_ELEM_ID = 'error-message'
    INPUT_ELEM_XPATH = '//input[@value="Login"]'

    def set_username(self, uesrname):
        self.fill_form_by_name(self.USERNAME_ELEM_NAME, uesrname)

    def set_password(self, password):
        self.fill_form_by_name(self.PASSWORD_ELEM_NAME, password)
    
    def set_user_data(self, username, password):
        self.set_username(username)
        self.set_password(password)

    def get_errors(self):
        return self.driver.find_element_by_id(self.ERROR_ELEM_ID)

    # success:

    def submit(self):
        self.driver.find_element_by_xpath(self.INPUT_ELEM_XPATH).click()
        return IndexPage(self.driver, self.live_server_url)

    def login_as(self, username, password):
        self.set_user_data(username, password)
        return self.submit()
    # super?

    # failure:

    def submitExpectingFailure(self):
        self.driver.find_element_by_xpath(self.INPUT_ELEM_XPATH).click()
        return LoginPage(self.driver, self.live_server_url)

    def expect_failure_to_login_as(self, username, password):
        self.set_user_data(username, password)
        return self.submitExpectingFailure()



class RegisterPage(LoginPage):
    url = "/register"

    # ELEMENTS:
    EMAIL_ELEM_NAME = 'email'
    CONFIRMATION_ELEM_NAME = "confirmation"
    INPUT_ELEM_XPATH = '//input[@value="Register"]'

    def set_email(self, email):
        self.fill_form_by_name(self.EMAIL_ELEM_NAME, email)

    def set_confirmation(self, confirmation):
        self.fill_form_by_name(self.CONFIRMATION_ELEM_NAME, confirmation)

    def set_user_data(self, username, email, password, confirmation):
        self.set_username(username)
        self.set_email(email)
        self.set_password(password)
        self.set_confirmation(confirmation)

    # success:

    def register_as(self, username, email, password, confirmation):
        self.set_user_data(username, email, password, confirmation)
        return self.submit()

    # failure:

    def submitExpectingFailure(self):
        self.driver.find_element_by_xpath(self.INPUT_ELEM_XPATH).click()
        return RegisterPage(self.driver, self.live_server_url)

    def expect_failure_to_register_as(self, username, email, password, confirmation):
        self.set_user_data(username, email, password, confirmation)
        return self.submitExpectingFailure()
    
