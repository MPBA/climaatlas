__author__ = 'arbitrio@fbk.eu'
#! /usr/bin/python
# -*- encoding: utf-8 -*-

from django import http
from django.template.loader import get_template
from django.template import Context
from analysis.models import Chart, ClimateIndexData
import xhtml2pdf.pisa as pisa
import cStringIO as StringIO
import cgi
from django.conf import settings
from django.contrib.staticfiles.finders import find as find_static_file


def dictfetchall(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


def fetch_resources(uri, rel):
    if uri.startswith(settings.STATIC_URL):
        uri = uri[len(settings.STATIC_URL):]
        path = find_static_file(uri)
        if path is None:
            raise Exception('Error retrieving static file ' +
                            '"{0}" during pdf generation.'.format(uri))
    else:
        print ('Warning: path {0} is not a staticfile'.format(uri))
        path = uri

    return path


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    html = template.render(context)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("ISO-8859-1")), result, link_callback=fetch_resources)
    if not pdf.err:
        return http.HttpResponse(result.getvalue(), mimetype='application/pdf')
    return http.HttpResponse('We had some errors<pre>%s</pre>' % cgi.escape(html))


def periodi_graph_dict(station_id, tipi_grafici):
    periodi = Chart.objects.filter(chart_type__in=tipi_grafici, station_id=station_id).values_list('variables', 'id')
    periodi_dict = []
    for p in periodi:
        periodi_dict.append({'periodo': p[0]['periodo_climatico'], 'id': p[1]})
    results = {}
    for pl in periodi_dict:
        if pl['periodo'] not in results.keys():
            results[pl['periodo']] = []
        results[pl['periodo']].append(str(pl['id']))
    return results


def anno_graph_dict(station_id, tipi_grafici, periodo_climatico):
    charts = Chart.objects.filter(station_id=station_id,
                                  chart_type__in=tipi_grafici,
                                  variables__contains={
                                      'periodo_climatico': periodo_climatico}).values_list('variables', 'id').order_by('chart_type')
    anni_dict = []
    for c in charts:
        anni_dict.append({'anno': c[0]['anno'], 'id': c[1]})
    results = {}
    for a in anni_dict:
        if a['anno'] not in results.keys():
            results[a['anno']] = []
        results[a['anno']].append(str(a['id']))
    return results


def intervallo_graph_dict(station_id, tipi_grafici):
    charts = Chart.objects.filter(station_id=station_id, chart_type__in=tipi_grafici).values_list('variables', 'id').order_by('-chart_type')
    intervallo_dict = []
    for c in charts:
        intervallo_dict.append({'intervallo': c[0]['intervallo'], 'id': c[1]})
    results = {}
    for a in intervallo_dict:
        if a['intervallo'] not in results.keys():
            results[a['intervallo']] = []
        results[a['intervallo']].append(str(a['id']))
    return results