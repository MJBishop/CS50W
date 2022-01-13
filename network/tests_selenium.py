from typing import get_args
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from .models import User

from selenium.webdriver.chrome.webdriver import WebDriver
local_chrome_driver_path = '/Users/drinkslist/opt/anaconda3/lib/python3.8/site-packages/chromedriver_py/chromedriver'
from selenium.common.exceptions import NoSuchElementException

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

class AnnonymousLayoutTests(SeleniumTests):

    def setUp(self):
        super().setUp()

        self.index_page = AllPostsPage(self.selenium, self.live_server_url, navigate=True)

    def test_allposts_heading(self):
        self.assertIn("All Posts", self.index_page.get_heading().text)

    def test_allposts(self):
        all_posts_page = self.index_page.click_allposts()
        self.assertIn("All Posts", self.index_page.get_heading().text)

    def test_following(self):
        self.assertRaises(NoSuchElementException, self.index_page.click_following)

    def test_profile(self):
        self.assertRaises(NoSuchElementException, self.index_page.click_profile)

    def test_register(self):
        register_page = self.index_page.click_register()
        self.assertIn("Register", self.selenium.page_source)

    def test_login(self):
        login_page = self.index_page.click_login()
        self.assertIn("Log In", self.selenium.page_source)

    def test_logout(self):
        self.assertRaises(NoSuchElementException, self.index_page.click_logout)


class LoginTests(SeleniumTests):

    def test_login_success(self):
        login_page = LoginPage(self.selenium, self.live_server_url, navigate=True)
        index_page = login_page.login_as(username, password)
        self.assertIn(username, index_page.get_user().text)

    def test_login_fail(self):
        login_page = LoginPage(self.selenium, self.live_server_url, navigate=True)
        login_page = login_page.expect_failure_to_login_as('foo', 'bar')
        self.assertIn("Invalid", login_page.get_errors().text)


class RegisterTests(SeleniumTests):

    def test_register_success(self):
        register_page = RegisterPage(self.selenium, self.live_server_url, navigate=True)
        index_page = register_page.register_as(username2, email2, password2, password2)
        self.assertIn(username, index_page.get_user().text)

    def test_register_fail_username_exists(self):
        register_page = RegisterPage(self.selenium, self.live_server_url, navigate=True)
        register_page = register_page.expect_failure_to_register_as(username, email, password, password)
        self.assertIn("Username", register_page.get_errors().text)

    def test_register_fail_unmatched_passwords(self):
        register_page = RegisterPage(self.selenium, self.live_server_url, navigate=True)
        register_page = register_page.expect_failure_to_register_as('foo', 'foo@bar.com', 'foo', 'bar')
        self.assertIn("Passwords", register_page.get_errors().text)


class LayoutTests(SeleniumTests):

    def setUp(self):
        super().setUp()

        login_page = LoginPage(self.selenium, self.live_server_url, navigate=True)
        self.index_page = login_page.login_as(username, password)

    def test_allposts_heading(self):
        self.assertIn("All Posts", self.index_page.get_heading().text)

    def test_allposts(self):
        all_posts_page = self.index_page.click_allposts()
        self.assertIn("All Posts", self.index_page.get_heading().text)

    def test_following(self):
        following_page = self.index_page.click_following()
        self.assertIn("Following", following_page.get_heading().text)

    def test_profile(self):
        profile_page = self.index_page.click_profile()
        self.assertIn(username, profile_page.get_heading().text)

    def test_register(self):
        self.assertRaises(NoSuchElementException, self.index_page.click_register)

    def test_login(self):
        self.assertRaises(NoSuchElementException, self.index_page.click_login)

    def test_logout(self):
        index_page = self.index_page.click_logout()
        self.assertIn("All Posts", self.index_page.get_heading().text) #?


class NewPostTests(SeleniumTests):

    def setUp(self):
        super().setUp()

        login_page = LoginPage(self.selenium, self.live_server_url, navigate=True)
        self.index_page = login_page.login_as(username, password)
    
    def test_post_success(self):
        string_to_test = "Hello World!"
        profile_page = self.index_page.post_text(string_to_test)
        self.assertIn(string_to_test, self.selenium.page_source)


