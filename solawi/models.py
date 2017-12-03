#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core import validators
from django.db import models
from django.db.models.signals import post_save
from django.core.exceptions import ObjectDoesNotExist
from django.dispatch import receiver
from solawi.validators import *
from django.utils.translation import ugettext_lazy as _
import json
from solawi import utils

class User(AbstractUser):
    ''' '''
    is_member = models.BooleanField(_('Make a paying member'), default=True)
    is_supervisor = models.BooleanField(_('Make a depot supervisor'),
                                        default=False)

    depot = models.ForeignKey('Depot', on_delete=models.PROTECT,
                              related_name='members', blank=True, null=True)

    countshares = models.IntegerField(blank=False,
                                      default=1,
                                      validators=[validators.MinValueValidator(0)])

    defaultbasket = models.ForeignKey('DefaultBasket',
                                      blank=False,
                                      null=True,
                                      on_delete=models.PROTECT)

    counterorders = models.OneToOneField('OrderContent',
                                    blank=False,
                                    null=True,
                                    on_delete=models.PROTECT)

    # validate couterorders is out of default basket

    assets = models.IntegerField(blank=False, default=0,
                                 validators=[validators.MinValueValidator(0)])

    def add_to_present_order(self, prdctprop, count=1):
        '''Add a product to the present order.'''
        value = prdctprop.exchange_value*count
        present = OrderBasket.objects.get(user=self, week=utils.this_week())

        if not (prdctprop.orderable and prdctprop.product.orderable):
            # TODO raise validation error should not be possible but not orderable
            pass
        elif self.assets < value:
            # TODO raise validation error not enough assets
            pass
        else:
            value, created = present.add_or_create_product(prdctprop, count)

            self.assets -= value
            self.save()
                            
    def sub_from_present_order(self, prdctprop, count=None):
        '''Remove a product from the present order.'''
        present = OrderBasket.objects.get(user=self, week=utils.this_week())

        value, existed = present.sub_or_delete_product(prdctprop, count)

        if existed:
            self.assets += value
            # TODO maybe self.clean() with clean cleans to big assets
            self.save()
        else:
            # TODO raise did not exit

    def create_current_order(self):
        # TODO Implement
        # but somewhere else and implement create sub_from and add_to order in
        # order with option to account in users assets
        pass

    class Meta:
        ''' '''
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        if self.first_name == '' and self.last_name == '':
            name = self.username
        else:
            name = self.first_name + ' ' + self.last_name
        if self.depot is None:
            return _('{name}').format(name=name)
        else:
            return _('{name} ({depot})').format(name=name,
                                                depot=self.depot.name)
# TODO rework the clean function
#     def clean(self):
#         ''' '''
#         super(User, self).clean()
#         if self.is_supervisor:
#             if self.depot is None:
#                 raise ValidationError(_('A Member has to have an depot.'))
#         if self.is_member:
#             if self.depot is None:
#                 raise ValidationError(_('A Member has to have an depot.'))
#         if self.weeklybasket.defaultbasket.objects.all():
#             raise ValidationError(_('A Member has to have an '
#                                     'weekly basket.'))


class ProductProperty(models.Model):
    product = models.ForeignKey('Product',
                                on_delete=models.CASCADE,
                                related_name='properties',
                                blank=False)

    orderable = models.BooleanField(default=True)

    packagesize = models.FloatField(default=1)
    producttype = models.CharField(max_length=15,
                                   default='',
                                   blank=True,
                                   help_text=_('product type'))

    def exchange_value(self):
        return product.exchange_value*packagesize

    def __str__(self):
        return _('{packagesize} {unit} of {producttype} {product}').format(
            product=self.product,
            producttype=self.producttype,
            packagesize=self.packagesize,
            unit=self.product.unit)

    class Meta:
        verbose_name = _('properties of product')
        verbose_name_plural = _('properties of products')
        unique_together = ('product', 'producttype', 'packagesize')


class Product(models.Model):
    ''' '''
    name = models.CharField(max_length=30, unique=True)
    orderable = models.BooleanField(default=True)

    unit = models.CharField(max_length=15, default='',
                            help_text=_('measuring unit,'
                                        'e.g. kg or L'))

    # default value none means not modular the time am regular order many not
    # be changed
    module_time = models.IntegerField(help_text=_('module duration in weeks'),
                                      blank=True,
                                      null=True)
    price_of_module = models.FloatField(help_text=_('modular product price'),
                                        blank=True,
                                        null=True)

    # default 0 means not exchangable or better you woun't get anything for it
    exchange_value = models.FloatField(null=True,
                                       default=0,
                                       validators=[validators.MinValueValidator(0)],
                                       help_text=_('exchange value per unit'))

    class Meta:
        ''' '''
        verbose_name = _('product')
        verbose_name_plural = _('products')

    def __str__(self):
        return _('{name}').format(name=self.name)


