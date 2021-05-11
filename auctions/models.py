from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils.translation import ugettext_lazy as _

# Max & Min Bids
SYSTEM_MAX_BID = Decimal('10000.00')
SYSTEM_MIN_BID = Decimal('5.00')
SYSTEM_MIN_BID_INCREMENT = Decimal('1.00')


class User(AbstractUser):
    pass

class Listing(models.Model):
    owner = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=75)
    description = models.TextField(max_length=500)
    starting_bid = models.DecimalField(max_digits=7, 
                                       decimal_places=2, 
                                       validators=[MinValueValidator(SYSTEM_MIN_BID), MaxValueValidator(SYSTEM_MAX_BID)], 
                                       verbose_name='Starting Bid')
    category = models.CharField(max_length=30, blank=True, default='')
    img_url = models.URLField(blank=True, default='', verbose_name='Image URL')
    watching = models.ManyToManyField(User, blank=True, related_name="watchlist")
    date_created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}. Posted by: {self.owner}. Status: {'Active' if self.active else 'Closed'}"

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    bid = models.DecimalField(max_digits=7, 
                              decimal_places=2, 
                              validators=[MinValueValidator(SYSTEM_MIN_BID), MaxValueValidator(SYSTEM_MAX_BID)])
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid: {self.bid} Date: {self.date_created}"

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user_name = models.ForeignKey(User, to_field="username", on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField(max_length=400)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name}, {self.comment}, {self.date_created}"
