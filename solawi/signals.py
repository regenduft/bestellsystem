#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.db.models.signals import post_save
from django.db.models import Prefetch
from django.dispatch import receiver
from solawi import OrderBasket, User

@receiver(post_save, sender=OrderBasket, dispatch_uid="createorder")
def post_create_orderbasket(sender, instance, created, **kwargs):
    if created:
        
        instance.content = OrderContent.objects.create()
        instance.save()

        # take defaultBasket of user in
        defaults = instance.user.defaultbasket.content.contains.filter(productproperty__orderable=True,
                productproperty__product__orderable=True).prefetch_related('productproperty__product')
        for amount in defaults:
            instance.content.add_or_create_product(amount.productproperty, amount.count)

        # get counterorders of user
        counters = instance.user.regularyorders.filter(productproperty__in=[a.productproperty
                for a in defaults], is_counterorder=True).prefetch_related('productproperty__product')
        # substract deorders of user and account to user
        for each in counters:
            instance.sub_from_order(each.productproperty, -each.count)         

        # update lastorder date
        counters.update(lastorder_isoweek=instance.isoweek, lastorder_isoyear=instance.isoyear)

        # fetch regulary orders which are orderable, ready and not counterorders
        regords = instance.user.regularyorders.select_for_update().filter(productproperty__orderable=True,
                                                      productproperty__product__orderable=True,
                                                      is_ready_order=True).prefetch_related('productproperty__product','count')

        # add regords of user and account to user
        for each in regords:
            instance.add_to_order(each.productproperty, each.count)         
        regords.update(lastorder_isoweek=instance.isoweek, lastorder_isoyear=instance.isoyear)
