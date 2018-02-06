#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import date
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
    # probably change this field into member since/ next order after vecation
    is_member = models.BooleanField(_('Make a paying member'), default=True)
    is_supervisor = models.BooleanField(_('Make a depot supervisor'),
                                        default=False)

    depot = models.ForeignKey('Depot', on_delete=models.PROTECT,
                              related_name='members', blank=False, null=True)

    countshares = models.IntegerField(blank=False,
                                      default=1,
                                      validators=[validators.MinValueValidator(0)])

    defaultbasket = models.ForeignKey('DefaultBasket',
                                      blank=False,
                                      null=True,
                                      on_delete=models.PROTECT)

    assets = models.IntegerField(blank=False, default=0,
                                 validators=[validators.MinValueValidator(0),
                                             validators.MaxValueValidator(settings.MAX_USER_ASSET)])


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

    def clean(self):
        ''' '''
        if self.is_supervisor:
            if self.depot is None:
                raise ValidationError(_('A Member has to have an depot.'))
        if self.is_member:
            if self.depot is None:
                raise ValidationError(_('A Member has to have an depot.'))
        if self.defaultbasket is None:
            raise ValidationError(_('A Member has to have an default basket.'))
        if self.assets > settings.MaxValueValidator:
            self.assets = settings.MaxValueValidator
            self.save()


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

    max_at_once = models.IntegerField(help_text=_('max amount orderable at once'),
                                      blank=False,
                                      default=5)

    @property
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
    '''Intermediate model for OrderContent and Productproperty.
    
    Prefetch_related productproperty and productproperty__product if you use
    the @properties'''

    productproperty = models.ForeignKey('ProductProperty',
                                        related_name='amount',
                                        on_delete=models.PROTECT,
                                        blank=False)
    count = models.IntegerField(default=1,
                                validators = [ validators.MinValueValidator(1) ]
                                )

    ordercontent = models.ForeignKey('OrderContent',
                                      related_name='contains',
                                      on_delete=models.CASCADE,
                                      blank=False)

    @property
    def exchange_value(self):
        return self.count*self.productproperty.exchange_value
    
    def clean(self):
        productp = self.productproperty
        if count > productp.max_at_once/productp.packagesize: 
            raise ValidationError(_('You can not order more then {max} of'
                '{product} at onces ').format(maxx = productp.max_at_once, product=productp))

    class Meta:
        ''' '''
        verbose_name = _('packed product')
        verbose_name_plural = _('packed products')
        # uniqueness for productproperty to map e.g. flour or oat flakes types
        unique_together = ('ordercontent' ,'productproperty')

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
        '''Add count or create productproperty for ordercontent.

        defaults count=1 
        returns: amount.exchange_value , created'''
        amount, created = Amount.objects.get_or_create(
                productproperty=prdctprop, 
                ordercontent=self,
                defaults={'count': count})

        if not created:
            amount.count += count
            amount.save()

        return amount.exchange_value, created

    def sub_or_delete_product(self, prdctprop, count=None):
        '''Subtract count or delete productproperty form ordercontent.

        defaults count=None deleates product
            returns: (min(amount.echange_value, prdctprop.exchange_value) , persists) of amount'''
        try:
            amount = Amount.objects.get(productproperty=prdctprop, 
                                        ordercontent=present.content)
            value = amount.exchange_value

            if amount.count > count:
                amount.count -= count
                amount.save()
                return prdctprop.exchange_value, True
            else:
                amount.delete()
                return value, False

        except Amount.DoesNotExist:
            # No Product -> no value
            return 0, False

    class Meta:
        verbose_name = _('content of order')
        verbose_name_plural = _('content of orders')

    def __str__(self):
        ostr = ', '.join([str(i.product)[:3] for i
            in self.productproperties.all()])
        return _('{order} (ID: {id}) ').format(order=ostr, id=self.id)
        # return _('{order} ').format(order=self.id)


class DefaultBasket(models.Model):
    ''' '''
    content = models.OneToOneField('OrderContent',
                                   blank=False,
                                   null=True,
                                   parent_link=True,
                                   on_delete=models.PROTECT,
                                   related_name='defaultbaskets')

    name = models.CharField(max_length=15,
                            blank=False,
                            unique=True,
                            default='',
                            help_text=_('basket name'))

    class Meta:
        verbose_name = _('default orderbasket')
        verbose_name_plural = _('default orderbaskets')

    def __str__(self):
        return _('Default Order: {name}').format(name=self.name,
                                                 order=self.content)


