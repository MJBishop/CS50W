from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Max, Count
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid, Comment

# Forms
class NewBidForm(forms.Form):
    new_bid = forms.IntegerField(label='')


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.annotate(max_bid=Max('bids__bid'))
    })

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Listing.objects.order_by().values_list('category', flat=True).distinct().exclude(category__exact='')
    })

def category(request, category):
    return render(request, "auctions/category.html", {
        "listings": Listing.objects.filter(category=category).annotate(max_bid=Max('bids__bid')), 
        "category": category
    })

def watchlist(request):
    return render(request, "auctions/watchlist.html", {
        "listings": request.user.watchlist.all().annotate(max_bid=Max('bids__bid'))
    })

def listing(request, listing_id):

    return render(request, "auctions/listing.html", {
        "listing": Listing.objects.annotate(max_bid=Max('bids__bid'), bid_count=Count('bids__bid')).get(pk=listing_id),
        "comments": Comment.objects.filter(listing_id=listing_id),
        "form": NewBidForm()
    })

def toggleWatchlist(request, listing_id):
    if request.method == "POST":
        current_user = request.user
        listing = Listing.objects.get(pk=listing_id)
        
        if current_user in listing.watching.all():
            # remove user from watchlist
            listing.watching.remove(current_user)
        else:
            # add user to watchlist
            listing.watching.add(current_user)

        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

def placeBid(request, listing_id):
    if request.method == "POST":
        form = NewBidForm(request.POST)
        if form.is_valid():
            current_user = request.user
            listing = Listing.objects.annotate(max_bid=Max('bids__bid')).get(pk=listing_id)
            current_bid = listing.max_bid
            new_bid_amount = form.cleaned_data["new_bid"]
            if new_bid_amount > current_bid:
                # Add a new bid to the listing
                new_bid = Bid(listing=listing, user=current_user, bid=new_bid_amount)
                new_bid.save()
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))








def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
