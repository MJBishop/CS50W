from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class FollowManager(models.Manager):
    def create_follow(self, from_user, to_user):
        follow = Follow(from_user=from_user, to_user=to_user)
        follow.save()
        return follow

    def delete_follow(self, from_user, to_user):
        unfollow = self.filter(from_user=from_user, to_user=to_user)
        unfollow.delete()

class Follow(models.Model):
    from_user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name='following')
    to_user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name='followers')

    objects = FollowManager()

class Post(models.Model):
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name='posts')
    likes = models.ManyToManyField(User, blank=True, related_name='liked_posts')
    date_created = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=200)
