import json
from django.test import Client, TestCase
from django.core.exceptions import ValidationError

from .models import User, Follow, Post
from .views import NewPostForm

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.chrome.webdriver import WebDriver

chrome_driver_path = '/Users/drinkslist/opt/anaconda3/lib/python3.8/site-packages/chromedriver_py/chromedriver'

class SeleniumTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # create a test user
        user = User.objects.create(username='testuser')
        user.set_password('12345')
        user.save()
        
        # webdriver - chromedriver
        cls.selenium = WebDriver(executable_path=chrome_driver_path)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/login'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('testuser')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('12345')
        self.selenium.find_element_by_xpath('//input[@value="Login"]').click()
        # check login by finding element on index.html 
        self.selenium.find_element_by_id("page-heading")


# Create your tests here.
class ViewsTestCase(TestCase):
    def setUp(self):
        # create a test user
        user = User.objects.create(username='testuser')
        user.set_password('12345')
        user.save()

        # create another test user
        user2 = User.objects.create(username='testuser2')
        user2.set_password('54321')
        user2.save()

    # NewPostForm
    def test_valid_newpost_form_data(self):
        form = NewPostForm({
            'text': "Hello World!",
        })
        self.assertTrue(form.is_valid())
        post_text = form.cleaned_data["text"]
        self.assertEqual(post_text, "Hello World!")

    def test_blank_newpost_form_data(self):
        form = NewPostForm({
            'text': "",
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'text': ['This field is required.'],
        })

    # index tests
    def test_index(self):
        c = Client()

        response = c.get("/")
        # print(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.num_pages, 1)
        self.assertEqual(response.context['page_obj'].object_list.count(), 0)

    # def test_POST_new_post_to_index(self):
    #     c = Client()
    #     logged_in = c.login(username='testuser', password='12345')

    #     response = c.post("/", data={"text": "Hello World!"})
    #     # print(response)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.context['page_obj'].paginator.num_pages, 1)
    #     self.assertEqual(response.context['page_obj'].object_list.count(), 1)


    def test_following_PUT_reverse_to_index(self):
        c = Client()

        response = c.put("/following")
        # print(response)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/following") 

    def test_following(self):
        c = Client()
        logged_in = c.login(username='testuser', password='12345')

        response = c.get('/following')
        # print(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.num_pages, 1)
        self.assertEqual(response.context['page_obj'].object_list.count(), 0)

    def test_following_redirects_when_not_signed_in(self):
        c = Client()

        response = c.get('/following')
        # print(response)
        self.assertEqual(response.status_code, 302)

    # def test_POST_new_post_form_to_following(self):

    def test_profile(self):
        c = Client()
        logged_in = c.login(username='testuser', password='12345')
        username = 'testuser2'
        u2 = User.objects.get(username=username)

        user_id = str(u2.id)
        path = '/profile/' + user_id
        response = c.get(path)
        # print(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.num_pages, 1)
        self.assertEqual(response.context['page_obj'].object_list.count(), 0)
        self.assertEqual(response.context['profile'].username, username)

    def test_profile_raises_404_exception_for_invalid_user(self):
        c = Client()
        logged_in = c.login(username='testuser', password='12345')

        user_id = '100'
        path = '/profile/' + user_id
        response = c.generic('GET', path)
        # print(response)
        self.assertEqual(response.status_code, 404)

    def test_profile_PUT_POST_DELETE_reverse_to_index(self):
        c = Client()
        logged_in = c.login(username='testuser', password='12345')
        username = 'testuser2'
        u2 = User.objects.get(username=username)

        user_id = str(u2.id)
        path = '/profile/' + user_id
        
        response = c.put(path)
        # print(response)
        self.assertEqual(response.status_code, 302)

        response = c.delete(path)
        # print(response)
        self.assertEqual(response.status_code, 302)

        response = c.post(path)
        # print(response)
        self.assertEqual(response.status_code, 302)

    # def test_POST_new_post_form_to_profile(self):
        

    # new_post
    

    # def test_new_post(self):
    #     c = Client()
    #     logged_in = c.login(username='testuser', password='12345')

    #     response = c.generic('POST', '/post', json.dumps({"text":"New Post Test Text!!"}))
    #     # print(response)
    #     self.assertEqual(response.status_code, 201)

    #     u1 = User.objects.get(username='testuser')
    #     self.assertEqual(u1.posts.count(), 1)

    

    def test_new_post_redirects_when_not_signed_in(self):
        c = Client()

        response = c.generic('POST', '/post', json.dumps({"text":"New Post Test Text"}))
        # print(response)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/post") # todo - check: calls again after login?


    # update_post
    def test_update_post_returns_an_error_for_post_that_does_not_exist(self):
        c = Client()
        logged_in = c.login(username='testuser', password='12345')

        post_id = '100'
        path = '/post/' + post_id
        response = c.generic('PUT', path, json.dumps({"text":"Updated Post Text"}))
        # print(response)
        self.assertEqual(response.status_code, 404)

    def test_update_post(self):
        c = Client()
        logged_in = c.login(username='testuser', password='12345')

        # create a post, and retrieve it
        response = c.post("/post", data={"text": "Hello World!"})
        u1 = User.objects.get(username='testuser')
        u1_posts = Post.objects.posts_from_user(u1)

        # update the post text
        post_id = str(u1_posts[0].id)
        path = '/post/' + post_id
        updated_post_text = "Updated Post Text!!"
        response = c.generic('PUT', path, json.dumps({"text":updated_post_text}))
        # print(response)
        self.assertEqual(response.status_code, 201)

        # check Post text
        u1_posts = Post.objects.posts_from_user(u1)
        post = u1_posts[0]
        self.assertEqual(post.text, updated_post_text)

    def test_update_post_fails_for_post_text_greater_than_MAX_POST_LENGTH(self):
        c = Client()
        logged_in = c.login(username='testuser', password='12345')

        # create a post, and retrieve it
        response = c.post("/post", data={"text": "Hello World!"})
        u1 = User.objects.get(username='testuser')
        u1_posts = Post.objects.posts_from_user(u1)

        # update the post text
        post_id = str(u1_posts[0].id)
        path = '/post/' + post_id
        updated_post_text = "Updated Post Text!!!Updated Post Text!!!Updated Post Text!!!Updated Post Text!!!Updated Post Text!!!Updated Post Text!!!Updated Post Text!!!Updated Post Text!!!Updated Post Text!!!Updated Post Text!!!Updated Post Text!!!"
        response = c.generic('PUT', path, json.dumps({"text":updated_post_text}))
        # print(response)
        self.assertEqual(response.status_code, 400)

    def test_update_post_fails_for_empty_post_text(self):
        c = Client()
        logged_in = c.login(username='testuser', password='12345')

        # create a post, and retrieve it
        response = c.post("/post", data={"text": "Hello World!"})
        u1 = User.objects.get(username='testuser')
        u1_posts = Post.objects.posts_from_user(u1)

        # update the post text
        post_id = str(u1_posts[0].id)
        path = '/post/' + post_id
        updated_post_text = ""
        response = c.generic('PUT', path, json.dumps({"text":updated_post_text}))
        # print(response)
        self.assertEqual(response.status_code, 400)
        
    def test_update_fails_for_GET_and_POST(self):
        c = Client()
        logged_in = c.login(username='testuser', password='12345')

        # create a post, and retrieve it
        response = c.post("/post", data={"text": "Hello World!"})
        u1 = User.objects.get(username='testuser')
        u1_posts = Post.objects.posts_from_user(u1)

        # update the post text
        post_id = str(u1_posts[0].id)
        path = '/post/' + post_id
        updated_post_text = "Updated Post Text!!"
        response = c.generic('GET', path, json.dumps({"text":updated_post_text}))
        # print(response)
        self.assertEqual(response.status_code, 400)

        response = c.generic('POST', path, json.dumps({"text":updated_post_text}))
        # print(response)
        self.assertEqual(response.status_code, 400)

    # toggle_like
    def test_like_post_returns_an_error_for_post_that_does_not_exist(self):
        c = Client()
        logged_in = c.login(username='testuser', password='12345')

        post_id = '100'
        path = '/like/' + post_id
        response = c.generic('PUT', path)
        # print(response)
        self.assertEqual(response.status_code, 404)

    def test_like_post_fails_for_GET_and_POST(self):
        c = Client()
        logged_in = c.login(username='testuser', password='12345')

        # create a post, and retrieve it
        # c.generic('POST', '/post', json.dumps({"text":"New Post Test Text!!"}))
        response = c.post("/post", data={"text": "Hello World!"})
        u1 = User.objects.get(username='testuser')
        u1_posts = Post.objects.posts_from_user(u1)

        # like the post 
        post_id = str(u1_posts[0].id)
        path = '/like/' + post_id

        response = c.generic('GET', path)
        # print(response)
        self.assertEqual(response.status_code, 400)

        response = c.generic('POST', path)
        # print(response)
        self.assertEqual(response.status_code, 400)

    def test_like_post(self):
        c = Client()
        logged_in = c.login(username='testuser', password='12345')

        # create a post, and retrieve it
        response = c.post("/post", data={"text": "Hello World!"})
        u1 = User.objects.get(username='testuser')
        u1_posts = Post.objects.posts_from_user(u1)

        # like the post 
        post_id = str(u1_posts[0].id)
        path = '/like/' + post_id

        response = c.generic('PUT', path)
        # print(response)
        self.assertEqual(response.status_code, 201)

        # check Post text
        u1_posts = Post.objects.posts_from_user(u1)
        post = u1_posts[0]
        self.assertEqual(post.likes.count(), 1)

        # un-like the post 
        post_id = str(post.id)
        path = '/like/' + post_id

        response = c.generic('PUT', path)
        # print(response)
        self.assertEqual(response.status_code, 201)

        # check Post text
        u1_posts = Post.objects.posts_from_user(u1)
        post = u1_posts[0]
        self.assertEqual(post.likes.count(), 0)

    # Follow / Unfollow
    def test_follow_returns_an_error_for_user_that_does_not_exist(self):
        c = Client()
        logged_in = c.login(username='testuser', password='12345')

        # u1 follows 
        path = '/follow/' + '100'
        response = c.generic('POST', path)

        # print(response)
        self.assertEqual(response.status_code, 404)

    def test_follow_fails_for_GET_and_PUT(self):
        c = Client()
        logged_in = c.login(username='testuser', password='12345')
        u2 = User.objects.get(username='testuser2')

        # u1 follows u2
        user_id = str(u2.id)
        path = '/follow/' + user_id
        response = c.generic('GET', path)
        # print(response)
        self.assertEqual(response.status_code, 400)

        response = c.generic('PUT', path)
        # print(response)
        self.assertEqual(response.status_code, 400)

    def test_follow(self):
        c = Client()
        logged_in = c.login(username='testuser', password='12345')
        u2 = User.objects.get(username='testuser2')

        # u1 follows u2
        user_id = str(u2.id)
        path = '/follow/' + user_id
        response = c.generic('POST', path)
        # print(response)
        self.assertEqual(response.status_code, 201)

        u1 = User.objects.get(username='testuser')
        self.assertEqual(u1.following.count(), 1)

    def test_follow_returns_an_error_for_user_already_following_user2(self):
        c = Client()
        logged_in = c.login(username='testuser', password='12345')
        u2 = User.objects.get(username='testuser2')

        # u1 follows u2
        user_id = str(u2.id)
        path = '/follow/' + user_id
        response = c.generic('POST', path)

        # u1 follows u2..
        user_id = str(u2.id)
        path = '/follow/' + user_id
        response = c.generic('POST', path)

        # print(response)
        self.assertEqual(response.status_code, 400)

    def test_unfollow_returns_an_error_for_user_that_does_not_exist(self):
        c = Client()
        logged_in = c.login(username='testuser', password='12345')

        # u1 follows 
        path = '/follow/' + '100'
        response = c.generic('DELETE', path)

        # print(response)
        self.assertEqual(response.status_code, 404)

    def test_unfollow(self):
        c = Client()
        logged_in = c.login(username='testuser', password='12345')
        u2 = User.objects.get(username='testuser2')

        # u1 follows u2
        user_id = str(u2.id)
        path = '/follow/' + user_id
        resp = c.generic('POST', path)

        response = c.generic('DELETE', path)

        # print(response)
        self.assertEqual(response.status_code, 201)

        u1 = User.objects.get(username='testuser')
        self.assertEqual(u1.following.count(), 0)

    def test_unfollow_returns_an_error_for_user_not_following_user2(self):
        c = Client()
        logged_in = c.login(username='testuser', password='12345')
        u2 = User.objects.get(username='testuser2')

        # u1 unfollows u2..
        user_id = str(u2.id)
        path = '/follow/' + user_id
        response = c.generic('DELETE', path)

        # print(response)
        self.assertEqual(response.status_code, 400)

    # test for is_following 1?


