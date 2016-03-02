# coding=utf-8
from __future__ import absolute_import
import os
import sys
import inspect
import functools
from datetime import datetime
import psycopg2

from dataupload.celeryapp import app
from celery import group, chain, chord
from django.conf import settings

psycopg_conf = settings.PSYCOPG_CONF
MAPGEN_BINS = settings.MAPGEN_BINS
MAPGEN_TIFFS = settings.MAPGEN_TIFFS
# I TRULY HOPE NOBODY WILL HAVE TO WORK ON THIS CODE :)

# import mapgen
currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, os.path.join(parentdir, 'mapgen'))

from scripts.mapgen.genday import Mapgen


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
                    # A: I know, but this won't be accessible by evil ppl. NP.
                    cur.execute(
                        'UPDATE task_progress SET {0}_start=%s, {0}_status=1 WHERE active'.format(
                            name),
                        (datetime.now(),)
                    )
            ret = func(*args, **kwargs)

            with psycopg2.connect(**psycopg_conf) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        'UPDATE task_progress SET {0}_end=%s, {0}_status=2 WHERE active'.format(
                            name),
                        (datetime.now(),)
                    )

            return ret if ret is not None else True

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
            tasks_group = func(*args, **kwargs)
            return set_started.si(name) | group(tasks_group) | set_finished.si(name)

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

    return tasks


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


@track_status_group('step10')
def step10_group(params):
    tasks = []
    if params['periods']:
        for period in params['periods']:
            pstart, pend = map(int, period.split('-'))
            tasks.append(_step10.si(pstart, pend))

    return tasks


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
    pc = psycopg_conf
    m = Mapgen(MAPGEN_BINS, MAPGEN_TIFFS,
               pguser=pc['user'], pgdb=pc['database'],
               pgpass=pc['password'], pghost=pc['host'])
    m.generate_day(type_prefix, day.year, day.month, day.day)


def generate_days_group(params):
    tasks = []

    for day in params['dates']:
        tasks.append(_generate_day.si(day, 'p'))
        tasks.append(_generate_day.si(day, 't'))

    return set_started.si('map') | chord(tasks, chord_finisher.si())


@app.task(queue='geoatlas')
def generate_all(params):
    # va eseguito dopo avere modificato i giorni, non prende parametri
    pc = psycopg_conf
    m = Mapgen(MAPGEN_BINS, MAPGEN_TIFFS,
               pguser=pc['user'], pgdb=pc['database'],
               pgpass=pc['password'], pghost=pc['host'])
    m.generate_all()


@app.task(queue='geoatlas')
def set_finished_megachain():
    with psycopg2.connect(**psycopg_conf) as conn:
        with conn.cursor() as cur:
            cur.execute(
                'UPDATE task_progress SET active=false, ts_end=%s WHERE active',
                datetime.now()
            )

@app.task(queue='geoatlas')
def dumb_task():
    """
    Needed for task-synchronization purposes.
    As of celery 3.1.11, this is needed, otherwise celery will blow up
    """
    return True


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

    print "here"
    min_date = res[0] if res[0] < 1921 else 1921
    max_date = res[1] if res[1] > 2011 else 2011
    min_date, max_date = map(int, (min_date, max_date))
    dates = res[3]
    print dates

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

    step8 = step8_group(p)
    step10 = step10_group(p)
    generate_days = generate_days_group(p)

    return (
        step1.si(p) |
        group(step2.si(p), step4.si(p)) |
        dumb_task.si() | dumb_task.si() |
        group(
            step11.si(p),
            step7.si(p),
            step5.si(p),
            step6.si(p),
        ) |
        dumb_task.si() | dumb_task.si() |
        step10 | step8 |
        generate_days |
        generate_all.si(p) |
        set_finished_megachain.si(p)
    ).apply_async(queue='geoatlas')


@app.task(queue='geoatlas')
def generate_maps():
    with psycopg2.connect(**psycopg_conf) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT COUNT(*) FROM task_progress WHERE active')
            if cur.fetchone()[0]:
                return False

            cur.callproc('import_sites')
            date_start, date_end = cur.fetchone()

            if None in (date_start, date_end):
                return False

            cur.execute('INSERT INTO task_progress(id) VALUES(DEFAULT)')

            # set all the other task as 'finished'
            giant_query = \
                'UPDATE task_progress SET ' \
                'step1_start={ts}, step1_status=2, step1_end={ts},' \
                'step2_start={ts}, step2_status=2, step2_end={ts}' \
                'step4_start={ts}, step4_status=2, step4_end={ts}' \
                'step5_start={ts}, step5_status=2, step5_end={ts}' \
                'step6_start={ts}, step6_status=2, step6_end={ts}' \
                'step7_start={ts}, step7_status=2, step7_end={ts}' \
                'step8_start={ts}, step8_status=2, step8_end={ts}' \
                'step10_start={ts}, step10_status=2, step10_end={ts}' \
                'step11_start={ts}, step11_status=2, step11_end={ts}' \
                'map_start={ts}, map_status=1 WHERE active'.format(
                    ts=cur.mogrify('%s', datetime.now()),
                )
            cur.execute(giant_query)

        pc = psycopg_conf
        m = Mapgen(MAPGEN_BINS, MAPGEN_TIFFS,
                   pguser=pc['user'], pgdb=pc['database'],
                   pgpass=pc['password'], pghost=pc['host'])
        m.DATE_START = datetime(date_start.year, 1, 1)
        m.DATE_END = datetime(date_end.year, 12, 31)
        m.generate_all()

    set_finished.delay('map')
    set_finished_megachain.apply_async(queue='geoatlas')



