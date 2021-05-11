from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django import forms
from django.forms import ModelForm
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

from django.db.models import Max, Count
# from django.db.models.functions import Cast

from .models import User, Listing, Bid, Comment, SYSTEM_MAX_BID, SYSTEM_MIN_BID, SYSTEM_MIN_BID_INCREMENT

# Forms
class NewBidForm(forms.ModelForm):
    class Meta:
        model = Bid
        exclude = ['listing', 'user', 'date_created']
        widgets = {
            'bid': forms.NumberInput(attrs={'class': 'form-control mx-auto my-1', 'placeholder': SYSTEM_MIN_BID }),
        }
        labels = {
            'bid': ''
        }
    
    def __init__(self, *args, **kwargs):
        initial_arguments = kwargs.get('initial', None)

        super(NewBidForm, self).__init__(*args, **kwargs)

        # 
        if initial_arguments:
            min_bid = initial_arguments.get('min_bid', None)
            self.fields['bid'].widget.attrs['min'] = min_bid
            self.fields['bid'].widget.attrs['placeholder'] = round(min_bid, 2)

class NewCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ['listing', 'user_name', 'date_created']
        widgets = {
            'comment': forms.Textarea(attrs={'placeholder': 'Comment', 'class':'form-control mx-3'})
        }
        labels = {
            'comment': ''
        }

class NewListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = ['watching', 'date_created', 'active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control' }),
            'description': forms.Textarea(attrs={'class': 'form-control' }),
            'starting_bid': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': SYSTEM_MIN_BID }),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "optional" }),
            'img_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': "optional" })
        }
        


# Views
def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(active=True)
                                   .annotate(max_bid=Max('bids__bid'), bid_count=Count('bids__bid'))
                                   .order_by('-date_created'),
        "listings_page": "active"
    })

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Listing.objects.filter(active=True)
                                     .values('category')
                                     .order_by('category')
                                     .distinct()
                                     .annotate(count=Count('category'))
                                     .exclude(category__exact=''),
        "categories_page": "active"
    })

def category(request, category):
    return render(request, "auctions/category.html", {
        "listings": Listing.objects.filter(category=category, active=True)
                                   .annotate(max_bid=Max('bids__bid'), bid_count=Count('bids__bid')),
        "category": category
    })

def watchlist(request):
    return render(request, "auctions/watchlist.html", {
        "listings": request.user.watchlist.all().annotate(max_bid=Max('bids__bid'), bid_count=Count('bids__bid')),
        "watchlist_page" :"active"
    })


@login_required
def createListing(request):
    if request.method == "POST":
        listing = Listing(owner=request.user) 
        form = NewListingForm(request.POST, instance=listing)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/new.html", {
                "form": form,
                "new_listing_page" :"active"
            })

    return render(request, "auctions/new.html", {
        "form": NewListingForm(),
        "new_listing_page" :"active"
    })


def listing(request, listing_id):
    listing = Listing.objects.annotate(max_bid=Max('bids__bid'), bid_count=Count('bids__bid')).get(pk=listing_id)

    # minimum bid: £{SYSTEM_MIN_BID_INCREMENT} greater than current bid
    min_bid = listing.starting_bid
    if listing.max_bid is not None:
        min_bid = listing.max_bid + SYSTEM_MIN_BID_INCREMENT

    # bid form or None: 
    bid_form_or_None = None 
    if min_bid <= SYSTEM_MAX_BID:
        bid_form_or_None = NewBidForm(initial={ 'min_bid':min_bid })

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comment_form": NewCommentForm(),
        "comments": Comment.objects.filter(listing_id=listing_id).order_by('-date_created'),
        "bid_form_or_None": bid_form_or_None,
        "bid_or_None": Bid.objects.filter(listing=listing).order_by('-bid').first()
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
            new_bid_amount = form.cleaned_data["bid"]
            listing = Listing.objects.annotate(max_bid=Max('bids__bid'), bid_count=Count('bids__bid')).get(pk=listing_id)
    
            # check new_bid_amount is still > max_bid
            if ((listing.max_bid is None and new_bid_amount >= listing.starting_bid) or new_bid_amount > listing.max_bid):

                # Create & Save a new listing bid
                new_bid = Bid(listing=listing, user=request.user, bid=new_bid_amount)
                new_bid.save()

                # redirect to Listing
                return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
            else:
                # min_bid has changed since loading the page (by another user)
                min_bid = listing.starting_bid
                if listing.max_bid is not None:
                    min_bid = listing.max_bid + SYSTEM_MIN_BID_INCREMENT

                # notify user by returning a new form and a message
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "comment_form": NewCommentForm(),
                    "comments": Comment.objects.filter(listing_id=listing_id).order_by('-date_created'),
                    "bid_form_or_None": NewBidForm(initial={ 'min_bid':min_bid }),
                    "message": "The price has changed. Your bid was below the new minimum bid.",
                    "bid_or_None": Bid.objects.filter(listing=listing).order_by('-bid').first()
                })
        else:
            # model form validation failed: bid < SYSTEM_MIN_BID || bid > SYSTEM_MAX_BID
            listing = Listing.objects.annotate(max_bid=Max('bids__bid'), bid_count=Count('bids__bid')).get(pk=listing_id)
            return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "comment_form": NewCommentForm(),
                    "comments": Comment.objects.filter(listing_id=listing_id).order_by('-date_created'),
                    "bid_form_or_None": form,
                    "bid_or_None": Bid.objects.filter(listing=listing).order_by('-bid').first()
            })


def addComment(request, listing_id):
    if request.method == "POST":
        form = NewCommentForm(request.POST)

        if form.is_valid():
            comment = form.cleaned_data["comment"]
            listing = Listing.objects.get(pk=listing_id)

            # Create & Save the new comment
            new_comment = Comment(comment=comment, user_name=request.user, listing=listing)
            new_comment.save()
        
        # Else return to listing

    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))


def closeAuction(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)

        # Check the user is the listing.owner
        if request.user.id == listing.owner.id:

            # Set listing as inactive
            setattr(listing, "active", False)
            listing.save()

    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))



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
                "message": "Invalid username and/or password.",
                "login_page": "active"
            })
    else:
        return render(request, "auctions/login.html", {
            "login_page": "active"
        })


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
                "message": "Passwords must match.",
                "register_page" :"active"
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken.",
                "register_page" :"active"
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html", {
            "register_page" :"active"
        })
