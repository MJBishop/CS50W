from django.contrib import admin
from .models import User, Post, Follow

# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "date_created", "text")
    filter_horizontal = ("likes",)

class FollowAdmin(admin.ModelAdmin):
    list_display = ("id", "from_user", "to_user")

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "is_superuser")


admin.site.register(Post, PostAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(User, UserAdmin)