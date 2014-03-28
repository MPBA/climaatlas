#-*- encoding: utf-8 -*-
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.views.generic.base import View
from django.conf import settings
from .models import ClimateIndex, ClimateIndexData, ClimateExtremesData, Chart
from climatlas.utils import render_to_pdf, periodi_graph_dict, anno_graph_dict, intervallo_graph_dict, export_csv
from climatlas.models import Station
from export_xls.views import export_xlwt
import json
from genPng import GenerateImmage
from django.core import serializers


class ClimateIndexListView(ListView):
    template_name = 'analysis/indici_climatici_list.html'
    context_object_name = 'indici'

    def get_queryset(self):
        indici = ClimateIndex.objects.filter(sezione='index').order_by('-type','name')
        return indici

    def get_context_data(self, **kwargs):
        context = super(ClimateIndexListView, self).get_context_data()
        periodo = ClimateIndexData.objects.values('periodo').distinct().order_by('periodo')
        context['periodo'] = periodo
        return context


class ClimateIndexDetailsView(ListView):
    template_name = 'analysis/indici_climatici_details.html'
    context_object_name = 'data'

    def get_queryset(self):
        self.index = get_object_or_404(ClimateIndex, r_name=self.kwargs['r_name'])

        if self.kwargs['periodo'] not in self.index.get_climateindex_periodo_list:
            raise Http404('No %s matches the given query.')

        data = ClimateIndexData.objects.filter(periodo=self.kwargs['periodo'],
                                               climate_index=self.index).exclude(gen=None,
                                                                                 feb=None,
                                                                                 mar=None,
                                                                                 apr=None,
                                                                                 mag=None,
                                                                                 giu=None,
                                                                                 lug=None,
                                                                                 ago=None,
                                                                                 sett=None,
                                                                                 ott=None,
                                                                                 nov=None,
                                                                                 dic=None,
                                                                                 annua=None,
                                                                                 autunno=None,
                                                                                 primavera=None,
                                                                                 inverno=None,
                                                                                 estate=None).order_by('station__stname')
        for d in data:
            print d.gen
        return data

    def get_context_data(self, **kwargs):
        context = super(ClimateIndexDetailsView, self).get_context_data()
        context['indice'] = self.index
        context['periodo'] = self.kwargs['periodo']
        # print serializers.serialize('json', self.get_queryset())
        return context


class ClimateIndexDetailsViewExport(View):
    template_name = 'analysis/indici_climatici_export_pdf.html'

    def get(self, request, *args, **kwargs):
        self.index = get_object_or_404(ClimateIndex, r_name=self.kwargs['r_name'])

        if self.kwargs['periodo'] not in self.index.get_climateindex_periodo_list:
            raise Http404('No %s matches the given query.' )

        data = ClimateIndexData.objects.filter(periodo=self.kwargs['periodo'],
                                               climate_index=self.index).exclude(gen=None,
                                                                                 feb=None,
                                                                                 mar=None,
                                                                                 apr=None,
                                                                                 mag=None,
                                                                                 giu=None,
                                                                                 lug=None,
                                                                                 ago=None,
                                                                                 sett=None,
                                                                                 ott=None,
                                                                                 nov=None,
                                                                                 dic=None,
                                                                                 annua=None,
                                                                                 autunno=None,
                                                                                 primavera=None,
                                                                                 inverno=None,
                                                                                 estate=None).order_by('station__stname')

        title = '%s' % self.index.name
        periodo_rif = '%s' % 'Periodo di riferimento ' + self.kwargs['periodo']

        if self.kwargs['tipo_export'] == 'pdf':
            return render_to_pdf(self.template_name, {'tabella': data,
                                                      'pagesize': 'A4 landscape',
                                                      'title': title, 'periodo_rif': periodo_rif})
        elif self.kwargs['tipo_export'] == 'xls':
            fields = ["station__stname", "station__elevation", "gen", "feb", "mar", "apr", "mag", "giu", "lug",
                      "ago", "sett", "ott", "nov", "dic", "inverno", "primavera", "estate", "autunno"]
            col_name = ["station__stname", "station__elevation", "gen", "feb", "mar", "apr", "mag", "giu", "lug",
                      "ago", "sett", "ott", "nov", "dic", "DGF", "MAM", "GLA", "SON"]
            queryset = data
            filename = title
            try:
                return export_xlwt(filename, col_name, queryset.values_list(*fields))
            except Exception, e:
                raise e
        elif self.kwargs['tipo_export'] == 'csv':
            fields = ["station__stname", "station__elevation", "gen", "feb", "mar", "apr", "mag", "giu", "lug",
                      "ago", "sett", "ott", "nov", "dic", "inverno", "primavera", "estate", "autunno"]
            col_name = ["station__stname", "station__elevation", "gen", "feb", "mar", "apr", "mag", "giu", "lug",
                      "ago", "sett", "ott", "nov", "dic", "DGF", "MAM", "GLA", "SON"]
            filename = title
            queryset = data
            return export_csv(filename, fields, col_name, queryset.values_list(*fields))
        else:
            pass


