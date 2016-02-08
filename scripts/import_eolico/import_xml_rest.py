import os
from lxml import etree
import requests
import re

# Uso dei file xml di esempio da un raster per cui ho fatto il processo manualmente con GUI del geoserver
# Nei file cambio il nome del raster con {0}, e formatto la stringa

path = './geotiffeolico/'

# Remove format (mi aspetto tif)
files = [re.sub(r'\.\w*\Z', '', f) for f in os.listdir(path)]

'''
Richieste di esempio che ho usato per prendere i file xml
1) coverageStore
curl -u admin:geoserver -XGET -H "Accept: text/xml" http://geoatlas:50001/geoserver/rest/workspaces/mpba/coveragestores/w2004-2013ave10anno
Togliere a mano il tag <coverages>, viene inserito con i layer
2) layer
curl -u admin:geoserver -XGET -H "Accept: text/xml" http://geoatlas:50001/geoserver/rest/workspaces/mpba/coverages/w2004-2013ave10anno
3) style
curl -u admin:geoserver -XGET http://geoatlas:50001/geoserver/rest/layers/mpba:w2004-2013ave10anno.xml
Stili possibili:
w2004-2013ave
w2004-2013shape
w2004-2013scale
'''

parser = etree.XMLParser(remove_blank_text=True)
headers = {'Content-type': 'text/xml'}
with open('coveragestore.xml') as csf, open('coverages.xml') as cf, open('style.xml') as sf:
    coveragestore_data = etree.tostring(etree.parse(csf, parser), encoding='unicode', pretty_print=True)
    coverage_data = etree.tostring(etree.parse(cf, parser), encoding='unicode', pretty_print=True)
    style_data = etree.tostring(etree.parse(sf, parser), encoding='unicode', pretty_print=True)
    for i, f in enumerate(files):
        print(i, f)
        requests.post('http://geoatlas:50001/geoserver/rest/workspaces/mpba/coveragestores',
                      data=coveragestore_data.format(f), headers=headers, auth=('admin', 'geoserver'))
        requests.post('http://geoatlas:50001/geoserver/rest/workspaces/mpba/coveragestores/{}/coverages'.format(f),
                      data=coverage_data.format(f), headers=headers, auth=('admin', 'geoserver'))
        requests.put('http://geoatlas:50001/geoserver/rest/layers/mpba:{}'.format(f),
                     data=style_data.format(f, re.sub(r'\d{2}[a-z]*\Z', '', f)), headers=headers,
                     auth=('admin', 'geoserver'))
