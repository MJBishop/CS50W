from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

MAX_STORE_NAME_LENGTH = 20
MAX_SESSION_NAME_LENGTH = 20


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