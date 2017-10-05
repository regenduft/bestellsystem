import datetime
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core import validators
from django.db import models
from django.db.models.signals import post_save
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

    depot = models.ForeignKey('Depot', on_delete=models.DO_NOTHING,
                              related_name='members', blank=True, null=True)

    weeklybasket = models.OneToOneField('WeeklyBasket',
                                        on_delete=models.CASCADE,
                                        blank=True,
                                        null=True,
                                        related_name='members')

    countshares = models.IntegerField(blank=False,
                                      default=1,
                                      validators=[validators.MinValueValidator(0)])

    assets = models.IntegerField(blank=False, default=0,
                                 validators=[validators.MinValueValidator(0)])

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

    def clean(self):
        ''' '''
        super().clean()
        if self.is_supervisor:
            if self.depot is None:
                raise ValidationError(_('A Member has to have an depot.'))
        if self.is_member:
            if self.depot is None:
                raise ValidationError(_('A Member has to have an depot.'))
        if self.defaultbasket is None:
            raise ValidationError(_('A Member has to have an '
                                    'weekly basket.'))


class ProductProperty(models.Model):
    product = models.ForeignKey('Product',
                                on_delete=models.PROTECT,
                                related_name='productproperties',
                                blank=False)

    packagesize = models.FloatField(default=1)
    producttype = models.CharField(max_length=12,
                                   default='',
                                   blank=True,
                                   help_text=_('product type'))

    def __unicode__(self):
        return _('{product} of {producttype} in {packagesize} {unit}').format(
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
    orderable = models.BooleanField(default=False)

    unit = models.CharField(max_length=15, default='',
                            help_text=_('measuring unit,'
                                        'e.g. kg or L'))

    # default value none means not modular
    module_time = models.IntegerField(help_text=_('module duration in weeks'),
                                      default=1)
    price_of_module = models.FloatField(help_text=_('modular product price'),
                                        default=0)
    # null means not exchangable
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


class ProductAmountProperty(models.Model):
    # ForeignKey or OneToOneField? parent link
    product = models.ForeignKey('Product', )
    productproperty = models.ForeignKey('ProductProperty')
    count = models.FloatField(default=0)

    ordercontents = models.ForeignKey('OrderContent',
                                      on_delete=models.DO_NOTHING,
                                      blank=True,
                                      null=True)

    class Meta:
        ''' '''
        verbose_name = _('packed product')
        verbose_name_plural = _('packed products')
        unique_together = ('ordercontents' ,'product', 'productproperty')

    def __unicode__(self):
        return '{count} {pro} in {ordr}'.format(
            count=self.count, pro=self.productproperty,
            ordr=self.ordercontents)


class OrderContent(models.Model):
    ''' '''
    products = models.ManyToManyField('Product',
                                      through='ProductAmountProperty',
                                      related_name='contentof',
                                      blank=True)

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
                                   parent_link=True,
                                   # TODO limit_choices_to without
                                   # Order basket functions
                                   on_delete=models.CASCADE,
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


class WeeklyBasket(models.Model):
    ''' '''
    defaultbasket = models.ForeignKey('DefaultBasket',
                                      blank=False,
                                      null=True,
                                      on_delete=models.DO_NOTHING)

    deorders = models.OneToOneField('OrderContent',
                                    blank=False,
                                    null=True,
                                    on_delete=models.CASCADE)

    class Meta:
        pass

    def __unicode__(self):
        return _('deordered: {deor} of {defa}').format(defa=self.defaultbasket,
                deor=self.deorders)
        pass


class OrderBasket(models.Model):
    ''' .'''
    content = models.OneToOneField('OrderContent',
                                   parent_link=True,
                                   blank=True,
                                   null=True)
    week = models.DateField(blank=False,
                            null=True)
    user = models.ForeignKey('User',
                             on_delete=models.PROTECT,
                             related_name='orders',
                             blank=False,
                             null=True)

    def clean(self):
        ''' .'''
        super().clean()
        self.week = utils.get_monday(self.week)

    def save(self, *args, **kwargs):
        ''' .'''
        # Set every date on Monday!
        self.week = utils.get_monday(self.week)
        super().save(*args, **kwargs)

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
                             on_delete=models.DO_NOTHING, # TODO 
                             related_name='regularymodularorders',
                             blank=False,
                             null=True)

    product = models.ForeignKey('Product')
    productproperty = models.ForeignKey('ProductProperty')
    count = models.IntegerField(default=0) # TODO validator

    period = models.IntegerField(default=1) # TODO validator

    # if modular product lastorder = last changing time!
    lastorder = models.DateField()

    def aprox_next_order(self):
        pass # TODO

    def book_into_order(self, orderbasket):
        pass # TODO

    class Meta:
        ''' '''
        verbose_name = _('regularly order')
        verbose_name_plural = _('regularly orders')
        unique_together = ('product', 'productproperty')

    def __unicode__(self):
        return _('{user} regularly orders: {product}').format(user=self.user,
                                                              product=self.product)
