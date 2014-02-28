import os
import subprocess
from copy import copy

#import logging
#logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s')


class PGUtils(object):
    def __init__(self, port=5432, pgpath="", host="", user="", password=""):
        self.pgpath = pgpath if pgpath else ""
        self.env = None

        command = []
        if host:
            command.append("--host=%s" % host)
        if user:
            command.append("--username=%s" % user)
        command += ["--port=%d" % int(port)]
        self.cmd_psql = [os.path.join(self.pgpath, 'psql')] + command

        if password:
            self.env = {'PGPASSWORD': password}

    #calls an os command, returns a tuple with (stdout, stderr, unix_process_exit_code)
    @staticmethod
    def os_command(command, environment=None):
        env = os.environ.copy()
        if environment:
            env.update(environment)

        if type(command) is str:
            command = command.split(' ')

        #logging.debug("command: " + " ".join(command))

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, cwd=os.getcwd())
        streamdata = process.communicate()

        return streamdata[0], streamdata[1], process.returncode

    #performs a query using psql, returns query output on success
    def pg_command(self, sql, db_name, tuple_only=True):

        command = copy(self.cmd_psql)
        if tuple_only:
            command.append("-t")
        command += ["--dbname=%s" % db_name, "--command=%s" % str(sql)]

        stdout, stderr, retcode = self.os_command(command, environment=self.env)
        if retcode != 0:
            raise Exception('An error has occurred while executing command [%s] (%d): %s' % (str(sql), retcode, stderr))

        if tuple_only:
            return stdout.strip()
        else:
            return stdout.strip() + "\n"

    #executes an sql file using psql, returns query output on success
    def pg_exec_file(self, sql_file, db_name, tuple_only=True):

        command = copy(self.cmd_psql)
        if tuple_only:
            command.append("-t")
        command += ["--dbname=%s" % db_name, "--file=%s" % str(sql_file)]

        stdout, stderr, retcode = self.os_command(command, environment=self.env)
        if retcode != 0:
            raise Exception('An error has occurred while executing file [%s] (%d): %s' % (str(sql_file), retcode, stderr))

        if tuple_only:
            return stdout.strip()
        else:
            return stdout.strip() + "\n"