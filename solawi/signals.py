#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.db.models.signals import post_save
from django.db.models import Prefetch
from django.dispatch import receiver
from solawi import OrderBasket, User

@receiver(post_save, sender=OrderBasket)
def post_create_orderbasket(sender, instance, created, **kwargs):
    if created:
        defaults = instance.user.defaultbasket.content.contains.filter(productproperty__orderable=True,
                productproperty__product__orderable=True).prefetch_related('productproperty__product','count')
        # take defaultBasket of user in
        for amount in defaults:
            instance.content.add_or_create_product(amount.productproperty, amount.count)

        # substract deorders of user and account to user
        counters = instance.user.regularyorders.filter(productproperty__in=[a.productproperty
                for a in defaults],
                is_counterorder=True).prefetch_related('productproperty__product','count')

        #income = 0
        for each in counters:
            instance.sub_from_order(each.productproperty, each.count)         
            #TODO UPDATE last order
            # old with savings       
            # value, existed = instance.content.sub_or_delete_product(amount.productproperty,
            #                                                         amount.count)         
            # if existed:
               # income += value
        counters.update(lastorder = datetime.date.today())

        # distribute savings on users Regular orders
        regords = instance.user.regularyorders.filter(productproperty__orderable=True,
                                                      productproperty__product__orderable=True,
                                                      is_counterorder=False).prefetch_related('productproperty__product','count')

        for each in regords:
            instance.add_to_order(each.productproperty, each.count)         
            #TODO UPDATE last order
        regords.update(lastorder = datetime.date.today())

# old savings version
#        leftout = income
#        for reg in regords:
#            if reg.ready:
#                pass
#            else:
#                saved = min(reg.current_counterorder_share(regords)*income,
#                        reg.exchange_value/period)
#                reg.savings += saved
#                leftout -= saved
#            # account regular orders in if ready
#            if reg.orderable:
#                instance.content.add_or_create_product(reg.productproperty, reg.count)
#
#        # add leftout to Users assets
#        instance.user.assets += leftout
