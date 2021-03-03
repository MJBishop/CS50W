from django.urls import path

from . import views

app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/", views.index, name="index"),
    path("wiki/search/", views.search, name="search"),
    path("wiki/new/", views.add, name="add"),
    path("wiki/<str:title>/", views.entry, name="entry"),
    # path("wiki/<str:title>", views.randomEntry, name="randomEntry"),
    path("wiki/<str:title>/edit/", views.edit, name="edit")
]
