from django.contrib import admin
from .models import *


@admin.register(DefaultBasket, Weeklybasket)
class DefaultBasketInline(admin.StackedInline):
    ''' '''
    model = OrderBasket

class DefaultBasketAdmin(admin.ModelAdmin):
    ''' '''
    inlines = [DefaultBasketInline,]

class ProductAdmin(admin.ModelAdmin):
    ''' '''
    pass


class DepotAdmin(admin.ModelAdmin):
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
admin.site.register(DefaultBasket)
admin.site.register(OrderContent, DefaultBasketAdmin)
admin.site.register(RegularyOrder, DepotAdmin)
admin.site.register(Depot, DepotAdmin)
admin.site.register(WeeklyBasket, ProductAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(OrderBasket, OrderBasketAdmin)
