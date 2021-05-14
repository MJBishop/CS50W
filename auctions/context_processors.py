from .models import Listing

'''
Add the count of active listings to template context.
    displayed in navbar badge: layout.html
'''
def add_listing_counts_to_context(request):
    active_listings = Listing.objects.filter(active=True)
    return {
        'active_listings_count': active_listings.count(),
    }