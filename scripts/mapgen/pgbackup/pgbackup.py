#!/usr/bin/env python
import os
import logging
import optparse
import re
from datetime import datetime
from copy import copy

from utils import call_command, cpu_count

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


class PGBackup(object):
    def __init__(self, port=5432, pgpath="", host="", user="", password=""):
        self.pgpath = pgpath if pgpath else ""
        self.details_file = ""
        self.force_safe_backup = False
        self.pg_dump_version = ""
        self.env = None
        self.__is_superuser = None
        self.dbs = []
        self.stdout = ""
        self.stderr = ""
        self.retcode = 0

        command = []
        if host:
            command.append("--host=%s" % host)
        if user:
            command.append("--username=%s" % user)
        command += ["--port=%d" % int(port)]
        self.cmd_psql = [os.path.join(self.pgpath, 'psql')] + command
        self.cmd_pg_dump = [os.path.join(self.pgpath, 'pg_dump')] + command
        self.cmd_pg_dumpall = [os.path.join(self.pgpath, 'pg_dumpall')] + command

        if password:
            self.env = {'PGPASSWORD': password}

        #check pg_dump version
        try:
            self.stdout, self.stderr, self.retcode = call_command(os.path.join(pgpath, 'pg_dump') + " --version")
            self.pg_dump_version = self.__parse_version__(self.stdout)
            if self.pg_dump_version < 9.3:
                self.force_safe_backup = True
                logging.warn("pg_dump version found < 9.3. Fast backup not available.")
            self.details_file += "pg_dump version used: %s\n" % (str(self.pg_dump_version))
        except:
            raise Exception('pg_dump executable not found!')

    #parses a postgres version string to float value
    @staticmethod
    def __parse_version__(version_string):
        version_string = version_string.split(" ")[-1]
        trim = re.search("^[\d]+.[\d]+", version_string).end()
        version_string = version_string[0:trim]
        return float(version_string)

    #check if folder is writable
    @staticmethod
    def __preparepath__(path):
        logging.info("checking if destination is writable...")
        dirname = os.path.dirname(os.path.abspath(path))
        if not os.access(dirname, os.W_OK):
            raise Exception("Destination folder %s is not writable, backup aborted" % dirname)

    #check db server version, superuser capabilities, active roles and extensions
    def __preparedb__(self, dbname):
        #check server version
        logging.info("Starting pre-backup checks on database %s" % dbname)
        logging.info("checking server version...")
        stdout = self.pg_command(dbname, "show server_version")
        server_version = self.__parse_version__(stdout)
        logging.info("Version found: %s" % (str(server_version)))
        if server_version < 9.2:
            self.force_safe_backup = True
            logging.warn("PostgreSQL version found < 9.2. Fast backup not available")
        self.details_file += "server version: %s\n" % (str(server_version))

        #check for superuser capabilities
        self.is_superuser(dbname, True)

        #list db users and roles
        logging.info("listing DB users and roles...")
        self.details_file += "\n--++" + self.pg_command(dbname, "\du", False) + "--..\n"

        #list installed db extensions
        logging.info("listing installed extensions...")
        self.details_file += "\n--++" + self.pg_command(dbname, "\dx", False) + "--..\n"

    #check and setup db and path permissions, backup details
    def __prepare__(self, dbname, dest):
        self.details_file = "-- PostgreSQL database dump info --\n" + \
                            "Time: %s\n" % (datetime.now()) + \
                            "DbName: %s\n" % dbname
        self.__preparedb__(dbname)
        self.__preparepath__(dest)

    def list_dbs(self):
        if len(self.dbs):
            return copy(self.dbs)

        psql = " ".join(self.cmd_psql)
        cmd = ["-c", "{psql} -lqt | cut -d \| -f 1".format(psql=psql)]

        logging.info("fetching database list from server...")
        self.stdout, self.stderr, self.retcode = call_command(cmd, environment=self.env, shell=True)
        if self.retcode != 0:
            raise Exception('An error has occurred while executing command [%s] (%d): %s'
                            % (str(cmd), self.retcode, self.stderr))
        dbs = self.stdout.splitlines()
        self.dbs = filter(None, [x.strip() for x in dbs])

        return copy(self.dbs)

    #finding a db on destination server different from the one provided
    def get_maintenance_db(self, dbname):
        logging.info("Finding a maintenance db...")
        db_list = self.list_dbs()
        if dbname in db_list:
            db_list.remove(dbname)
        maintenance_db = None
        for db in db_list:
            try:
                self.is_superuser(db)
                maintenance_db = db
                break
            except Exception:
                continue
        if maintenance_db is None:
            raise Exception("Unable to find a maintenance db on server")
        return maintenance_db

    def drop_db(self, dbname):
        logging.info("Dropping db {database}...".format(database=dbname))
        maintenance_db = self.get_maintenance_db(dbname)
        logging.debug("Terminating all connections on db {database}".format(database=dbname))
        self.pg_command(maintenance_db, "SELECT pg_terminate_backend(pg_stat_activity.pid) "
                                        "FROM pg_stat_activity "
                                        "WHERE pg_stat_activity.datname = '{database}' "
                                        .format(database=dbname))
        self.pg_command(maintenance_db, "DROP DATABASE {database}".format(database=dbname))

    #performs a query using psql, returns query output on success
    def pg_command(self, dbname, cmd, tuple_only=True, output={"format": "std"}):
        if ("format" in output) and (output["format"] != "std"):
            if "delimiter" in output:
                separator = output["delimiter"]
            else:
                separator = ","

            if output["format"] == "csv":
                cmd = "COPY ({cmd}) TO STDOUT with CSV DELIMITER '{sep}'".format(cmd=cmd, sep=separator)
            elif output["format"] == "csvh":
                cmd = "COPY ({cmd}) TO STDOUT with CSV DELIMITER '{sep}' HEADER".format(cmd=cmd, sep=separator)

        command = copy(self.cmd_psql)
        if tuple_only:
            command.append("-t")
        command += ["--dbname={db}".format(db=dbname), '--command={cmd}'.format(cmd=cmd)]

        self.stdout, self.stderr, self.retcode = call_command(command, environment=self.env)
        #if len(self.stderr.strip()) > 0:
        #    logging.warning(self.stderr)
        if self.retcode != 0:
            raise Exception('An error has occurred while executing command [%s] (%d): %s'
                            % (str(cmd), self.retcode, self.stderr))

        if tuple_only:
            return self.stdout.strip()
        else:
            return self.stdout.strip() + "\n"

    #check for superuser capabilities (checks only first time and then saves in variable)
    def is_superuser(self, dbname, raise_if_not=False):
        if self.__is_superuser is not None:
            if raise_if_not and self.__is_superuser is not True:
                raise Exception('User is not superuser, action aborted')
            else:
                return self.__is_superuser

        logging.info("Checking for superuser capabilities...")
        superuser = self.pg_command(dbname, "show is_superuser")
        if superuser != 'on':
            self.__is_superuser = False
        else:
            self.__is_superuser = True

        return self.is_superuser(dbname, raise_if_not)

    #run an sql file on db
    def pg_file(self, dbname, file, tuple_only=True):
        #check if file is readable
        logging.info("Checking if file is readable...")
        if not os.access(file, os.R_OK):
            raise Exception("File %s is not readable, command aborted" % file)

        command = copy(self.cmd_psql)
        if tuple_only:
            command.append("-t")
        command += ["--dbname=%s" % dbname, "--file=%s" % str(file)]

        self.stdout, self.stderr, self.retcode = call_command(command, environment=self.env)
        #if len(self.stderr.strip()) > 0:
        #    logging.warning(self.stderr)
        if self.retcode != 0:
            raise Exception('An error has occurred while executing command [%s] (%d): %s'
                            % (str(command), self.retcode, self.stderr))

        if tuple_only:
            return self.stdout.strip()
        else:
            return self.stdout.strip() + "\n"

    #performs a plain sql dump of the db (only extensions/schema/functions/data, no roles/ownership/privileges)
    def sql_dump(self, dbname, dest):
        #check if destination file is writable
        logging.info("checking if destination file is writable...")
        if not os.access(dest, os.W_OK):
            raise Exception("Destination file %s is not writable, dump aborted" % dest)

        dump_command = copy(self.cmd_pg_dump)
        dump_command += ["--file=%s" % dest, "--no-owner", "--no-tablespaces",
                         "--no-privileges", "--no-unlogged-table-data", dbname]

        #dumping the db
        logging.info("Performing sql dump...")
        self.stdout, self.stderr, self.retcode = call_command(dump_command, environment=self.env)
        if self.retcode != 0:
            raise Exception('Error during dump (%d): %s' % (self.retcode, self.stderr))

    #TODO: not implemented yet!
    def csv_import(self, dbname, table, path, guess_types=True):
        from messytables import CSVTableSet, type_guess, \
            types_processor, headers_guess, headers_processor, \
            offset_processor, any_tableset

        #check if file is readable
        logging.info("checking if file is readable...")
        if not os.access(path, os.R_OK):
            raise Exception("File %s is not readable, import aborted" % path)

        fh = open(path, 'rb')

        # let's take the first table we found in the file (yeah, there could be more than one)
        row_set = CSVTableSet(fh).tables[0]

        # guess header names and the offset of the header:
        offset, headers = headers_guess(row_set.sample)
        row_set.register_processor(headers_processor(headers))

        # add one to begin with content, not the header:
        row_set.register_processor(offset_processor(offset + 1))

        # guess column types:
        types = type_guess(row_set.sample, strict=True)

        # and tell the row set to apply these types to
        # each row when traversing the iterator:
        row_set.register_processor(types_processor(types))

        # now run some operation on the data:
        return headers, types, row_set

    #performs a plain csv dump of a table (or sql se)
    def csv_dump(self, dbname, table, dest=""):
        pass

    #performs backup
    def backup(self, dbname, dest, backup_type):
        self.__prepare__(dbname, dest)

        prefix_path = "/".join(dest.split("/")[0:-1])
        filename = dest.split("/")[-1]
        if prefix_path != "":
            prefix_path = "-C " + prefix_path

        dump_command = copy(self.cmd_pg_dump)
        dump_command += [dbname]

        if self.force_safe_backup or backup_type != "fast":
            backup_type = "safe"
            dump_command += ["--file=%s.sql" % dest, "--no-tablespaces", "--no-unlogged-table-data",
                             "--clean", "--create"]
            tar_command = "tar %s -czf %s.tgz %s.sql %s.details %s.roles" % (prefix_path, dest,
                                                                             filename, filename, filename)
            rm_command = "rm -f %s.sql %s.details %s.roles" % (dest, dest, dest)
            details_file = '%s.details' % dest
            roles_file = '%s.roles' % dest
        else:
            nproc = cpu_count(2)
            logging.info("Processors used: " + str(nproc))

            dump_command += ['--file=%s' % dest, '-Fd', '--jobs=%d' % nproc]
            tar_command = "tar %s -cf %s.tar %s" % (prefix_path, dest, filename)
            rm_command = "rm -rf %s" % dest
            details_file = os.path.join(dest, '%s.details' % filename)
            roles_file = os.path.join(dest, '%s.roles' % filename)

        #dumping the db
        logging.info("Performing %s backup" % backup_type.upper())
        self.stdout, self.stderr, self.retcode = call_command(dump_command, environment=self.env)
        if self.retcode != 0:
            raise Exception('Error during backup (%d): %s' % (self.retcode, self.stderr))

        #dumping roles
        logging.info("dumping roles...")
        dumpall_command = copy(self.cmd_pg_dumpall) + ["--clean", "--roles-only", "--file=%s" % roles_file]
        self.stdout, self.stderr, self.retcode = call_command(dumpall_command, environment=self.env)
        if self.retcode != 0:
            raise Exception('Error dumping roles (%d): %s' % (self.retcode, self.stderr))

        #write dump details and roles file.
        logging.info("writing dump details/roles file in %s ..." % details_file)
        with open(details_file, 'w') as f:
            f.write(self.details_file)

        #tar and rm directory
        try:
            logging.info("archiving backup...")
            stdout, stderr, retcode = call_command(tar_command)
            rstdout, rstderr, rretcode = call_command(rm_command)
            if retcode != 0:
                raise Exception('tar error (%d): %s' % (retcode, stderr))
            if rretcode != 0:
                raise Exception('rm error (%d): %s' % (rretcode, rstderr))
        except:
            raise Exception('tar/rm command not found!')


