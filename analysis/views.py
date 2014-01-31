from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.base import View
from .models import ChiaveIndiciClimatici

class TabelleIndiciClimaticiView(TemplateView):
    template_name = 'analysis/tabelle_indici_climatici.html'

    def get_context_data(self, **kwargs):
        context = super(TabelleIndiciClimaticiView, self).get_context_data()

        indici = ChiaveIndiciClimatici.objects.all()
        context['indici'] = indici

        return context
