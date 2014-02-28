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
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse, HttpResponseNotFound
from .models import Station


#class based view for home page rendering
class MainView(TemplateView):
    template_name = 'climatlas/index.html'

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data()
        return context


class StazioniClimaticheView(TemplateView):
    template_name = 'climatlas/stazioni_climatiche.html'

    def get_context_data(self, **kwargs):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM station_view")
        context = super(StazioniClimaticheView, self).get_context_data()
        context['meteo_stations'] = dictfetchall(cursor)
        #context['meteo_stations'] = Station.objects./
        return context


class StazioniClimaticheDetailView(View):
    template_name = 'climatlas/stazione_climatica_detail.html'

    def get(self, request, **kwargs):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM station_view WHERE id=%s", [self.kwargs['pk']])
        context = {'station': dictfetchall(cursor)}

        try:
            station = Station.objects.get(pk=self.kwargs['pk'])
            context['station1'] = station
            context['url'] = 'img/qualita/qualita_staz%s.png' % station.code
        except Station.DoesNotExist:
            pass

        return render(request, self.template_name, context)