class ClimateExtremesListView(ListView):
    template_name = 'analysis/valori_estremi_list.html'
    context_object_name = 'estremi'

    def get_queryset(self):
        estremi = ClimateIndex.objects.filter(sezione='extreme').order_by('type', 'name')
        return estremi

    def get_context_data(self, **kwargs):
        context = super(ClimateExtremesListView, self).get_context_data()

        return context


class ClimateExtremesDetailsView(ListView):
    template_name = 'analysis/valori_estremi_details.html'
    context_object_name = 'data'

    def get_queryset(self):
        self.estremo = get_object_or_404(ClimateIndex, r_name=self.kwargs['r_name'])

        data = ClimateExtremesData.objects.filter(climate_index=self.estremo).order_by('station__stname')
        return data

    def get_context_data(self, **kwargs):
        context = super(ClimateExtremesDetailsView, self).get_context_data()
        context['estremo'] = self.estremo

        return context


class ClimateExtremesDetailsViewExport(View):
    template_name = 'analysis/valori_estremi_export_pdf.html'

    def get(self, request, *args, **kwargs):
        self.index = get_object_or_404(ClimateIndex, r_name=self.kwargs['r_name'])

        data = ClimateExtremesData.objects.filter(climate_index=self.index).order_by('station__stname')

        title = '%s' % (self.index.name)

        if self.kwargs['tipo_export'] == 'pdf':
            return render_to_pdf(self.template_name, {'tabella': data,
                                                      'estremo': self.index,
                                                      'pagesize': 'A4 landscape',
                                                      'title': title})
        elif self.kwargs['tipo_export'] == 'xls':
            fields = ["station__stname", "station__elevation", "anno_inizio", "gen", "gen_data", "feb", "feb_data", "mar",
                      "mar_data", "apr", "apr_data", "mag", "mag_data", "giu", "giu_data", "lug", "lug_data",
                      "ago", "ago_data", "sett", "sett_data", "ott", "nov", "nov_data", "dic", "dic_data"]
            col_name = ["station__stname", "station__elevation", "anno_inizio", "gen", "gen_data", "feb", "feb_data", "mar",
                      "mar_data", "apr", "apr_data", "mag", "mag_data", "giu", "giu_data", "lug", "lug_data",
                      "ago", "ago_data", "sett", "sett_data", "ott", "nov", "nov_data", "dic", "dic_data"]
            if self.index.resolution == 'mensili':
                fields += ["annua", "annua_data", "inverno", "inverno_data", "primavera", "primavera_data", "estate",
                           "estate_data", "autunno", "autunno_data"]
                col_name += ["annua", "annua_data", "DGF", "DGF_data", "MAM", "MAM_data", "GLA",
                           "GLA_data", "SON", "SON_data"]
            queryset = data
            filename = title
            try:
                return export_xlwt(filename, col_name, queryset.values_list(*fields))
            except Exception, e:
                raise e
        elif self.kwargs['tipo_export'] == 'csv':
            fields = ["station__stname", "station__elevation",  "anno_inizio","gen", "gen_data", "feb", "feb_data", "mar",
                      "mar_data", "apr", "apr_data", "mag", "mag_data", "giu", "giu_data", "lug", "lug_data",
                      "ago", "ago_data", "sett", "sett_data", "ott", "nov", "nov_data", "dic", "dic_data"]
            col_name = ["station__stname", "station__elevation", "anno_inizio", "gen", "gen_data", "feb", "feb_data", "mar",
                      "mar_data", "apr", "apr_data", "mag", "mag_data", "giu", "giu_data", "lug", "lug_data",
                      "ago", "ago_data", "sett", "sett_data", "ott", "nov", "nov_data", "dic", "dic_data"]
            if self.index.resolution == 'mensili':
                fields += ["annua", "annua_data", "inverno", "inverno_data", "primavera", "primavera_data", "estate",
                           "estate_data", "autunno", "autunno_data"]
                col_name += ["annua", "annua_data", "DGF", "DGF_data", "MAM", "MAM_data", "GLA",
                           "GLA_data", "SON", "SON_data"]
            filename = title
            queryset = data
            return export_csv(filename, fields, col_name, queryset.values_list(*fields))
        else:
            pass


