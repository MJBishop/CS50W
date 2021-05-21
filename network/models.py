from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Follow(models.Model):
    from_user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name='following')
    to_user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name='followers')

class Post(models.Model):
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name='posts')
    likes = models.ManyToManyField(User, blank=True, related_name='liked_posts')
    date_created = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=200)
