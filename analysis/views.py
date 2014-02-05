from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.base import View
from .models import ChiaveIndiciClimatici, TempTxMed
from climatlas.utils import render_to_pdf
from export_xls.views import export_xlwt


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


class TempTxMedViewExport(View):
    template_name = 'analysis/tabelle_temp_pdf.html'

    def get(self, request, *args, **kwargs):
        tb = TempTxMed.objects.all()
        if self.kwargs['tipo_export'] == 'pdf':
            return render_to_pdf(self.template_name, {'tabella': tb,
                                                      'pagesize': 'A4 landscape',
                                                      'title': 'Tabella Indici Climatici'})
        elif self.kwargs['tipo_export'] == 'xls':
            fields = ["stazione", "quota", "gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "sett", "ott", "nov", "dic" ]
            queryset = tb
            filename = TempTxMed._meta.verbose_name_plural.lower()
            try:
                return export_xlwt(filename, fields, queryset.values_list(*fields))
            except Exception, e:
                raise e
        else:
            pass

