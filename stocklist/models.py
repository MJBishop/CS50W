from decimal import Decimal
from datetime import date, timedelta
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
DEFAULT_STORE_NAME = 'Store'


class User(AbstractUser):
    pass


class Store(models.Model):
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name="stores")
    name = models.CharField(max_length=MAX_STORE_NAME_LENGTH, default=DEFAULT_STORE_NAME)

    class Meta:
        '''
        Store name must be unique for user
        '''
        constraints = [
            models.UniqueConstraint(fields=['user', 'name',], name='unique name user')
        ]

    def __str__(self):
        return self.name


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
    timestamp = models.DateTimeField(auto_now_add=True) # should be date added to store

    objects = models.Manager()
    additions = AdditionListManager()
    subtractions = SubtractionListManager()
    counts = CountListManager()

    def __str__(self):
        return '{} List - {} {}'.format(self.name, self.store.name, self.get_type_display())


class Item(models.Model):
    store = models.ForeignKey(Store, editable=False, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=MAX_ITEM_NAME_LENGTH)
    origin = models.CharField(blank=True, max_length=MAX_ITEM_ORIGIN_NAME_LENGTH) # both blank? editable?
    # spare cols?

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


class StockPeriod(models.Model):
    MONTHLY = 'MO'
    WEEKLY = "WE"
    DAILY = "DA"
    COUNT_FREQUENCY_CHOICES = [
        (MONTHLY, "Monthly"),
        (WEEKLY, "Weekly"),
        (DAILY, "Daily"),
    ]

    store = models.ForeignKey(Store, editable=False, on_delete=models.CASCADE, related_name="stock_periods")
    frequency = models.CharField(editable=False, max_length=2, choices=COUNT_FREQUENCY_CHOICES, default=DAILY)

    def __str__(self):
        return '{} {} Count'.format(self.store.name, self.get_frequency_display())

    def next_date(self, previous_date):
        if self.frequency == self.MONTHLY:
            # end of each month
            temp1 = previous_date + timedelta(days=32)
            temp2 = date(year=temp1.year, month=temp1.month, day=1)
            next_date = temp2 - timedelta(days=1)
            return next_date
        elif self.frequency == self.WEEKLY:
            # next week
            return previous_date + timedelta(days=7)
        else:
            # next day
            return previous_date + timedelta(days=1) #is this what we want? or just set the next date!!!


class Stocktake(models.Model):
    stock_period = models.ForeignKey(StockPeriod, editable=False, on_delete=models.CASCADE, related_name="stocktakes")
    end_date = models.DateField(default=timezone.localdate) #sequential counts can have same start date??

    def __str__(self):
        if self.stock_period.frequency == self.stock_period.MONTHLY:
            return self.end_date.strftime("%B %Y")
        elif self.stock_period.frequency == self.stock_period.WEEKLY:
            return "Week Ending {}".format(self.end_date.strftime("%A %d %b %Y"))
        else:
            return self.end_date.strftime("%A %d %b %Y")

    # set_end_date() ???


class StockList(models.Model):
    stocktake = models.ForeignKey(Stocktake, editable=False, on_delete=models.CASCADE, related_name="stocklists")   #M21
    list = models.ForeignKey(List, editable=False, on_delete=models.CASCADE, related_name="stocklists")         #121
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name="stocklists")         #M21