
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("following", views.following, name="following"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.new_post, name="new_post"),

    # API Routes
    path("post/<int:post_id>", views.update_post, name="update_post"),
    path("like/<int:post_id>", views.like_post, name="like_post"),
    path("follow/<int:user_id>", views.follow, name="follow_user"),
]