class DiagrammiClimaticiListView(TemplateView):
    template_name = 'analysis/diagrammi_climatici_list.html'

    def get_context_data(self, **kwargs):
        context = super(DiagrammiClimaticiListView, self).get_context_data()
        meteo_stations = Station.objects.all().order_by('stname')

        context['meteo_stations'] = meteo_stations
        context['type'] = (20,)
        return context


class DiagrammiClimaticiDetailsView(TemplateView):
    template_name = 'analysis/diagrammi_climatici_details.html'

    def get_context_data(self, **kwargs):
        context = super(DiagrammiClimaticiDetailsView, self).get_context_data()
        pk = self.kwargs['pk']
        periodo = self.kwargs['periodo']

        station = Station.objects.get(pk=pk)
        dataidx = station.climateindexdata_set.filter(periodo=periodo, climate_index__sezione='index')\
            .order_by('-climate_index__type', 'climate_index__name')
        dataext = station.climateextremesdata_set.filter(climate_index__sezione='extreme')\
            .order_by('climate_index__resolution', 'climate_index__type', 'climate_index__name')

        context['station'] = station
        context['dataidx'] = dataidx
        context['dataext'] = dataext
        context['periodo'] = periodo
        context['charts'] = Chart.objects.filter(chart_type__in=(20,),
                                                 station=station,
                                                 variables__contains={
                                                     'periodo_climatico': self.kwargs['periodo']
                                                 })
        context['periodo_list'] = station.climateindexdata_set.filter(station=station).values_list('periodo').distinct().order_by('periodo')
        context['station_list'] = Station.objects.all().order_by('stname')

        return context


class DiagrammiClimaticiIndexDetailsViewExport(View):
    template_name = 'analysis/diagrammi_climatici_indici_export_pdf.html'

    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        periodo = self.kwargs['periodo']

        station = Station.objects.get(pk=pk)
        dataidx = station.climateindexdata_set.filter(periodo=periodo, climate_index__sezione='index')\
            .order_by('-climate_index__type', 'climate_index__name')

        title = 'Indici climatici %s' % station.stname
        periodo_rif = '%s' % 'Periodo di riferimento ' + periodo

        if self.kwargs['tipo_export'] == 'pdf':
            return render_to_pdf(self.template_name, {'tabella': dataidx,
                                                      'pagesize': 'A4 landscape',
                                                      'title': title, 'periodo_rif': periodo_rif})
        elif self.kwargs['tipo_export'] == 'xls':
            fields = ["climate_index__name", "gen", "feb", "mar", "apr", "mag", "giu", "lug",
                      "ago", "sett", "ott", "nov", "dic",  "nota"]
            col_name = ["indice",  "gen", "feb", "mar", "apr", "mag", "giu", "lug",
                      "ago", "sett", "ott", "nov", "dic", "unione di due serie"]
            queryset = dataidx
            filename = title
            try:
                return export_xlwt(filename, col_name, queryset.values_list(*fields))
            except Exception, e:
                raise e
        elif self.kwargs['tipo_export'] == 'csv':
            fields = ["climate_index__name", "gen", "feb", "mar", "apr", "mag", "giu", "lug",
                      "ago", "sett", "ott", "nov", "dic",  "nota"]
            col_name = ["indice",  "gen", "feb", "mar", "apr", "mag", "giu", "lug",
                      "ago", "sett", "ott", "nov", "dic", "unione di due serie"]
            filename = title
            queryset = dataidx
            return export_csv(filename, fields, col_name, queryset.values_list(*fields))
        else:
            pass


