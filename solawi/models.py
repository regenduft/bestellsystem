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

    defaultbasket = models.ForeignKey('WeeklyBasket',
                                      on_delete=models.PROTECT,
                                      blank=True,
                                      null=True,
                                      related_name='members')

    count_shares = models.IntegerField(blank=False,
                                       default=1,
                                       validators=[validators.MinValueValidator(0)])

    assets = models.IntegerField(blank=False, default=0,
                                 validators=[validators.MinValueValidator(0)])

    presentorder = models.OneToOneField('OrderContents',
                                        blank=False,
                                        null=True,
                                        on_delete=models.CASCADE,
                                        related_name='userofpresentorder')

    def recalculate_present_order(self):
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

#    def save(self, *args, **kwargs):
#        '''
#
#        Args:
#          *args:
#          **kwargs:
#
#        Returns:
#
#        '''
#        if self.account:
#            self.assets = 0
#            this_week = utils.date_from_week()
#            valid_days = settings.WEEKS_TO_SAVE_ACCOUNTS * 7
#            for (year, week, asset) in json.loads(self.account):
#                date_delta = this_week - utils.date_from_week(year, week)
#                if date_delta.days <= valid_days:
#                    self.assets += asset
#        super().save(*args, **kwargs)


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

    def __str__(self):
        return _('{product} of {producttype} in {packagesize} {unit}').format(
            product=self.product,
            producttype=self.producttype,
            packagesize=self.packagesize,
            unit=self.product.unit)

    class Meta:
        verbose_name = _('product and properties')
        verbose_name_plural = _('products and properties')
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

    def __str__(self):
        return self.name


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


# class ProductWithAmount(models.Model):
#    product = models.ForeignKey('Product', )
#    productproperty = models.ForeignKey('ProductProperty')
#    count = models.IntegerField(default=0)
#
#    class Meta:
#        ''' '''
#        verbose_name = _('product with property and amount')
#        verbose_name_plural = _('product with properties and amount')
#
#    def __str__(self):
#        week = self.order.week.strftime('%W')
#        year = self.order.week.year
#        return '{count} of {pro}'.format(
#            count=self.count, pro=self.productproperty)


class ProductAmountProperty(models.Model):
    # ForeignKey or OneToOneField? parent link
    product = models.ForeignKey('Product', )
    productproperty = models.ForeignKey('ProductProperty')
    count = models.IntegerField(default=0)

    ordercontents = models.ForeignKey('OrderContents',
                                      on_delete=models.DO_NOTHING,
                                      blank=True,
                                      null=True)

    class Meta:
        ''' '''
        verbose_name = _('product with amount and properties')
        verbose_name_plural = _('products with amount and properties')

    def __str__(self):
        week = self.order.week.strftime('%W')
        year = self.order.week.year
        return '{count} {pro} by {user} in {year}-{week}'.format(
            count=self.count, pro=self.productproperty, user=self.order.user,
            year=year, week=week)


class OrderContents(models.Model):

    products = models.ManyToManyField('Product',
                                      through='ProductAmountProperty',
                                      related_name='contentof',
                                      blank=True)

    def __str__(self):
        ostr = ', '.join([str(i) for i in self.products.all()])
        return _('{order} ').format(order=ostr)


class WeeklyBasket(models.Model):
    ''' '''
    content = models.OneToOneField('OrderContents',
                                   blank=False,
                                   null=True,
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

    def __str__(self):
        return _('Default Order: {name}, {order} ').format(name=self.name,
                                                           order=self.content)


class OrderBasket(models.Model):
    ''' .'''
    content = models.OneToOneField('OrderContents',
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

    def __str__(self):
        week = self.week.strftime('%W')
        year = self.week.year
        return _('{year}-{week} by {user}: {contents}').format(
            year=year, week=week, user=self.user, contents=self.content)

# class PresentOrderBasket(models.Model):
#     ''' .'''
#     order = models.OneToOneField('OrderBasket',
#             null = True, blank = False,
#             on_delete = models.DO_NOTHING,
#             parent_link = True,
#             #validator
#             related_name ='momentaryordering')
#
#     def __str__(self):
#         ostr = ', '.join([str(i) for i in self.order.contents.all()])
#         return _('Present order: {contents}').format(contents=ostr)
#
#     class Meta:
#         ''' '''
#         verbose_name = _('present ordering')
#         verbose_name_plural = _('present orderings')


class RegularyDeorder(models.Model):

    user = models.OneToOneField('User',
                                on_delete=models.PROTECT,
                                related_name='regularydeorders',
                                blank=False,
                                null=True)

    content = models.OneToOneField(
            'OrderContents',
            parent_link=True,
            # validator =
            # validate order is present order
            # limit_choices_to = weekly basket products
            blank=True)

    class Meta:
        ''' '''
        verbose_name = _('regularly deorder')
        verbose_name_plural = _('regularly deorders')

    def __str__():
        ostr = ', '.join([str(i) for i in self.content.contents.all()])

        return _('{user} regularly deorders: {content}').format(user=self.user,
                                                                content=self.content)


class RegularyModularOrder(models.Model):

    user = models.OneToOneField('User',
                                on_delete=models.PROTECT,
                                related_name='regularymodularorders',
                                blank=False,
                                null=True)

    content = models.OneToOneField(
            'OrderContents',
            parent_link=True,
            # validator =
            # validate order is present order
            # limit_choices_to = {'modular': True},
            blank=True)

    starttime = models.DateField()

    class Meta:
        ''' '''
        verbose_name = _('regularly modular order')
        verbose_name_plural = _('regularly modular orders')

    def __str__():
        return _('{user} regularly orders: {content}').format(user=self.user,
                                                              content=self.content)


class RegularyExchange(models.Model):

    user = models.OneToOneField('User',
                                on_delete=models.PROTECT,
                                related_name='regularyexchanges',
                                blank=False,
                                null=True)

    inproduct = models.ManyToManyField(
            'Product',
            # limit_choices_to = weekly basket products
            # validate order is present order
            blank=True)

    outproduct = models.OneToOneField(
            'OrderContents',
            parent_link=True,
            # limit_choices_to =
            blank=True)

    asset = models.IntegerField(default=0)

    # period to order in, in weeks
    period = models.IntegerField(default=1)

    def aprox_next(self):
        '''Approximate Nr. of weeks to next order of week to next order.'''
        pass

    class Meta:
        ''' '''
        verbose_name = _('regularly exchange')
        verbose_name_plural = _('regularly exchanges')

    def __str__():
        instr = ', '.join([str(i) for i in self.inproduct.all()])
        return _('''Exchange {inproduct} for {outproduct}''').format(
                inproduct=instr,
                outproduct=self.outproduct)
