#!/usr/bin/env python
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

# TODO Work on unicode problems try Gemüse as Product

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

    assets = models.IntegerField(blank=False, default=0,
                                 validators=[validators.MinValueValidator(0)])

    def create_present_order(self):
        try:
            presentorder = OrderBasket.objects.create(week=utils.this_week(),
                user=self)
        except ObjectDoesExist:
            pass


    class Meta:
        ''' '''
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __unicode__(self):
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
                                related_name='productproperties',
                                blank=False)

    orderable = models.BooleanField(default=True)

    packagesize = models.FloatField(default=1)
    producttype = models.CharField(max_length=15,
                                   default='',
                                   blank=True,
                                   help_text=_('product type'))

    def ex_value(self):
        return product.exchange_value*packagesize

    def __unicode__(self):
        return _('{producttype}, {product}  in {packagesize} {unit}').format(
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

    # default 0 means not exchangable
    exchange_value = models.FloatField(null=True,
                                       default=0,
                                       validators=[validators.MinValueValidator(0)],
                                       help_text=_('exchange value per unit'))

    class Meta:
        ''' '''
        verbose_name = _('product')
        verbose_name_plural = _('products')

    def __unicode__(self):
        return _('{name}').format(name=self.name)


class Depot(models.Model):
    ''' '''
    name = models.CharField(max_length=30, unique=True)
    location = models.CharField(max_length=30, default='')

    class Meta:
        ''' '''
        verbose_name = _('depot')
        verbose_name_plural = _('depots')

    def __unicode__(self):
        return _('{name} at {location}').format(name=self.name,
                                                location=self.location)


class Amount(models.Model):
    productproperty = models.ForeignKey('ProductProperty',
                                        on_delete=models.PROTECT)
    count = models.IntegerField(default=1)

    ordercontent = models.ForeignKey('OrderContent',
                                      related_name='contains',
                                      on_delete=models.CASCADE,
                                      blank=False,
                                      null=True)

    def calc_exchange_value(self):
        if product.orderable and productproperty.orderable:
            return self.count*self.product.exchange_value
        else:
            return 0 # TODO document this!

    class Meta:
        ''' '''
        verbose_name = _('packed product')
        verbose_name_plural = _('packed products')
        unique_together = ('ordercontent' ,'productproperty')

    def __unicode__(self):
        return '{count} {pro} in {ordr}'.format(
            count=self.count, pro=self.productproperty,
            ordr=self.ordercontent)


class OrderContent(models.Model):
    ''' '''
    products = models.ManyToManyField('ProductProperty',
                                      through='Amount',
                                      related_name='contentof',
                                      blank=False)

    def account_other_in(self, other):
        '''.'''
    #TODO TEST this! FIXME rework it!
        tomerge = self.products.all().intersection(other.products.all())
        toinclude = other.products.all().difference(self.products.all())

        for prdkt in toinclude:
            prdkt.packedin.filter(product=prdkt,
                    ordercontent=other).update(ordercontent=self)
        for prdkt in tomerge:

            for othrprop in other.contains.filter(product=prdkt):
                try: 
                    selfprop = self.contains.get(ordercontent=self,
                            productproperty=othrprop.productproperty,
                            product=othrprop.product) # may be prdkt as well
                except ObjectDoesNotExist:
                    prdkt.packedin.filter(product=prdkt,
                            productproperty=othrprop.productproperty,
                            ordercontent=other).update(ordercontent=self)
                else:
                    selfprop.count += othrprop.count()
                    selfprop.save()
                    othrprop.delete()

        self.delete()


    class Meta:
        ''' '''
        verbose_name = _('content of order')
        verbose_name_plural = _('content of orders')

    def __unicode__(self):
        ostr = ', '.join([str(i) for i in self.products.all()])
        return _('{order} (ID: {id}) ').format(order=ostr, id=self.id)
        # return _('{order} ').format(order=self.id)


class DefaultBasket(models.Model):
    ''' '''
    content = models.OneToOneField('OrderContent',
                                   blank=False,
                                   null=True,
                                   # default=OrderContent.objects.create(),
                                   # TODO limit_choices_to without
                                   # Order basket functions
                                   on_delete=models.PROTECT,
                                   related_name='defaultordering')
    name = models.CharField(max_length=15,
                            blank=False,
                            unique=True,
                            default='',
                            help_text=_('basket name'))

    class Meta:
        pass

    def __unicode__(self):
        return _('Default Order: {name}, {order} ').format(name=self.name,
                                                           order=self.content)


class OrderBasket(models.Model):
    ''' .'''
    content = models.OneToOneField('OrderContent',
                                   blank=False,
                                   null=True,
                                   # default=OrderContent.objects.create(),
                                   on_delete=models.PROTECT)
    week = models.DateField(blank=False,
                            null=True)
    user = models.ForeignKey('User',
                             on_delete=models.CASCADE,
                             related_name='orders',
                             blank=False,
                             null=True)


    def clean(self):
        ''' .'''
        super().clean()
        self.week = utils.get_monday(self.week)
        # TODO kick product out of OrderContent if not oderable (in product an
        # productproperties!) or don't and assert that only orderable product
        # for this week are taken into account

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

    def __unicode__(self):
        week = self.week.strftime('%W')
        year = self.week.year
        return _('{year}-{week} by {user}: {contents}').format(
            year=year, week=week, user=self.user, contents=self.content)


class RegularyOrder(models.Model):

    user = models.ForeignKey('User',
                             on_delete=models.CASCADE,
                             related_name='regularymodularorders',
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

    def aprox_next_order(self):
        # if bigger than a certain period never
        # if higher than period -> warning
        pass # TODO

    def book_into_current_order(self):
        # check if period is already reached (probably not necessary)
        if self.lastorder+datetime.timedelta(weeks=period)<utils.this_week():
            return
        # check savings are high enough or null, if not do nothing and return
        elif self.savings<self.amount*self.productproperty.ex_value():
            return
        # book into current order of the user
        else:
            # FIXME get or create?
            current = OrderBasket.objects.get(user=self.user, week=utils.this_week())
            Amount(count=self.count, ordercontent=current.ordercontent,
                   productproperty=self.productproperty)
            # if modular don't change last order
            if self.savings==None:
                return
            else:
                self.lastorder=utils.this_week()

    class Meta:
        ''' '''
        verbose_name = _('regularly order')
        verbose_name_plural = _('regularly orders')
        unique_together = ('user', 'productproperty')
        # FIXME uniqueness should somehow refer to the product in
        # productproperty

    def __unicode__(self):
        return _('{user} regularly orders: {product}').format(user=self.user,
                                                              product=self.productproperty)
