from django.db import models
from django_hstore import hstore
from climatlas.models import Station


class Chart(models.Model):
    id = models.BigIntegerField(primary_key=True)
    chart_type = models.IntegerField()
    station = models.ForeignKey(Station)
    variables = hstore.DictionaryField()
    image = models.BinaryField()

    objects = hstore.HStoreManager()

    class Meta:
        db_table = 'chart'


class ClimateIndex(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.TextField(unique=True)
    r_name = models.TextField(unique=True)
    resolution = models.TextField(blank=True)
    type = models.TextField()
    sezione = models.TextField()

    class Meta:
        db_table = 'climate_index'

    @property
    def get_climateindex_periodo(self):
        return self.climateindexdata_set.values('periodo').distinct()

    @property
    def get_climateindex_periodo_list(self):
        values = self.climateindexdata_set.values_list('periodo').distinct()
        return [v[0] for v in values]

    @property
    def get_climateextremes_count(self):
        return self.climateextremesdata_set.count()


class ClimateExtremesData(models.Model):
    id = models.BigIntegerField(primary_key=True)
    station = models.ForeignKey(Station)
    climate_index = models.ForeignKey(ClimateIndex)
    anno_inizio = models.IntegerField()
    gen = models.FloatField(blank=True, null=True)
    gen_data = models.TextField(blank=True)
    feb = models.FloatField(blank=True, null=True)
    feb_data = models.TextField(blank=True)
    mar = models.FloatField(blank=True, null=True)
    mar_data = models.TextField(blank=True)
    apr = models.FloatField(blank=True, null=True)
    apr_data = models.TextField(blank=True)
    mag = models.FloatField(blank=True, null=True)
    mag_data = models.TextField(blank=True)
    giu = models.FloatField(blank=True, null=True)
    giu_data = models.TextField(blank=True)
    lug = models.FloatField(blank=True, null=True)
    lug_data = models.TextField(blank=True)
    ago = models.FloatField(blank=True, null=True)
    ago_data = models.TextField(blank=True)
    sett = models.FloatField(blank=True, null=True)
    sett_data = models.TextField(blank=True)
    ott = models.FloatField(blank=True, null=True)
    ott_data = models.TextField(blank=True)
    nov = models.FloatField(blank=True, null=True)
    nov_data = models.TextField(blank=True)
    dic = models.FloatField(blank=True, null=True)
    dic_data = models.TextField(blank=True)
    annua = models.FloatField(blank=True, null=True)
    annua_data = models.TextField(blank=True)
    inverno = models.FloatField(blank=True, null=True)
    inverno_data = models.TextField(blank=True)
    primavera = models.FloatField(blank=True, null=True)
    primavera_data = models.TextField(blank=True)
    estate = models.FloatField(blank=True, null=True)
    estate_data = models.TextField(blank=True)
    autunno = models.FloatField(blank=True, null=True)
    autunno_data = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'climate_extremes_data'


class ClimateIndexData(models.Model):
    id = models.BigIntegerField(primary_key=True)
    station = models.ForeignKey(Station)
    climate_index = models.ForeignKey(ClimateIndex)
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
    periodo = models.TextField()
    nota = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'climate_index_data'



