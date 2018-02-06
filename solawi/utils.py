#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
import datetime
from solawi import settings

def view_property(method):
    '''

    Args:
      method:

    Returns:

    '''
    @property
    def method_wrapper(self, *args, **kwargs):
        '''

        Args:
          *args:
          **kwargs:

        Returns:

        '''
        prop_name = '_' + method.__name__
        if prop_name not in self.__dict__:
            self.__dict__[prop_name] = method(self, *args, **kwargs)
        return self.__dict__[prop_name]
    return method_wrapper


def get_monday(date=None):
    '''

    Args:
      date:

    Returns:

    '''
    if date is None:
        date = datetime.date.today()
    return date - datetime.timedelta(date.weekday())


def is_leapyear(isoyear):
    '''Returns if input is leapyear.'''
    return 3 == datetime.date(isoyear,1,1).weekday() == datetime.date(isoyear,12,31).weekday()


def iso_weeks_add(isoyear, isoweek, addning):
    '''Add weeks to an isoweek in an isoyear.'''

    resweek = isoweek + adding
    resyear = isoyear

    while resweek > 53:
        if is_leapyear(resyear):
            resweek -= 53
            resyear += 1
        else:
            resweek -= 52
            resyear += 1

    if resweek == 53 and not is_leapyear(resyear):
            resweek -= 52
            resyear += 1

    return resyear, resweek


def get_delivery_week(date=None):
    '''Returns delivery year, week in isoformat according to settings.DELIVERY_DAY.'''
    if date is None:
        date = datetime.date.today()

    # if today is del day scip to nextweek
    if date.day >= settings.DELIVERY_DAY:
       date += datetime.timedelta(days=7) 
    return date.isocalendar()[:2]

def date_from_week(year=None, week=None):
    pass
