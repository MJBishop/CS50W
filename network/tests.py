from django.test import TestCase

from .models import User, Follow, Post

# Create your tests here.
class NetworkModelTestCase(TestCase):

    def setUp(self):

        # create Users
        user1 = User.objects.create_user('Mike')
        user2 = User.objects.create_user('James')

        # create Follow
        f1 = Follow.objects.create(from_user=user1, to_user=user2)

    # Follow tests
    def test_follower_count_zero(self):
        u1 = User.objects.get(username='Mike')
        self.assertEqual(u1.followers.count(), 0)
    
    def test_follower_count_one(self):
        u2 = User.objects.get(username='James')
        self.assertEqual(u2.followers.count(), 1)
        
    def test_create_follow(self):
        u1 = User.objects.get(username='Mike')
        u2 = User.objects.get(username='James')
        follow = Follow.objects.create_follow(u2, u1)
        self.assertEqual(u1.followers.count(), 1)

    def test_delete_follow(self):
        u1 = User.objects.get(username='Mike')
        u2 = User.objects.get(username='James')
        follow = Follow.objects.delete_follow(u1, u2)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_string(self):
        u1 = User.objects.get(username='Mike')
        u2 = User.objects.get(username='James')
        follow = Follow.objects.create_follow(u2, u1)
        self.assertEqual(follow.__str__(), "James is following Mike")

