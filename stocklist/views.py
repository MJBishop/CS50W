import json
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import F
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

from django.db.models import F
from django.db.models.lookups import Exact

from stocklist.forms import StoreNameForm
from .models import User, Store, Item, List, ListItem, MIN_LIST_ITEM_AMOUNT


def index(request):

    # Users must authenticate
    if request.user.is_authenticated:

        # GET Store
        if request.method == 'GET':
            store = Store.objects.filter(user=request.user).last() or None 

            # return StoreNameForm if no store
            if not store:
                return render(request, "stocklist/index.html",{
                    'page_title':'Home',
                    'store_name_form':StoreNameForm(),
                })
        
            else:
                # redirect to /store/id
                path = "/store/{}".format(store.pk)
                return redirect(path)
            
        # POST new Store name
        if request.method == 'POST':
            store = Store(user=request.user)
            store_name_form = StoreNameForm(request.POST, instance=store)

            # check for integrity error - must be done here
            store_name = store_name_form['name'].value()
            if Store.objects.filter(user=request.user, name=store_name).exists():  
                return render(request, "stocklist/index.html",{
                    'page_title':'Home',
                    'store_name_form':store_name_form,
                    'message':"Store name must be unique for user",
                })

            if store_name_form.is_valid():
                try:
                    # save new Store
                    new_store = store_name_form.save()

                except ValidationError as e:
                    return render(request, "stocklist/index.html",{
                        'page_title':'Home',
                        'store_name_form':store_name_form,
                        'message':e.messages,
                    })

                # redirect to /store/id
                path = "/store/{}".format(new_store.pk)
                return redirect(path)
            
            else:
                return render(request, "stocklist/index.html",{
                    'page_title':'Home',
                    'store_name_form':store_name_form,
                })
        
        return HttpResponseRedirect(reverse("index"))
            
    return HttpResponseRedirect(reverse("login"))
    

@login_required
def store(request, store_id):

    #  check for valid Store
    store = get_object_or_404(Store, user=request.user, pk=store_id)
    
    if request.method == "GET":

        return render(request, "stocklist/store.html",{
                'store':store,
            })
    
    if request.method == "POST":

        # delete store
        store.delete()

    return HttpResponseRedirect(reverse("index"))


# @login_required
# def delete_store(request, store_id):

#     #  check for valid Store
#     store = get_object_or_404(Store, user=request.user, pk=store_id)

#     store.delete()

#     return HttpResponseRedirect(reverse("index"))



@login_required
def update_store(request, store_id): 

    # check for valid Store
    store = get_object_or_404(Store, user=request.user, pk=store_id)

    if request.method == 'PUT':

        data = json.loads(request.body)
        new_store_name = data.get("name", "")

        if new_store_name == '':   # done in form now
            return JsonResponse({"validation_error": f"Store name cannot be empty"}, status=400)
        if new_store_name == store.name:
            return JsonResponse({"message": "No update necessary."}, status=201)
        if Store.objects.filter(user=request.user, name=new_store_name).exists():  # must be done here
            return JsonResponse({"integrity_error": f"Store name must be unique for user"}, status=400)

        try:
            store.name = new_store_name
            store.full_clean()
            store.save()
        except ValidationError as e:
            return JsonResponse({"validation_error": e.messages}, status=400)
        else:
            return JsonResponse({"message": "Store update successful."}, status=201)
    
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
                        # print(ve.messages)
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
def items(request, store_id):

     # check for valid store
    store = get_object_or_404(Store, user=request.user, pk=store_id)

    if request.method == 'GET':

        items = Item.objects.filter(store_id=store_id).prefetch_related("list_items")

        data = {
            'items' : [item.serialize() for item in items],
            'lists' : [list.serialize() for list in store.lists.all()]
        }
        return JsonResponse(data, safe=False)

    return JsonResponse({"error": "POST request Required."}, status=400)


@login_required
def create_list(request, store_id): #list

    # check for valid store
    store = get_object_or_404(Store, user=request.user, pk=store_id)

    if request.method == 'POST':

        data = json.loads(request.body)
        for dict in data:
            name = dict.get("name", "")
            type = dict.get("type", "")

            try:
                list = List(name=name, type=type, store=store)
                list.full_clean()
                list.save()
            except ValidationError as e:
                # print(e.messages)
                return JsonResponse({"error": e.messages}, status=400)
        
        return JsonResponse(data = {"message": "Import successful.", "list":list.serialize()}, status=201, safe=False)

    return JsonResponse({"error": "POST request Required."}, status=400)


@login_required
def create_item(request, store_id): #item

    # TODO - need to add it to a list also: pass in list_id!

    # check for valid store
    store = get_object_or_404(Store, user=request.user, pk=store_id)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get("name", "")

        try:
            item = Item(name=name, store=store)
            item.full_clean()
            item.save()
        except ValidationError as e:
            # print(e.messages)
            return JsonResponse({"error": e.messages}, status=400)
        
        return JsonResponse({"message": "Import successful."}, status=201)

    return JsonResponse({"error": "POST request Required."}, status=400)


@login_required
def create_list_item(request, list_id, item_id): #list_item

    # check for valid List
    list = get_object_or_404(List, pk=list_id)

    # check for valid Item
    item = get_object_or_404(Item, pk=item_id)
    # create item?

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
        # return list_item..

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
        return HttpResponseRedirect(reverse("index"))

    return render(request, "stocklist/register.html")