class DiagrammiClimaticiEstremiDetailsViewExport(View):
    template_name = 'analysis/diagrammi_climatici_estremi_export_pdf.html'

    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        periodo = self.kwargs['periodo']

        station = Station.objects.get(pk=pk)
        dataext = station.climateextremesdata_set.filter(climate_index__sezione='extreme')\
            .order_by('climate_index__resolution', 'climate_index__type', 'climate_index__name')

        title = 'Estremi climatici %s' % station.stname
        periodo_rif = '%s' % 'Periodo di riferimento ' + periodo

        if self.kwargs['tipo_export'] == 'pdf':
            return render_to_pdf(self.template_name, {'tabella': dataext,
                                                      'pagesize': 'A4 landscape',
                                                      'title': title, 'periodo_rif': periodo_rif})
        elif self.kwargs['tipo_export'] == 'xls':
            fields = ["climate_index__name", "gen", "gen_data", "feb", "feb_data", "mar",
                      "mar_data", "apr", "apr_data", "mag", "mag_data", "giu", "giu_data", "lug", "lug_data",
                      "ago", "ago_data", "sett", "sett_data", "ott", "nov", "nov_data", "dic", "dic_data",
                      "annua", "annua_data", "inverno", "inverno_data", "primavera", "primavera_data", "estate",
                       "estate_data", "autunno", "autunno_data"]
            col_name = ["estremo climatico", "gen", "gen_data", "feb", "feb_data", "mar",
                      "mar_data", "apr", "apr_data", "mag", "mag_data", "giu", "giu_data", "lug", "lug_data",
                      "ago", "ago_data", "sett", "sett_data", "ott", "nov", "nov_data", "dic", "dic_data",
                      "annua", "annua_data", "DGF", "DGF_data", "MAM", "MAM_data", "GLA",
                       "GLA_data", "SON", "SON_data"]
            col_name += []
            queryset = dataext
            filename = title
            try:
                return export_xlwt(filename, col_name, queryset.values_list(*fields))
            except Exception, e:
                raise e
        elif self.kwargs['tipo_export'] == 'csv':
            fields = ["climate_index__name", "gen", "gen_data", "feb", "feb_data", "mar",
                      "mar_data", "apr", "apr_data", "mag", "mag_data", "giu", "giu_data", "lug", "lug_data",
                      "ago", "ago_data", "sett", "sett_data", "ott", "nov", "nov_data", "dic", "dic_data",
                      "annua", "annua_data", "inverno", "inverno_data", "primavera", "primavera_data", "estate",
                       "estate_data", "autunno", "autunno_data"]
            col_name = ["estremo climatico", "gen", "gen_data", "feb", "feb_data", "mar",
                      "mar_data", "apr", "apr_data", "mag", "mag_data", "giu", "giu_data", "lug", "lug_data",
                      "ago", "ago_data", "sett", "sett_data", "ott", "nov", "nov_data", "dic", "dic_data",
                      "annua", "annua_data", "DGF", "DGF_data", "MAM", "MAM_data", "GLA",
                       "GLA_data", "SON", "SON_data"]
            filename = title
            queryset = dataext
            return export_csv(filename, fields, col_name, queryset.values_list(*fields))
        else:
            pass

class TrendClimaticiAnomalieList(TemplateView):
    template_name = 'analysis/trend_anomalie_list.html'

    def get_context_data(self, **kwargs):
        context = super(TrendClimaticiAnomalieList, self).get_context_data()
        stations_from_charts = Chart.objects.filter(chart_type__in=(6, 7)).values_list('station_id').distinct()
        stations = Station.objects.filter(pk__in=stations_from_charts).order_by('stname')
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
        context['station_list'] = Station.objects.filter(pk__in=stations_from_charts).order_by('stname')
        context['station'] = station
        context['charts'] = Chart.objects.filter(id__in=ids)
        context['periodo_climatico'] = Chart.objects.filter(id__in=ids).values_list('variables')[0][0]['periodo_climatico']
        context['type'] = (6, 7)
        return context


class TrendClimaticiDistribuzioniStatisticheList(TemplateView):
    template_name = 'analysis/trend_distribuzioni_statistiche_list.html'

    def get_context_data(self, **kwargs):
        context = super(TrendClimaticiDistribuzioniStatisticheList, self).get_context_data()
        stations_from_charts = Chart.objects.filter(chart_type__in=(14, 15)).values_list('station_id').distinct()
        stations = Station.objects.filter(pk__in=stations_from_charts).order_by('stname')
        context['stations'] = stations
        context['type'] = (14, 15)
        return context


