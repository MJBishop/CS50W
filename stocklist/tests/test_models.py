import json
from django.test import Client, TestCase
from django.core.exceptions import ValidationError

from stocklist.models import User

class UserTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:

        # create User
        cls.user1 = User.objects.create_user('Mike')

        return super().setUpTestData()
    
    # User tests
    def test_user(self):

        users = User.objects.all()
        self.assertEqual(users.count(), 1)
        self.assertEqual(users[0].username, 'Mike')