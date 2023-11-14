from django.contrib import admin

from stocklist.models import User, Store, List, Item, ListItem #StockPeriod, Stocktake, StockList

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_superuser', 'id')

class StoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'id')

# class StockPeriodAdmin(admin.ModelAdmin):
#     list_display = ('frequency', 'store', 'id')

# class StocktakeAdmin(admin.ModelAdmin):
#     list_display = ('stock_period', 'end_date', 'id')

class ListAdmin(admin.ModelAdmin):
    list_display = ('store', 'name', 'type', 'date_added')

class ItemAdmin(admin.ModelAdmin):
    list_display = ('store', 'name')

class ListItemAdmin(admin.ModelAdmin):
    list_display = ('list', 'item', 'amount')

# class StockListAdmin(admin.ModelAdmin):
#     list_display = ('list', 'stocktake', 'user')

admin.site.register(ListItem, ListItemAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(List, ListAdmin)
# admin.site.register(Stocktake, StocktakeAdmin)
# admin.site.register(StockPeriod, StockPeriodAdmin)
admin.site.register(Store, StoreAdmin)
# admin.site.register(StockList, StockListAdmin)
admin.site.register(User, UserAdmin)

