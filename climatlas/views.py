# -*- encoding: utf-8 -*-
__author__ = 'ernesto'

#This file contains only the views for the main app. It's made just to render an home page for the project

from django.views.generic import TemplateView
from django.views.generic.base import View
from .utils import dictfetchall
from django.db import transaction, connection, DatabaseError, IntegrityError
from django.shortcuts import render
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse, HttpResponseNotFound, Http404
from .models import Station
from analysis.models import Chart


#class based view for home page rendering
class MainView(TemplateView):
    template_name = 'climatlas/index.html'

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data()
        return context


class StazioniClimaticheView(TemplateView):
    template_name = 'climatlas/stazioni_climatiche.html'

    def get_context_data(self, **kwargs):
        #cursor = connection.cursor()
        #cursor.execute("SELECT * FROM station_view")
        context = super(StazioniClimaticheView, self).get_context_data()
        #context['meteo_stations'] = dictfetchall(cursor)
        station = Station.objects.all().order_by('stname')
        context['meteo_stations'] = station
        return context


class StazioniClimaticheDetailView(TemplateView):
    template_name = 'climatlas/stazione_climatica_detail.html'

    def get_context_data(self, **kwargs):
        context = super(StazioniClimaticheDetailView, self).get_context_data()
        #try:
        station = Station.objects.get(pk=self.kwargs['pk'])
        context['station'] = station
        try:
            quality_graph = Chart.objects.get(station_id=station.pk, chart_type=22)
            context['graph_id'] = quality_graph.pk
        except Chart.DoesNotExist:
            context['graph_id'] = "notfound"
        return context
        #except Station.DoesNotExist:
        #    return Http404