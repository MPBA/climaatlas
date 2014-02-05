from django.db import models
from climatlas.models import Station

class IndiciClimatici(models.Model):
    nome_indice_climatico = models.CharField(max_length=250)
    variabile_r = models.CharField(max_length=250, blank=True)
    db_name = models.CharField(max_length=250, primary_key=True)

    class Meta:
        managed = False
        db_table = 'indici_climatici'

    @property
    def periodo_disponibile(self):
        return self.indiciclimaticidata_set.values('periodo').distinct()

    @property
    def periodo_disponibile_list(self):
        values = self.indiciclimaticidata_set.values_list('periodo').distinct()
        return [v[0] for v in values]


class IndiciClimaticiData(models.Model):
    stazione = models.ForeignKey(Station)
    indice = models.ForeignKey(IndiciClimatici)
    gen = models.FloatField(blank=True, null=True)
    feb = models.FloatField(blank=True, null=True)
    mar = models.FloatField(blank=True, null=True)
    apr = models.FloatField(blank=True, null=True)
    mag = models.FloatField(blank=True, null=True)
    giu = models.FloatField(blank=True, null=True)
    lug = models.FloatField(blank=True, null=True)
    ago = models.FloatField(blank=True, null=True)
    sett = models.FloatField(blank=True, null=True)
    ott = models.FloatField(blank=True, null=True)
    nov = models.FloatField(blank=True, null=True)
    dic = models.FloatField(blank=True, null=True)
    annua = models.FloatField(blank=True, null=True)
    inverno = models.FloatField(blank=True, null=True)
    primavera = models.FloatField(blank=True, null=True)
    estate = models.FloatField(blank=True, null=True)
    autunno = models.FloatField(blank=True, null=True)
    periodo = models.CharField(max_length=250, blank=True)
    nota = models.CharField(max_length=250, blank=True)