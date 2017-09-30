import datetime
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core import validators
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from solawi.validators import portion_account_validate
from django.utils.translation import ugettext_lazy as _
import json
from solawi import utils


class User(AbstractUser):
    ''' '''
    is_member = models.BooleanField(_('Make a paying member'), default=True)
    is_supervisor = models.BooleanField(_('Make a depot supervisor'),
            default=False)

    depot = models.ForeignKey('Depot', on_delete=models.CASCADE,
            related_name='members', blank=True, null=True)
    defaultbasket = models.ForeignKey('OrderBasket', on_delete=models.CASCADE,
            related_name='members', blank=True,
            null=True)
    count_shares = models.IntegerField(null=True, blank=True, default=0,
            validators=[validators.MinValueValidator(0)])

    assets = models.IntegerField(null=True, blank=True, default=0,
            validators=[validators.MinValueValidator(0)])
    #    account = models.TextField(null=True, blank=True, default='[]',
#                               help_text=_('Containing the JSON array of '
#                                           'this users gained potentials'),
#                               validators=[portion_account_validate])

    momentary_order = models.ForeignKey('WeeklyBasket',
            on_delete=models.CASCADE,
            related_name='members',
            blank=True,
            null=True)

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
            on_delete=models.CASCADE, related_name='productproperties')

    packagesize = models.IntegerField()
    unit = models.CharField(max_length=15,
                            help_text=_('The unit to measure this food in, '
                                        'e.g. kg or L'))
    producttype = models.CharField(max_length=12,
            help_text=_('Type of the product'))

    def __str__(self):
        pass


class Product(models.Model):
    ''' '''
    name = models.CharField(max_length=30, unique=True)
    orderable = models.BooleanField(default=False)
    
    # default value none means not modular
    modular = ( models.IntegerField(), models.FloatField( help_text=_('The price of the modular product.')))
    # 0 means not exchangable
    exchange_value = models.FloatField(null=True, blank=True, default=0,
        validators=[validators.MinValueValidator(0)],
        help_text=_('The exchange value per unit.'))


    class Meta:
        ''' '''
        verbose_name = _('product')
        verbose_name_plural = _('products')

    def __str__(self):
        return self.name

class Depot(models.Model):
    ''' '''
    name = models.CharField(max_length=30, unique=True)
    location = models.CharField(max_length=30)

    class Meta:
        ''' '''
        verbose_name = _('depot')
        verbose_name_plural = _('depots')

    def __str__(self):
        return _('{name} at {location}').format(name=self.name,
                                                location=self.location)

class ProductAmountPerOrder(models.Model):
    product = models.ForeignKey('Product')
    order = models.ForeignKey('OrderBasket')
    count = models.IntegerField(default=0)

    def __str__(self):
        week = self.basket.week.strftime('%W')
        year = self.basket.week.year
        return '{count} of {product} for {user} in {year}-{week}'.format(
            count=self.count, product=self.product, user=self.basket.user,
            year=year, week=week)

    class Meta:
        ''' '''
        verbose_name = _('PAPO')
        verbose_name_plural = _('PAPOs')

    def __str__(self):
        return _('{name} at {location}').format(name=self.name,
                                                location=self.location)

class OrderBasket(models.Model):
    ''' '''
    week = models.DateField()
    # uniquenes of the order?
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='orders')
    contents = models.ManyToManyField('Product', through='ProductAmountPerOrder')

    edited_weekly_basket = models.BooleanField(
        _('Has edited the weekly basket for this week'), default=False)

    class Meta:
        ''' '''
        verbose_name = _('order basket')
        verbose_name_plural = _('order baskets')
        unique_together = ('week', 'user')

    def clean(self):
        ''' '''
        super().clean()
        self.week = utils.get_moday(self.week)

    def save(self, *args, **kwargs):
        '''

        Args:
          *args:
          **kwargs:

        Returns:

        '''
        # Set every date on Monday!
        self.week = utils.get_moday(self.week)
        super().save(*args, **kwargs)

    def __str__(self):
        ostr = ', '.join([str(i) for i in self.contents.all()])
        week = self.week.strftime('%W')
        year = self.week.year
        return _('{year}-{week} by {user}: {contents}').format(
            year=year, week=week, user=self.user, contents=ostr)


class WeeklyBasket(models.Model):
    ''' '''
    order = OrderBasket()
