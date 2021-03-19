from .models import Listing

def add_listing_counts_to_context(request):
    active_listings = Listing.objects.filter(active=True)
    return {
        'active_listings_count': active_listings.count(),
        'categories_count': active_listings.values('category')
                                           .distinct()
                                           .exclude(category__exact='')
                                           .count()
    }