__author__ = 'droghetti'
from django.conf.urls import patterns, include, url
from .views import IndiciClimaticiListView, IndiciClimaticiDetailsView, IndiciClimaticiDetailsViewExport,\
                   ValoriEstremiListView, ValoriEstremiDetailsView, ValoriEstremiDetailsViewExport

urlpatterns = patterns('climatlas.analysis.views',
    ### Indici climatici
    url(regex='^indici/$', view=IndiciClimaticiListView.as_view(), name='tabelle_indici_view'),
    url(regex='^indici/details/(?P<indice>[-\w_]+)/(?P<periodo>[-\w_]+)/$', view=IndiciClimaticiDetailsView.as_view(),
        name='tabelle_indici_details'),
    url(regex='^indici/export/(?P<indice>[-\w_]+)/(?P<periodo>[-\w_]+)/(?P<tipo_export>\w+)/$',
        view=IndiciClimaticiDetailsViewExport.as_view(), name='tabelle_indici_export'),
    ### Valori estremi
    url(regex='^estremi/$', view=ValoriEstremiListView.as_view(), name='valori_estremi_view'),
    url(regex='^estremi/details/(?P<indice>[-\w_]+)/$', view=ValoriEstremiDetailsView.as_view(),
        name='valori_estremi_details'),
    url(regex='^estremi/export/(?P<indice>[-\w_]+)/(?P<tipo_export>\w+)/$',
        view=ValoriEstremiDetailsViewExport.as_view(), name='valori_estremi_export'),
)