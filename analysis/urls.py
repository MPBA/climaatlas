__author__ = 'droghetti'
from django.conf.urls import patterns, include, url
from .views import TabelleIndiciClimaticiView

urlpatterns = patterns('climaatlas.analysis.views',
    url(regex='^indici/$', view=TabelleIndiciClimaticiView.as_view(), name='tabelle_indici_climatici'),
)