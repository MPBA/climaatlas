# -*- encoding: utf-8 -*-
__author__ = 'ernesto'

#This file contains only the views for the main app. It's made just to render an home page for the project

from django.views.generic import TemplateView
from django.shortcuts import render
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseBadRequest


#class based view for home page rendering
class MainView(TemplateView):
    template_name = 'climatlas/index.html'

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data()
        return context


class StazioniClimaticheView(TemplateView):
    template_name = 'climatlas/stazioni_climatiche.html'

    def get_context_data(self, **kwargs):
        context = super(StazioniClimaticheView, self).get_context_data()
        return context
