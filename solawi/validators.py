import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import json

def weekly_basket_validator(basket, order):
    '''Validate that order in weekly basket has user and week null.'''
    pass

def present_order_validator(basket, order):
    '''Validate Present order basket is present.'''
    pass


def regulary_order_validator(productWamount, exchange, order):
    '''
    Validate if a regularly order is possible to book.
    Args: 

    Return: 

    '''
    pass

def product_property_validator(Property, Product):
    '''
    Validate if a product property works for a product.
    Args: 
        Property: Property to check product off.
        Product: Product to check.
    Return: 

    '''
    try:
        if not Product.product == Product:
            raise ValidationError(
                _('''{Prop} is not the property of
                {Prod}.''').format(Prop=Property, Prod=Product),
                params={'ProductProperty': Property, 'Product': Product},)
    except AttributeError:
        raise ValidationError( _('''Your Product Property {prop} has no attribute
        Product.''').format(Prop=Property),
        params={'ProductProperty': Property, 'Product': Product},) 

def portion_account_validate(value):
    '''

    Args:
      value: 

    Returns:

    '''
    try:
        j = json.loads(value)
    except json.JSONDecodeError:
        raise ValidationError(
            _('{v} is not a valid JSON.').format(v=value),
            params={'value': value},)
    else:
        if not isinstance(j, list):
            raise ValidationError(
                _('The Account is just a list of tuples'
                  ' [year, week, assets].'),
                params={'value': value},)
        for i in j:
            if not isinstance(i, list) or len(i) < 3:
                raise ValidationError(
                    _('{i} is not a list in the form of'
                      ' [year, week, assets].').format(i=i),
                    params={'value': value},)
            (year, week, asset) = i
            if not isinstance(year, int) or year < datetime.MINYEAR or year > datetime.MAXYEAR:
                raise ValidationError(
                    _('{y} is not a year number.').format(y=year),
                    params={'value': value},)
            if not isinstance(week, int) or week > 53 or week < 0:
                raise ValidationError(
                    _('{w} is not a week number.').format(w=week),
                    params={'value': value},)
            if not isinstance(asset, int) or asset < 0:
                raise ValidationError(
                    _('{v} is not a valid asset').format(v=asset),
                    params={'value': value},)
