import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import F
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

from stocklist.forms import StoreNameForm, StockPeriodForm, StocktakeForm, StockListForm
from .models import User, Store, Item, List, ListItem, StockPeriod, Stocktake, StockList


def index(request):

    # Users must authenticate
    if request.user.is_authenticated:

        if request.method == 'GET':
            # Stores
            stores_or_None = Store.objects.filter(user=request.user) or None
            if not stores_or_None:
                return HttpResponseRedirect(reverse("store"))

            stock_takes_or_None = None
            # Stocktakes & StockLists
            oldest_store = stores_or_None[0] # Default is oldest Store
            stock_takes_or_None = Stocktake.objects.filter(
                stock_period__store=oldest_store
            ).annotate(frequency=F('stock_period__frequency')).prefetch_related('stocklists')

            return render(request, "stocklist/index.html",{
                'page_title':'Stores',
                'stores_or_None':stores_or_None,
                'stock_takes_or_None':stock_takes_or_None,
            })
            # Items?
            
    return HttpResponseRedirect(reverse("login"))
    

@login_required
def store(request, store_id): #items() / lists()!

    if request.method == "GET":
        return render(request, "stocklist/index.html",{
                'page_title':'New Store',
                'store_name_form':StoreNameForm(prefix='store_name_form', initial={'user':request.user}),
                # 'stock_period_form':StockPeriodForm(prefix='stock_period_form'),
                'stocktake_form':StocktakeForm(prefix='stocktake_form'),
            })

    if request.method == 'POST':
            store_name_form = StoreNameForm(request.POST, prefix='store_name_form',)
            stock_period_form = StockPeriodForm(request.POST, prefix='stock_period_form')
            stocktake_form = StocktakeForm(request.POST, prefix='stocktake_form')

            if store_name_form.is_valid() and stocktake_form.is_valid(): #nd stock_period_form.is_valid()

                # save new Store
                new_store = store_name_form.save()

                # save new StockPeriod
                new_stock_period = StockPeriod.objects.create(
                    store=new_store,
                    frequency=StockPeriod.DAILY,#stock_period_form.cleaned_data["frequency"],
                )# Integrity not checked - freq & store!!!

                # save new Stocktake
                new_stocktake = Stocktake.objects.create(
                    stock_period=new_stock_period,
                    end_date=stocktake_form.cleaned_data["end_date"],
                )

                return HttpResponseRedirect(reverse("index"))

            else:
                return render(request, "stocklist/index.html",{
                    'page_title':'New Store',
                    'store_name_form':store_name_form,
                    # 'stock_period_form':stock_period_form,
                    'stocktake_form':stocktake_form,
                })

    if request.method == 'PUT':

        # check for valid Store
        store = get_object_or_404(Store, user=request.user, pk=store_id)

        data = json.loads(request.body)
        new_store_name = data.get("store_name", "")

        if new_store_name == '':
            return JsonResponse({"validation_error": f"Store name cannot be empty"}, status=400)

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
    
    return JsonResponse({"error": "GET request Required."}, status=400)


@login_required
def count(request, count_id):

    # check for valid count
    stocktake = get_object_or_404(Stocktake, stock_period__store__user=request.user, pk=count_id)

    if request.method == "GET":
        # serialized_items = Item.objects.serialized_count_items(stocktake)
        # return JsonResponse(serialized_items, safe=False)  # store.name count.date/name?
        return JsonResponse({"message":"TODO"}, safe=False, status=200)

    return JsonResponse({"error": "GET request Required."}, status=400)


@login_required
def import_items(request, count_id):

    # check for valid count
    stocktake = get_object_or_404(Stocktake, stock_period__store__user=request.user, pk=count_id)

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





# def create_stocktake(self, previous_stocktake, new_date):
#         '''
#         Creates a new Stocktake object

#         previous_stocktake (Stocktake): Calculate the next end_date for MONTHLY, WEEKLY stock_period
#         new_date (Date): The next end_date for DAILY stock_period

#         Return: Stocktake 
#         '''
#         stock_period = previous_stocktake.stock_period
#         # next_date = date()
#         if stock_period.frequency == StockPeriod.DAILY:
#             next_date = new_date
#         else:
#             next_date = stock_period.next_date(previous_stocktake.end_date)
        
#         stocktake = Stocktake(stock_period=stock_period, end_date=next_date)
#         try:
#             stocktake.full_clean()
#             stocktake.save()
#         except ValidationError as e:
#             raise e
#         else:
#             return stocktake






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