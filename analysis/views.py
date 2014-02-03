from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.base import View
from .models import ChiaveIndiciClimatici, TempTxMed

class TabelleIndiciClimaticiView(TemplateView):
    template_name = 'analysis/tabelle_indici_climatici.html'

    def get_context_data(self, **kwargs):
        context = super(TabelleIndiciClimaticiView, self).get_context_data()

        indici = ChiaveIndiciClimatici.objects.all()
        context['indici'] = indici

        return context


class TempTxMedView(TemplateView):
    template_name = 'analysis/tabelle_temp.html'

    def get_context_data(self, **kwargs):
        context = super(TempTxMedView, self).get_context_data()

        tb = TempTxMed.objects.all()
        context['tabella'] = tb

        return context