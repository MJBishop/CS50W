import json
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

from .models import User, Store, Item, Session, List, ListItem


def index(request):

    # Users must authenticate
    if request.user.is_authenticated:

        # TODO - Add forms to template

        return render(request, "stocklist/index.html")
    return HttpResponseRedirect(reverse("login"))


@login_required
def home(request):

    # load active store and session (lazy) 
    # !! invited user will only access list!
    active_session = request.user.active_store().active_session()
    serialized_items = Item.objects.serialized_session_items(active_session)
    return JsonResponse(serialized_items, safe=False)  # store.name session.date/name?


@login_required
def store(request, store_id):

    # check for valid store
    try:
        store = Store.objects.get(owner=request.user, pk=store_id)
    except Store.DoesNotExist:
        return JsonResponse({"error": "Store not found."}, status=404)

    # 
    session = store.active_session()
    serialized_items = Item.objects.serialized_session_items(session)
    return JsonResponse(serialized_items, safe=False)  # store.name session.date/name?


@login_required
def session(request, session_id):

    # check for valid session
    try:
        session = Session.objects.get(store__owner=request.user, pk=session_id)
    except Session.DoesNotExist:
        return JsonResponse({"error": "Session not found."}, status=404)

    if request.method == "GET":
        serialized_items = Item.objects.serialized_session_items(session)
        return JsonResponse(serialized_items, safe=False)  # store.name session.date/name?

    return JsonResponse({"error": "GET request Required."}, status=400)
    
    
@login_required
def import_items(request, session_id):
    
    return JsonResponse({"error": "POST request Required."}, status=400)


def count_item(request):
    pass
    # json - no form










    # get all stores?
    # get active store?
    # only 1 store for free account
    # Signal?

    # User has default Store?
















def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "stocklist/login.html", {
                "message": "Invalid username and/or password."
            })

    return render(request, "stocklist/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        # Ensure password matches confirmation
        if password != confirmation:
            return render(request, "stocklist/register.html", {
                "message": "Passwords must match."
            })
        
        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "stocklist/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))

    return render(request, "stocklist/register.html")