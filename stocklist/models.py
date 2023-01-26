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
MAX_SESSION_NAME_LENGTH = 10
MAX_LIST_NAME_LENGTH = 20
MAX_ITEM_NAME_LENGTH = 80
MAX_ITEM_ORIGIN_NAME_LENGTH = 30
MIN_LIST_ITEM_AMOUNT = Decimal('0')
MAX_LIST_ITEM_AMOUNT = Decimal('100000')
DEFAULT_STORE_NAME = 'Stocklist'
DEFAULT_SESSION_NAME = 'Session'


class User(AbstractUser):
    def active_store(self):
        '''
        Lazy load active Store

        Return: Store
        '''
        return Store.objects.filter(owner=self).last() or Store.objects.create(owner=self, name=DEFAULT_STORE_NAME)


class Store(models.Model):
    owner = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name="stores")
    name = models.CharField(max_length=MAX_STORE_NAME_LENGTH)

    class Meta:
        '''
        Store name must be unique for owner
        '''
        constraints = [
            models.UniqueConstraint(fields=['owner', 'name',], name='unique name owner')
        ]

    def __str__(self):
        return self.name

    def active_session(self):
        '''
        Lazy load active Session

        Return: Session
        '''
        return Session.objects.filter(store=self).last() or Session.objects.create(store=self, name=DEFAULT_SESSION_NAME)


class Session(models.Model):
    store = models.ForeignKey(Store, editable=False, on_delete=models.CASCADE, related_name="sessions") #m2m!?
    name = models.CharField(max_length=MAX_SESSION_NAME_LENGTH)
    start_date = models.DateField(default=timezone.localdate) #sequential sessions can have same start date??
    end_date = models.DateField(null=True, blank=True)
    previous_session = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='next_session') #checks!?, editable?

    objects = models.Manager()

    def save(self, *args, **kwargs):
        '''
        Overides Save to Validate end_date >= start_date
        '''
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date!")
        super(Session, self).save(*args, **kwargs)

    def __str__(self):
        if (not self.end_date or self.start_date == self.end_date): 
            return "{} Session: {}".format(self.name, self.start_date)
        else:
            return "{} Session - starts: {}, ends: {}".format(self.name, self.start_date, self.end_date)


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

# class SessionListManager(models.Manager):
#     def session_lists(self, session):
#         return List.objects.filter(session=session)#group?
#     def serialized_session_lists(self, session):
#         session_lists = self.session_lists(session)
#         serialized_session_lists = []
#         for list in session_lists:
#             serialized_session_lists.append({
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
    owner = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name="lists")
    name = models.CharField(max_length=MAX_LIST_NAME_LENGTH)
    type = models.CharField(editable=False, max_length=2, choices=LIST_TYPE_CHOICES, default=ADDITION)
    # date?

    objects = models.Manager()
    additions = AdditionListManager()
    subtractions = SubtractionListManager()
    counts = CountListManager()

    def __str__(self):
        return '{} List - {} {}'.format(self.name, self.store.name, self.get_type_display())


class SessionList(models.Model):
    session = models.ForeignKey(Session, editable=False, on_delete=models.CASCADE, related_name="session_lists")
    list = models.ForeignKey(List, editable=False, on_delete=models.CASCADE, related_name="session_list")


class SessionItemsManager(models.Manager):
    def session_items(self, session):
        '''
        Annotates total list_item.amount for lists, by type, for the given session:
        total_previous:     List.type=count totals for the previous session (opening stock)
        total_added:        List.type=addition totals for this session (additions)
        total_subtracted:   List.type=subtraction totals for this session (subtractions)
        total_counted:      List.type=count totals for this session (closing stock)

        session (Session): The Session

        Return: QuerySet
        '''
        storeQ = Q(store=session.store)
        previous_sessionQ = Q(list_items__list__session_list__session=session.previous_session)
        sessionQ = Q(list_items__list__session_list__session=session)
        additionQ = Q(list_items__list__type=List.ADDITION)
        subtractionQ = Q(list_items__list__type=List.SUBTRACTION)
        countQ = Q(list_items__list__type=List.COUNT)

        return self.annotate(
            total_previous=Coalesce( Sum('list_items__amount', filter=(storeQ & previous_sessionQ & countQ)), Decimal('0') ),
            total_added=Coalesce( Sum('list_items__amount', filter=(storeQ & sessionQ & additionQ)), Decimal('0') ),
            total_subtracted=Coalesce( Sum('list_items__amount', filter=(storeQ & sessionQ & subtractionQ)), Decimal('0') ),
            total_counted=Coalesce( Sum('list_items__amount', filter=(storeQ & sessionQ & countQ)), Decimal('0') ),
        )#order_by (get_queryset?)

    def serialized_session_items(self, session):
        '''
        Calls session_items(session)
        Serializes the annotated items

        session (Session): The Session

        Return: An Array of serialized, annotated items
        '''
        session_items = self.session_items(session)
        serialized_session_items = []
        for item in session_items:
            serialized_session_items.append({
                    'id':item.id,
                    'store_id':item.store.id,
                    'name':item.name,
                    'origin':item.origin,
                    'total_added':'{:.1f}'.format(item.total_added),
                    'total_previous':'{:.1f}'.format(item.total_previous),
                    'total_subtracted':'{:.1f}'.format(item.total_subtracted),
                    'total_counted':'{:.1f}'.format(item.total_counted),
            })
        return serialized_session_items 

class Item(models.Model):
    store = models.ForeignKey(Store, editable=False, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=MAX_ITEM_NAME_LENGTH)
    origin = models.CharField(blank=True, max_length=MAX_ITEM_ORIGIN_NAME_LENGTH) # both blank? editable?
    # spare cols?

    objects = SessionItemsManager() #items?

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