class Depot(models.Model):
    ''' '''
    name = models.CharField(max_length=30, unique=True)
    location = models.CharField(max_length=30, default='')

    class Meta:
        ''' '''
        verbose_name = _('depot')
        verbose_name_plural = _('depots')

    def __str__(self):
        return _('{name} at {location}').format(name=self.name,
                                                location=self.location)


class Amount(models.Model):
    productproperty = models.ForeignKey('ProductProperty',
                                        related_name='amount',
                                        on_delete=models.PROTECT)
    count = models.IntegerField(default=1)

    ordercontent = models.ForeignKey('OrderContent',
                                      related_name='contains',
                                      on_delete=models.CASCADE,
                                      blank=False,
                                      null=True)

    def exchange_value(self):
        return self.count*self.productproperty.exchange_value()

    class Meta:
        ''' '''
        verbose_name = _('packed product')
        verbose_name_plural = _('packed products')
        unique_together = ('ordercontent' ,'productproperty')
        # FIXME decide if uniqueness should be for product

    def __str__(self):
        return '{count}'.format(
            count=self.count, pro=self.productproperty,
            ordr=self.ordercontent)


class OrderContent(models.Model):
    ''' '''
    productproperties = models.ManyToManyField('ProductProperty',
                                      through='Amount',
                                      related_name='isin',
                                      blank=False)

    def add_or_create_product(self, prdctprop, count=1):
        amount, created = Amount.objects.get_or_create(
                productproperty=prdctprop, 
                ordercontent=self
                defaults={'count': count})

        if not created:
            amount.count += count
            amount.save()

        return amount.exchange_value(), created

    def sub_or_delete_product(self, prdctprop, count=None):
        '''Subtract count or delete productproperty form ordercontent.
        
        returns: (min(amount.echange_value, prdctprop.exchange_value) , existed) of amount'''
        try:
            amount = Amount.objects.get(productproperty=prdctprop, 
                                        ordercontent=present.content)
            value = amount.exchange_value()

            if amount.count > count:
                # TODO maybe self.clean() with clean cleans to big assets
                amount.count -= count
                amount.save()

                return prdctprop.exchange_value(), True

            else:
                amount.delete()

                return value, True


        except Amount.DoesNotExist:
            # should not happen #TODO
            return None, False


    def remove(self, product):
        pass

#    def __iadd__(self, other):
#        '''! Ignore not oderables.'''
#        #TODO TEST this! FIXME rework it!
#
#        toinclude = other.productproperty.all().difference(self.productproperty.all())
#        for prdkt in toinclude:
#            prdkt.amount.filter(ordercontent=other).update(ordercontent=self)
#
#        tomerge = self.productproperty.all().intersection(other.productproperty.all())
#        for prdkt in tomerge:
#
#            for othrprop in other.contains.filter(productproperty=prdkt):
#                try: 
#                    selfprop = self.contains.get(ordercontent=self,
#                            productproperty=othrprop.productproperty)
#
#                except ObjectDoesNotExist:
#                    prdkt.amount.filter(productproperty=othrprop.productproperty,
#                                        ordercontent=other).update(ordercontent=self)
#                else:
#                    selfprop.count += othrprop.count()
#                    selfprop.save()
#                    othrprop.delete()
#
#        self.delete()
#
#    def __isub__(self, other):
#        '''.'''
#        pass


    class Meta:
        ''' '''
        verbose_name = _('content of order')
        verbose_name_plural = _('content of orders')

    def __str__(self):
        ostr = ', '.join([str(i.amount.get(ordercontent=self))+'x'+str(i) for i in self.productproperty.all()])
        return _('{order} (ID: {id}) ').format(order=ostr, id=self.id)
        # return _('{order} ').format(order=self.id)


