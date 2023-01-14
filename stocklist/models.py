from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

MAX_STORE_NAME_LENGTH = 20
MAX_SESSION_NAME_LENGTH = 10
MAX_LIST_NAME_LENGTH = 20
MAX_ITEM_NAME_LENGTH = 40 #enough?
MIN_LIST_ITEM_AMOUNT = Decimal('0')
MAX_LIST_ITEM_AMOUNT = Decimal('1000000')


class User(AbstractUser):
    pass


class Store(models.Model):
    owner = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name="stores")
    name = models.CharField(max_length=MAX_STORE_NAME_LENGTH)

    def __str__(self):
        return self.name


class Session(models.Model):
    store = models.ForeignKey(Store, editable=False, on_delete=models.CASCADE, related_name="sessions")
    name = models.CharField(max_length=MAX_SESSION_NAME_LENGTH)
    start_date = models.DateField() #datetime?
    end_date = models.DateField()

    def save(self, *args, **kwargs):
        if self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date!")
        super(Session, self).save(*args, **kwargs)

    def __str__(self):
        if (self.start_date == self.end_date):
            return "{} Session: {}".format(self.name, self.start_date)
        else:
            return "{} Session - starts: {}, ends: {}".format(self.name, self.start_date, self.end_date)


class AdditionListManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(list_type='AD')

class SubtractionListManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(list_type='SU')

class CountListManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(list_type='CO')

class List(models.Model):
    
    ADDITION = 'AD'
    SUBTRACTION = 'SU'
    COUNT = 'CO'
    # ORDER = 'OR', PAR = 'PA'
    LIST_TYPE_CHOICES = [
        (ADDITION, "Addition"),
        (SUBTRACTION, "Subtraction"),
        (COUNT, "Count"),
    ]

    session = models.ForeignKey(Session, editable=False, on_delete=models.CASCADE, related_name="lists")
    owner = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name="lists")
    name = models.CharField(max_length=MAX_LIST_NAME_LENGTH) #optional?
    # date?
    list_type = models.CharField(blank=False, max_length=2, choices=LIST_TYPE_CHOICES, default=ADDITION)

    objects = models.Manager()
    additions = AdditionListManager()
    subtractions = SubtractionListManager()
    counts = CountListManager()


class AnnotatedItemManager(models.Manager):
    def annotated_items_for_session(self, session):

        storeQ = Q(store=session.store)
        sessionQ = Q(list_items__list__session=session)
        additionQ = Q(list_items__list__list_type=List.ADDITION)
        subtractionQ = Q(list_items__list__list_type=List.SUBTRACTION)
        countQ = Q(list_items__list__list_type=List.COUNT)

        return self.annotate(
            total_added=Coalesce( Sum('list_items__amount', filter=(storeQ & sessionQ & additionQ)), Decimal('0') ),
            total_subtracted=Coalesce( Sum('list_items__amount', filter=(storeQ & sessionQ & subtractionQ)), Decimal('0') ),
            total_counted=Coalesce( Sum('list_items__amount', filter=(storeQ & sessionQ & countQ)), Decimal('0') ),
        )#order_by (get_queryset?)

class Item(models.Model):
    store = models.ForeignKey(Store, editable=False, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(unique=True, max_length=MAX_ITEM_NAME_LENGTH)
    # spare cols?

    objects = AnnotatedItemManager()


class ListItem(models.Model):
    list = models.ForeignKey(List, editable=False, on_delete=models.CASCADE, related_name="list_items")
    item = models.ForeignKey(Item, to_field='name', editable=False, on_delete=models.CASCADE, related_name="list_items")
    amount = models.DecimalField(
        max_digits=7, 
        decimal_places=1, 
        validators=[MinValueValidator(MIN_LIST_ITEM_AMOUNT), MaxValueValidator(MAX_LIST_ITEM_AMOUNT)]
    )