class IndexTests(SeleniumTests):

    def test_allposts(self):
        index_page = IndexPage(self.selenium, self.live_server_url, navigate=True)
        self.assertIn("All Posts", index_page.get_heading().text)

# class FollowingTests(SeleniumTests):

    

# class ProfileTests(SeleniumTests):

    


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


class LayoutTemplate(BasePage):
    url = "/"

    # ELEMENTS:
    HEADING_ELEM_ID = 'post-list-heading'
    USERID_ELEM_ID = 'userid'
    ALLPOSTS_LINK_TEXT = 'All Posts'
    FOLLOWING_LINK_TEXT = 'Following'
    PROFILE_LINK_TEXT = username
    LOGIN_LINK_TEXT = 'Log In' 
    REGISTER_LINK_TEXT = 'Register' 
    LOGOUT_LINK_TEXT = 'Log Out' 

    def get_heading(self):
        return self.driver.find_element_by_id(self.HEADING_ELEM_ID)

    def get_user(self):
        return self.driver.find_element_by_id(self.USERID_ELEM_ID)

    def click_allposts(self):
        self.driver.find_element_by_link_text(self.ALLPOSTS_LINK_TEXT).click()
        return AllPostsPage(self.driver, self.live_server_url)

    def click_following(self):
        self.driver.find_element_by_link_text(self.FOLLOWING_LINK_TEXT).click()
        return FollowingPage(self.driver, self.live_server_url)

    def click_profile(self):
        self.driver.find_element_by_link_text(self.PROFILE_LINK_TEXT).click()
        return ProfilePage(self.driver, self.live_server_url)

    def click_login(self):
        self.driver.find_element_by_link_text(self.LOGIN_LINK_TEXT).click()
        return LoginPage(self.driver, self.live_server_url)

    def click_register(self):
        self.driver.find_element_by_link_text(self.REGISTER_LINK_TEXT).click()
        return RegisterPage(self.driver, self.live_server_url)

    def click_logout(self):
        self.driver.find_element_by_link_text(self.LOGOUT_LINK_TEXT).click()
        return AllPostsPage(self.driver, self.live_server_url)


class LoginPage(LayoutTemplate):
    url = "/login"

    # ELEMENTS:
    USERNAME_ELEM_NAME = 'username'
    PASSWORD_ELEM_NAME = "password"
    ERROR_ELEM_ID = 'error-message'
    INPUT_ELEM_XPATH = '//input[@value="Login"]'


    def set_username(self, username):
        self.fill_form_by_name(self.USERNAME_ELEM_NAME, username)

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


class NewPostTemplate(LayoutTemplate):
    
    # ELEMENTS:
    POST_TEXTAREA_ELEM_ID = 'id_text'
    INPUT_ELEM_XPATH = '//input[@value="NewPost"]'

    def set_post_text(self, post_text):
        self.fill_form_by_id(self.POST_TEXTAREA_ELEM_ID, post_text)


    # success:

    def submit(self):
        self.driver.find_element_by_xpath(self.INPUT_ELEM_XPATH).click()
        return ProfilePage(self.driver, self.live_server_url) #profile_id !!

    def post_text(self, text):
        self.set_post_text(text)
        return self.submit()


    # failure:

    def submitExpectingFailure(self):
        self.driver.find_element_by_xpath(self.INPUT_ELEM_XPATH).click()
        return ProfilePage(self.driver, self.live_server_url) #profile_id !!

    def expect_failure_to_post_text(self, text):
        self.set_post_text(text)
        return self.submitExpectingFailure()



class IndexPage(NewPostTemplate):
    url = "/"


    
    # toggle like
    # edit post


class AllPostsPage(IndexPage):
    url = "/"



    


class FollowingPage(IndexPage):
    url = "/following"


class ProfilePage(IndexPage):
    url = "/profile/1"

    
    # def __init__(self, driver, live_server_url, pro, navigate=False):
    #     super().__init__(self, driver, live_server_url, navigate)
    #     self.url = '/profile/' + profile_id

    # sign in
    # profile (other user)
    # toggle follow