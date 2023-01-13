from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

MAX_STORE_NAME_LENGTH = 20
MAX_SESSION_NAME_LENGTH = 10
MAX_LIST_NAME_LENGTH = 20


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
    start_date = models.DateField()
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

class CountListManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(list_type='CO')

class List(models.Model):
    session = models.ForeignKey(Session, editable=False, on_delete=models.CASCADE, related_name="lists")
    owner = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name="lists")
    name = models.CharField(max_length=MAX_LIST_NAME_LENGTH) #optional?
    # date?

    ADDITION = 'AD'
    COUNT = 'CO'
    # SUBTRACTION = 'SU'
    # ORDER = 'OR'
    LIST_TYPE_CHOICES = [
        (ADDITION, "Addition"),
        (COUNT, "Count"),
    ]
    list_type = models.CharField(blank=False, max_length=2, choices=LIST_TYPE_CHOICES, default=ADDITION)

    objects = models.Manager()
    additions = AdditionListManager()
    counts = CountListManager()
