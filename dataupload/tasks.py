# coding=utf-8
from __future__ import absolute_import
import time

from .celery import app
from celery import group, chain, chord
from celery.utils.log import get_task_logger
from django.conf import settings

from .mapgen.genday import Mapgen

import psycopg2

logger = get_task_logger(__name__)

dj_db = settings.DATABASES['default']
psycopg_conf = {
    'database': dj_db['NAME'],
    'user': dj_db['USER'],
    'password': dj_db['PASSWORD'],
    'host': dj_db['HOST'],
    'port': dj_db['PORT']
}


@app.task
def step1(params):
    with psycopg2.connect(**psycopg_conf) as conn:
        with conn.cursor() as cur:
            cur.execute("select * from plr_set_display(':5.0');")
            cur.execute("delete from rdata where step = 1;")
            cur.execute(
                "insert into rdata values "
                "(1,step_one({min_date}::INT, {max_date}::INT));"
                .format(**params)
            )


@app.task
def step2(params):
    with psycopg2.connect(**psycopg_conf) as conn:
        with conn.cursor() as cur:
            cur.execute("select * from plr_set_display(':5.0');")
            cur.execute("delete from rdata where step = 2;")
            cur.execute(
                "insert into rdata values (2,"
                "step_two((select robj from rdata where step = 1),"
                "{min_date}::INT,{max_date}::INT));".format(**params)
            )


@app.task
def step3():
    pass


@app.task
def step4(params):
    if params['periods']:
        with psycopg2.connect(**psycopg_conf) as conn:
            with conn.cursor() as cur:
                cur.execute("select * from plr_set_display(':5.0');")
                cur.execute("delete from rdata where step = 4;")
                cur.execute(
                    "insert into rdata values (4,"
                    "step_four((select robj from rdata where step = 1)));"
                )


@app.task
def step5(params):
    with psycopg2.connect(**psycopg_conf) as conn:
        with conn.cursor() as cur:
            cur.execute("select * from plr_set_display(':5.0');")
            cur.execute(" delete from rdata where step = 5;")
            cur.execute(
                "insert into rdata values (5, "
                "step_five( (select robj from rdata where step = 1),"
                " (select robj from rdata where step = 2),"
                " {min_date}::INT, {max_date}::INT ) );".format(**params)
            )


@app.task
def step6(params):
    with psycopg2.connect(**psycopg_conf) as conn:
        with conn.cursor() as cur:
            cur.execute(" select * from plr_set_display(':5.0');")
            cur.execute(
                """
                with rdata as (
                    select (select robj from rdata where step = 1) as step1,
                        (select robj from rdata where step = 2) as step2
                ), periods as (
                    select 1961 pstart, 1990 pend
                    union select 1971, 2000
                    union select 1981, 2010
                ) select step_six(
                    step1,
                    step2,
                    pstart,
                    pend
                ) from rdata cross join periods;
                """
            )


@app.task
def step7(params):
    if params['periods']:
        with psycopg2.connect(**psycopg_conf) as conn:
            with conn.cursor() as cur:
                cur.execute(" select * from plr_set_display(':5.0');")
                cur.execute(
                    "select * from step_seven( "
                    "(select robj from rdata where step = 1),"
                    " (select robj from rdata where step = 2),"
                    " (select robj from rdata where step = 4) "
                    ");"
                )


@app.task
def _step8(mean_year, pstart, pend):
    with psycopg2.connect(**psycopg_conf) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select * from step_eight_celery({0}::INT, {1}::INT, {2}::INT);"
                .format(mean_year, pstart, pend)
            )

@app.task
def step8_group(params):
    tasks = []

    # todo: GESTIRE POOL SEPARATI PER EVITARE DI FARE ESPLODERE IL SERVER
    if params['periods']:
        years = range(params['min_date'], params['max_date']+1)
        periods = params['periods']
    else:
        years = params['years']
        periods = ['1961-1990', '1971-2000', '1981-2010']

    for year in years:
        if '1961-1990' in periods:
            tasks.append(_step8.si(year, 1961, 1990))

        if '1971-2000' in periods:
            tasks.append(_step8.si(year, 1971, 2000))

        if '1981-2010' in periods:
            tasks.append(_step8.si(year, 1981, 2010))

    return group(*tasks)


@app.task
def step9():
    #
    pass

@app.task
def _step10(pstart, pend):
    with psycopg2.connect(**psycopg_conf) as conn:
        with conn.cursor() as cur:
            cur.execute(
                'select * from step_ten_celery({0}::INT,{1}::INT)'
                .format(pstart, pend)
            )


@app.task
def step10_group(params):
    tasks = []
    if params['periods']:
        for period in params['periods']:
            pstart, pend = map(int, period.split('-'))
            tasks.append(_step10.si(pstart, pend))

    return group(*tasks)


@app.task
def step11(params):
    with psycopg2.connect(**psycopg_conf) as conn:
        with conn.cursor() as cur:
            cur.execute(" select * from plr_set_display(':5.0');")
            cur.execute(
                "select * from step_eleven("
                " (select robj from rdata where step = 1)"
                " ); "
            )


@app.task
def _generate_day(day, type_prefix):
    m = Mapgen("/geostore/mapgen/bins", "/geostore/tiffs")
    m.generate_day(type_prefix, day.year, day.month, day.day)


@app.task
def generate_days_group(params):
    tasks = []

    for day in params['dates']:
        tasks.append(_generate_day.si(day, 'p'))
        tasks.append(_generate_day.si(day, 't'))

    return group(*tasks)


@app.task
def generate_all(params):
    # va eseguito dopo avere modificato i giorni, non prende parametri
    m = Mapgen("/geostore/mapgen/bins", "/geostore/tiffs")
    m.generate_all()


@app.task
def launch_celery_tasks():
    with psycopg2.connect(**psycopg_conf) as conn:
        with conn.cursor() as cur:
            cur.execute("select * from import_all();")

    with psycopg2.connect(**psycopg_conf) as conn:
        with conn.cursor() as cur:
            cur.execute("select * from import_changes();")
            res = cur.fetchone()

    min_date = res[0] if res[0] < 1921 else 1921
    max_date = res[1] if res[1] > 2011 else 2011
    min_date, max_date = map(int, (min_date, max_date))
    dates = res[3]
    years = list({ date.year for date in dates })
    p = dict(
        min_date=min_date,
        max_date=max_date,
        periods=res[2],
        dates=dates,
        years=years
    )

    logger.info(u'==== LAUNCHING MEGACHAIN  ====')

    (
        step1.si(p) |  # launch step1 and wait until it finishes
        group(  # then launch step2, 4, 8 and 11 together
            (
                group(step2.si(p), step4.si(p)) |

                # when both step2 and step4 have finished, launch step10,7,5,6.
                # note that step10 spawns a bunch of subtasks
                group(step10_group(p), step7.si(p), step5.si(p), step6.si(p))
            ),
            step8_group(p),
            step11.si(p)
        ) |  # when all of the above terminates, launch generate_days first
        generate_days_group(p) |
        generate_all.si(p)  # and generate_all then
    )()

