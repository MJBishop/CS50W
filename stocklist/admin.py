from django.contrib import admin

from stocklist.models import User, Store

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_superuser', 'id')

class StoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'id')

admin.site.register(User, UserAdmin)
admin.site.register(Store, StoreAdmin)