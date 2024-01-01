from decimal import Decimal
# from datetime import date, timedelta
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator, MaxValueValidator


from django.core.exceptions import ValidationError

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stores")
    name = models.CharField(max_length=MAX_STORE_NAME_LENGTH)

    class Meta:
        '''Store name must be unique for User.'''
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
    COUNT = 'CO' # FOR Stocklist: ORDER = 'OR', PAR = 'PA', CHECKLIST = 'CH'...
    LIST_TYPE_CHOICES = [
        (ADDITION, "Addition"),
        (SUBTRACTION, "Subtraction"),
        (COUNT, "Count"),
    ]

    store = models.ForeignKey(Store, editable=False, on_delete=models.CASCADE, related_name="lists")
    name = models.CharField(max_length=MAX_LIST_NAME_LENGTH)
    # origin = models.CharField(blank=True, max_length=MAX_ITEM_ORIGIN_NAME_LENGTH) # both blank? editable?
    type = models.CharField(editable=False, max_length=2, choices=LIST_TYPE_CHOICES, default=COUNT, blank=False) #default=COUNT?
    date_added = models.DateTimeField(
        default=timezone.now, 
        help_text="The date these items were added/removed from the Store."
    )
    objects = models.Manager()
    additions = AdditionListManager()
    subtractions = SubtractionListManager()
    counts = CountListManager()

    def __str__(self):
        return self.name#'{} List - {} {}'.format(self.name, self.store.name, self.get_type_display())
    
    def save(self, *args, **kwargs): # Save or Clean??
        if not [i for i in List.LIST_TYPE_CHOICES if self.type in i]:
            raise ValidationError({'type': ["Invalid Type",]})
        super(List, self).save(*args, **kwargs)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.get_type_display(),
            # TODO date
            "count":self.list_items.count(),
        }

class Item(models.Model):
    store = models.ForeignKey(Store, editable=False, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=MAX_ITEM_NAME_LENGTH)
    # spare cols?

    class Meta:
        '''Item name must be unique for Store.'''
        constraints = [
            models.UniqueConstraint(fields=['store', 'name',], name='unique name store')
        ]

    def __str__(self):
        return self.name
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "list_items": [{ "list_id":list_item.list.id, "amount":list_item.amount } for list_item in self.list_items.all()],
        }


class ListItem(models.Model):
    list = models.ForeignKey(List, editable=False, on_delete=models.CASCADE, related_name="list_items")
    item = models.ForeignKey(Item, editable=False, on_delete=models.CASCADE, related_name="list_items")
    amount = models.DecimalField(
        max_digits=7,
        decimal_places=1,
        validators=[MinValueValidator(MIN_LIST_ITEM_AMOUNT), MaxValueValidator(MAX_LIST_ITEM_AMOUNT)],
        default=MIN_LIST_ITEM_AMOUNT
    )

    # TODO - Item must be unique for List

    def __str__(self):
        return '{} {}'.format(self.amount, self.item.name)

    @property
    def name(self):
        '''Get the item name.'''
        return self.item.name

