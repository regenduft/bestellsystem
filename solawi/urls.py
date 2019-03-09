"""solawi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from . import views
from .views import *


urlpatterns = [
    url('^', include('django.contrib.auth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^test/(?P<username>[a-zA-Z0-9\.@+-_]*)/$', views.test, name='test'),
    url(r'^accounts/profile/$', BaseMemberView.as_view(), name='basemember'),
    url(r'^accounts/order/$', BaseMemberView.as_view(), name='basemember'),
    url(r'^accounts/order/edit/$', BaseMemberView.as_view(), name='basemember'),
    url(r'^products/$', ProductList.as_view(), name='products'),
    # url(r'^accounts/order/(?P<year>[0-9]{4})/(?P<week>[1-5]?[1-9])/$', Orderview.as_view(), name='orderdetail'),
    url(r'^order/(?P<username>[a-zA-Z0-9\.@+-_]*)/(?P<year>[0-9]{4})/(?P<week>[1-5]?[1-9])/$', views.order, name='order'),

    
    # url(r'^depots/', views.DepotTestView.as_view(), name='depotview' ),
#    url(r'^woche/$', views.WeekView.as_view()),
#    url(r'^woche/(?P<year>[0-9]{4})/$', views.WeekView.as_view()),
#    url(r'^woche/(?P<year>[0-9]{4})/(?P<week>[0-9]{1,2})/$', views.WeekView.as_view()),
]
