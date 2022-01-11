from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.exceptions import ValidationError
from .models import User

from selenium.webdriver.chrome.webdriver import WebDriver
local_chrome_driver_path = '/Users/drinkslist/opt/anaconda3/lib/python3.8/site-packages/chromedriver_py/chromedriver'

# testuser
username = 'testuser'
password = '12345'
# testuser2
username2 = 'testuser2'
password2 = '54321'
email2 = 'testuser@test.com'

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
        login_page = LoginPage(self.selenium, self.live_server_url)
        login_page.navigate()
        index_page = login_page.login_as(username, password)
        self.assertIn(username, index_page.get_userid().text)

    def test_login_denies_access(self):
        login_page = LoginPage(self.selenium, self.live_server_url)
        login_page.navigate()
        login_page = login_page.expect_failure_to_login_as('foo', 'bar')
        self.assertIn("Invalid", login_page.get_errors().text)

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

    def test_register_denies_access_for_unmatched_passwords(self):
        
        register_page = RegisterPage(self.selenium, self.live_server_url)
        register_page.navigate()

        # check for testuser2 not in page_source
        assert username2 not in self.selenium.page_source

        register_page.set_username('foo')
        register_page.set_email('foo@bar.com')
        register_page.set_password('foo')
        register_page.set_confirmation('bar')
        register_page = register_page.submitExpectingFailure()
        self.assertIn("Passwords", register_page.get_errors().text)
        
        # check for testuser2 in page_source
        assert username2 not in self.selenium.page_source

    # def test_register_denies_access_for_username_already_taken(self):
        
    #     register_page = RegisterPage(self.selenium, self.live_server_url)
    #     register_page.navigate()

    #     # check for testuser2 not in page_source
    #     assert username2 not in self.selenium.page_source

    #     register_page.set_username(username2)
    #     register_page.set_email(email2)
    #     register_page.set_password(password2)
    #     register_page.set_confirmation(password2)
    #     register_page = register_page.submitExpectingFailure()
    #     self.assertIn("Username", register_page.get_errors().text)
        
    #     # check for testuser2 in page_source
    #     assert username2 not in self.selenium.page_source

    #  test links to these pages?

class IndexTests(SeleniumTests):

    def test_index(self):

        index_page = IndexPage(self.selenium, self.live_server_url)
        index_page.navigate()

        # check login by finding element on index.html 
        self.selenium.find_element_by_id("page-heading")


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

class IndexPage(BasePage):
    url = "/"

    # id
    post_text = 'id_text'
    user_id = 'userid'

    # input value
    xpath = '//input[@value="NewPost"]'

    def get_userid(self):
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


class AllPostsPage(IndexPage):
    pass

    # sign in

    # toggle like
    # edit post

class FollowingPage(IndexPage):
    url = "/following"

class ProfilePage(IndexPage):
    
    def __init__(self, driver, live_server_url, profile_id):
        self.driver = driver
        self.live_server_url = live_server_url
        self.url = '/profile/' + profile_id

    # sign in
    # profile (other user)
    # toggle follow