from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from .models import User, Follow, Post

from selenium.webdriver.chrome.webdriver import WebDriver
chrome_driver_path = '/Users/drinkslist/opt/anaconda3/lib/python3.8/site-packages/chromedriver_py/chromedriver'

# testuser
username = 'testuser'
password = '12345'
# testuser2
username2 = 'testuser2'
password2 = '54321'
email2 = 'testuser@test.com'

# POM
class BasePage(object):
    url = None

    def __init__(self, driver, live_server_url):
        self.driver = driver
        self.live_server_url = live_server_url

    def fill_form_by_css(self, form_css, value):
        elem = self.driver.find(form_css)
        elem.send_keys(value)

    def fill_form_by_id(self, form_element_id, value):
        elem = self.driver.find_element_by_id(form_element_id)
        elem.send_keys(value)

    def fill_form_by_name(self, name, value):
        elem = self.driver.find_element_by_name(name)
        elem.send_keys(value)

    @property
    def title(self):
        return self.driver.title
    
    def navigate(self):
        self.driver.get(
			"{}{}".format(
				self.live_server_url,
				self.url
			)
        )

class LoginPage(BasePage):
    url = "/login"

    # input names
    username = 'username'
    password = "password"

    # input value
    xpath = '//input[@value="Login"]'
    
    # ERRORS_CLASS = 'errorlist'


    def set_username(self, username):
        self.fill_form_by_name(self.username, username)

    def set_password(self, password):
        self.fill_form_by_name(self.password, password)

    # def get_errors(self):
    #     return self.driver.find_element_by_class_name(self.ERRORS_CLASS)

    def submit(self):
        self.driver.find_element_by_xpath(self.xpath).click()
        return IndexPage(self.driver, self.live_server_url)

    def submitExpectingFailure(self):
        self.driver.find_element_by_xpath(self.xpath).click()
        return LoginPage(self.driver, self.live_server_url)


class RegisterPage(LoginPage):
    url = "/register"

    # input names
    email = 'email'
    confirmation = "confirmation"

    # input value
    xpath = '//input[@value="Register"]'


    def set_email(self, email):
        self.fill_form_by_name(self.email, email)

    def set_confirmation(self, confirmation):
        self.fill_form_by_name(self.confirmation, confirmation)

    def submitExpectingFailure(self):
        self.driver.find_element_by_xpath(self.xpath).click()
        return RegisterPage(self.driver, self.live_server_url)


class IndexPage(BasePage):
    pass


# Selenium Tests
class SeleniumTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # create a test user
        user = User.objects.create(username=username)
        user.set_password(password)
        user.save()
        
        # webdriver - chromedriver
        cls.selenium = WebDriver(executable_path=chrome_driver_path)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

class LoginTests(SeleniumTests):

    def test_login(self):

        login_page = LoginPage(self.selenium, self.live_server_url)
        login_page.navigate()

        # check for testuser not in page_source
        assert username not in self.selenium.page_source

        login_page.set_username(username)
        login_page.set_password(password)
        index_page = login_page.submit()

        # check login by finding element on index.html 
        self.selenium.find_element_by_id("page-heading")
        
        # check for testuser in page_source
        assert username in self.selenium.page_source

class RegisterTests(SeleniumTests):

    def test_register(self):

        register_page = RegisterPage(self.selenium, self.live_server_url)
        register_page.navigate()

        # check for testuser2 not in page_source
        assert username2 not in self.selenium.page_source

        register_page.set_username(username2)
        register_page.set_email(email2)
        register_page.set_password(password2)
        register_page.set_confirmation(password2)
        index_page = register_page.submit()

        # check login by finding element on index.html 
        self.selenium.find_element_by_id("page-heading")
        
        # check for testuser2 in page_source
        assert username2 in self.selenium.page_source


    #  test links to these pages?