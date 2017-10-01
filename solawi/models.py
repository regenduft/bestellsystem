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
    defaultbasket = models.ForeignKey('WeeklyBasket', on_delete=models.PROTECT,
            blank=True, null=True, related_name='members')
    count_shares = models.IntegerField(blank=False, default=1,
            validators=[validators.MinValueValidator(0)])

    assets = models.IntegerField(blank=False, default=0,
            validators=[validators.MinValueValidator(0)])
    #    account = models.TextField(null=True, blank=True, default='[]',
#                               help_text=_('Containing the JSON array of '
#                                           'this users gained potentials'),
#                               validators=[portion_account_validate])

    present_order = models.OneToOneField('PresentOrderBasket',
            on_delete=models.CASCADE,
            related_name='presentorderofmember',
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
            on_delete=models.CASCADE, related_name='productproperties',
            blank=False)

    packagesize = models.IntegerField(default=1)
    producttype = models.CharField(max_length=12, default='',
            help_text=_('product type'))

    def __str__(self):
        pass
        return _('{product} of {producttype} in {packagesize} {unit}'
                ).format(product=self.product,
                        producttype=self.producttype,
                        packagesize=self.packagesize, unit=self.product.unit)

    class Meta:
        verbose_name = _('product and properties')
        verbose_name_plural = _('products and properties')
        unique_together= ('product', 'producttype', 'packagesize')

class Product(models.Model):
    ''' '''
    name = models.CharField(max_length=30, unique=True)
    orderable = models.BooleanField(default=False)
    
    unit = models.CharField(max_length=15, default='',
                            help_text=_('measuring unit,'
                                        'e.g. kg or L'))
    # default value none means not modular
    module_time = models.IntegerField( help_text=_('''module duration in weeks.
        Default'''), default = 1)
    price_of_module = models.FloatField( help_text=_('''modular product price'''), default = 0)
    # null means not exchangable
    exchange_value = models.FloatField(null=True, default=0,
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


class ProductWithAmount(models.Model):
    product = models.ForeignKey('Product', )
    productproperty = models.ForeignKey(
            'ProductProperty', 
        )
    count = models.IntegerField(default=0)

    class Meta:
        ''' '''
        verbose_name = _('product with property and amount')
        verbose_name_plural = _('product with properties and amount')

    def __str__(self):
        week = self.order.week.strftime('%W')
        year = self.order.week.year
        return '{count} of {pro}'.format(
            count=self.count, pro=self.productproperty)


class ProductInOrder(models.Model):
    #ForeignKey or OneToOneField? parent link
    productAmount = models.ForeignKey('ProductWithAmount') 

    order = models.ForeignKey('OrderBasket')

    class Meta:
        ''' '''
        verbose_name = _('product with property and amount')
        verbose_name_plural = _('product with properties and amount')

    def __str__(self):
        week = self.order.week.strftime('%W')
        year = self.order.week.year
        return '{count} {pro} by {user} in {year}-{week}'.format(
            count=self.count, pro=self.productproperty, user=self.order.user,
            year=year, week=week)


class OrderBasket(models.Model):
    ''' '''
    week = models.DateField()
    # uniquenes of the order?
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='orders')
    contents = models.ManyToManyField('Product', through='ProductInOrder')

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


    class Meta:
        ''' '''
        verbose_name = _('ordering basket')
        verbose_name_plural = _('ordering baskets')
        unique_together = ('week', 'user')


    def __str__(self):
        ostr = ', '.join([str(i) for i in self.contents.all()])
        week = self.week.strftime('%W')
        year = self.week.year
        return _('{year}-{week} by {user}: {contents}').format(
            year=year, week=week, user=self.user, contents=ostr)


class WeeklyBasket(models.Model):
    ''' '''
    order = models.OneToOneField('OrderBasket', null=True, blank=False,
            on_delete=models.CASCADE, related_name='defaultordering')
    name = models.CharField(max_length=15, blank=False, unique=True,
            default='', help_text=_('basket name'))


class PresentOrderBasket(models.Model):
    ''' '''
    order = models.OneToOneField('OrderBasket', null=True, blank=False,
            on_delete=models.DO_NOTHING, related_name='momentaryordering')

    
    def book_regulary_order(self, date):
        # do booking -> delet
        user = self.order.user
        order = OrderBasket.Objects.get(user = user).defaultbasket.order
        # update order
        # create new order
        # reset ordering
        pass

class RegularyDeorder(models.Model):
    pass

class RegularyModularOrder(models.Model):
    pass

class RegularyExchange(models.Model):

    inproduct = models.ForeignKey(
           'Product',
           #limit_choices_to =
           on_delete = models.CASCADE,
           blank=False, null=True)
    outproduct = models.ForeignKey(
           'ProductWithAmount',
           #limit_choices_to =
           on_delete = models.CASCADE,
           blank=True, null=True)
    asset = models.IntegerField(default = 0)

    #period to order in, in weeks
    period = models.IntegerField(default = 0)

#    def book_into_order(self, order):
#       regulary_order_validator(self,order)
#    
#
#       user = order.user
#       week = datetime.today()
#       
#       newP = ProductInOrder(productAmount = outproduct, order = order)
#       newP.save()
#
#       # get outproduct via Product in Order
#       return order


    class Meta:
        ''' '''
        verbose_name = _('regularly exchange of a product')
        verbose_name_plural = _('regularly exchange of products')
        unique_together = (inproduct, outproduct)

   