class TrendClimaticiDistribuzioniStatisticheDetail(TemplateView):
    template_name = 'analysis/trend_distribuzioni_statistiche_detail.html'

    def get_context_data(self, **kwargs):
        context = super(TrendClimaticiDistribuzioniStatisticheDetail, self).get_context_data()
        station = Station.objects.get(id=self.kwargs['station_id'])
        # charts = Chart.objects.filter(chart_type__in=(14, 15), station_id=station.pk)
        context['station'] = station
        # context['charts'] = charts
        context['type'] = (14, 15)
        stations_from_charts = Chart.objects.filter(chart_type__in=(14, 15)).order_by('station__stname').values_list('station_id').distinct()
        context['station_list'] = Station.objects.filter(pk__in=stations_from_charts).order_by('stname')
        intervalli = intervallo_graph_dict(context['station'].pk, context['type'])
        context['intervalli_dict'] = intervalli

        return context


class TrendAndamentoAnnualeList(ListView):
    template_name = 'analysis/trend_andamento_annuale_list.html'
    context_object_name = 'stations'

    def get_queryset(self):
        stations_from_charts = Chart.objects.filter(chart_type__in=(16, 17)).values_list('station_id').distinct()
        stations = Station.objects.filter(pk__in=stations_from_charts).order_by('stname')
        return stations

    def get_context_data(self, **kwargs):
        context = super(TrendAndamentoAnnualeList, self).get_context_data()
        context['type'] = (16, 17)
        return context


class TrendAndamentoAnnualeDetail(TemplateView):
    template_name = 'analysis/trend_andamento_annuale_detail.html'

    def get_context_data(self, **kwargs):
        context = super(TrendAndamentoAnnualeDetail, self).get_context_data()
        context['station'] = Station.objects.get(pk=self.kwargs['station_id'])
        stations_from_charts = Chart.objects.filter(chart_type__in=(16, 17)).values_list('station_id').distinct()
        context['station_list'] = Station.objects.filter(pk__in=stations_from_charts).order_by('stname')
        context['periodo_climatico'] = self.kwargs['periodo']
        context['type'] = (16, 17)
        anni_graph = anno_graph_dict(context['station'].pk, context['type'], context['periodo_climatico'])
        context['anno_graph_dict'] = anni_graph
        jsonlist = []
        for k, p in anni_graph.iteritems():
            jsonlist.append({
                'anno': k,
                'ids': p
            })
        context['jsonlist'] = sorted(jsonlist)
        context['annographjson'] = json.dumps(sorted(jsonlist))
        return context


class MappeClimaticheListView(TemplateView):
    template_name = 'analysis/mappe_climatiche.html'

    def get_context_data(self, **kwargs):
        context = super(MappeClimaticheListView, self).get_context_data()
        context['type'] = settings.LAYER_TYPE
        context['period'] = settings.LAYER_PERIOD
        context['month'] = settings.LAYER_MONTH
        return context


class MappeTrendListView(TemplateView):
    template_name = 'analysis/mappe_trend.html'

    def get_context_data(self, **kwargs):
        context = super(MappeTrendListView, self).get_context_data()
        context['type'] = settings.LAYER_TYPE
        #context['period'] = settings.LAYER_PERIOD
        context['year'] = settings.LAYER_YEAR
        context['month'] = settings.LAYER_MONTH
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

def popola_periodi_grandezze_select(request):
    periodi = periodi_graph_dict(request.GET['station_id'], request.GET.getlist('tipi_grafici[]'))
    result = []
    for k, p in periodi.iteritems():
        result.append({
            'periodo': k,
            'ids': '-'.join(p)
        })
    return HttpResponse(json.dumps(result))
###############################EO AJAX FUNCTIONS##################################################


def export_mappe_climatiche(request, ltype, periodo, month):
    g = GenerateImmage()

    if month in ('1win', '2spr', '3sum', '4aut'):
        map = g.generate_png(ltype, periodo, month=None, season="1win")
    elif month:
        map = g.generate_png(ltype, periodo, month=int(month), season=None)
    else:
        map = g.generate_png(ltype, period, month=None, season=None)

    response = HttpResponse(mimetype="image/png")
    map.save(response, "PNG")

    return response
