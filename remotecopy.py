from subprocess import call
map_type='t'
trentenni=['1961-1990','1971-2000','1981-2010']
mesi=['','01','02','03','04','05','06','07','08','09','10','11','12','1win','2spr','3sum','4aut']
for period in trentenni:
    for m in mesi:
        paste_str=map_type+period+m
        call(["scp", "geoserver@geoatlas:/geostore/geoserver/data_dir_50001/data/mpba/{0}/{0}.geotiff".format(paste_str),"./t_maps"])
