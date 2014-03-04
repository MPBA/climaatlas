#-*- encoding: utf-8 -*-
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.base import View
from .models import IndiciClimatici, IndiciClimaticiData, EstremiClimatici, ValoriEstremiData, Chart
from climatlas.utils import render_to_pdf, periodi_graph_dict
from climatlas.models import Station
from export_xls.views import export_xlwt
from django.db import transaction, connection, DatabaseError
import json


class IndiciClimaticiListView(TemplateView):
    template_name = 'analysis/indici_climatici_list.html'

    def get_context_data(self, **kwargs):
        context = super(IndiciClimaticiListView, self).get_context_data()

        indici = IndiciClimatici.objects.all()
        periodo = IndiciClimaticiData.objects.values('periodo').distinct().order_by('periodo')
        context['indici'] = indici
        context['periodo'] = periodo

        return context


class IndiciClimaticiDetailsView(TemplateView):
    template_name = 'analysis/indici_climatici_details.html'

    def get_context_data(self, **kwargs):
        context = super(IndiciClimaticiDetailsView, self).get_context_data()
        indice = self.kwargs['indice']
        periodo = self.kwargs['periodo']

        data = IndiciClimaticiData.objects.filter(periodo=periodo, indice=indice).order_by('stazione__stname')
        indice = IndiciClimatici.objects.get(db_name=indice)

        context['data'] = data
        context['indice'] = indice
        context['periodo'] = periodo

        return context


class IndiciClimaticiDetailsViewExport(View):
    template_name = 'analysis/indici_climatici_export_pdf.html'

    def get(self, request, *args, **kwargs):
        indice = self.kwargs['indice']
        periodo = self.kwargs['periodo']
        data = IndiciClimaticiData.objects.filter(periodo=periodo, indice=indice).order_by('stazione__stname')
        indice = IndiciClimatici.objects.get(db_name=indice)
        title = '%s %s' % (indice.nome_indice_climatico, periodo)

        if self.kwargs['tipo_export'] == 'pdf':
            return render_to_pdf(self.template_name, {'tabella': data,
                                                      'pagesize': 'A4 landscape',
                                                      'title': title})
        elif self.kwargs['tipo_export'] == 'xls':
            fields = ["stazione__stname", "stazione__elevation", "gen", "feb", "mar", "apr", "mag", "giu", "lug",
                      "ago", "sett", "ott", "nov", "dic", "inverno", "primavera", "estate", "autunno"]
            queryset = data
            filename = title
            try:
                return export_xlwt(filename, fields, queryset.values_list(*fields))
            except Exception, e:
                raise e
        else:
            pass


class ValoriEstremiListView(TemplateView):
    template_name = 'analysis/valori_estremi_list.html'

    def get_context_data(self, **kwargs):
        context = super(ValoriEstremiListView, self).get_context_data()

        estremi = EstremiClimatici.objects.all().order_by('type', 'nome_indice_climatico')
        context['estremi'] = estremi

        return context


class ValoriEstremiDetailsView(TemplateView):
    template_name = 'analysis/valori_estremi_details.html'

    def get_context_data(self, **kwargs):
        context = super(ValoriEstremiDetailsView, self).get_context_data()
        indice = self.kwargs['indice']

        data = ValoriEstremiData.objects.filter(indice=indice).order_by('stazione__stname')
        estremo = EstremiClimatici.objects.get(db_name=indice)

        context['data'] = data
        context['estremo'] = estremo

        return context


class ValoriEstremiDetailsViewExport(View):
    template_name = 'analysis/valori_estremi_export_pdf.html'

    def get(self, request, *args, **kwargs):
        indice = self.kwargs['indice']

        data = ValoriEstremiData.objects.filter(indice=indice).order_by('stazione__stname')
        indice = EstremiClimatici.objects.get(db_name=indice)
        title = '%s' % (indice.nome_indice_climatico)

        if self.kwargs['tipo_export'] == 'pdf':
            return render_to_pdf(self.template_name, {'tabella': data,
                                                      'estremo': indice,
                                                      'pagesize': 'A4 landscape',
                                                      'title': title})
        elif self.kwargs['tipo_export'] == 'xls':
            fields = ["stazione__stname", "stazione__elevation", "gen", "gen_data", "feb", "feb_data", "mar",
                      "mar_data", "apr", "apr_data", "mag","mag_data", "giu", "giu_data", "lug", "lug_data",
                      "ago", "ago_data", "sett", "sett_data", "ott", "nov", "nov_data", "dic", "dic_data"]
            if indice.type == 'mensili':
                fields += ["annua", "annua_data", "inverno", "inverno_data", "primavera", "primavera_data", "estate",
                           "estate_data", "autunno", "autunno_data"]
            queryset = data
            filename = title
            try:
                return export_xlwt(filename, fields, queryset.values_list(*fields))
            except Exception, e:
                raise e
        else:
            pass


