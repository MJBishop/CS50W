from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register_view, name="register"),

    # FREE API
    path("store", views.store, name="store"),
    path("store/<int:store_id>", views.store, name="store"),
    path("import_items/<int:count_id>", views.import_items, name="import_items"),
    path("count_item/<int:list_id>/<int:item_id>", views.count_item, name="count_item"),

    # PAID API
    path("count/<int:count_id>", views.count, name="count"),

]