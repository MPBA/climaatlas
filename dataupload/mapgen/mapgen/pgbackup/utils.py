import os
import subprocess
import logging
import shutil
import errno


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


def copy_anything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc:
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else:
            raise


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise