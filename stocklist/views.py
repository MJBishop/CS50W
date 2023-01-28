import json
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

from .models import User, Store, Item, List, ListItem, DEFAULT_STORE_NAME, Stocktake


def index(request):

    # Users must authenticate
    if request.user.is_authenticated:

        # Add Stores, StockPeriods, Stocktakes, & Items?
        stores = Store.objects.filter(user=request.user) or [Store.objects.create(user=request.user, name=DEFAULT_STORE_NAME)]

        # Add forms - Store, StockPeriod, Stocktake

        return render(request, "stocklist/index.html",{
            'stores':stores
        })

    return HttpResponseRedirect(reverse("login"))


@login_required
def store(request, store_id):

    # check for valid Store
    try:
        store = Store.objects.get(user=request.user, pk=store_id)
    except Store.DoesNotExist:
        return JsonResponse({"error": "Store not found."}, status=404)

    if request.method == "GET":
        # stocktake = Stocktake.objects.filter(store=store).last() or Stocktake.objects.create(store=store)
        # serialized_items = Item.objects.serialized_count_items(stocktake)
        # return JsonResponse(serialized_items, safe=False)  # store.name count.date/name?
        return JsonResponse({"message":"TODO"}, safe=False, status=200)
    
    return JsonResponse({"error": "GET request Required."}, status=400)


@login_required
def count(request, count_id):

    # check for valid count
    try:
        stocktake = Stocktake.objects.get(stock_period__store__user=request.user, pk=count_id)
    except Stocktake.DoesNotExist:
        return JsonResponse({"error": "Stocktake not found."}, status=404)

    if request.method == "GET":
        # serialized_items = Item.objects.serialized_count_items(stocktake)
        # return JsonResponse(serialized_items, safe=False)  # store.name count.date/name?
        return JsonResponse({"message":"TODO"}, safe=False, status=200)

    return JsonResponse({"error": "GET request Required."}, status=400)


@login_required
def import_items(request, count_id):

    # check for valid count
    try:
        stocktake = Stocktake.objects.get(stock_period__store__user=request.user, pk=count_id)
    except Stocktake.DoesNotExist:
        return JsonResponse({"error": "Stocktake not found."}, status=404)

    if request.method == "POST":
        
        data = json.loads(request.body)
        # origin = data.get("origin", "") - not implemented!
        list_name = data.get("name", "")
        list_type = data.get("type", "")
        items = data.get("items", "")

        # create List
        try:
            list = List(name=list_name, type=list_type, store=stocktake.stock_period.store)
            list.full_clean()
            list.save()
        except ValidationError as e:
            return JsonResponse({"error": e.messages}, status=400)

        # create Items & ListItems
        for item_data in items:
            item_name = item_data.get("name", "")
            # TODO - item = Item.objects.filter(name=item_name, store=stocktake.stock_period.store)
            try:
                item = Item(name=item_name, store=stocktake.stock_period.store)
                item.full_clean()
                item.save()
            except ValidationError as e: 
                # Collect these all up? currently stops loop after 1st ValidationError!
                return JsonResponse({"error": e.messages}, status=400)

            # create ListItem
            item_amount = item_data.get("amount", "")
            try:
                list_item = ListItem(item=item, list=list, amount=item_amount)
                list_item.full_clean()
                list_item.save()
            except ValidationError as e:
                return JsonResponse({"error": e.messages}, status=400)

        return JsonResponse({"message": "Import successful."}, status=201)
    
    return JsonResponse({"error": "POST request Required."}, status=400)












# class CountItemsManager(models.Manager):
#     def count_items(self, stocktake):
#         '''
#         Annotates total list_item.amount for lists, by type, for the given count:
#         total_previous:     List.type=count totals for the previous count (opening stock)
#         total_added:        List.type=addition totals for this count (additions)
#         total_subtracted:   List.type=subtraction totals for this count (subtractions)
#         total_counted:      List.type=count totals for this count (closing stock)

#         count (Count): The Count

#         Return: QuerySet
#         '''

#         # TODO - filter between dates

#         storeQ = Q(store=stocktake.stock_period.store)
#         previous_countQ = Q(list_items__list__count_list__stocklist__stocktake=stocktake.previous_count)
#         countQ = Q(list_items__list__count_list__count=stocktake)
#         additionTypeQ = Q(list_items__list__type=List.ADDITION)
#         subtractionTypeQ = Q(list_items__list__type=List.SUBTRACTION)
#         countTypeQ = Q(list_items__list__type=List.COUNT)

#         return self.annotate(
#             total_previous=Coalesce( Sum('list_items__amount', filter=(storeQ & previous_countQ & countTypeQ)), Decimal('0') ),
#             total_added=Coalesce( Sum('list_items__amount', filter=(storeQ & countQ & additionTypeQ)), Decimal('0') ),
#             total_subtracted=Coalesce( Sum('list_items__amount', filter=(storeQ & countQ & subtractionTypeQ)), Decimal('0') ),
#             total_counted=Coalesce( Sum('list_items__amount', filter=(storeQ & countQ & countTypeQ)), Decimal('0') ),
#         )#order_by (get_queryset?)

#     def serialized_count_items(self, count): #move out serialize.py
#         '''
#         Calls count_items(count)
#         Serializes the annotated items

#         count (Count): The count

#         Return: An Array of serialized, annotated items
#         '''
#         count_items = self.count_items(count)
#         serialized_count_items = []
#         for item in count_items:
#             serialized_count_items.append({
#                     'id':item.id,
#                     'store_id':item.store.id,
#                     'name':item.name,
#                     'origin':item.origin,
#                     'total_added':'{:.1f}'.format(item.total_added),
#                     'total_previous':'{:.1f}'.format(item.total_previous),
#                     'total_subtracted':'{:.1f}'.format(item.total_subtracted),
#                     'total_counted':'{:.1f}'.format(item.total_counted),
#             })
#         return serialized_count_items 

# def create_next_count(self, stocktake):
    #     next_stocktake = Stocktake(
    #         stock_period=stocktake.stock_period,
    #         end_date=stocktake.next_date(),
    #     )
    #     next_stocktake.full_clean()
    #     next_stocktake.save()
    #     return next_stocktake








@login_required
def count_item(request, list_id, item_id):

    # check for valid List
    try:
        list = List.objects.get(pk=list_id)
    except List.DoesNotExist:
        return JsonResponse({"error": "List not found."}, status=404)

    # check for valid Item
    try:
        item = Item.objects.get(pk=item_id)
    except Item.DoesNotExist:
        return JsonResponse({"error": "Item not found."}, status=404)

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
        return HttpResponseRedirect(reverse("index"))

    return render(request, "stocklist/register.html")