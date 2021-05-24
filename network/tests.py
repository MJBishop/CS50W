from django.test import Client,TestCase

from .models import User, Follow, Post


# Create your tests here.
class NetworkViewsTestCase(TestCase):
    def setUp(self):
        pass

    # index tests
    def test_index(self):
        c = Client()
        response = c.get("//")
        print(response)
        self.assertEqual(response.status_code, 200)


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

    def test_edit_post_raises_exception_for_invalid_user(self):
        u1 = User.objects.get(username='Mike')
        post = Post.objects.get(user=u1)
        u2 = User.objects.get(username='James')
        test_post_string = "UPDATED POST"
        self.assertRaises(Exception, post.update, u2, test_post_string)
        
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
        all_posts = Post.objects.posts_for_users((u1, u2))
        self.assertEqual(all_posts.count(), 1)

    def test_posts_for_user2_returns_no_posts(self):
        u2 = User.objects.get(username='James')
        all_posts = Post.objects.posts_for_users((u2, ))
        self.assertEqual(all_posts.count(), 0)

    def test_posts_for_single_user_call_missing_comma_throws_exception(self):
        






