from django.contrib import admin
from .models import *



@admin.register(DefaultBasket)
class DefaultBasketAdmin(admin.ModelAdmin):
    ''' '''
    pass


@admin.register(Product, ProductProperty)
class ProductAdmin(admin.ModelAdmin):
    ''' '''
    pass


class DepotAdmin(admin.ModelAdmin):
    ''' '''
    pass




class UserAdmin(admin.ModelAdmin):
    ''' '''
    pass


@admin.register(OrderBasket)
class OrderBasketAdmin(admin.ModelAdmin):
    ''' '''
    pass


admin.site.register(Amount, ProductAdmin)
admin.site.register(OrderContent, OrderBasketAdmin)
admin.site.register(RegularyOrder, DepotAdmin)
admin.site.register(Depot, DepotAdmin)
admin.site.register(User, UserAdmin)
