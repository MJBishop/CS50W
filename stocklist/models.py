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
DEFAULT_STORE_NAME = 'Store'
MAX_LIST_NAME_LENGTH = 20
MAX_ITEM_NAME_LENGTH = 80
# MAX_ITEM_ORIGIN_NAME_LENGTH = 30
MIN_LIST_ITEM_AMOUNT = Decimal('0')
MAX_LIST_ITEM_AMOUNT = Decimal('100000')


class User(AbstractUser):
    pass


class Store(models.Model):
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name="stores")
    name = models.CharField(max_length=MAX_STORE_NAME_LENGTH, default=DEFAULT_STORE_NAME)

    class Meta:
        '''
        Store name must be unique for User
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
    date_added = models.DateTimeField(default=timezone.localdate, help_text="The date items were added/removed from the Store") 
    # origin = models.CharField(blank=True, max_length=MAX_ITEM_ORIGIN_NAME_LENGTH) # both blank? editable?

    objects = models.Manager()
    additions = AdditionListManager()
    subtractions = SubtractionListManager()
    counts = CountListManager()

    def __str__(self):
        return '{} List - {} {}'.format(self.name, self.store.name, self.get_type_display())


class Item(models.Model):
    store = models.ForeignKey(Store, editable=False, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=MAX_ITEM_NAME_LENGTH)
    # spare cols?

    class Meta:
        '''
        Item name must be unique for Store
        '''
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

    class Meta:
        '''
        Item must be unique for List
        '''
        constraints = [
            models.UniqueConstraint(fields=['list', 'item',], name='unique item list')
        ]

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
    frequency = models.CharField(blank=False, max_length=2, choices=COUNT_FREQUENCY_CHOICES, default=DAILY)

    class Meta:
        '''
        StockPeriod frequency MONTHLY, WEEKLY must be unique for store
        '''
        constraints = [
            models.UniqueConstraint(fields=['store', 'frequency',], condition=Q(frequency='MO'), name='unique monthly_frequency store'),
            models.UniqueConstraint(fields=['store', 'frequency',], condition=Q(frequency='WE'), name='unique weekly_frequency store')
        ]

    def __str__(self):
        return '{} {} Count'.format(self.store.name, self.get_frequency_display())

    def next_date(self, previous_date): # here or view or other?
        '''
        Calculates the next Stocktake date for a given date:
        MONTHLY frequency = last day of next month
        WEEKLY frequency += 7 days
        DAILY frequency += 1 day

        previous_date (Date): the previous Stocktake Date

        Return: Date
        '''
        if self.frequency == self.MONTHLY:
            # add 32 days - definitely 2 months ahead
            temp1 = previous_date + timedelta(days=32)
            # first day of that month
            temp2 = date(year=temp1.year, month=temp1.month, day=1)
            # minus 1 day = last day of next month
            next_date = temp2 - timedelta(days=1)
            return next_date
        elif self.frequency == self.WEEKLY:
            # add 7 days
            return previous_date + timedelta(days=7)
        else:
            # add 1 day
            return previous_date + timedelta(days=1) #is this what we want? or just set the next date!!!


class Stocktake(models.Model):
    stock_period = models.ForeignKey(StockPeriod, editable=False, on_delete=models.CASCADE, related_name="stocktakes")
    end_date = models.DateField(default=timezone.localdate) 

    def __str__(self):
        if self.stock_period.frequency == self.stock_period.MONTHLY:
            return self.end_date.strftime("%B %Y")
        elif self.stock_period.frequency == self.stock_period.WEEKLY:
            return "Week Ending {}".format(self.end_date.strftime("%A %d %b %Y"))
        else:
            return self.end_date.strftime("%A %d %b %Y")

    # set_end_date() ??? by type
    # unique end date per period (MONTHLY & WEEKLY only!)?
    # sequential counts can have same start date??


class StockList(models.Model):
    stocktake = models.ForeignKey(Stocktake, editable=False, on_delete=models.CASCADE, related_name="stocklists")
    list = models.OneToOneField(List, editable=False, on_delete=models.CASCADE) #must be type count!
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name="stocklists") # editable?

    def __str__(self):
        return '{} on {}'.format(self.list.name, self.list.date_added.strftime("%A %d %b %Y")) #?

    
    # create - check for list type COUNT, or create the list within