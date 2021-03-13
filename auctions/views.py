from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Max, Count
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Bid, Comment

# Forms
class NewBidForm(forms.Form):
    newbid = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': '0.00', 'class':'form-control'}), label='', min_value=1)

    def __init__(self, *args, **kwargs):
        initial_arguments = kwargs.get('initial', None)

        super(NewBidForm, self).__init__(*args, **kwargs)

        if initial_arguments:
            min_bid = initial_arguments.get('min_bid', None)
            self.fields['newbid'].widget.attrs['min'] = min_bid


class NewCommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Comment'}), label='')


class NewListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = ['watching', 'date_created', 'active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['starting_bid'].widget.attrs['min'] = 0.01
        self.fields['starting_bid'].widget.attrs['placeholder'] = "0.00"
        self.fields['img_url'].widget.attrs['placeholder'] = "optional"
        self.fields['category'].widget.attrs['placeholder'] = "optional"
        



def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(active=True).annotate(max_bid=Max('bids__bid'), bid_count=Count('bids__bid')).order_by('-date_created')
    })

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Listing.objects.order_by().values_list('category', flat=True).distinct().exclude(category__exact='').order_by('category')
    })

def category(request, category):
    return render(request, "auctions/category.html", {
        "listings": Listing.objects.filter(category=category, active=True).annotate(max_bid=Max('bids__bid'), bid_count=Count('bids__bid')), 
        "category": category
    })

def watchlist(request):
    return render(request, "auctions/watchlist.html", {
        "listings": request.user.watchlist.all().annotate(max_bid=Max('bids__bid'), bid_count=Count('bids__bid'))
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
                "form": NewListingForm(),
                "message": "Invalid Form" # more details
            })

    return render(request, "auctions/new.html", {
        "form": NewListingForm()
    })

def listing(request, listing_id):
    listing = Listing.objects.annotate(max_bid=Max('bids__bid'), bid_count=Count('bids__bid')).get(pk=listing_id)
    min_bid = listing.starting_bid

    if listing.max_bid is not None:
        min_bid = listing.max_bid + 1

    bid = Bid.objects.filter(listing=listing).order_by('-bid').first()
    
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": Comment.objects.filter(listing_id=listing_id), # TODO - most recent first
        "bid_form": NewBidForm(initial={ 'min_bid':min_bid }),
        "comment_form": NewCommentForm(),
        "bid_or_None": bid
    })

def toggleWatchlist(request, listing_id):
    # TODO - Inform user if un-watching an auction the user has won

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
            new_bid_amount = form.cleaned_data["newbid"]
            listing = Listing.objects.annotate(max_bid=Max('bids__bid'), bid_count=Count('bids__bid')).get(pk=listing_id)
    
            if (listing.max_bid is None and new_bid_amount >= listing.starting_bid or new_bid_amount > listing.max_bid):

                # Create & Save a new listing bid
                new_bid = Bid(listing=listing, user=request.user, bid=new_bid_amount)
                new_bid.save()

                return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
            else:
                # min_bid has changed since loading the page (by another user)
                min_bid = listing.starting_bid
                if listing.max_bid is not None:
                    min_bid = listing.max_bid + 1

                # notify user by returning a new form and a message
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "comments": Comment.objects.filter(listing_id=listing_id), # TODO - most recent first
                    "bid_form": NewBidForm(initial={ 'min_bid':min_bid }),
                    "comment_form": NewCommentForm(),
                    "message": "Your bid was below the new minimum bid."
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
