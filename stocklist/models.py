from decimal import Decimal
from datetime import date
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

MAX_STORE_NAME_LENGTH = 20
MAX_COUNT_NAME_LENGTH = 10
MAX_LIST_NAME_LENGTH = 20
MAX_ITEM_NAME_LENGTH = 80
MAX_ITEM_ORIGIN_NAME_LENGTH = 30
MIN_LIST_ITEM_AMOUNT = Decimal('0')
MAX_LIST_ITEM_AMOUNT = Decimal('100000')
DEFAULT_STORE_NAME = 'Stocklist'
DEFAULT_COUNT_NAME = 'Count'


class User(AbstractUser):
    def active_store(self):
        '''
        Lazy load active Store

        Return: Store
        '''
        return Store.objects.filter(user=self).last() or Store.objects.create(user=self, name=DEFAULT_STORE_NAME)


class Store(models.Model):
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name="stores")
    name = models.CharField(max_length=MAX_STORE_NAME_LENGTH)

    class Meta:
        '''
        Store name must be unique for user
        '''
        constraints = [
            models.UniqueConstraint(fields=['user', 'name',], name='unique name user')
        ]

    def __str__(self):
        return self.name

    def active_count(self):
        '''
        Lazy load active Count

        Return: Count
        '''
        return Count.objects.filter(store=self).last() or Count.objects.create(store=self, name=DEFAULT_COUNT_NAME)


class Count(models.Model):
    MONTHLY = 'MO'
    WEEKLY = "WE"
    DAILY = "DA"
    COUNT_FREQUENCY_CHOICES = [
        (MONTHLY, "Monthly"),
        (WEEKLY, "Weekly"),
        (DAILY, "Daily"),
    ]

    store = models.ForeignKey(Store, editable=False, on_delete=models.CASCADE, related_name="counts")
    name = models.CharField(max_length=MAX_COUNT_NAME_LENGTH)
    previous_count = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='next_count') #checks!?, editable?
    end_date = models.DateField(default=timezone.localdate) #sequential counts can have same start date??
    frequency = models.CharField(editable=False, max_length=2, choices=COUNT_FREQUENCY_CHOICES, default=DAILY)

    objects = models.Manager()

    # def save(self, *args, **kwargs):
    #     check that previous.end_date is before self.end_date

    # def __str__(self):
    #     if (not self.end_date or self.start_date == self.end_date): 
    #         return "{} Count: {}".format(self.name, self.start_date)
    #     else:
    #         return "{} Count - starts: {}, ends: {}".format(self.name, self.start_date, self.end_date)


class AdditionListManager(models.Manager):
    def get_queryset(self):
        '''
        Filters for Lists with type=ADDITION

        Return: QuerySet
        '''
        return super().get_queryset().filter(type='AD')

class SubtractionListManager(models.Manager):
    def get_queryset(self):
        '''
        Filters for Lists with type=SUBTRACTION

        Return: QuerySet
        '''
        return super().get_queryset().filter(type='SU')

class CountListManager(models.Manager):
    def get_queryset(self):
        '''
        Filters for Lists with type=COUNT 

        Return: QuerySet
        '''
        return super().get_queryset().filter(type='CO')

# class countListManager(models.Manager):
#     def count_lists(self, count):
#         return List.objects.filter(count=count)#group?
#     def serialized_count_lists(self, count):
#         count_lists = self.count_lists(count)
#         serialized_count_lists = []
#         for list in count_lists:
#             serialized_count_lists.append({
#                 # todo
#             })


