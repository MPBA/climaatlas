from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

#class based view for home page rendering
class CronologiaTemperature(TemplateView):
    template_name = 'exhibit/temperature_history.html'

    def get_context_data(self, **kwargs):
        context = super(CronologiaTemperature, self).get_context_data()
        return context