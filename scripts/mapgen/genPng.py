#import genday
from owslib.wms import WebMapService
import urllib2
import StringIO
import Image, ImageDraw, ImageFont
import os

class GenerateImmage(object):
    P_YEAR = "PrecipitazioniAnnuali"
    P_MONTH = "PrecipitazioniMensili"
    P_SEASON = "PrecipitazioniStagionali"
    T = "Temperature"
    P_YEAR_L = "PrecipitazioniAnnualiLegend"
    P_MONTH_L = "PrecipitazioniMensiliLegend"
    P_SEASON_L = "PrecipitazioniStagionaliLegend"
    TEMP_PREFIX = "t"
    PREC_PREFIX = "p"
    STYLEA = "{D}A{P}{T}{L}"

    T_L = "TemperatureLegend"
    TESTO1="{type} media{s}{annual}"
    TESTO2="Periodo di riferimento {period}"

    TESTO1A="{type} - {s}{sp}{year}"

    BORDO="mpba:bordoTrentino"
    BORDOS="bordo"

    FONT="/geostore/script/verdana.ttf"

    MAP="{work}:{name}"

    MAP_SEASONS = ["1win", "2spr", "3sum", "4aut"]

    SEASONS = ["inverno", "primavera", "estate", "autunno"]
    MONTHS = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno"," luglio", "agosto", "settembre", "ottobre",
            "novembre", "dicembre"]
    STATION="{work}:station{prefix}"
    STATIONS="point"
    STAGIONE={(MAP_SEASONS[0]): SEASONS[0], (MAP_SEASONS[1]): SEASONS[1],
              (MAP_SEASONS[2]): SEASONS[2], (MAP_SEASONS[3]): SEASONS[3]}
    #def __init__(self, mapgen):
    GEOSERVER_HOST = "http://geoatlas:50001/geoserver/rest"
    GEOSERVER_WMS = "http://geoatlas:50001/geoserver/wms"
    GEOSERVER_USER = "admin"
    GEOSERVER_PASSWORD = "geoserver"
    GEOSERVER_WORKSPACE = "mpba"

    FILE_PERIOD = "{type}{period}{suffix}"
    FILE_PERIOD_MONTH = "{type}{period}{m}{suffix}"
    FILE_PERIOD_SEASON = "{type}{period}{season}{suffix}"

    FILE_ANOMALY = "{type}{period}-{y}{suffix}.tif"
    FILE_ANOMALY_MONTH = "{type}{period}{m}-{y}{m}{suffix}.tif"
    FILE_ANOMALY_SEASON = "{type}{period}{season}-{y}{season}{suffix}.tif"


    def __init__(self):
        pass
        #self.mapgen = mapgen
        #self.tiffdir = tiffdir
        #self.ref_map = os.path.join(self.tiffdir, self.REFERENCE_MAP)
    #mapName, style, leggend, testo, testoR, testol
    def __generate_pngL (self, mapName, style, leggend, testo, testop, testol, station, testos=""):
        #wms = WebMapService(GenerateImmage.GEOSERVER_WMS, version='1.1.1')
        #print "WMS end connect"
        #print mapName
        print station, self.STATIONS
        #img = wms.getmap(layers=["mpba:dtm_alps_all", mapName, self.BORDO, station], styles=["fbk_digital_terrain_model_0_4000", style,self.BORDOS,self.STATIONS ], srs='EPSG:32632', bbox=(610167.0,5057545.0,750567.0,5159345.0),size=(1400, 1000),format='image/png',  transparent=False)
        #img = wms.getmap(layers=['mpba:aspect', mapName, self.BORDO, station], styles=["rasterA", style,self.BORDOS,self.STATIONS ], srs='EPSG:32632', bbox=(610167.0,5057545.0,750567.0,5159345.0),size=(1400, 1000),format='image/png',  transparent=False)
        #img = wms.getmap(layers=[ mapName, self.BORDO, station], styles=[ style,self.BORDOS,self.STATIONS ], srs='EPSG:32632', bbox=(610167.0,5057545.0,750567.0,5159345.0),size=(1400, 1000),format='image/png',  transparent=False)
        img = self.getmap(layers=[ mapName, self.BORDO, station], styles=[ style,self.BORDOS,self.STATIONS ], srs='EPSG:32632', bbox=(610167.0,5057545.0,750567.0,5159345.0),size=(1400, 1000),format='image/png')

        #img = wms.getmap(layers=[ self.BORDO, station], styles=[self.BORDOS,self.STATIONS ], srs='EPSG:32632', bbox=(610167.0,5057545.0,750567.0,5159345.0),size=(1400, 1000),format='image/png',  transparent=False)
        leggend = self.getLeggend(leggend, mapName)
        #self.saveLayerAsImage(img, "/geostore/test/img.png")

        #self.saveLayerAsImage(leggend, "/geostore/test/legged.png")

        buffL = StringIO.StringIO()
        buffL.write(leggend.read())
        buffL.seek(0)
        legendPNG = Image.open(buffL)

        buffM= StringIO.StringIO()
        #print img.read()
        buffM.write(img.read())
        buffM.seek(0)
        ofset=200
        mapPNG = Image.new("RGB", (1400, 1100+ofset), "white")

        mapPNG1 = Image.open(buffM)
        mapPNG.paste(mapPNG1, (00, 0+ofset))

        mapPNG.paste(legendPNG, (1200, 50+ofset))#1200,100
        draw = ImageDraw.Draw(mapPNG)
        font = ImageFont.truetype(self.FONT, 36)
        font1 = ImageFont.truetype(self.FONT, 30)
        font2 = ImageFont.truetype(self.FONT, 16)

        testoLF="Leaflet: @PAT-Climatrentino"
        testoLF="@PAT-Climatrentino"

        #draw.text((50, 30),"Precipitazione Maggio ",(0,0,0),font=font)
        w, h = draw.textsize(testo,font=font)
        draw.text(((1400-w)/2, 30),testo,(0,0,0),font=font)
        #draw.text((50, 60),"Periodo di riferimento 1961 - 1990",(0,0,0),font=font1)
        w, h = draw.textsize(testop,font=font1)
        draw.text(((1400-w)/2, 80), testop, (0,0,0), font=font1)

        draw.text((1200, 0+ofset), testos, (0,0,0), font=font2)
        draw.text((1200, 30+ofset), testol, (0,0,0), font=font2)


        w, h = draw.textsize(testoLF,font=font1)
        draw.text(((1400-w)/2, 130), testoLF, (0,0,0), font=font1)

        #mapPNG.show()
        #####################################
        #Test Simboli
        img1 = Image.open("/geostore/test/PAT.png")
        x,y=img1.size
        div=3
        img1=img1.resize((x/div,y/div))
        #print img1
        mapPNG.paste(img1, (50, 30), mask=img1)

        img2 = Image.open("/geostore/test/p.png")
        x,y=img2.size
        div=1
        img2=img2.resize((x/div,y/div))
        #print img1
        mapPNG.paste(img2, (1200,30 ) , mask=img2)

        #
        #####################################

        mapPNG.save("/geostore/test/combinata1.png")

    @staticmethod
    def get_anomaly_name(type_prefix, period, year, month=None, season=None, suffix=None):
        if month is not None and month != "":
            month = str(int(month)).zfill(2)

            return GenerateImmage.FILE_ANOMALY_MONTH.format(type=type_prefix, period=period, y=year, m=month, suffix=suffix)
        elif season is not None and season != "":
            return GenerateImmage.FILE_ANOMALY_SEASON.format(type=type_prefix, period=period, y=year, season=season, suffix=suffix)
        else:
            return GenerateImmage.FILE_ANOMALY.format(type=type_prefix, period=period, y=year, suffix=suffix)
    @staticmethod
    def get_period_name( type_prefix, period, isoline=False, month=None, season=None):
        if not isoline:
            suffix = ".tif"
        else:
            suffix = ""

        if month is not None and month != "":
            month = str(int(month)).zfill(2)
            return GenerateImmage.FILE_PERIOD_MONTH.format(type=type_prefix, period=period, m=month, suffix=suffix)
        elif season is not None and season != "":
            return GenerateImmage.FILE_PERIOD_SEASON.format(type=type_prefix, period=period, season=season, suffix=suffix)
        else:
            return GenerateImmage.FILE_PERIOD.format(type=type_prefix, period=period, suffix=suffix)



    def generate_png(self, type_prefix, period, month=None, season=None, ):

        if type_prefix == GenerateImmage.TEMP_PREFIX:
            type = "Temperatura"
            style = self.T
            leggend = self.T_L
            testol=u"Temperatura [\xb0C]"

        elif type_prefix == GenerateImmage.PREC_PREFIX:
            type = "Precipitazione"
            style = None
            leggend = None
            testol="Precipitazione [mm]"
        else:
            raise Exception("Prefix not allow")

        station = self.STATION.format(work=GenerateImmage.GEOSERVER_WORKSPACE, prefix=type_prefix)

        if season is not None:
            symbol = " - "
            annual = self.STAGIONE[season]#SEASONS[season - 1]
            if type_prefix == GenerateImmage.PREC_PREFIX:
                style = self.P_SEASON
                leggend = self.P_SEASON_L

        elif month is not None:
            symbol = " - "
            annual = self.MONTHS[int(month) - 1]
            if type_prefix == GenerateImmage.PREC_PREFIX:
                style = self.P_MONTH
                leggend = self.P_MONTH_L
                #testol="Precipitazione [mm]"
        else:
            symbol = " "
            annual = "annuale"
            if type_prefix == GenerateImmage.PREC_PREFIX:
                style = self.P_YEAR
                leggend = self.P_YEAR_L
                #testol="Precipitazione [mm]"

        input_file = GenerateImmage.get_period_name(type_prefix, period, month=month, season=season)

        path, file_ext = os.path.split(input_file)
        f = os.path.splitext(file_ext)[0]

        mapName = GenerateImmage.MAP.format(work=GenerateImmage.GEOSERVER_WORKSPACE, name=f)
        #print "WMS start connect"
        #elf.TESTO1.format(type=type, s=symbol, annual=annual)
        testo = self.TESTO1.format(type=type, s=symbol, annual=annual)
        testoR = self.TESTO2.format(period = period)

        self.__generate_pngL(mapName, style, leggend, testo, testoR, testol,station)



    def generate_png_anomaly(self, type_prefix, types, year, month=None, season=None):
        period = "1981-2010"

        if type_prefix == GenerateImmage.TEMP_PREFIX:
            type = "Anomalia temperatura assoluta"
            pre = "Temperature"
            suf = ""
            testo="differenza"
            testol = u"Temperatura [\xb0C]"

        elif type_prefix == GenerateImmage.PREC_PREFIX:
            pre = "Precipitazioni"
            type = "Anomalia precipitazione "

            if types == "d":
                type += "assoluta"
                testol = "Precipitazione [mm]"
                suf = "A"
            elif types == "p":
                type += "percentuale"
                testol = "Precipitazione [%]"
                suf = ""
        else:
            raise Exception("Prefix not allow")
        station = self.STATION.format(work=GenerateImmage.GEOSERVER_WORKSPACE, prefix=type_prefix)

        y = str(year)
        if season is not None:
            symbol = " "
            annual = self.STAGIONE[season]#SEASONS[season - 1]
            per = "S"

        elif month is not None:
            symbol = " "
            annual = self.MONTHS[int(month) - 1]
            per = "M"
        else:
            symbol = ""
            annual = ""#str(year)
            per = "A"
        "{D}A{P}{T}{L}"
        style = self.STYLEA.format(D=pre, P=per, T=suf, L="")
        leggend = self.STYLEA.format(D=pre, P=per, T=suf, L="")

        input_file = GenerateImmage.get_anomaly_name(type_prefix,period, year,month, season, types)
        #input_file = self.mapgen.get_period_path(type_prefix, period, month=month, season=season)
        print "input_file", input_file
        path, file_ext = os.path.split(input_file)
        f = os.path.splitext(file_ext)[0]

        mapName = GenerateImmage.MAP.format(work=GenerateImmage.GEOSERVER_WORKSPACE, name=f)
        #print "WMS start connect"
        #elf.TESTO1.format(type=type, s=symbol, annual=annual)




        testo = self.TESTO1A.format(type=type, sp=symbol, s=annual, year=y )
        testoR = self.TESTO2.format(period = period)
        print "mapName", mapName
        self.__generate_pngL(mapName, style, leggend, testo, testoR, testol, station, "Anomalia" )




    def saveLayerAsImage(self, layer, inname):
        out = open(inname, 'wb')
        data = layer.read()
        #print data
        out.write(data)
        out.close()

    def getLeggend(self, style,layer):
        #print "getLeggend"
        print style
        print layer
        #legendUrl='http://geodata:50001/geoserver/wms?REQUEST=GetLegendGraphic&FORMAT=image/png&VERSION=1.1.0&&STYLE=PioggeMensili&WIDTH=30&HEIGHT=50&LEGEND_OPTIONS=forceRule:false;border:true;dx:2.2;dy:0.2;mx:2.2;my:0.2;&LAYER=test:PMediaMese_1961196205.tif'
        legendUrl=GenerateImmage.GEOSERVER_WMS+'?REQUEST=GetLegendGraphic&FORMAT=image/png&VERSION=1.1.0&&STYLE='+style+"&WIDTH=30&HEIGHT=30&LEGEND_OPTIONS=forceRule:false;border:true;dx:2.2;dy:0.2;mx:2.2;my:0.2;fontSize:20;fontAntiAliasing:true&LAYER="+layer
        #&LEGEND_OPTIONS=forceRule:false;border:true;dx:2.2;dy:0.2;mx:2.2;my:0.2;&LAYER=test:PMediaMese_1961196205.tif
        legend = urllib2.urlopen(legendUrl)
        return legend

    #img = wms.getmap(layers=[ mapName, self.BORDO, station], styles=[ style,self.BORDOS,self.STATIONS ], srs='EPSG:32632', bbox=(610167.0,5057545.0,750567.0,5159345.0),size=(1400, 1000),format='image/png',  transparent=False)
    def getmap(self, styles, layers,srs,bbox,size,format):

        ls=str(layers[0])
        for l in layers[1:]:
                ls +=","+l

        ss=str(styles[0])
        for s in styles[1:]:
                ss +=","+s
        bb1,bb2,bb3,bb4 = bbox
        bboxs = "{0},{1},{2},{3}".format(bb1,bb2,bb3,bb4)
        stringa = GenerateImmage.GEOSERVER_WMS +"?service=WMS&version=1.1.0&request=GetMap&" \
                                                "layers={layers}&styles={styles}&bbox={bbox}&" \
                                                "width={width}&height={heigth}&srs={srs}&format={format}"#image%2Fpng"# +"?REQUEST="+"""
        width, heigth = size
        url = stringa.format(layers=ls, styles=ss, bbox=bboxs, width=width, heigth=heigth, srs=srs, format=format )
        #print  url
        legend = urllib2.urlopen(url)
        return legend


def main():
    #m = genday.Mapgen("/geostore/mapgen/bins", "/geostore/tiffs")
    g = GenerateImmage()
    PERIODS = ["1961-1990", "1971-2000", "1981-2010"]
    #g.generate_png("t", PERIODS[0], month=None, season="1win" )#, season=genday.Mapgen.SEASONS[0])
    g.generate_png_anomaly("t", "d", year=2009, month=2, season=None)#, season=genday.Mapgen.SEASONS[0])
    mapName = ""
    #g.getMap()
if __name__ == "__main__":
    main()