class DefaultBasket(models.Model):
    ''' '''
    content = models.OneToOneField('OrderContent',
                                   blank=False,
                                   null=True,
                                   parent_link=True,
                                   # default=OrderContent.objects.create(),
                                   # TODO limit_choices_to without
                                   # Order basket functions
                                   # on_delete=models.PROTECT,
                                   related_name='defaultbaskets')
    name = models.CharField(max_length=15,
                            blank=False,
                            unique=True,
                            default='',
                            help_text=_('basket name'))

    class Meta:
        pass

    def __str__(self):
        return _('Default Order: {name}').format(name=self.name,
                                                           order=self.content)
#    def __iadd__(self, other):
#        self.content += other.content
#
#    def __isub__(self, other):
#        self.content -= other.content


class OrderBasket(models.Model):
    ''' .'''
    content = models.OneToOneField('OrderContent',
                                   blank=False,
                                   null=True,
                                   parent_link=True,
                                   # default=OrderContent.objects.create(),
                                   # on_delete=models.PROTECT,
                                   related_name='orderbaskets')
    week = models.DateField(blank=False,
                            null=True)
    user = models.ForeignKey('User',
                             on_delete=models.CASCADE,
                             related_name='orders',
                             blank=False,
                             null=True)

#    def __iadd__(self, other):
#        self.content += other.content
#
#    def __isub__(self, other):
#        self.content -= other.content

#    def clean(self):
#        ''' .'''
#        super().clean()
#        self.week = utils.get_monday(self.week)
#        # TODO kick product out of OrderContent if not oderable (in product an
#        # productproperties!) or don't and assert that only orderable product
#        # for this week are taken into account

    # TODO replace get_moday with get packing day and do this for all other
    # contents aswell
    def save(self, *args, **kwargs):
        ''' .'''
        # Set every date on Monday!
        self.week = utils.get_monday(self.week)
        super(OrderBasket, self).save(*args, **kwargs)

    class Meta:
        ''' .'''
        verbose_name = _('ordering basket')
        verbose_name_plural = _('ordering baskets')
        unique_together = ('week', 'user')

    def __str__(self):
        week = self.week.strftime('%W')
        year = self.week.year
        return _('{year}-{week} by {user}').format(
            year=year, week=week, user=self.user, contents=self.content)


class RegularyOrder(models.Model):

    user = models.ForeignKey('User',
                             on_delete=models.CASCADE,
                             related_name='regularyorders',
                             blank=False,
                             null=True)

    productproperty = models.ForeignKey('ProductProperty',
                                        on_delete=models.PROTECT)
    count = models.IntegerField(default=0) 

    savings = models.FloatField(default=0,
                                null=True) # TODO validate

    period = models.IntegerField(default=1) # TODO validate via approx_next_order
    # used as well to calculate the EV  and minimum 1

    # if modular product lastorder = last changing time!
    lastorder = models.DateField()

    def exchange_value(self):
        return self.count*self.productproperty.exchange_value()

    def ready(self):
        return self.exchange_value()>=self.savings() or self.savings=None

    def orderable(self):
        return (self.ready() and self.productproperty.orderable and
                self.productproperty.product.orderable and
                self.lastorder+datetime.timedelta(weeks=self.period-1)<utils.this_week())

    def current_counterorder_share(self):
        # TODO test if summ of all current counterorder shares is one!
        regord = self.user.regularyorders.objects.all()
        evSum, regSumPeriod = 0, 0
        for reg in regord:
            evSum += reg.exchange_value()
            regSumPeriod += reg.period()

        return (self.exchange_value()/self.period)*(evSum/regSumPeriod)

    # TODO changingtime for modular validate savings = None if
    # about productproperty.product.modular =True
    def approx_next_order(self):
        if self.ready():
            return self.lastorder+datetime.timedelta(weeks=self.period)
        else:
            # TODO Send warning not enough counterorders
            ccs = current_counterorder_share()
            haveings = sum([ amount.exchange_value() for amount in
                self.user.counterorders.contains.objects.all()])
            # needs to be saved
            rest = (savings - self.exchange_value())
            # approx weeks left till order
            # round integer up without import any math
            left = (rest // ccs + (rest % ccs > 0))
            if left > 3*self.period:
                # TODO Document behavior or just send warning or raise
                # Validation Error
                return None
            else: 
                return self.lastorder+datetime.timedelta(weeks=left)


    class Meta:
        ''' '''
        verbose_name = _('regularly order')
        verbose_name_plural = _('regularly orders')
        unique_together = ('user', 'productproperty')
        # FIXME decide if uniqueness should be for product

    def __str__(self):
        return _('{user} regularly orders: {count}x{product}').format(user=self.user,
                                                                      product=self.productproperty,
                                                                      count=self.count)
