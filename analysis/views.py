from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.base import View
from .models import IndiciClimatici, IndiciClimaticiData
from climatlas.utils import render_to_pdf
from export_xls.views import export_xlwt


class IndiciClimaticiListView(TemplateView):
    template_name = 'analysis/indici_climatici_list.html'

    def get_context_data(self, **kwargs):
        context = super(IndiciClimaticiListView, self).get_context_data()

        indici = IndiciClimatici.objects.all()
        periodo = IndiciClimaticiData.objects.values('periodo').distinct()
        context['indici'] = indici
        context['periodo'] = periodo

        return context


class IndiciClimaticiDetailsView(TemplateView):
    template_name = 'analysis/indici_climatici_details.html'

    def get_context_data(self, **kwargs):
        context = super(IndiciClimaticiDetailsView, self).get_context_data()
        indice = self.kwargs['indice']
        periodo = self.kwargs['periodo']
        print periodo
        print indice
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

