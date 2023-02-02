from django.contrib import admin

from stocklist.models import User, Store, StockPeriod, Stocktake

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_superuser', 'id')

class StoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'id')

class StockPeriodAdmin(admin.ModelAdmin):
    list_display = ('frequency', 'store', 'id')

class StocktakeAdmin(admin.ModelAdmin):
    list_display = ('stock_period', 'end_date', 'id')

admin.site.register(User, UserAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(StockPeriod, StockPeriodAdmin)
admin.site.register(Stocktake, StocktakeAdmin)