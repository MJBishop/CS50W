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

system_max_bid = 10000
system_min_bid = 5

# Forms
class NewBidForm(forms.Form):
    newbid = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': '0.00', 'class':'form-control mx-auto my-1'}), label='', min_value=system_min_bid, max_value=system_max_bid)

    def __init__(self, *args, **kwargs):
        initial_arguments = kwargs.get('initial', None)

        super(NewBidForm, self).__init__(*args, **kwargs)

        if initial_arguments:
            min_bid = initial_arguments.get('min_bid', None)
            self.fields['newbid'].widget.attrs['min'] = min_bid


class NewCommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Comment', 'class':'form-control mx-3'}), label='')
    # max length check?

class NewListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = ['watching', 'date_created', 'active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control' }),
            'description': forms.Textarea(attrs={'class': 'form-control' }),
            # 'starting_bid': forms.NumberInput(attrs={'class': 'form-control', 'min': 5.00, 'max': 10000.00, 'placeholder': "0.00" }),
            'starting_bid': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': "0.00" }),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "optional" }),
            'img_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': "optional" })
        }
        



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
    min_bid = listing.starting_bid

    if listing.max_bid is not None:
        min_bid = listing.max_bid + 1

    bid_form_or_None = None 
    if min_bid < system_max_bid:
        bid_form_or_None = NewBidForm(initial={ 'min_bid':min_bid })

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": Comment.objects.filter(listing_id=listing_id).order_by('-date_created'),
        "bid_form_or_None": bid_form_or_None,
        "comment_form": NewCommentForm(),
        "bid_or_None": Bid.objects.filter(listing=listing).order_by('-bid').first()
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
    
            if ((listing.max_bid is None and new_bid_amount >= listing.starting_bid) or new_bid_amount > listing.max_bid):

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
                    "comments": Comment.objects.filter(listing_id=listing_id).order_by('-date_created'),
                    "bid_form": NewBidForm(initial={ 'min_bid':min_bid }),
                    "comment_form": form, #NewCommentForm(),
                    "message": "The price has changed. Your bid was below the new minimum bid.",
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
