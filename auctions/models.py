from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class User(AbstractUser):
    pass

class Listing(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    starting_bid = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    img_url = models.URLField(blank=True, default='')
    category = models.CharField(max_length=30, blank=True, default='')
    watching = models.ManyToManyField(User, blank=True, related_name="watchlist")

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    bid = models.DecimalField(max_digits=7, decimal_places=2)

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, to_field="username", on_delete=models.CASCADE, related_name="comments")
    # user_name = models.CharField(max_length=150)
    comment = models.TextField(max_length=200)
