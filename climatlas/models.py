from django.db import models


class Station(models.Model):
    id = models.BigIntegerField(primary_key=True)
    code = models.CharField(unique=True, max_length=15, blank=True)
    datasets = models.BigIntegerField()
    stname = models.CharField(max_length=55, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    elevation = models.FloatField()
    commence = models.DateField()
    cease = models.DateField(blank=True, null=True)
    last_modification = models.DateTimeField()
    description = models.TextField(blank=True)
    the_geom = models.TextField() # This field type is a guess.

    class Meta:
        managed = False
        ordering = ['code']
        db_table = 'station'

    @property
    def periodo_disponibile_list(self):
        values = self.indiciclimaticidata_set.values_list('periodo').distinct().order_by('periodo')
        return [v[0] for v in values]

    @property
    def diagramma_disponibile(self):
        if self.diagrammiclimatici_set.all().count():
            return True
        else:
            return False

    @property
    def tabella_disponibile(self):
        if self.indiciclimaticidata_set.all().count():
            return True
        else:
            return False

    def __unicode__(self):
        return u'%s %s' % (self.code, self.stname)


class StationView(models.Model):
    id = models.BigIntegerField(primary_key=True)
    code = models.CharField(max_length=15, blank=True)
    datasets = models.TextField(blank=True) # This field type is a guess.
    stname = models.CharField(max_length=55, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    elevation = models.FloatField(blank=True, null=True)
    commence = models.DateField(blank=True, null=True)
    cease = models.DateField(blank=True, null=True)
    last_modification = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True)
    the_geom = models.TextField(blank=True) # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'station_view'