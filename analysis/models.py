from django.db import models

# Create your models here.

class TempTxMed(models.Model):
    periodo = models.CharField(max_length=250, blank=True)
    stazione = models.CharField(max_length=250, blank=True, primary_key=True)
    quota = models.FloatField(blank=True, null=True)
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
    nota = models.CharField(max_length=250, blank=True)

    class Meta:
        managed = False
        db_table = 'temp_tx_med'


class ChiaveIndiciClimatici(models.Model):
    nome_indice_climatico = models.CharField(max_length=250, blank=True, primary_key=True)
    variabile_r = models.CharField(max_length=250, blank=True)
    db_name = models.CharField(max_length=250, blank=True)
    class Meta:
        managed = False
        db_table = 'chiave_indici_climatici'