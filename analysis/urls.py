__author__ = 'droghetti'
from django.conf.urls import patterns, include, url
from .views import IndiciClimaticiListView, IndiciClimaticiDetailsView, IndiciClimaticiDetailsViewExport

urlpatterns = patterns('climatlas.analysis.views',
    url(regex='^indici/$', view=IndiciClimaticiListView.as_view(), name='tabelle_indici_view'),
    url(regex='^indici/details/(?P<indice>[-\w_]+)/(?P<periodo>[-\w_]+)/$', view=IndiciClimaticiDetailsView.as_view(),
        name='tabelle_indici_details'),
    url(regex='^indici/export/(?P<indice>[-\w_]+)/(?P<periodo>[-\w_]+)/(?P<tipo_export>\w+)/$',
        view=IndiciClimaticiDetailsViewExport.as_view(), name='tabelle_indici_tmed_export'),
)