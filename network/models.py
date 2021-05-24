from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class FollowManager(models.Manager):
    def create_follow(self, from_user, to_user):
        '''
        Creates a new Follow object (Follow User)

        from_user (User): The User initiating the follow
        to_user (User): The User being followed

        Return: Follow if not a duplicate, otherwise raises an Exception
        '''
        if not self.filter(from_user=from_user, to_user=to_user).exists():
            follow = Follow(from_user=from_user, to_user=to_user)
            follow.save()
            return follow
        else:
            raise Exception(f'Error: {from_user} is already following {to_user}')

    def delete_follow(self, from_user, to_user):
        '''
        Deletes Follow object (Unfollow User)
        
        from_user (User): The User unfollowing
        to_user (User): The User being unfollowed
        '''
        if self.filter(from_user=from_user, to_user=to_user).exists():
            unfollow = self.filter(from_user=from_user, to_user=to_user)
            unfollow.delete()
        else:
            raise Exception(f'Error: {from_user} is not following {to_user}')

class Follow(models.Model):
    from_user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name='following')
    to_user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name='followers')

    objects = FollowManager()

    def __str__(self):
        return f"{self.from_user.username} is following {self.to_user.username}"

class PostManager(models.Manager):
    def create_post(self, user, text):
        '''
        user (User): The User making the Post
        text (string): The Post text

        Return: Post
        '''
        post = Post(user=user, text=text)
        post.save()
        return post
        #exception? text length?

    def posts_for_users(self, user_list):
        if len(user_list) == 0:
            # fetch all posts
            return self.all()
        elif len(user_list) == 1:
            return self.filter(user=user_list[0])
        else:
            # fetch all posts where user in user_list
            return self.filter(user__in=user_list)


class Post(models.Model):
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name='posts')
    likes = models.ManyToManyField(User, blank=True, related_name='liked_posts')#test
    date_created = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=200)

    objects = PostManager()

    def __str__(self):
        return f"{self.user.username}, {self.text}. {self.likes.count()} likes."

    def update(self, user, new_text):
        '''
        Updates the Post
        
        user (User): The User editing the Post
        new_text (string): The edited Post text

        Return: Updated Post if user is the post owner, otherwise raises an exception
        '''
        if user == self.user:
            self.text = new_text
            self.save()
            return self
        else:
            raise Exception(f'Error: {user} is not the Post owner')
    
    def toggle_like(self, user): 
        '''
        Toggles status of User liking Post

        If User hasn't liked the post yet: Adds the user to the Post 'likes'.
        If User has already liked the post: Removes the user from the Post 'likes'.

        user (User): The User liking/unliking the Post

        Return: Post
        '''
        if not user.liked_posts.filter(pk=self.id).exists():
            self.likes.add(user)
        else:
            self.likes.remove(user)
        return self # return post.likes.count or post?