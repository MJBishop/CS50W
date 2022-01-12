from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.exceptions import ValidationError
from .models import User

from selenium.webdriver.chrome.webdriver import WebDriver
local_chrome_driver_path = '/Users/drinkslist/opt/anaconda3/lib/python3.8/site-packages/chromedriver_py/chromedriver'

# testuser
username = 'testuser'
password = '12345'
email = 'testuser@test.com'
# testuser2
username2 = 'testuser2'
password2 = '54321'
email2 = 'testuser2@test.com'

# Selenium Tests
class SeleniumTests(StaticLiveServerTestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username=username, email=email, password=password)
        
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # webdriver - chromedriver: separate method that can be tested?
        try:
            cls.selenium = WebDriver()
        except:
            try:
                cls.selenium = WebDriver(executable_path=local_chrome_driver_path)
            except Exception as e:
                print(e)
            
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()


class LoginTests(SeleniumTests):

    def test_login(self):
        login_page = LoginPage(self.selenium, self.live_server_url, navigate=True)
        index_page = login_page.login_as(username, password)
        self.assertIn(username, index_page.get_user().text)

    def test_login_denies_access(self):
        login_page = LoginPage(self.selenium, self.live_server_url, navigate=True)
        login_page = login_page.expect_failure_to_login_as('foo', 'bar')
        self.assertIn("Invalid", login_page.get_errors().text)


class RegisterTests(SeleniumTests):
    
    def test_register_success(self):
        register_page = RegisterPage(self.selenium, self.live_server_url, navigate=True)
        index_page = register_page.register_as(username2, email2, password2, password2)
        self.assertIn(username, index_page.get_user().text)

    def test_register_fails_username_exists(self):
        register_page = RegisterPage(self.selenium, self.live_server_url, navigate=True)
        register_page = register_page.expect_failure_to_register_as(username, email, password, password)
        self.assertIn("Username", register_page.get_errors().text)

    def test_register_fails_unmatched_passwords(self):
        register_page = RegisterPage(self.selenium, self.live_server_url, navigate=True)
        register_page = register_page.expect_failure_to_register_as('foo', 'foo@bar.com', 'foo', 'bar')
        self.assertIn("Passwords", register_page.get_errors().text)

        


class IndexTests(SeleniumTests):

    def test_index(self):

        index_page = IndexPage(self.selenium, self.live_server_url)
        index_page.navigate()

        # check login by finding element on index.html 
        self.selenium.find_element_by_id("page-heading")


# POMs
class BasePage(object):
    url = None

    def __init__(self, driver, live_server_url, navigate=False):
        self.driver = driver
        self.live_server_url = live_server_url
        if navigate:
            self.navigate()

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
    
    # error message
    ERROR_CLASS = 'error'


    def set_username(self, username):
        self.fill_form_by_name(self.username, username)

    def set_password(self, password):
        self.fill_form_by_name(self.password, password)

    def get_errors(self):
        return self.driver.find_element_by_class_name(self.ERROR_CLASS)

    def submit(self):
        self.driver.find_element_by_xpath(self.xpath).click()
        return IndexPage(self.driver, self.live_server_url)

    def submitExpectingFailure(self):
        self.driver.find_element_by_xpath(self.xpath).click()
        return LoginPage(self.driver, self.live_server_url)

    def login_as(self, username, password):
        self.set_username(username)
        self.set_password(password)
        return self.submit()

    def expect_failure_to_login_as(self, username, password):
        self.set_username(username)
        self.set_password(password)
        return self.submitExpectingFailure()

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

    def register_as(self, username, email, password, confirmation):
        self.set_username(username)
        self.set_email(email)
        self.set_password(password)
        self.set_confirmation(confirmation)
        return self.submit()

    def expect_failure_to_register_as(self, username, email, password, confirmation):
        self.set_username(username)
        self.set_email(email)
        self.set_password(password)
        self.set_confirmation(confirmation)
        return self.submitExpectingFailure()

class IndexPage(BasePage):
    url = "/"

    # id
    post_text = 'id_text'
    user_id = 'userid'

    # input value
    xpath = '//input[@value="NewPost"]'

    def get_user(self):
        return self.driver.find_element_by_id(self.user_id)

    def set_post_text(self, post_text):
        self.fill_form_by_id(self.post_text, post_text)

    def get_errors(self):
        return self.driver.find_element_by_class_name(self.ERROR_CLASS)

    def submit(self):
        self.driver.find_element_by_xpath(self.xpath).click()
        return ProfilePage(self.driver, self.live_server_url) #profile_id !!

    def submitExpectingFailure(self):
        self.driver.find_element_by_xpath(self.xpath).click()
        return ProfilePage(self.driver, self.live_server_url) #profile_id !!


    # sign in
    # logout
    
    # toggle like
    # edit post

class AllPostsPage(IndexPage):
    pass

class FollowingPage(IndexPage):
    url = "/following"

class ProfilePage(IndexPage):
    
    def __init__(self, driver, live_server_url, profile_id, navigate=False):
        super().__init__(self, driver, live_server_url, navigate)
        self.url = '/profile/' + profile_id

    # sign in
    # profile (other user)
    # toggle follow