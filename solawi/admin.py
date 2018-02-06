from django.contrib import admin
from .models import *



class DefaultBasketInline(admin.StackedInline):
    ''' '''
    model = DefaultBasket

class OrderBasketInline(admin.StackedInline):
    ''' '''
    model = OrderBasket

@admin.register(OrderContent)
class OrderContentAdmin(admin.ModelAdmin):
    ''' '''
    inlines = [
            OrderBasketInline,
            DefaultBasketInline,
            ]
            
class ProductPropertyInline(admin.StackedInline):
    ''' '''
    model = ProductProperty

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    ''' '''
    inlines = [
            ProductPropertyInline,
            ]

admin.site.register(ProductProperty)
admin.site.register(Amount)
admin.site.register(RegularyOrder)
admin.site.register(Depot)
admin.site.register(User)
