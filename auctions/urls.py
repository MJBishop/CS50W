from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("listing/watchlist/<str:listing_id>", views.toggleWatchlist, name="toggleWatchlist"),
    path("listing/bid/<str:listing_id>", views.placeBid, name="placeBid"),
    path("listing/<str:listing_id>", views.listing, name="listing"),
    path("<str:category>", views.category, name="category")
]
