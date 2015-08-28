__author__ = 'ernesto'
from zipfile import ZipFile
import collections
from django.conf import settings
from datetime import date
import os
import subprocess
import logging
import psycopg2
# from local_settings import psycopg_conf
from django.conf import settings

def valid_zip_file(request, file, accepted_names, typeofvalidation):
    if typeofvalidation == 'stazioni':
        zip_content = map(lambda x:x.lower(), ZipFile(file).namelist())
        zip_content_2 = map(lambda x:x, ZipFile(file).namelist())
        compare = lambda x, y: collections.Counter(x) == collections.Counter(y)
        if compare(zip_content, accepted_names):
            return True, zip_content_2
        else:
            return False, None
    elif typeofvalidation == 'dati':
        zip_content = map(lambda x: x.lower(), ZipFile(file).namelist())
        zip_content_2 = map(lambda x:x, ZipFile(file).namelist())
        compare = lambda x, y: collections.Counter(x) == collections.Counter(y)
        if compare(zip_content, accepted_names):
            return True, zip_content_2
        else:
            if len(list(set(zip_content).intersection(accepted_names))) > 0:
                return_list = []
                for a in zip_content_2:
                    if a.lower() in list(set(zip_content).intersection(accepted_names)):
                        return_list.append(a)
                return True, return_list
            else:
                return False, None
    else:
        return False, None


def handle_upload(request, file):
    upload_dir = date.today().strftime(settings.UPLOAD_PATH)
    upload_full_path = os.path.join(settings.UPLOAD_DIR, upload_dir)
    saved = ""
    if not os.path.exists(upload_full_path):
        os.makedirs(upload_full_path)
    if file:
        upload = file
        while os.path.exists(os.path.join(upload_full_path, upload.name)):
            upload.name = '_' + upload.name
        dest = open(os.path.join(upload_full_path, upload.name), 'wb')
        for chunk in upload.chunks():
            dest.write(chunk)
        dest.close()
        saved = os.path.join(upload_dir, upload.name)
    return saved


#Generic Postgres Server connection parameters
class PGServer(object):
    def __init__(self, name, port=5432, alias="", user="", password="", host="", bindir=""):
        self.name = name
        self.port = port
        self.user = user
        self.password = password
        self.host = host
        self.bindir = bindir
        self.alias = alias if alias else name


#calls an os command, returns a tuple with (stdout, stderr, unix_process_exit_code)
def call_command(command, environment=None, shell=False):
    env = os.environ.copy()
    if environment:
        env.update(environment)

    if type(command) is str:
        command = command.split(' ')

    logging.debug("COMMAND: " + " ".join(command))

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, shell=shell)
    streamdata = process.communicate()

    logging.debug("RETCOD: {code}".format(code=process.returncode))
    logging.debug("STDOUT: {outs}".format(outs=streamdata[0]))
    if len(streamdata[1].strip()) > 0:
        logging.warning("STDERR: {errs}".format(errs=streamdata[1]))

    return streamdata[0], streamdata[1], process.returncode


#determine nr. of cpu cores
def cpu_count(divide_by=1):
    import multiprocessing
    procs = multiprocessing.cpu_count()/int(divide_by)
    return procs if procs > 0 else 1


def get_tasks_progress():
    # with psycopg2.connect(**psycopg_conf) as conn:
    with psycopg2.connect(**settings.psycopg_conf) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM task_progress WHERE active')
            res = cur.fetchone()

            task_progress = None

            if res:  # a task is already running
                task_progress = {
                    'ts_start': res[2],
                    'steps': [
                        {
                            'name': 'step1',
                            'ts_start': res[4],
                            'ts_end': res[5],
                            'status': res[6]
                        },
                        {
                            'name': 'step2',
                            'ts_start': res[7],
                            'ts_end': res[8],
                            'status': res[9]
                        },
                        {
                            'name': 'step4',
                            'ts_start': res[10],
                            'ts_end': res[11],
                            'status': res[12]
                        },
                        {
                            'name': 'step5',
                            'ts_start': res[13],
                            'ts_end': res[14],
                            'status': res[15]
                        },
                        {
                            'name': 'step6',
                            'ts_start': res[16],
                            'ts_end': res[17],
                            'status': res[18]
                        },
                        {
                            'name': 'step7',
                            'ts_start': res[19],
                            'ts_end': res[20],
                            'status': res[21]
                        },
                        {
                            'name': 'step8',
                            'ts_start': res[22],
                            'ts_end': res[23],
                            'status': res[24]
                        },
                        {
                            'name': 'step10',
                            'ts_start': res[25],
                            'ts_end': res[26],
                            'status': res[27]
                        },
                        {
                            'name': 'step11',
                            'ts_start': res[28],
                            'ts_end': res[29],
                            'status': res[30]
                        },
                        {
                            'name': 'map_generation',
                            'ts_start': res[31],
                            'ts_end': res[32],
                            'status': res[33]
                        }
                    ]
                }

            return task_progress
