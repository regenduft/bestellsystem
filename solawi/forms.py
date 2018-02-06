import copy
from django import forms
from solawi.models import (
    User,
    OrderBasket,
)

# Old code for use in validation/ warning process of assets and ordering
#    def current_counterorder_share(self, regords=None):
#        # TODO test if summ of all current counterorder shares is one!
#        if regords == None:
#            regord = self.user.regularyorders.objects.all().prefetch_related('productproperty__product')
#
#        evSum, regSumPeriod = 0, 0
#        for reg in regords:
#            evSum += reg.exchange_value
#            regSumPeriod += reg.period()
#
#        return (self.exchange_value/self.period)*(evSum/regSumPeriod)
#
#    # TODO changingtime for modular validate savings = None if
#    # about productproperty.product.modular =True
#    def approx_next_order(self):
#        if self.ready():
#            return _('surely'), self.lastorder+datetime.timedelta(weeks=self.period)
#        else:
#            # TODO Send warning not enough counterorder
#            # calculate current counterorder share
#            cc = current_counterorder_share()*sum([ amount.exchange_value for amount in
#                self.user.counterorder.contains.all()])
#
#            # needs to be saved
#            rest = (savings - self.exchange_value)
#            # approx weeks left till order
#            # round integer up without import any math
#            left = (rest // ccs + (rest % ccs > 0))
#            if left > 3*self.period:
#                # TODO Document behavior or just send warning or raise
#                # Validation Error
#                return _('never'), None
#            elif:
#                return _('longer than wished'), self.lastorder+datetime.timedelta(weeks=left)
#            else: 
#                return _('approximately'), self.lastorder+datetime.timedelta(weeks=left)

#class WeeklyBasketForm(forms.Form):
#    ''' '''
#    prefix = 'weekly'
#    contents = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)
#
#    def __init__(self, orderbasket, weeklybasket, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#
#        choices, initial = self._get_weekly_basket_form_choices(orderbasket,
#                                                                weeklybasket)
#        self.fields['contents'].choices = choices
#        self.fields['contents'].initial = initial
#
#    def _get_weekly_basket_form_choices(self, orderbasket, weeklybasket):
#        order_set = weekly_set = weeklybasket.contents.all()
#        if orderbasket.edited_weekly_basket:
#            order_set = orderbasket.contents.all()
#        choices = [(i.id, str(i)) for i in weekly_set]
#        initial = [s.id for s in order_set if s in weekly_set]
#        return choices, initial
#
#
#class OrderBasketForm(forms.ModelForm):
#    ''' '''
#    prefix = 'basket'
#
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#
#        if self.instance.edited_weekly_basket:
#            order_set = self.instance.contents.all()
#            weekly_set = list(self.instance.user.weeklybasket.contents.all())
#            already_removed = [False] * len(weekly_set)
#            choices = []
#            for item in order_set:
#                if item not in weekly_set:
#                    choices.append(item)
#                elif already_removed[weekly_set.index(item)]:
#                    choices.append(item)
#                else:
#                    already_removed[weekly_set.index(item)] = True
#            self.fields['contents'].choices = choices
#
#    class Meta:
#        ''' '''
#        model = OrderBasket
#        fields = ['contents']
