from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register_view, name="register"),

    # FREE API
    path("home", views.home, name="home"),
    path("next_session/<int:session_id>", views.next_session, name="next_session"),

    # PAID API
    path("store/<int:store_id>", views.store, name="store")
]