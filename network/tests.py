import json
from django.test import RequestFactory, Client, TestCase
from django.core.exceptions import ValidationError

from .models import User, Follow, Post
from .views import NewPostForm


# Create your tests here.
class FormsTestCase(TestCase):

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
        
testuser = 'testuser'

class ViewsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.user1 = User.objects.create_user(
            username=testuser, email='testuser@test.com', password='12345')

        cls.user2 = User.objects.create_user(
            username='testuser2', email='testuser2@test.com', password='54321')

    # index tests
    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.num_pages, 1)
        self.assertEqual(response.context['page_obj'].object_list.count(), 0)

    
    # following 
    def test_following_PUT_reverse_to_index(self):
        response = self.client.put("/following")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/following") 

    def test_following(self):
        logged_in = self.client.login(username=testuser, password='12345')

        response = self.client.get('/following')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.num_pages, 1)
        self.assertEqual(response.context['page_obj'].object_list.count(), 0)

    def test_following_redirects_when_not_signed_in(self):
        response = self.client.get('/following')
        self.assertEqual(response.status_code, 302)

    def test_following_PUT_POST_DELETE_reverse_to_index(self):
        logged_in = self.client.login(username=testuser, password='12345')
        path = '/following'

        response = self.client.put(path)
        self.assertEqual(response.status_code, 302)

        response = self.client.delete(path)
        self.assertEqual(response.status_code, 302)

        response = self.client.post(path)
        self.assertEqual(response.status_code, 302)

    # profile
    def test_profile(self):
        logged_in = self.client.login(username=testuser, password='12345')
        username = str(self.user2.username)
        user_id = str(self.user2.id)
        path = '/profile/' + user_id

        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.num_pages, 1)
        self.assertEqual(response.context['page_obj'].object_list.count(), 0)
        self.assertEqual(response.context['profile'].username, username)

    def test_profile_raises_404_exception_for_invalid_user(self):
        logged_in = self.client.login(username=testuser, password='12345')
        user_id = '100'
        path = '/profile/' + user_id

        response = self.client.generic('GET', path)
        self.assertEqual(response.status_code, 404)

    def test_profile_PUT_POST_DELETE_reverse_to_index(self):
        logged_in = self.client.login(username=testuser, password='12345')
        user_id = str(self.user2.id)
        path = '/profile/' + user_id
        
        response = self.client.put(path)
        self.assertEqual(response.status_code, 302)

        response = self.client.delete(path)
        self.assertEqual(response.status_code, 302)

        response = self.client.post(path)
        self.assertEqual(response.status_code, 302)


    # new_post
    def test_new_post(self):
        logged_in = self.client.login(username=testuser, password='12345')

        response = self.client.post("/post", data={"text": "Hello World!"})
        self.assertEqual(self.user1.posts.count(), 1)

    def test_new_post_redirects_to_profile(self):
        logged_in = self.client.login(username=testuser, password='12345')

        response = self.client.post("/post", data={"text": "Hello World!"})
        self.assertEqual(response.url, "/profile/1") 
    
    def test_new_post_redirects_when_not_signed_in(self):
        response = self.client.post("/post", data={"text": "Hello World!"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/post")


    # update_post
    def test_update_post_returns_an_error_for_post_that_does_not_exist(self):
        logged_in = self.client.login(username=testuser, password='12345')
        post_id = '100'
        path = '/post/' + post_id

        response = self.client.generic('PUT', path, json.dumps({"text":"Updated Post Text"}))
        self.assertEqual(response.status_code, 404)

    def test_update_post(self):
        logged_in = self.client.login(username=testuser, password='12345')

        # create a post, and retrieve it
        response = self.client.post("/post", data={"text": "Hello World!"})
        u1_posts = Post.objects.posts_from_user(self.user1)

        # update the post text
        post_id = str(u1_posts[0].id)
        path = '/post/' + post_id
        updated_post_text = "Updated Post Text!!"

        response = self.client.generic('PUT', path, json.dumps({"text":updated_post_text}))
        self.assertEqual(response.status_code, 201)

        # check Post text
        u1_posts = Post.objects.posts_from_user(self.user1)
        post = u1_posts[0]
        self.assertEqual(post.text, updated_post_text)

    def test_update_post_fails_for_post_text_greater_than_MAX_POST_LENGTH(self):
        logged_in = self.client.login(username=testuser, password='12345')

        # create a post, and retrieve it
        response = self.client.post("/post", data={"text": "Hello World!"})
        u1_posts = Post.objects.posts_from_user(self.user1)

        # update the post text
        post_id = str(u1_posts[0].id)
        path = '/post/' + post_id
        updated_post_text = "Updated Post Text!!!Updated Post Text!!!Updated Post Text!!!Updated Post Text!!!Updated Post Text!!!Updated Post Text!!!Updated Post Text!!!Updated Post Text!!!Updated Post Text!!!Updated Post Text!!!Updated Post Text!!!"
        
        response = self.client.generic('PUT', path, json.dumps({"text":updated_post_text}))
        self.assertEqual(response.status_code, 400)

    def test_update_post_fails_for_empty_post_text(self):
        logged_in = self.client.login(username=testuser, password='12345')

        # create a post, and retrieve it
        response = self.client.post("/post", data={"text": "Hello World!"})
        u1_posts = Post.objects.posts_from_user(self.user1)

        # update the post text
        post_id = str(u1_posts[0].id)
        path = '/post/' + post_id
        updated_post_text = ""

        response = self.client.generic('PUT', path, json.dumps({"text":updated_post_text}))
        self.assertEqual(response.status_code, 400)
        
    def test_update_fails_for_GET_and_POST(self):
        logged_in = self.client.login(username=testuser, password='12345')

        # create a post, and retrieve it
        response = self.client.post("/post", data={"text": "Hello World!"})
        u1_posts = Post.objects.posts_from_user(self.user1)

        # update the post text
        post_id = str(u1_posts[0].id)
        path = '/post/' + post_id
        updated_post_text = "Updated Post Text!!"

        response = self.client.generic('GET', path, json.dumps({"text":updated_post_text}))
        self.assertEqual(response.status_code, 400)

        response = self.client.generic('POST', path, json.dumps({"text":updated_post_text}))
        self.assertEqual(response.status_code, 400)

    # toggle_like
    def test_like_post_returns_an_error_for_post_that_does_not_exist(self):
        logged_in = self.client.login(username=testuser, password='12345')
        post_id = '100'
        path = '/like/' + post_id

        response = self.client.generic('PUT', path)
        self.assertEqual(response.status_code, 404)

    def test_like_post_fails_for_GET_and_POST(self):
        logged_in = self.client.login(username=testuser, password='12345')

        # create a post, and retrieve it
        response = self.client.post("/post", data={"text": "Hello World!"})
        u1_posts = Post.objects.posts_from_user(self.user1)

        # like the post 
        post_id = str(u1_posts[0].id)
        path = '/like/' + post_id

        response = self.client.generic('GET', path)
        self.assertEqual(response.status_code, 400)

        response = self.client.generic('POST', path)
        self.assertEqual(response.status_code, 400)

    def test_like_post(self):
        logged_in = self.client.login(username=testuser, password='12345')

        # create a post, and retrieve it
        response = self.client.post("/post", data={"text": "Hello World!"})
        u1_posts = Post.objects.posts_from_user(self.user1)

        # like the post 
        post_id = str(u1_posts[0].id)
        path = '/like/' + post_id

        response = self.client.generic('PUT', path)
        self.assertEqual(response.status_code, 201)

        # check Post text
        u1_posts = Post.objects.posts_from_user(self.user1)
        post = u1_posts[0]
        self.assertEqual(post.likes.count(), 1)

        # un-like the post 
        post_id = str(post.id)
        path = '/like/' + post_id

        response = self.client.generic('PUT', path)
        self.assertEqual(response.status_code, 201)

        # check Post text
        u1_posts = Post.objects.posts_from_user(self.user1)
        post = u1_posts[0]
        self.assertEqual(post.likes.count(), 0)

    # Follow / Unfollow
    def test_follow_returns_an_error_for_user_that_does_not_exist(self):
        logged_in = self.client.login(username=testuser, password='12345')
        path = '/follow/' + '100'

        response = self.client.generic('POST', path)
        self.assertEqual(response.status_code, 404)

    def test_follow_fails_for_GET_and_PUT(self):
        logged_in = self.client.login(username=testuser, password='12345')

        # u1 follows u2
        user_id = str(self.user2.id)
        path = '/follow/' + user_id

        response = self.client.generic('GET', path)
        self.assertEqual(response.status_code, 400)

        response = self.client.generic('PUT', path)
        self.assertEqual(response.status_code, 400)

    def test_follow(self):
        logged_in = self.client.login(username=testuser, password='12345')

        # u1 follows u2
        user_id = str(self.user2.id)
        path = '/follow/' + user_id
        response = self.client.generic('POST', path)
        self.assertEqual(response.status_code, 201)

        self.assertEqual(self.user1.following.count(), 1)

    def test_follow_returns_an_error_for_user_already_following_user2(self):
        logged_in = self.client.login(username=testuser, password='12345')

        # u1 follows u2
        user_id = str(self.user2.id)
        path = '/follow/' + user_id
        response = self.client.generic('POST', path)

        # u1 follows u2..
        user_id = str(self.user2.id)
        path = '/follow/' + user_id

        response = self.client.generic('POST', path)
        self.assertEqual(response.status_code, 400)

    def test_unfollow_returns_an_error_for_user_that_does_not_exist(self):
        logged_in = self.client.login(username=testuser, password='12345')

        # u1 follows 
        path = '/follow/' + '100'

        response = self.client.generic('DELETE', path)
        self.assertEqual(response.status_code, 404)

    def test_unfollow(self):
        logged_in = self.client.login(username=testuser, password='12345')

        # u1 follows u2
        user_id = str(self.user2.id)
        path = '/follow/' + user_id
        resp = self.client.generic('POST', path)

        response = self.client.generic('DELETE', path)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.user1.following.count(), 0)

    def test_unfollow_returns_an_error_for_user_not_following_user2(self):
        logged_in = self.client.login(username=testuser, password='12345')

        # u1 unfollows u2..
        user_id = str(self.user2.id)
        path = '/follow/' + user_id

        response = self.client.generic('DELETE', path)
        self.assertEqual(response.status_code, 400)

    # test for is_following 1?


class NetworkModelsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):

        # create Users
        cls.user1 = User.objects.create_user('Mike')
        cls.user2 = User.objects.create_user('James')

        # create Follow
        cls.follow1 = Follow.objects.create(from_user=cls.user1, to_user=cls.user2)

        # create Post
        cls.post1 = Post.objects.create(user=cls.user1, text='MY FIRST POST')
            

    # Follow tests
    def test_follower_count_zero(self):
        self.assertEqual(self.user1.followers.count(), 0)
    
    def test_follower_count_one(self):
        self.assertEqual(self.user2.followers.count(), 1)

    def test_following_count_zero(self):
        self.assertEqual(self.user2.following.count(), 0)

    def test_following_count_one(self):
        self.assertEqual(self.user1.following.count(), 1)

    def test_create_follow(self):
        follow = Follow.objects.create_follow(self.user2, self.user1)
        self.assertEqual(self.user1.followers.count(), 1)

    def test_invalid_create_follow_raises_exception(self):
        self.assertRaises(Exception, Follow.objects.create_follow, self.user1, self.user2)

    def test_delete_follow(self):
        follow = Follow.objects.delete_follow(self.user1, self.user2)
        self.assertEqual(self.user2.followers.count(), 0)

    def test_invalid_delete_follow_raises_exception(self):
        self.assertRaises(Exception, Follow.objects.delete_follow, self.user2, self.user1)

    def test_follow_string(self):
        follow = Follow.objects.create_follow(self.user2, self.user1)
        self.assertEqual(follow.__str__(), "James is following Mike")

    
    def test_isFollowing_returns_false_when_not_following(self):
        following = Follow.objects.isFollowing(self.user2, self.user1)
        self.assertEqual(following, False)

    def test_isFollowing_returns_true_when_following(self):
        following = Follow.objects.isFollowing(self.user1, self.user2)
        self.assertEqual(following, True)

    # Post tests
    def test_post_string(self):
        self.assertEqual(self.post1.__str__(), "Mike, MY FIRST POST. 0 likes.")

    def test_create_post(self):
        test_post_string = "MY SECOND POST"
        post = Post.objects.create_post(self.user2, text=test_post_string)
        self.assertEqual(post.text, test_post_string)

    def test_create_post_raises_exception_for_post_length_greater_than_MAX_POST_LENGTH(self):
        test_post_string = "MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST "
        with self.assertRaises(ValidationError):
            Post.objects.create_post(self.user2, text=test_post_string)

    def test_edit_post_raises_exception_for_invalid_user(self):
        post = Post.objects.get(user=self.user1)
        test_post_string = "UPDATED POST"
        self.assertRaises(Exception, self.post1.update, self.user2, test_post_string)

    def test_edit_post_raises_exception_for_for_post_length_greater_than_MAX_POST_LENGTH(self):
        post = Post.objects.get(user=self.user1)
        test_post_string = "MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST MY SECOND TEST POST "
        with self.assertRaises(ValidationError):
            post.update(self.user1, test_post_string)
        
    def test_edit_post_updates_for_valid_user(self):
        post = Post.objects.get(user=self.user1)
        test_post_string = "UPDATED POST"
        updated_post = post.update(self.user1, test_post_string)
        self.assertEqual(updated_post.text, test_post_string)

    def test_post_likes_count_like(self):
        self.post1.toggle_like(self.user2)
        self.assertEqual(self.post1.likes.count(), 1)
        
    def test_post_likes_count_unlike(self):
        self.post1.toggle_like(self.user2)
        self.post1.toggle_like(self.user2)
        self.assertEqual(self.post1.likes.count(), 0)

    def test_post_toggle_like_returns_count_and_liked(self):
        count, liked = self.post1.toggle_like(self.user2)
        self.assertEqual(count, 1)
        self.assertEqual(liked, 'liked')

    def test_two_users_like_post_count(self):
        self.post1.toggle_like(self.user2)
        self.post1.toggle_like(self.user1)
        self.assertEqual(self.post1.likes.count(), 2)

    def test_posts_for_all_users_returns_one_post(self):
        all_posts = Post.objects.posts_from_all_users()
        self.assertEqual(all_posts.count(), 1)

    def test_posts_for_user2_returns_no_posts(self):
        u2_posts = Post.objects.posts_from_user(self.user2)
        self.assertEqual(u2_posts.count(), 0)

    def test_posts_for_user1_returns_one_post(self):
        u1_posts = Post.objects.posts_from_user(self.user1)
        self.assertEqual(u1_posts.count(), 1)

    def test_posts_from_users_followed_by_user_two_returns_no_posts(self):
        all_posts = Post.objects.posts_from_users_followed_by_user(self.user2)
        self.assertEqual(all_posts.count(), 0)

    def test_posts_from_users_followed_by_user_one_returns_one_post(self):
        test_post_string = "JAMES' POST"
        post = Post.objects.create_post(self.user2, text=test_post_string)
        all_posts = Post.objects.posts_from_users_followed_by_user(self.user1)
        self.assertEqual(all_posts.count(), 1)

    def test_posts_from_users_followed_by_user_one_returns_four_posts(self):
        test_post_string = "JAMES' POST"
        post = Post.objects.create_post(self.user2, text=test_post_string)
        post2 = Post.objects.create_post(self.user2, text=test_post_string)

        u3 = User.objects.create_user('Paul')
        f1 = Follow.objects.create(from_user=self.user1, to_user=u3)
        test_post_string = "PAUL'S POST"
        post3 = Post.objects.create_post(u3, text=test_post_string)
        post4 = Post.objects.create_post(u3, text=test_post_string)

        all_posts = Post.objects.posts_from_users_followed_by_user(self.user1)
        self.assertEqual(all_posts.count(), 4)

    def test_posts_annotate_like_count_zero(self):
        posts = Post.objects.posts_from_user(self.user1)
        self.assertEqual(posts[0].like_count, 0)

    def test_posts_annotate_like_count_one(self):
        posts = Post.objects.posts_from_user(self.user1)
        posts[0].toggle_like(self.user2)
        self.assertEqual(posts[0].like_count, 1)

    def test_posts_annotate_order_by(self):
        p1 = Post.objects.create_post(self.user1, 'MY SECOND POST')
        p2 = Post.objects.create_post(self.user1, 'MY THIRD POST')
        posts = Post.objects.posts_from_user(self.user1)
        self.assertEqual(posts[0], p2)



