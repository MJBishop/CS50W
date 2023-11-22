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
    path("create_list/<int:store_id>", views.create_list, name="create_list"),
    path("create_list_item/<int:list_id>/<int:item_id>", views.create_list_item, name="create_list_item"),
    path("create_item/<int:store_id>", views.create_item, name="create_item"),
    


]