class OrderBasket(models.Model):
    ''' .'''
    content = models.OneToOneField('OrderContent',
                                   blank=False,
                                   null=True,
                                   parent_link=True,
                                   on_delete=models.PROTECT,
                                   related_name='order')

    isoweek = models.IntegerField(default=1,
                                  validators=[validators.MinValueValidator(1),
                                              validators.MaxValueValidator(53)],  
                                  blank=False)
    isoyear = models.IntegerField(default=1,
                                  validators=[validators.MinValueValidator(2018)],
                                  blank=False)

    user = models.ForeignKey('User',
                             on_delete=models.CASCADE,
                             related_name='orderbaskets',
                             blank=False,
                             null=True)

    def add_to_order(self, prdctprop, count=1, account=True):
        '''Add a product to order.'''
        value = prdctprop.exchange_value*count

        if not (prdctprop.orderable and prdctprop.product.orderable):
            raise ValidationError(_('%(prdctprop)s is not orderable'),
                                    params={'prdctprop': prdctprop},
                                    code='notorderable')
                                    # TODO Maybe pass why not orderable

        elif account:
            if self.user.assets < value:
                raise ValidationError(_('%(user)s assets where to low to order %(count)s %(prdctprop)s'),
                                        params={'prdctprop': prdctprop,
                                                'count': count,
                                                'prdctprop': prdctprop},
                                        code='notorderable')

            else:
                value, created = self.content.add_or_create_product(prdctprop, count)

                self.user.assets -= value
                self.user.save()
        else:
            self.content.add_or_create_product(prdctprop, count)

    def sub_from_order(self, prdctprop, count=None, account=True):
        '''Subtract or delete a product from order.'''

        value, persists = self.content.sub_or_delete_product(prdctprop, count)

        if not persits and value == 0:
            raise ValidationError(_('%(prdctprop)s was not ordered'),
                                    params={'prdctprop': productproperty},
                                    code='notordered')
        elif account and value > 0:
            self.user.assets += value
            self.user.clean()
            self.user.save()

    def save(self, *args, **kwargs):
        ''' .'''
        # TODO kick product out of OrderContent if not oderable (in product an
        # productproperties!) or don't and assert that only orderable product
        # for this week are taken into account
        # Set every date on Monday!
        super(OrderBasket, self).save(*args, **kwargs)

    class Meta:
        ''' .'''
        verbose_name = _('ordering basket')
        verbose_name_plural = _('ordering baskets')
        unique_together = ('isoweek', 'isoyear', 'user')

    def __str__(self):
        return _('{week} {year} by {user}').format(
            week=self.isoweek, year=selfisoyear, user=self.user)


class RegularyOrder(models.Model):

    user = models.ForeignKey('User',
                             on_delete=models.CASCADE,
                             related_name='regularyorders',
                             blank=False,
                             null=True)

    productproperty = models.ForeignKey('ProductProperty',
                                        on_delete=models.PROTECT)
    count = models.IntegerField(default=1,)

    period = models.IntegerField(default=1,
                                 validators=[validators.MinValueValidator(1),
                                             validators.MaxValueValidator(52)])
    #approx_next_order or the current counterorder share

    lastorder_isoweek = models.IntegerField(default=1,
                                  validators=[validators.MinValueValidator(1),
                                              validators.MaxValueValidator(53)],  
                                  blank=False)
    lastorder_isoyear = models.IntegerField(default=1,
                                  validators=[validators.MinValueValidator(2018)],
                                  blank=False)

    lastaccses = models.DateField(auto_now=True)

    @property
    def is_counterorder(self):
        '''True if is self is counterorder else order.'''
        return self.count < 0

    @property
    def is_ready_order(self):
        '''True if self ist ready to be booked and not counterorder.'''
        if self.is_counterorder:
            return False
        bookingyear, bookingweek = utils.iso_weeks_add(self.lastorder_isoyear,
                                                       self.lastorder_isoweek,
                                                       self.period)
        thisyear, thisweek = date.today().isocalender[:1]
        return bookingweek <= thisweek or bookingyear < thisyear

    class Meta:
        ''' '''
        verbose_name = _('regularly order')
        verbose_name_plural = _('regularly orders')
        unique_together = ('user', 'productproperty')

    def __str__(self):
        return _('{user} regularly orders: {count}x{product}').format(user=self.user,
                                                                      product=self.productproperty,
                                                                      count=self.count)
