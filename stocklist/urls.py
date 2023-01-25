from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register_view, name="register"),

    # FREE API
    path("home", views.home, name="home"),
    path("session/<int:session_id>", views.session, name="session"),
    path("import_items/<int:session_id>", views.import_items, name="import_items"),
    path("count_item", views.count_item, name="count_item"),

    # PAID API
    path("store/<int:store_id>", views.store, name="store")
]