class DiagrammiClimaticiListView(TemplateView):
    template_name = 'analysis/diagrammi_climatici_list.html'

    def get_context_data(self, **kwargs):
        context = super(DiagrammiClimaticiListView, self).get_context_data()
        meteo_stations = Station.objects.all().order_by('stname')

        context['meteo_stations'] = meteo_stations
        return context


class DiagrammiClimaticiDetailsView(TemplateView):
    template_name = 'analysis/diagrammi_climatici_details.html'

    def get_context_data(self, **kwargs):
        context = super(DiagrammiClimaticiDetailsView, self).get_context_data()
        pk = self.kwargs['pk']
        periodo = self.kwargs['periodo']

        station = Station.objects.get(pk=pk)
        data = station.indiciclimaticidata_set.filter(periodo=periodo).order_by('indice__nome_indice_climatico', 'periodo')

        context['station'] = station
        context['data'] = data
        context['periodo'] = periodo
        context['grafico'] = station.diagrammiclimatici_set.filter(periodo=periodo)
        context['periodo_list'] = ['1961-1990', '1971-2000', '1981-2010']   ### TODO FIX mettere nei settings o prendere da db!!!
        context['station_list'] = Station.objects.all().order_by('stname')

        return context


class TrendClimaticiAnomalieList(TemplateView):
    template_name = 'analysis/trend_anomalie_list.html'

    def get_context_data(self, **kwargs):
        context = super(TrendClimaticiAnomalieList, self).get_context_data()
        stations_from_charts = Chart.objects.filter(chart_type__in=(6, 7)).values_list('station_id').distinct()
        stations = Station.objects.filter(pk__in=stations_from_charts)
        context['stations'] = stations
        context['type'] = (6, 7)
        return context


class TrendClimaticiAnomalieDetailsView(TemplateView):
    template_name = 'analysis/trend_anomalie_details.html'

    def get_context_data(self, **kwargs):
        context = super(TrendClimaticiAnomalieDetailsView, self).get_context_data()
        ids = list(map(int, self.kwargs['ids'].split('-')))
        station_from_chart = Chart.objects.filter(id__in=ids).values('station_id').distinct()
        if len(station_from_chart) > 1:
            raise Http404
        else:
            station = Station.objects.get(id=station_from_chart[0]['station_id'])
        stations_from_charts = Chart.objects.filter(chart_type__in=(6, 7)).values_list('station_id').distinct()
        context['periodo_list'] = periodi_graph_dict(station, (6, 7))
        context['station_list'] = Station.objects.filter(pk__in=stations_from_charts)
        context['station'] = station
        context['charts'] = Chart.objects.filter(id__in=ids)
        context['periodo_climatico'] = Chart.objects.filter(id__in=ids).values_list('variables')[0][0]['periodo_climatico']
        context['type'] = (6, 7)
        return context


###############################CHARTS FUNCTIONS##################################################
def get_charts(request, chart_type, stazione, tipo_dato, periodo):
    var = {
        "tipo_dato": tipo_dato,
        "periodo_climatico": periodo
    }

    chart = Chart.objects.filter(station=stazione, chart_type=chart_type, variables__contains=var)
    if len(chart):
        return HttpResponse(chart[0].image, mimetype="image/png", status=200)
    else:
        return HttpResponseNotFound('Not found.')


def get_chart_by_id(request, pk):
    try:
        chart = Chart.objects.get(pk=pk)
        return HttpResponse(chart.image, mimetype="image/png", status=200)
    except Chart.DoesNotExist:
        return HttpResponseNotFound('Not found.')
###############################EO CHARTS FUNCTIONS##################################################


###############################AJAX FUNCTIONS##################################################
def popola_periodi_select(request):
    periodi = periodi_graph_dict(request.GET['station_id'], request.GET.getlist('tipi_grafici[]'))
    result = []
    for k, p in periodi.iteritems():
        result.append({
            'periodo': k,
            'ids': '-'.join(p)
        })
    return HttpResponse(json.dumps(result))
###############################EO AJAX FUNCTIONS##################################################
