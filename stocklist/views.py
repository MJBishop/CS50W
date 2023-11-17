import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import F
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

from stocklist.forms import StoreNameForm #, StockPeriodForm, StocktakeForm, StockListForm
from .models import User, Store, Item, List, ListItem, MIN_LIST_ITEM_AMOUNT #, StockPeriod, Stocktake, StockList


def index(request):

    # Users must authenticate
    if request.user.is_authenticated:

        if request.method == 'GET':
            # Stores
            stores = Store.objects.filter(user=request.user) or None #get or create!
            if not stores:
                return HttpResponseRedirect(reverse("store"))

            return render(request, "stocklist/index.html",{
                'page_title':'Store',
                'stores':stores,
            })
            # Items?
            
    return HttpResponseRedirect(reverse("login"))
    

@login_required
def store(request):

    if request.method == "GET":
        return render(request, "stocklist/store.html",{
                'page_title':'New Store',
                'store_name_form':StoreNameForm(prefix='store_name_form', initial={'user':request.user}),
            })

    if request.method == 'POST':

        # check it's still the first store
        # better still: create the store first!!
        # just need date!

        store_name_form = StoreNameForm(request.POST, prefix='store_name_form',)

        if store_name_form.is_valid():

            # save new Store
            new_store = store_name_form.save()
            return HttpResponseRedirect(reverse("index"))

        else:
            return render(request, "stocklist/index.html",{
                'page_title':'New Store',
                'store_name_form':store_name_form,
            })

    return HttpResponseRedirect(reverse("store"))


@login_required
def update_store(request, store_id):

    # check for valid Store
    store = get_object_or_404(Store, user=request.user, pk=store_id)

    if request.method == 'PUT':

        data = json.loads(request.body)
        new_store_name = data.get("store_name", "")

        # done in form now
        if new_store_name == '':
            return JsonResponse({"validation_error": f"Store name cannot be empty"}, status=400)
        # must be done here
        if Store.objects.filter(user=request.user, name=new_store_name).exists():
            return JsonResponse({"integrity_error": f"Store name must be unique for user"}, status=400)

        try:
            store.name = new_store_name
            store.full_clean()
            store.save()
        except ValidationError as e:
            return JsonResponse({"validation_error": e.messages}, status=400)
        else:
            return JsonResponse({"message": "Store update successful."}, status=201)

        # if not store_name:
        #     return JsonResponse({"validation_error": f"Store name cannot be empty"}, status=400)
    
    return JsonResponse({"error": "PUT request Required."}, status=400)


@login_required
def import_items(request, store_id): # import_list

    # check for valid store
    store = get_object_or_404(Store, user=request.user, pk=store_id)

    if request.method == "POST":
        
        # list data
        data = json.loads(request.body)
        list_name = data.get("name", "")
        list_type = data.get("type", "")
        items = data.get("items", "")

        # create List
        try:
            list = List(name=list_name, type=list_type, store=store)
            list.full_clean()
            list.save()
        except ValidationError as e:
            return JsonResponse({"error": e.messages}, status=400)

        # create ListItems
        for item_data in items:

            item_name = item_data.get("name", "") # default name? line number?
            if item_name == '':
                # skip rows with empty names - TODO - record total skipped?
                pass
            else:

                # check for Item in Store
                item_query = Item.objects.filter(name=item_name, store=store)
                if item_query.exists():
                    item = item_query.first()
                else:

                    # save Item to Store
                    try:
                        item = Item(name=item_name, store=store)
                        item.full_clean()
                        item.save()
                    except ValidationError as ve: 
                        # Collect these all up? currently stops loop after 1st ValidationError!
                        print(ve.messages)
                        # IF not unique add item as ref
                        return JsonResponse({"error": ve.messages}, status=400)

                # save ListItem to List
                item_amount = item_data.get("amount", '')
                if item_amount == '':
                    item_amount = MIN_LIST_ITEM_AMOUNT
                try:
                    list_item = ListItem(item=item, list=list, amount=item_amount)
                    list_item.full_clean()
                    list_item.save()
                except ValidationError as e:
                    return JsonResponse({"error": e.messages}, status=400)
                

        return JsonResponse({"message": "Import successful."}, status=201)
    
    return JsonResponse({"error": "POST request Required."}, status=400)



@login_required
def create_list(request, store_id):
    pass


@login_required
def count_item(request, list_id, item_id):

    # check for valid List
    list = get_object_or_404(List, pk=list_id)

    # check for valid Item
    item = get_object_or_404(Item, pk=item_id)

    # save Item amount: create ListItem
    if request.method == 'POST':
        data = json.loads(request.body)
        item_amount = data.get("amount", "")

        try:
            list_item = ListItem(item=item, list=list, amount=item_amount)
            list_item.full_clean()
            list_item.save()
        except ValidationError as e:
            return JsonResponse({"error": e.messages}, status=400)

        return JsonResponse({"message": "Import successful."}, status=201)

    return JsonResponse({"error": "POST request Required."}, status=400)




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

        # Redirect to store after User registered
        return HttpResponseRedirect(reverse("store"))

    return render(request, "stocklist/register.html")