__author__ = 'droghetti'
from django.conf.urls import patterns, include, url
from .views import CronologiaTemperature

urlpatterns = patterns('exhibit.views',
    ### Indici climatici ###
    url(regex='^temperature/$', view=CronologiaTemperature.as_view(), name='cronologia_temperature'),
)