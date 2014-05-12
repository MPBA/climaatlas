import os
import shutil
from tempfile import mkdtemp
import datetime
from osgeo import gdal
from osgeo.gdalconst import *
from calendar import monthrange
import numpy as np
import logging

from pgbackup import utils
from pgbackup.pgbackup import PGBackup
from geoserver.catalog import Catalog, UploadError
from geoserver.util import shapefile_and_friends

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


class Mapgen(object):
    REFERENCE_MAP = "reference_map.tif"
    TEMP_PREFIX = "t"
    PREC_PREFIX = "p"

    FILE_DAY = "{type}{y}{m}{d}.tif"
    FILE_MONTH = "{type}{y}{m}.tif"
    FILE_YEAR = "{type}{y}.tif"
    FILE_SEASON = "{type}{y}{season}.tif"

    FILE_PERIOD = "{type}{period}{suffix}"
    FILE_PERIOD_MONTH = "{type}{period}{m}{suffix}"
    FILE_PERIOD_SEASON = "{type}{period}{season}{suffix}"

    FILE_ANOMALY = "{type}{period}-{y}{suffix}.tif"
    FILE_ANOMALY_MONTH = "{type}{period}{m}-{y}{m}{suffix}.tif"
    FILE_ANOMALY_SEASON = "{type}{period}{season}-{y}{season}{suffix}.tif"

    PERIODS = ["1961-1990", "1971-2000", "1981-2010"]
    SEASONS = ["1win", "2spr", "3sum", "4aut"]

    GEOSERVER_HOST = "http://geoatlas:50001/geoserver/rest"
    GEOSERVER_WMS = "http://geoatlas:50001/geoserver/wms"
    GEOSERVER_USER = "admin"
    GEOSERVER_PASSWORD = "geoserver"
    GEOSERVER_WORKSPACE = "mpba"

    DATE_START = datetime.date(1941, 1, 1)
    DATE_END = datetime.date(2011, 12, 31)

    def __init__(self, bindir, tiffdir, pguser='postgres', pgdb='climatlas_dev',
                 pgpass='u7y6t5r4e3w2', pghost='geoatlas'):
        self.bindir = bindir
        self.tiffdir = tiffdir
        self.ref_map = os.path.join(self.tiffdir, self.REFERENCE_MAP)
        self.pguser = pguser
        self.pgdb = pgdb
        self.pgpass = pgpass
        self.pghost = pghost

    def geoserver_upload(self, input_file):
        print "upload", input_file
        path, file_ext = os.path.split(input_file)
        f = os.path.splitext(file_ext)[0]
        cat = Catalog(self.GEOSERVER_HOST, self.GEOSERVER_USER, self.GEOSERVER_PASSWORD)
        try:
            cat.create_coveragestore(name=f, data=input_file, workspace=cat.get_workspace(self.GEOSERVER_WORKSPACE),
                                     overwrite=True)
        except UploadError:
            print "map already exist"
            cat.delete(cat.get_layer(f))
            cat.delete(cat.get_resources(f, self.GEOSERVER_WORKSPACE)[0])
            cat.create_coveragestore(name=f, data=input_file, workspace=cat.get_workspace(self.GEOSERVER_WORKSPACE),
                                     overwrite=True)

    def geoserver_upload_shape(self, input_file):
        print "upload", input_file

        path, file_ext = os.path.split(input_file)

        cat = Catalog(self.GEOSERVER_HOST, self.GEOSERVER_USER, self.GEOSERVER_PASSWORD)
        shapeFile = shapefile_and_friends(input_file)
        print shapeFile
        cat.create_featurestore(name=file_ext, data=shapeFile, workspace=cat.get_workspace(self.GEOSERVER_WORKSPACE),
                                overwrite=True, charset=None)

    #convert asc file to geotiff
    @staticmethod
    def __asc_to_tiff(input_asc, out_tif):
        cmd = ["gdal_translate", "-of", "GTiff", "-a_srs", "EPSG:32632", input_asc, out_tif]
        utils.call_command(cmd)

    @staticmethod
    def period_start(period):
        return int(period.split("-")[0])

    @staticmethod
    def period_end(period):
        return int(period.split("-")[1])

    def get_period_path(self, type_prefix, period, isoline=False, month=None, season=None):
        if not isoline:
            suffix = ".tif"
        else:
            suffix = ""

        if month is not None and month != "":
            month = str(int(month)).zfill(2)
            return os.path.join(self.tiffdir, period, type_prefix, self.FILE_PERIOD_MONTH.
                                format(type=type_prefix, period=period, m=month, suffix=suffix))
        elif season is not None and season != "":
            return os.path.join(self.tiffdir, period, type_prefix, self.FILE_PERIOD_SEASON.
                                format(type=type_prefix, period=period, season=season, suffix=suffix))
        else:
            return os.path.join(self.tiffdir, period, type_prefix, self.FILE_PERIOD.
                                format(type=type_prefix, period=period, suffix=suffix))

    def get_anomaly_path(self, type_prefix, period, year, month=None, season=None, suffix=None):
        if month is not None and month != "":
            month = str(int(month)).zfill(2)
            return os.path.join(self.tiffdir, period, type_prefix, self.FILE_ANOMALY_MONTH.
                                format(type=type_prefix, period=period, y=year, m=month, suffix=suffix))
        elif season is not None and season != "":
            return os.path.join(self.tiffdir, period, type_prefix, self.FILE_ANOMALY_SEASON.
                                format(type=type_prefix, period=period, y=year, season=season, suffix=suffix))
        else:
            return os.path.join(self.tiffdir, period, type_prefix, self.FILE_ANOMALY.
                                format(type=type_prefix, period=period, y=year, suffix=suffix))

    @staticmethod
    def get_anomaly_name(type_prefix, period, year, month=None, season=None, suffix=None):
        if month is not None and month != "":
            month = str(int(month)).zfill(2)

            return Mapgen.FILE_ANOMALY_MONTH.format(type=type_prefix, period=period, y=year, m=month, suffix=suffix)
        elif season is not None and season != "":
            return Mapgen.FILE_ANOMALY_SEASON.format(type=type_prefix, period=period, y=year, season=season,
                                                     suffix=suffix)
        else:
            return Mapgen.FILE_ANOMALY.format(type=type_prefix, period=period, y=year, suffix=suffix)

    def get_season_pah(self, type_prefix, year, season):
        year = str(int(year)).zfill(4)
        return os.path.join(self.tiffdir, year, type_prefix,
                            self.FILE_SEASON.format(type=type_prefix, y=year, season=season))

    def get_file_path(self, type_prefix, year, month=None, day=None):
        year = str(int(year)).zfill(4)
        if month is not None and month != "":
            month = str(int(month)).zfill(2)
            if day is not None and day != "":
                day = str(int(day)).zfill(2)
                return os.path.join(self.tiffdir, year, type_prefix,
                                    self.FILE_DAY.format(type=type_prefix, y=year, m=month, d=day))
            else:
                return os.path.join(self.tiffdir, year, type_prefix,
                                    self.FILE_MONTH.format(type=type_prefix, y=year, m=month))
        else:
            return os.path.join(self.tiffdir, year, type_prefix, self.FILE_YEAR.format(type=type_prefix, y=year))

    def compute_map(self, input_list, output_file, computation_type="sum", around=-1):
        logging.info(output_file)
        ref_map = gdal.Open(self.ref_map, GA_ReadOnly)
        if ref_map is None:
            print 'Could not open ' + str(ref_map)

        map_width = ref_map.RasterXSize
        map_height = ref_map.RasterYSize
        sizes = (map_height, map_width)
        output = np.zeros(sizes)

        mask = ref_map.ReadAsArray(0, 0, map_width, map_height)

        maps_found = 0
        #ciclo su tutti i file
        for f in input_list:
            current_map = gdal.Open(f, GA_ReadOnly)
            if current_map is None:
                logging.critical('Could not open ' + f)
                continue
            maps_found += 1
            output += current_map.ReadAsArray(0, 0, map_width, map_height)

        if computation_type == "mean":
            output /= maps_found

        #set nodata values from reference map
        output[np.where(mask == -9999)] = -9999

        if around > -1:
            output = np.around(output, around)

        out_map = gdal.GetDriverByName('GTiff').Create(output_file, map_width, map_height, 1, gdal.GDT_Float32)
        out_map.SetProjection(ref_map.GetProjection())
        out_map.SetGeoTransform(ref_map.GetGeoTransform())
        out_map.GetRasterBand(1).SetNoDataValue(-9999)
        out_map.GetRasterBand(1).WriteArray(output, 0, 0)

    # generates tiff file (temperature/precipitation) for a given day (data is fetched from local postgres db)
    # the function is self contained and can be called any time.
    # If temp_dir is specified skips copying binary files (bindir) to working dir
    def generate_day(self, type_prefix, year, month, day, temp_dir=None):
        #sanitize inputs to avoid SQL injections and path problems
        year = str(int(year)).zfill(4)
        month = str(int(month)).zfill(2)
        day = str(int(day)).zfill(2)
        if type_prefix not in (self.PREC_PREFIX, self.TEMP_PREFIX):
            raise Exception("Wrong type prefix")

        #create temp dirs and prepare paths
        if temp_dir is None:
            tempdir = mkdtemp()
        else:
            tempdir = temp_dir
        tempbins = os.path.join(tempdir, "bins")
        outdir = os.path.join(self.tiffdir, "{y}".format(y=year), type_prefix)

        # copy fortran binaries for computation in temp dir and chdir to it
        # (this is needed because input file paths are hardcoded in fortran binaries :/ )
        if temp_dir is None:
            utils.copy_anything(self.bindir, tempbins)
        os.chdir(tempbins)

        # path and commands for temperature computation
        if type_prefix == self.TEMP_PREFIX:
            executable = "tmean_day_calc"
            tempout = os.path.join(tempbins, "t_{y}".format(y=year), "asc")
            tempasc = os.path.join(tempout, "Tgrd_{y}{m}{d}_0000.asc".format(y=year, m=month, d=day))
            db_table = "temp_avg"
            input_csv = "temperatura_auto.csv"
        # path and commands for precipitation computation
        elif type_prefix == self.PREC_PREFIX:
            executable = "rainmean_day_calc"
            tempout = os.path.join(tempbins, "p_{y}".format(y=year), "asc")
            utils.mkdir_p(os.path.join(tempbins, "p_stationanalisys"))
            tempasc = os.path.join(tempout, "Pgrd_{y}{m}{d}_0000.asc".format(y=year, m=month, d=day))
            db_table = "rain"
            input_csv = "precipitazione.csv"

        # connect to db and output CSVs file for computation in temp dir
        pg = PGBackup(host=self.pghost, user=self.pguser, password=self.pgpass)

        # export stations to CSV in temp dir
        query = 'SELECT code as "Cod_Hystra", ' \
            'ST_X(ST_Transform(ST_SetSRID(ST_MakePoint(longitude,latitude),4326),32632))::numeric(10,1) as "UTM_EX", ' \
            'ST_Y(ST_Transform(ST_SetSRID(ST_MakePoint(longitude,latitude),4326),32632))::numeric(10,1) as "UTM_NY", ' \
                'elevation::numeric(10,3) as "HEIGHT", ' \
                'commence as "DATA_INST", ' \
                'COALESCE(cease, CURRENT_TIMESTAMP) as "DATA_DISINST" ' \
                'FROM climatlas.station ORDER BY code'
        stations_csv = pg.pg_command(self.pgdb, query, output={"format": "csvh", "delimiter": ";"})
        with open(os.path.join(tempbins, "input", "anagrafica.csv"), "w") as text_file:
            text_file.write(stations_csv)

        # export data to CSV in temp dir
        query = "SELECT s.code, to_char(t.date, 'DD/MM/YYYY 00:00'), t.val," \
                "CASE WHEN t.code<4 THEN 1 ELSE 2 END, NULL " \
                "FROM climatlas.{dbtable} t LEFT JOIN climatlas.station s ON s.id = t.station_id " \
                "WHERE t.date = '{y}-{m}-{d}'".format(dbtable=db_table, y=year, m=month, d=day)
        data_csv = pg.pg_command(self.pgdb, query, output={"format": "csv", "delimiter": ";"})
        with open(os.path.join(tempbins, "input", input_csv), "w") as text_file:
            text_file.write(data_csv)

        # create output dirs (for fortran asc and final tiff file)
        utils.mkdir_p(tempout)
        utils.mkdir_p(outdir)

        # run computation (fortran executable)
        cmd = ["-c", "./{ex} {y}{m}{d}00 01 . . > execution.log".format(ex=executable, y=year, m=month, d=day)]
        utils.call_command(cmd, shell=True)

        # generate tiff from asc file in tiff dir (outside temp dir)
        out_tif = os.path.join(outdir, "{tp}{y}{m}{d}.tif".format(tp=type_prefix, y=year, m=month, d=day))
        self.__asc_to_tiff(tempasc, out_tif)

        # drop temp dir (or temporary outputs)
        if temp_dir is None:
            shutil.rmtree(tempdir)
        else:
            shutil.rmtree(tempout)
            if type_prefix == "p":
                shutil.rmtree(os.path.join(tempbins, "p_stationanalisys"))

        #check if map is empty
        map = gdal.Open(out_tif, GA_ReadOnly)
        map_width = map.RasterXSize
        map_height = map.RasterYSize
        arr = map.ReadAsArray(0, 0, map_width, map_height)
        if (arr == -9999).all():
            logging.info("Map " + out_tif + " is null")
            os.unlink(out_tif)
            return

        return out_tif

    # generates tiff file (temperature/precipitation) for a given month (input data is from daily tif file)
    def generate_month(self, type_prefix, year, month):
        year = int(year)
        month = int(month)
        skip, stop = monthrange(year, month)
        file_list = []
        for i in range(1, stop + 1):
            file_list.append(self.get_file_path(type_prefix, year=year, month=month, day=i))

        output_file = self.get_file_path(type_prefix, year=year, month=month)
        if type_prefix == self.TEMP_PREFIX:
            self.compute_map(file_list, output_file, "mean")
        elif type_prefix == self.PREC_PREFIX:
            self.compute_map(file_list, output_file, "sum")

        return output_file

    # generates tiff file (temperature/precipitation) for a given year (input data is from daily tif file)
    def generate_year(self, type_prefix, year):
        year = int(year)
        file_list = []
        for month in range(1, 13):
            skip, stop = monthrange(year, month)
            for i in range(1, stop + 1):
                file_list.append(self.get_file_path(type_prefix, year=year, month=month, day=i))

        output_file = self.get_file_path(type_prefix, year=year)
        if type_prefix == self.TEMP_PREFIX:
            self.compute_map(file_list, output_file, "mean")
        elif type_prefix == self.PREC_PREFIX:
            self.compute_map(file_list, output_file, "sum")

        return output_file

    # generates tiff file (temperature/precipitation) for a given season in a year (input data is from daily tif file)
    def generate_season(self, type_prefix, year, season):
        if season not in self.SEASONS:
            raise Exception("Season not found")
        year = int(year)
        file_list = []

        # winter (dec,jan,feb) is a special case, starts in previous year
        if season == self.SEASONS[0]:
            tupl = [(year - 1, 12), (year, 1), (year, 2)]
        # spring (mar, apr, may)
        elif season == self.SEASONS[1]:
            tupl = [(year, 3), (year, 4), (year, 5)]
        # summer (jun, jul, aug)
        elif season == self.SEASONS[2]:
            tupl = [(year, 6), (year, 7), (year, 8)]
        # autumn (sep, oct, nov)
        elif season == self.SEASONS[3]:
            tupl = [(year, 9), (year, 10), (year, 11)]

        for (y, m) in tupl:
            skip, stop = monthrange(y, m)
            for i in range(1, stop + 1):
                file_list.append(self.get_file_path(type_prefix, year=y, month=m, day=i))

        output_file = self.get_season_pah(type_prefix, year, season)
        if type_prefix == self.TEMP_PREFIX:
            self.compute_map(file_list, output_file, "mean")
        elif type_prefix == self.PREC_PREFIX:
            self.compute_map(file_list, output_file, "sum")

        return output_file

    def compute_anomaly(self, type_prefix, period, year, month=None, season=None, computation_type="diff", around=-1):
        ref_map = gdal.Open(self.ref_map, GA_ReadOnly)
        if ref_map is None:
            print 'Could not open ' + str(ref_map)

        map_width = ref_map.RasterXSize
        map_height = ref_map.RasterYSize
        mask = ref_map.ReadAsArray(0, 0, map_width, map_height)

        ref_file = self.get_period_path(type_prefix, period, month=month, season=season)
        if season is None:
            input_file = self.get_file_path(type_prefix, year, month)
        else:
            input_file = self.get_season_pah(type_prefix, year, season)

        current_map = gdal.Open(input_file, GA_ReadOnly)
        if current_map is None:
            raise Exception("Period not found")

        period_map = gdal.Open(ref_file, GA_ReadOnly)
        if current_map is None:
            raise Exception("Map not found")

        current_arr = current_map.ReadAsArray(0, 0, map_width, map_height)
        period_arr = period_map.ReadAsArray(0, 0, map_width, map_height)

        if computation_type == "diff":
            output = current_arr - period_arr
            output_file = self.get_anomaly_path(type_prefix, period, year=year, month=month, season=season, suffix="d")

        elif computation_type == "perc":
            #output = (current_arr - period_arr) * 100 / period_arr
            output = current_arr * 100 / period_arr
            output_file = self.get_anomaly_path(type_prefix, period, year=year, month=month, season=season, suffix="p")
        else:
            raise Exception("computation_type not allow")

        #set nodata values from reference map
        output[np.where(mask == -9999)] = -9999
        if around > -1:
            output = np.around(output, around)

        out_map = gdal.GetDriverByName('GTiff').Create(output_file, map_width, map_height, 1, gdal.GDT_Float32)
        out_map.SetProjection(ref_map.GetProjection())
        out_map.SetGeoTransform(ref_map.GetGeoTransform())
        out_map.GetRasterBand(1).SetNoDataValue(-9999)
        out_map.GetRasterBand(1).WriteArray(output, 0, 0)
        self.geoserver_upload(output_file)
        return output_file

    # generates tiff file (temperature/precipitation) for a given multiyear period (input is year(+month) tif file)
    def generate_period(self, type_prefix, period, month=None):
        if period not in self.PERIODS:
            raise Exception("Period not found")
        file_list = []
        pstart = self.period_start(period)
        pend = self.period_end(period)

        for year in range(pstart, pend + 1):
            file_list.append(self.get_file_path(type_prefix, year=year, month=month))

        output_file = self.get_period_path(type_prefix, period, month=month)
        if type_prefix == self.TEMP_PREFIX:
            self.compute_map(file_list, output_file, "mean")
        elif type_prefix == self.PREC_PREFIX:
            self.compute_map(file_list, output_file, "mean", around=-1)

        self.geoserver_upload(output_file)
        return output_file

    # generates tiff file (temperature/precipitation) for a given season in period (input is season tif file)
    def generate_period_season(self, type_prefix, period, season):
        if period not in self.PERIODS:
            raise Exception("Period not found")
        if season not in self.SEASONS:
            raise Exception("Season not found")
        file_list = []
        pstart = self.period_start(period)
        pend = self.period_end(period)

        for year in range(pstart, pend + 1):
            file_list.append(self.get_season_pah(type_prefix, year, season))

        output_file = self.get_period_path(type_prefix, period, season=season)
        if type_prefix == self.TEMP_PREFIX:
            self.compute_map(file_list, output_file, "mean")
        elif type_prefix == self.PREC_PREFIX:
            self.compute_map(file_list, output_file, "mean", around=-1)

        self.geoserver_upload(output_file)
        return output_file

    def generate_all_anomalies(self):
        period = self.PERIODS[2]

        delta = (self.DATE_END.year - self.DATE_START.year) + 1
        for y in range(self.DATE_START.year, self.DATE_START.year + delta):
            self.compute_anomaly(self.TEMP_PREFIX, period, year=y, month=None, season=None, computation_type="diff")
            self.compute_anomaly(self.PREC_PREFIX, period, year=y, month=None, season=None, computation_type="diff")
            self.compute_anomaly(self.PREC_PREFIX, period, year=y, month=None, season=None, computation_type="perc")
            for m in range(1, 13):
                self.compute_anomaly(self.TEMP_PREFIX, period, year=y, month=m, season=None, computation_type="diff")
                self.compute_anomaly(self.PREC_PREFIX, period, year=y, month=m, season=None, computation_type="diff")
                self.compute_anomaly(self.PREC_PREFIX, period, year=y, month=m, season=None, computation_type="perc")
            for s in self.SEASONS:
                self.compute_anomaly(self.TEMP_PREFIX, period, year=y, month=None, season=s, computation_type="diff")
                self.compute_anomaly(self.PREC_PREFIX, period, year=y, month=None, season=s, computation_type="diff")
                self.compute_anomaly(self.PREC_PREFIX, period, year=y, month=None, season=s, computation_type="perc")

    def generate_all_days(self):
        delta = (self.DATE_END - self.DATE_START).days + 1
        dateList = [self.DATE_START + datetime.timedelta(days=x) for x in range(0, delta)]
        for date in dateList:
            self.generate_day(self.TEMP_PREFIX, date.year, date.month, date.day)
            self.generate_day(self.PREC_PREFIX, date.year, date.month, date.day)

    def generate_all_months(self):
        delta = (self.DATE_END.year - self.DATE_START.year) + 1
        for y in range(self.DATE_START.year, self.DATE_START.year + delta):
            for m in range(1, 13):
                self.generate_month(self.TEMP_PREFIX, y, m)
                self.generate_month(self.PREC_PREFIX, y, m)

    def generate_all_years(self):
        delta = (self.DATE_END.year - self.DATE_START.year) + 1
        for y in range(self.DATE_START.year, self.DATE_START.year + delta):
            self.generate_year(self.TEMP_PREFIX, y)
            self.generate_year(self.PREC_PREFIX, y)

    def generate_all_seasons(self):
        delta = (self.DATE_END.year - self.DATE_START.year) + 1
        for y in range(self.DATE_START.year + 1, self.DATE_START.year + delta):
            for s in self.SEASONS:
                self.generate_season(self.TEMP_PREFIX, y, s)
                self.generate_season(self.PREC_PREFIX, y, s)

    def generate_all_periods(self):
        for p in self.PERIODS:
            self.generate_period(self.TEMP_PREFIX, p)
            self.generate_period(self.PREC_PREFIX, p)
            for m in range(1, 13):
                self.generate_period(self.TEMP_PREFIX, p, m)
                self.generate_period(self.PREC_PREFIX, p, m)
            for s in self.SEASONS:
                self.generate_period_season(self.TEMP_PREFIX, p, s)
                self.generate_period_season(self.PREC_PREFIX, p, s)

    def generate_all(self):
        self.generate_all_months()
        self.generate_all_years()
        self.generate_all_seasons()
        self.generate_all_periods()
        self.generate_all_anomalies()

    def generate_station(self, type_prefix):
        query = "SELECT code, " \
            "ST_X(ST_Transform(ST_SetSRID(ST_MakePoint(longitude,latitude),4326),32632))::numeric(10,1) as \"UTM_EX\", " \
            "ST_Y(ST_Transform(ST_SetSRID(ST_MakePoint(longitude,latitude),4326),32632))::numeric(10,1) as \"UTM_NY\", " \
                "the_geom FROM climatlas.station " \
                "RIGHT JOIN ( " \
                "   SELECT station_id FROM climatlas.{type} " \
                "   WHERE date between '1961-01-01' and '2011-01-01' group by station_id " \
                ") AS sta on station.id=sta.station_id;"
        if type_prefix == self.TEMP_PREFIX:
            queryf = query.format(type="temp_avg")
        else:
            queryf = query.format(type="rain")

        cmd = ["pgsql2shp", "-h", self.pghost, "-u", self.pguser, "-P", self.pgpass, "-f",
               "{td}/{tp}stations.shp".format(td=self.tiffdir, tp=type_prefix), self.pgdb,
               "{query}".format(query=queryf)]
        utils.call_command(cmd)
        self.geoserver_upload_shape("{td}/{tp}stations".format(td=self.tiffdir, tp=type_prefix))


# ./tmean_day_calc 1962101000 01 . out > execution.log
def main():
    m = Mapgen("/geostore/mapgen/bins", "/geostore/tiffs")

    #m.generate_season(m.PREC_PREFIX, 2010, m.SEASONS[0])

    #START = datetime.date(1940, 1, 1)
    #END = datetime.date(1961, 1, 1)
    #delta = (END - START).days + 1
    #dateList = [START + datetime.timedelta(days=x) for x in range(0, delta)]
    #for date in dateList:
    #    m.generate_day(m.TEMP_PREFIX, date.year, date.month, date.day)
    #    m.generate_day(m.PREC_PREFIX, date.year, date.month, date.day)

    #m.generate_day(m.TEMP_PREFIX, 1940, 1, 1)

    #m.compute_anomaly("p", m.PERIODS[2], 1961, computation_type="perc")

    #m.generate_station("p")


if __name__ == "__main__":
    main()
