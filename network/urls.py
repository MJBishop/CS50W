
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API Routes
    path("post", views.new_post, name="new_post"),
    path("post/<int:post_id>", views.update_post, name="update_post"),
    path("like_post/<int:post_id>", views.like_post, name="like_post")
]
