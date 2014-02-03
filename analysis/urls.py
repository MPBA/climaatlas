__author__ = 'droghetti'
from django.conf.urls import patterns, include, url
from .views import TabelleIndiciClimaticiView, TempTxMedView, TempTxMedViewExport

urlpatterns = patterns('climatlas.analysis.views',
    url(regex='^indici/$', view=TabelleIndiciClimaticiView.as_view(), name='tabelle_indici_climatici'),
    url(regex='^indici/tmedia/$', view=TempTxMedView.as_view(), name='tabelle_indici_tmed'),
    url(regex='^indici/tmedia/export/(?P<tipo_export>\w+)/$', view=TempTxMedViewExport.as_view(), name='tabelle_indici_tmed_export'),

)