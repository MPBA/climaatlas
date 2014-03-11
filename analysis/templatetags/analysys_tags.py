__author__ = 'ernesto'

from django import template
import locale
from analysis.models import Chart
from climatlas.utils import periodi_graph_dict, anno_graph_dict, intervallo_graph_dict
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
def intervalli_climatici(station_id, tipi_grafici):
    intervalli = intervallo_graph_dict(station_id, tipi_grafici)
    for k, p in intervalli.iteritems():
        intervalli[k] = '-'.join(p)

    jsonlist = []
    for k, p in intervalli.iteritems():
        jsonlist.append({
            'intervallo': k,
            'ids': p,
            'idslist': list(p.split('-'))
        })
    print jsonlist
    return sorted(jsonlist, key=lambda k:k['intervallo'])


@register.assignment_tag()
def dati_anomalie_disponibili(station, tipi_grafici):
    dati = station.chart_set.filter(chart_type__in=tipi_grafici).values_list('chart_type')
    return {d[0] for d in list(dati)}


@register.assignment_tag()
def dati_disponibili(station, tipi_grafici):
    dati = station.chart_set.filter(chart_type__in=tipi_grafici).values_list('chart_type')
    return {d[0] for d in list(dati)}


@register.filter()
def get_dati_chart(chart_id):
    dati = Chart.objects.get(pk=chart_id)
    return dati.variables

@register.filter()
def dateformat(datatxt):
    try:
        data = datatxt.split('-')
        return u'%s/%s/%s' % (data[2], data[1], data[0])
    except:
        data = datatxt
        return data
