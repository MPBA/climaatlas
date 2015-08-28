import os
import time
import shutil
from pgutils import PGUtils

#import logging
#logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s')


def import_meteo_stations(pgdbf_path, dbf_path, fpt_path):
    pgu = PGUtils(host='geopg', user='climatlas')
    random = int(time.time())
    dbf = os.path.join('/tmp', '%d.dbf' % random)
    fpt = os.path.join('/tmp', '%d.fpt' % random)
    sql = os.path.join('/tmp', '%d.sql' % random)

    shutil.move(dbf_path, dbf)
    shutil.move(fpt_path, fpt)

    ## example: pgdbf -d -e -s ISO-8859-1 -m site.fpt site.dbf > export.sql
    pgu.os_command('%s -d -e -s ISO-8859-1 -m %s %s > %s' % (pgdbf_path, fpt, dbf, sql))
    pgu.pg_exec_file(sql, 'climatlas')
    pgu.os_command('rm -f %s %s %s' % (dbf, fpt, sql))


def import_meteo_stations(pgdbf_path, dbf_path, fpt_path):
    pgu = PGUtils(host='geopg', user='climatlas')
    random = int(time.time())
    dbf = os.path.join('/tmp', '%d.dbf' % random)
    fpt = os.path.join('/tmp', '%d.fpt' % random)
    sql = os.path.join('/tmp', '%d.sql' % random)

    shutil.move(dbf_path, dbf)
    shutil.move(fpt_path, fpt)

    ## example: pgdbf -d -e -s ISO-8859-1 -m site.fpt site.dbf > export.sql
    pgu.os_command('%s -d -e -s ISO-8859-1 -m %s %s > %s' % (pgdbf_path, fpt, dbf, sql))
    pgu.pg_exec_file(sql, 'climatlas')
    pgu.os_command('rm -f %s %s %s' % (dbf, fpt, sql))
