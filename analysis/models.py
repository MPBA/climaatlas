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


class EstremiClimatici(models.Model):
    nome_indice_climatico = models.CharField(max_length=250, blank=True)
    variabile_r = models.CharField(max_length=250, blank=True)
    db_name = models.CharField(max_length=250, blank=True, primary_key=True)
    type = models.CharField(max_length=250, blank=True)

    class Meta:
        db_table = 'estremi_climatici'

    @property
    def data_available(self):
        return self.valoriestremidata_set.count()


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
    nota = models.CharField(max_length=250, blank=True, null=True)


class ValoriEstremiData(models.Model):
    stazione = models.ForeignKey(Station)
    indice = models.ForeignKey(EstremiClimatici)
    anno_inizio = models.IntegerField(blank=True, null=True)
    gen = models.FloatField(blank=True, null=True)
    gen_data = models.CharField(max_length=250, blank=True, null=True)
    feb = models.FloatField(blank=True, null=True)
    feb_data = models.CharField(max_length=250, blank=True, null=True)
    mar = models.FloatField(blank=True, null=True)
    mar_data = models.CharField(max_length=250, blank=True, null=True)
    apr = models.FloatField(blank=True, null=True)
    apr_data = models.CharField(max_length=250, blank=True, null=True)
    mag = models.FloatField(blank=True, null=True)
    mag_data = models.CharField(max_length=250, blank=True, null=True)
    giu = models.FloatField(blank=True, null=True)
    giu_data = models.CharField(max_length=250, blank=True, null=True)
    lug = models.FloatField(blank=True, null=True)
    lug_data = models.CharField(max_length=250, blank=True, null=True)
    ago = models.FloatField(blank=True, null=True)
    ago_data = models.CharField(max_length=250, blank=True, null=True)
    sett = models.FloatField(blank=True, null=True)
    sett_data = models.CharField(max_length=250, blank=True, null=True)
    ott = models.FloatField(blank=True, null=True)
    ott_data = models.CharField(max_length=250, blank=True, null=True)
    nov = models.FloatField(blank=True, null=True)
    nov_data = models.CharField(max_length=250, blank=True, null=True)
    dic = models.FloatField(blank=True, null=True)
    dic_data = models.CharField(max_length=250, blank=True, null=True)
    annua = models.FloatField(blank=True, null=True)
    annua_data = models.CharField(max_length=250, blank=True, null=True)
    inverno = models.FloatField(blank=True, null=True)
    inverno_data = models.CharField(max_length=250, blank=True, null=True)
    primavera = models.FloatField(blank=True, null=True)
    primavera_data = models.CharField(max_length=250, blank=True, null=True)
    estate = models.FloatField(blank=True, null=True)
    estate_data = models.CharField(max_length=250, blank=True, null=True)
    autunno = models.FloatField(blank=True, null=True)
    autunno_data = models.CharField(max_length=250, blank=True, null=True)


class DiagrammiClimatici(models.Model):
    stazione = models.ForeignKey(Station)
    grafico = models.ImageField(upload_to='diagrammi')
    periodo = models.CharField(max_length=250, blank=True, null=True)

    def __unicode__(self):
        return u'%s %s %s' % (self.stazione.code, self.stazione.stname, self.periodo)