__author__ = 'ernesto'

from django import template
import locale
from analysis.models import Chart
from climatlas.utils import periodi_graph_dict
from django.db import transaction, connection, DatabaseError
from django.conf import settings
from django.core import urlresolvers
import random
locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
register = template.Library()

@register.assignment_tag()
def periodi_climatici(station_id, tipi_grafici):
    periodi = periodi_graph_dict(station_id, tipi_grafici)
    for k, p in periodi.iteritems():
        periodi[k] = '-'.join(p)
    return periodi


@register.assignment_tag()
def dati_anomalie_disponibili(station, tipi_grafici):
    dati = station.chart_set.filter(chart_type__in=tipi_grafici).values_list('chart_type')
    return {d[0] for d in list(dati)}