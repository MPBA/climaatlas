__author__ = 'droghetti'
from django.conf.urls import patterns, include, url
from .views import (ClimateIndexListView, ClimateIndexDetailsView, ClimateIndexDetailsViewExport,
                    ClimateExtremesListView, ClimateExtremesDetailsView, ClimateExtremesDetailsViewExport,
                    DiagrammiClimaticiListView, DiagrammiClimaticiDetailsView, DiagrammiClimaticiIndexDetailsViewExport,
                    DiagrammiClimaticiEstremiDetailsViewExport,
                    TrendAndamentoAnnualeList, TrendClimaticiAnomalieList, TrendClimaticiAnomalieDetailsView,
                    TrendAndamentoAnnualeDetail, TrendClimaticiDistribuzioniStatisticheList, TrendClimaticiDistribuzioniStatisticheDetail,
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
   url(regex='^diagrammi/details/(?P<pk>\d+)/(?P<periodo>[-\d_]+)/(?P<tipo_export>\w+)/indici/$',
       view=DiagrammiClimaticiIndexDetailsViewExport.as_view(), name='diagrammi_climatici_indici_export'),
   url(regex='^diagrammi/details/(?P<pk>\d+)/(?P<periodo>[-\d_]+)/(?P<tipo_export>\w+)/estremi/$',
       view=DiagrammiClimaticiEstremiDetailsViewExport.as_view(), name='diagrammi_climatici_estremi_export'),

   ### Mappe climatiche ###
   url(regex='^mappe/$', view=MappeClimaticheListView.as_view(), name='mappe_climatiche_view'),
   url(regex='^mappe/export/(?P<ltype>[-\w_.]+)/(?P<periodo>[-\w_.]+)/(?P<month>[-\w_.]+)/$', view='export_mappe_climatiche', name='export_mappe_climatiche'),
   url(regex='^mappe/export/(?P<ltype>[-\w_.]+)/(?P<periodo>[-\w_.]+)/$', view='export_mappe_climatiche', name='export_mappe_climatiche'),
   url(regex='^mappe/export/(?P<ltype>[-\w_.]+)/(?P<periodo>[-\w_.]+)/(?P<vtype>\w*)/(?P<wheight>\w*)/(?P<month>[-\w_.]+)/$', view='export_mappe_climatiche_only_wind', name='export_mappe_climatiche_only_wind'),
   url(regex='^mappe/export/(?P<ltype>[-\w_.]+)/(?P<periodo>[-\w_.]+)/(?P<vtype>\w*)/(?P<wheight>\w*)/', view='export_mappe_climatiche_only_wind', name='export_mappe_climatiche_only_wind'),

   ### Mappe di trend ###
   url(regex='^trend/mappe/$', view=MappeTrendListView.as_view(), name='mappe_trend_view'),
   url(regex='^trend/mappe/export/(?P<ltype>[-\w_.]+)/(?P<suffix>[-\w_.]+)/(?P<year>\d+)/(?P<month>[-\w_.]+)/$', view='export_mappe_trend', name='export_mappe_trend'),

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
