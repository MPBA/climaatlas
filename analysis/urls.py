__author__ = 'droghetti'
from django.conf.urls import patterns, include, url
from .views import (ClimateIndexListView, ClimateIndexDetailsView, ClimateIndexDetailsViewExport,
                    ClimateExtremesListView, ClimateExtremesDetailsView, ClimateExtremesDetailsViewExport,
                    DiagrammiClimaticiListView, DiagrammiClimaticiDetailsView, TrendAndamentoAnnualeList,
                    TrendClimaticiAnomalieList, TrendClimaticiAnomalieDetailsView, TrendAndamentoAnnualeDetail,
                    TrendClimaticiDistribuzioniStatisticheList, TrendClimaticiDistribuzioniStatisticheDetail,
                    MappeClimaticheListView, MappeTrendListView)

urlpatterns = patterns('analysis.views',
   ### Indici climatici ###
   url(regex='^indici/$', view=ClimateIndexListView.as_view(), name='tabelle_indici_view'),
   url(regex='^indici/details/(?P<r_name>[-\w_.]+)/(?P<periodo>[-\w_]+)/$',
       view=ClimateIndexDetailsView.as_view(),
       name='tabelle_indici_details'),
   url(regex='^indici/export/(?P<r_name>[-\w_.]+)/(?P<periodo>[-\w_]+)/(?P<tipo_export>\w+)/$',
       view=ClimateIndexDetailsViewExport.as_view(),
       name='tabelle_indici_export'),

   #### Valori estremi ###
   url(regex='^estremi/$', view=ClimateExtremesListView.as_view(), name='valori_estremi_view'),
   url(regex='^estremi/details/(?P<r_name>[-\w_.]+)/$', view=ClimateExtremesDetailsView.as_view(),
       name='valori_estremi_details'),
   url(regex='^estremi/export/(?P<r_name>[-\w_.]+)/(?P<tipo_export>\w+)/$',
       view=ClimateExtremesDetailsViewExport.as_view(), name='valori_estremi_export'),

   #### Diagrammi climatici ###
   url(regex='^diagrammi/$', view=DiagrammiClimaticiListView.as_view(), name='diagrammi_climatici_view'),
   url(regex='^diagrammi/details/(?P<pk>\d+)/(?P<periodo>[-\d_]+)/$', view=DiagrammiClimaticiDetailsView.as_view(),
       name='diagrammi_climatici_details'),

   ### Mappe climatiche ###
   url(regex='^mappe/$', view=MappeClimaticheListView.as_view(), name='mappe_climatiche_view'),
   url(regex='^mappe/trend/$', view=MappeTrendListView.as_view(), name='mappe_trend_view'),

   #### Anomalie trend ####
   url(regex='^trend/anomalie/$', view=TrendClimaticiAnomalieList.as_view(), name='trend_anomalie_view'),
   url(regex='^trend/anomalie/details/(?P<ids>[-\d]+)/$', view=TrendClimaticiAnomalieDetailsView.as_view(), name='trend_anomalie_detail'),
   url(regex='^trend/stats/distribution/$',
       view=TrendClimaticiDistribuzioniStatisticheList.as_view(),
       name='trend_distr_stats_view'),
   url(regex='^trend/stats/distribution/details/(?P<station_id>\d+)/$',
       view=TrendClimaticiDistribuzioniStatisticheDetail.as_view(),
       name='trend_distr_stats_detail'),
   url(regex='^trend/andamento/annuale/list/$',
       view=TrendAndamentoAnnualeList.as_view(),
       name='trend_annuale_list'),
   url(regex='^trend/andamento/annuale/detail/(?P<station_id>\d+)/(?P<periodo>[-\d_]+)/$',
       view=TrendAndamentoAnnualeDetail.as_view(),
       name='trend_annuale_details'),
   #

   url(r'^ajax_periodi_select/$', 'popola_periodi_select', name='ajax_periodi_select'),
   url(r'^grafico/(?P<chart_type>\d+)/(?P<stazione>\d+)/(?P<tipo_dato>[-\w_]+)/(?P<periodo>[-\w_]+)/$', 'get_charts'),
   url(r'^grafico/(?P<pk>\d+)/$', 'get_chart_by_id', name='get_chart_by_id'),
)