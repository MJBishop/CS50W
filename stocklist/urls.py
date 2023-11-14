from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register_view, name="register"),

    # FREE API
    path("store", views.store, name="store"),
    path("update_store/<int:store_id>", views.update_store, name="update_store"),
    path("import_items/<int:store_id>", views.import_items, name="import_items"),
    path("count_item/<int:list_id>/<int:item_id>", views.count_item, name="count_item"),

    # PAID API
    path("count/<int:count_id>", views.count, name="count"),

]