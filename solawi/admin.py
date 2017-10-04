from django.contrib import admin
from .models import *



class PortionInline(admin.TabularInline):
    ''' '''
    pass


class ProductAdmin(admin.ModelAdmin):
    ''' '''
    pass


class DepotAdmin(admin.ModelAdmin):
    ''' '''
    pass


class WeeklyBasketAdmin(admin.ModelAdmin):
    ''' '''
    pass


class UserAdmin(admin.ModelAdmin):
    ''' '''
    pass


class OrderBasketAdmin(admin.ModelAdmin):
    ''' '''
    pass


admin.site.register(ProductAmountProperty, ProductAdmin)
admin.site.register(ProductProperty, ProductAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(DefaultBasket, DepotAdmin)
admin.site.register(RegularyOrder, DepotAdmin)
admin.site.register(Depot, DepotAdmin)
admin.site.register(WeeklyBasket, WeeklyBasketAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(OrderBasket, OrderBasketAdmin)
