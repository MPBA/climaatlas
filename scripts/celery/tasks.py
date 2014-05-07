# coding=utf-8
from __future__ import absolute_import
import time
import os
import sys
import inspect
import functools
from datetime import datetime
import psycopg2

from celeryapp import app
from celery import group, chain, chord
from celery.utils.log import get_task_logger

from local_settings import psycopg_conf

# import mapgen
currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, os.path.join(parentdir, 'mapgen'))

from genday import Mapgen


def track_status(name):
    def dat_actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # statuses:
            # 0: never executed
            # 1: executing
            # 2: already executed
            with psycopg2.connect(**psycopg_conf) as conn:
                with conn.cursor() as cur:
                    # Q: OMG n00b this is vulnerable to SQL injection
                    # A: I know, but this won't be accessible by anyone. NP.
                    cur.execute(
                        'UPDATE task_progress SET {0}_start=%s, {0}_status=1 WHERE active'.format(
                            name),
                        (datetime.now(),)
                    )
            ret = True
            time.sleep(5)
            # ret = func(*args, **kwargs)

            with psycopg2.connect(**psycopg_conf) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        'UPDATE task_progress SET {0}_end=%s, {0}_status=2 WHERE active'.format(
                            name),
                        (datetime.now(),)
                    )

            return ret

        return wrapper

    return dat_actual_decorator


@app.task(queue='geoatlas')
def set_started(name):
    with psycopg2.connect(**psycopg_conf) as conn:
        with conn.cursor() as cur:
            cur.execute(
                'UPDATE task_progress SET {0}_start=%s, {0}_status=1 WHERE active'.format(
                    name),
                (datetime.now(),)
            )


@app.task(queue='geoatlas')
def set_finished(name):
    with psycopg2.connect(**psycopg_conf) as conn:
        with conn.cursor() as cur:
            cur.execute(
                'UPDATE task_progress SET {0}_end=%s, {0}_status=2 WHERE active'.format(
                    name),
                (datetime.now(),)
            )


def track_status_group(name):
    def dat_actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # statuses:
            # 0: never executed
            # 1: executing
            # 2: already executed
            return set_started.si(name) | set_finished.si(name)
            tasks_group = func(*args, **kwargs)
            return set_started.si(name) | chord(tasks_group,
                                                set_finished.si(name))

        return wrapper

    return dat_actual_decorator


@app.task(queue='geoatlas')
def chord_finisher(*args, **kwargs):
    """
    Ugly hack borrowed from http://stackoverflow.com/questions/15123772/
    """
    return "OK"


@app.task(queue='geoatlas')
@track_status('step1')
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


@app.task(queue='geoatlas')
@track_status('step2')
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


@app.task(queue='geoatlas')
def step3():
    pass


@app.task(queue='geoatlas')
@track_status('step4')
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


@app.task(queue='geoatlas')
@track_status('step5')
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


@app.task(queue='geoatlas')
@track_status('step6')
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


@app.task(queue='geoatlas')
@track_status('step7')
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


@app.task(queue='geoatlas')
def _step8(mean_year, pstart, pend):
    with psycopg2.connect(**psycopg_conf) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select * from step_eight_celery({0}::INT, {1}::INT, {2}::INT);"
                .format(mean_year, pstart, pend)
            )


@app.task(queue='geoatlas')
@track_status_group('step8')
def step8_group(params):
    tasks = []

    # todo: GESTIRE POOL SEPARATI PER EVITARE DI FARE ESPLODERE IL SERVER
    if params['periods']:
        years = range(params['min_date'], params['max_date'] + 1)
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


@app.task(queue='geoatlas')
def step9():
    #
    pass


@app.task(queue='geoatlas')
def _step10(pstart, pend):
    with psycopg2.connect(**psycopg_conf) as conn:
        with conn.cursor() as cur:
            cur.execute(
                'select * from step_ten_celery({0}::INT,{1}::INT)'
                .format(pstart, pend)
            )


@app.task(queue='geoatlas')
@track_status_group('step10')
def step10_group(params):
    tasks = []
    if params['periods']:
        for period in params['periods']:
            pstart, pend = map(int, period.split('-'))
            tasks.append(_step10.si(pstart, pend))

    return group(*tasks)


@app.task(queue='geoatlas')
@track_status('step11')
def step11(params):
    with psycopg2.connect(**psycopg_conf) as conn:
        with conn.cursor() as cur:
            cur.execute(" select * from plr_set_display(':5.0');")
            cur.execute(
                "select * from step_eleven("
                " (select robj from rdata where step = 1)"
                " ); "
            )


@app.task(queue='geoatlas')
def _generate_day(day, type_prefix):
    m = Mapgen("/geostore/mapgen/bins", "/geostore/tiffs")
    m.generate_day(type_prefix, day.year, day.month, day.day)


@app.task(queue='geoatlas')
def generate_days_group(params):
    tasks = []

    for day in params['dates']:
        tasks.append(_generate_day.si(day, 'p'))
        tasks.append(_generate_day.si(day, 't'))

    return group(*tasks)


@app.task(queue='geoatlas')
def generate_all(params):
    # va eseguito dopo avere modificato i giorni, non prende parametri
    m = Mapgen("/geostore/mapgen/bins", "/geostore/tiffs")
    m.generate_all()

    # set active to False
    with psycopg2.connect(**psycopg_conf) as conn:
        with conn.cursor() as cur:
            cur.execute(
                'UPDATE task_progress SET active=false WHERE active=true')


@app.task(queue='geoatlas')
def launch_celery_tasks():
    # fixme: are 3 different connections really necessary?
    with psycopg2.connect(**psycopg_conf) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT COUNT(*) FROM task_progress WHERE active')
            if cur.fetchone()[0]:
                return

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

    if dates is None:
        return None

    # DAT python2.6 which doesn't support set comprehension ~.~"
    years = set()
    for date in dates:
        years.add(date.year)
    years = list(years)

    p = dict(
        min_date=min_date,
        max_date=max_date,
        periods=res[2],
        dates=dates,
        years=years
    )
    with psycopg2.connect(**psycopg_conf) as conn:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO task_progress(id) VALUES(DEFAULT)')

    return (
        step1.si(p) |  # launch step1 and wait until it finishes
        chord([  # then launch step2, 4, 8 and 11 together
                 (
                     chord([step2.si(p), step4.si(p)], chord_finisher.si()) |

                     # when both step2 and step4 have finished, launch step10,7,5,6.
                     # note that step10 spawns a bunch of subtasks
                     chord([step10_group(p), step7.si(p), step5.si(p),
                            step6.si(p)], chord_finisher.si())
                 ),
                 step8_group(p),
                 step11.si(p)
              ], chord_finisher.si())  # |

        # when all of the above terminates, launch generate_days first
        #generate_days_group(p) |
        #generate_all.si(p)  # and generate_all then
    ).apply_async(queue='geoatlas')


@app.task(queue='geoatlas')
def generate_maps():
    # todo: se chiamato solo per stazioni, settare tutti gli step a fatti e fare solo questo
    with psycopg2.connect(**psycopg_conf) as conn:
        with conn.cursor() as cur:
            cur.call_proc('import_sites')
            date_start, date_end = cur.fetchone()

    if date_start and date_end:
        m = Mapgen("/geostore/mapgen/bins", "/geostore/tiffs")
        m.DATE_START = datetime.date(date_start.year, 1, 1)
        m.DATE_END = datetime.date(date_end.year, 12, 31)
        m.generate_all()