class NetworkModelsTestCase(TestCase):
    def setUp(self):

        # create Users
        user1 = User.objects.create_user('Mike')
        user2 = User.objects.create_user('James')

        # create Follow
        f1 = Follow.objects.create(from_user=user1, to_user=user2)

        # create Post
        p1 = Post.objects.create(user=user1, text='MY FIRST POST')

    # Follow tests
    def test_follower_count_zero(self):
        u1 = User.objects.get(username='Mike')
        self.assertEqual(u1.followers.count(), 0)
    
    def test_follower_count_one(self):
        u2 = User.objects.get(username='James')
        self.assertEqual(u2.followers.count(), 1)

    def test_following_count_zero(self):
        u2 = User.objects.get(username='James')
        self.assertEqual(u2.following.count(), 0)

    def test_following_count_one(self):
        u1 = User.objects.get(username='Mike')
        self.assertEqual(u1.following.count(), 1)

    def test_create_follow(self):
        u1 = User.objects.get(username='Mike')
        u2 = User.objects.get(username='James')
        follow = Follow.objects.create_follow(u2, u1)
        self.assertEqual(u1.followers.count(), 1)

    def test_invalid_create_follow_raises_exception(self):
        u1 = User.objects.get(username='Mike')
        u2 = User.objects.get(username='James')
        self.assertRaises(Exception, Follow.objects.create_follow, u1, u2)

    def test_delete_follow(self):
        u1 = User.objects.get(username='Mike')
        u2 = User.objects.get(username='James')
        follow = Follow.objects.delete_follow(u1, u2)
        self.assertEqual(u2.followers.count(), 0)

    def test_invalid_delete_follow_raises_exception(self):
        u1 = User.objects.get(username='Mike')
        u2 = User.objects.get(username='James')
        self.assertRaises(Exception, Follow.objects.delete_follow, u2, u1)

    def test_follow_string(self):
        u1 = User.objects.get(username='Mike')
        u2 = User.objects.get(username='James')
        follow = Follow.objects.create_follow(u2, u1)
        self.assertEqual(follow.__str__(), "James is following Mike")

    
    def test_isFollowing_returns_false_when_not_following(self):
        u1 = User.objects.get(username='Mike')
        u2 = User.objects.get(username='James')
        following = Follow.objects.isFollowing(u2, u1)
        self.assertEqual(following, False)

    def test_isFollowing_returns_true_when_following(self):
        u1 = User.objects.get(username='Mike')
        u2 = User.objects.get(username='James')
        following = Follow.objects.isFollowing(u1, u2)
        self.assertEqual(following, True)

    # Post tests
    def test_post_string(self):
        u1 = User.objects.get(username='Mike')
        post = Post.objects.get(user=u1)
        self.assertEqual(post.__str__(), "Mike, MY FIRST POST. 0 likes.")

    def test_create_post(self):
        u2 = User.objects.get(username='James')
        test_post_string = "MY SECOND POST"
        post = Post.objects.create_post(u2, text=test_post_string)
        self.assertEqual(post.text, test_post_string)

    def test_create_post_raises_exception_for_post_length_greater_than_MAX_POST_LENGTH(self):
        u2 = User.objects.get(username='James')
        test_post_string = "MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST "
        with self.assertRaises(ValidationError):
            Post.objects.create_post(u2, text=test_post_string)

    def test_edit_post_raises_exception_for_invalid_user(self):
        u1 = User.objects.get(username='Mike')
        post = Post.objects.get(user=u1)
        u2 = User.objects.get(username='James')
        test_post_string = "UPDATED POST"
        self.assertRaises(Exception, post.update, u2, test_post_string)

    def test_edit_post_raises_exception_for_for_post_length_greater_than_MAX_POST_LENGTH(self):
        u1 = User.objects.get(username='Mike')
        post = Post.objects.get(user=u1)
        test_post_string = "MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST "
        with self.assertRaises(ValidationError):
            post.update(u1, test_post_string)
        
    def test_edit_post_updates_for_valid_user(self):
        u1 = User.objects.get(username='Mike')
        post = Post.objects.get(user=u1)
        test_post_string = "UPDATED POST"
        updated_post = post.update(u1, test_post_string)
        self.assertEqual(updated_post.text, test_post_string)

    def test_post_likes_count_like(self):
        u1 = User.objects.get(username='Mike')
        u2 = User.objects.get(username='James')
        post = Post.objects.get(user=u1)
        post.toggle_like(u2)
        self.assertEqual(post.likes.count(), 1)
        
    def test_post_likes_count_unlike(self):
        u1 = User.objects.get(username='Mike')
        u2 = User.objects.get(username='James')
        post = Post.objects.get(user=u1)
        post.toggle_like(u2)
        post.toggle_like(u2)
        self.assertEqual(post.likes.count(), 0)

    def test_post_toggle_like_returns_count_and_liked(self):
        u1 = User.objects.get(username='Mike')
        u2 = User.objects.get(username='James')
        post = Post.objects.get(user=u1)
        count, liked = post.toggle_like(u2)
        self.assertEqual(count, 1)
        self.assertEqual(liked, 'liked')

    def test_two_users_like_post_count(self):
        u1 = User.objects.get(username='Mike')
        u2 = User.objects.get(username='James')
        post = Post.objects.get(user=u1)
        post.toggle_like(u2)
        post.toggle_like(u1)
        self.assertEqual(post.likes.count(), 2)

    def test_posts_for_all_users_returns_one_post(self):
        u1 = User.objects.get(username='Mike')
        u2 = User.objects.get(username='James')
        all_posts = Post.objects.posts_from_all_users()
        self.assertEqual(all_posts.count(), 1)

    def test_posts_for_user2_returns_no_posts(self):
        u2 = User.objects.get(username='James')
        u2_posts = Post.objects.posts_from_user(u2)
        self.assertEqual(u2_posts.count(), 0)

    def test_posts_for_user1_returns_one_post(self):
        u1 = User.objects.get(username='Mike')
        u1_posts = Post.objects.posts_from_user(u1)
        self.assertEqual(u1_posts.count(), 1)

    def test_posts_from_users_followed_by_user_two_returns_no_posts(self):
        u2 = User.objects.get(username='James')
        all_posts = Post.objects.posts_from_users_followed_by_user(u2)
        self.assertEqual(all_posts.count(), 0)

    def test_posts_from_users_followed_by_user_one_returns_one_post(self):
        u1 = User.objects.get(username='Mike')
        u2 = User.objects.get(username='James')
        test_post_string = "JAMES' POST"
        post1 = Post.objects.create_post(u2, text=test_post_string)
        all_posts = Post.objects.posts_from_users_followed_by_user(u1)
        self.assertEqual(all_posts.count(), 1)

    def test_posts_from_users_followed_by_user_one_returns_four_posts(self):
        u1 = User.objects.get(username='Mike')

        u2 = User.objects.get(username='James')
        test_post_string = "JAMES' POST"
        post1 = Post.objects.create_post(u2, text=test_post_string)
        post2 = Post.objects.create_post(u2, text=test_post_string)

        u3 = User.objects.create_user('Paul')
        f1 = Follow.objects.create(from_user=u1, to_user=u3)
        test_post_string = "PAUL'S POST"
        post3 = Post.objects.create_post(u3, text=test_post_string)
        post4 = Post.objects.create_post(u3, text=test_post_string)

        all_posts = Post.objects.posts_from_users_followed_by_user(u1)
        self.assertEqual(all_posts.count(), 4)

    def test_posts_annotate_like_count_zero(self):
        u1 = User.objects.get(username='Mike')
        u2 = User.objects.get(username='James')
        posts = Post.objects.posts_from_user(u1)
        self.assertEqual(posts[0].like_count, 0)

    def test_posts_annotate_like_count_one(self):
        u1 = User.objects.get(username='Mike')
        u2 = User.objects.get(username='James')
        posts = Post.objects.posts_from_user(u1)
        posts[0].toggle_like(u2)
        self.assertEqual(posts[0].like_count, 1)

    def test_posts_annotate_order_by(self):
        u1 = User.objects.get(username='Mike')
        p1 = Post.objects.create_post(u1, 'MY SECOND POST')
        p1 = Post.objects.create_post(u1, 'MY THIRD POST')
        posts = Post.objects.posts_from_user(u1)
        self.assertEqual(posts[0], p1)