def main():
    usage = "usage: %prog [options] database_name path"
    parser = optparse.OptionParser(usage)
    parser.add_option("-p", "--port", dest="port", type="int",
                      default="5432",
                      help="PostgreSQL server port (default 5432)")
    parser.add_option("-a", "--address", dest="host", type="string",
                      help="PostgreSQL server address (hostname)")
    parser.add_option("-u", "--user", dest="user", type="string",
                      help="PostgreSQL username")
    parser.add_option("-s", "--password", dest="password", type="string",
                      help="PostgreSQL password")
    parser.add_option("-b", "--bin-dir", dest="bindir", type="string",
                      help="PostgreSQL executalbes dir (psql, pg_dump, pg_dumpall, ...)")
    parser.add_option("-t", "--backup-type", dest="bktype", type="string",
                      default="fast",
                      help="Backup type: [fast|safe|sql_only]. (default fast)")
    options, args = parser.parse_args()

    if len(args) != 2:
        parser.error('Number of arguments do not match (must be two)')
    dbname = args[0]
    destination = args[1]

    bindir = ""
    if options.bindir:
        bindir = options.bindir

    host = ""
    if options.host:
        host = options.host

    user = ""
    if options.user:
        user = options.user

    password = ""
    if options.password:
        password = options.password

    bktype = options.bktype
    port = options.port

    b = PGBackup(port, bindir, host, user, password)

    #start backup
    try:
        if bktype == 'sql_only':
            b.sql_dump(dbname, destination)
        else:
            b.backup(dbname, destination, bktype)
    except Exception, e:
        logging.critical(e)


if __name__ == "__main__":
    main()
