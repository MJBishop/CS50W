from django.contrib import admin

from stocklist.models import User, Store, List, Item, ListItem

# Register your models here.


class ListItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'list', 'item', 'amount')

class ListAdmin(admin.ModelAdmin):
    list_display = ('id', 'store', 'name', 'type', 'date_added')

class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'store', 'name')

class StoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name')

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'is_superuser')


admin.site.register(ListItem, ListItemAdmin)
admin.site.register(List, ListAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(User, UserAdmin)