class List(models.Model):
    ADDITION = 'AD'
    SUBTRACTION = 'SU'
    COUNT = 'CO' # ORDER = 'OR', PAR = 'PA', CHECKLIST = 'CH'
    LIST_TYPE_CHOICES = [
        (ADDITION, "Addition"),
        (SUBTRACTION, "Subtraction"),
        (COUNT, "Count"),
    ]

    store = models.ForeignKey(Store, editable=False, on_delete=models.CASCADE, related_name="lists")
    name = models.CharField(max_length=MAX_LIST_NAME_LENGTH)
    type = models.CharField(editable=False, max_length=2, choices=LIST_TYPE_CHOICES, default=ADDITION)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    additions = AdditionListManager()
    subtractions = SubtractionListManager()
    counts = CountListManager()

    def __str__(self):
        return '{} List - {} {}'.format(self.name, self.store.name, self.get_type_display())


class CountList(models.Model):
    count = models.ForeignKey(Count, editable=False, on_delete=models.CASCADE, related_name="count_lists")
    list = models.ForeignKey(List, editable=False, on_delete=models.CASCADE, related_name="count_list")
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name="count_lists")


class CountItemsManager(models.Manager):
    def count_items(self, count):
        '''
        Annotates total list_item.amount for lists, by type, for the given count:
        total_previous:     List.type=count totals for the previous count (opening stock)
        total_added:        List.type=addition totals for this count (additions)
        total_subtracted:   List.type=subtraction totals for this count (subtractions)
        total_counted:      List.type=count totals for this count (closing stock)

        count (Count): The Count

        Return: QuerySet
        '''

        # TODO - filter between dates

        storeQ = Q(store=count.store)
        previous_countQ = Q(list_items__list__count_list__count=count.previous_count)
        countQ = Q(list_items__list__count_list__count=count)
        additionTypeQ = Q(list_items__list__type=List.ADDITION)
        subtractionTypeQ = Q(list_items__list__type=List.SUBTRACTION)
        countTypeQ = Q(list_items__list__type=List.COUNT)

        return self.annotate(
            total_previous=Coalesce( Sum('list_items__amount', filter=(storeQ & previous_countQ & countTypeQ)), Decimal('0') ),
            total_added=Coalesce( Sum('list_items__amount', filter=(storeQ & countQ & additionTypeQ)), Decimal('0') ),
            total_subtracted=Coalesce( Sum('list_items__amount', filter=(storeQ & countQ & subtractionTypeQ)), Decimal('0') ),
            total_counted=Coalesce( Sum('list_items__amount', filter=(storeQ & countQ & countTypeQ)), Decimal('0') ),
        )#order_by (get_queryset?)

    def serialized_count_items(self, count):
        '''
        Calls count_items(count)
        Serializes the annotated items

        count (Count): The count

        Return: An Array of serialized, annotated items
        '''
        count_items = self.count_items(count)
        serialized_count_items = []
        for item in count_items:
            serialized_count_items.append({
                    'id':item.id,
                    'store_id':item.store.id,
                    'name':item.name,
                    'origin':item.origin,
                    'total_added':'{:.1f}'.format(item.total_added),
                    'total_previous':'{:.1f}'.format(item.total_previous),
                    'total_subtracted':'{:.1f}'.format(item.total_subtracted),
                    'total_counted':'{:.1f}'.format(item.total_counted),
            })
        return serialized_count_items 

class Item(models.Model):
    store = models.ForeignKey(Store, editable=False, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=MAX_ITEM_NAME_LENGTH)
    origin = models.CharField(blank=True, max_length=MAX_ITEM_ORIGIN_NAME_LENGTH) # both blank? editable?
    # spare cols?

    objects = CountItemsManager() #items?

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['store', 'name',], name='unique name store')
        ]

    def __str__(self):
        return self.name


class ListItem(models.Model):
    list = models.ForeignKey(List, editable=False, on_delete=models.CASCADE, related_name="list_items")
    item = models.ForeignKey(Item, editable=False, on_delete=models.CASCADE, related_name="list_items")
    amount = models.DecimalField(
        max_digits=7, 
        decimal_places=1, 
        validators=[MinValueValidator(MIN_LIST_ITEM_AMOUNT), MaxValueValidator(MAX_LIST_ITEM_AMOUNT)]
    )

    def __str__(self):
        return '{} {}'.format(self.amount, self.item.name)