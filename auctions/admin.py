from django.contrib import admin
from .models import User, Listing, Bid, Comment

# Register your models here.
class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "title", "description", "starting_bid", "img_url", "category", "active")
    filter_horizontal = ("watching",)

class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "user", "bid") 

class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "user_name", "comment")

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "is_superuser")

admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(User, UserAdmin)

