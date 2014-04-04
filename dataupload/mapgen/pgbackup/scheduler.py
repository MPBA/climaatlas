#!/usr/bin/env python
from ConfigParser import SafeConfigParser
import os
import logging
import optparse
import datetime
import calendar
import re

from pgbackup import PGBackup
from utils import PGServer

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


class Backup(object):
    _frequencies = (None, "hour", "day", "week", "month", "year")
    _types = ("fast", "safe")

    def __init__(self, name, server, databases=None, directory=".", file_prefix="",
                 frequency=None, rotation=None, bktype="fast"):
        self.name = name
        self.server = server
        self.databases = databases if databases is not None and len(databases) > 0 else None
        self.dir = directory
        self.file_prefix = file_prefix if file_prefix else name.replace(" ", "_")
        self.frequency = frequency
        self.rotation = rotation
        self.type = bktype

        if self.frequency not in self._frequencies:
            logging.warning("Wrong frequency value [%s]. Defaulting to None" % self.frequency)
            self.frequency = None

        if self.rotation not in self._frequencies:
            logging.warning("Wrong rotation value [%s]. Defaulting to None" % self.rotation)
            self.rotation = None
        if self.rotation is not None and \
                self._frequencies.index(self.rotation) < self._frequencies.index(self.frequency):
            logging.warning("Rotation value [%s] is less than frequency [%s]. Defaulting both to None"
                            % (self.rotation, self.frequency))
            self.frequency = None
            self.rotation = None

        if self.type not in self._types:
            logging.warning("Wrong type value [%s]. Defaulting to 'fast'" % self.type)
            self.type = "fast"

    def __str__(self):
        return self.name


class Scheduler(object):
    def __init__(self, config_path):
        #try to read config files
        servers_conf = SafeConfigParser()
        backups_conf = SafeConfigParser()
        try:
            servers_conf.readfp(open(os.path.join(config_path, 'servers.conf')))
            backups_conf.readfp(open(os.path.join(config_path, 'backups.conf')))
        except IOError:
            raise Exception("Unable to read config files (servers.conf, backups.conf) in: %s" % config_path)

        server_list = servers_conf.sections()
        backups_list = backups_conf.sections()

        if len(backups_list) < 1 or len(server_list) < 1:
            raise Exception("No sections found in config files")

        #parsing server list
        servers = {}
        for s in server_list:
            server = PGServer(s)
            server.port = (servers_conf.getint(s, "port") if servers_conf.has_option(s, "port") else 5432)
            server.alias = (servers_conf.get(s, "alias") if servers_conf.has_option(s, "alias") else s)
            server.user = (servers_conf.get(s, "user") if servers_conf.has_option(s, "user") else None)
            server.password = (servers_conf.get(s, "password") if servers_conf.has_option(s, "password") else None)
            server.host = (servers_conf.get(s, "host") if servers_conf.has_option(s, "host") else None)
            server.bindir = (servers_conf.get(s, "bindir") if servers_conf.has_option(s, "bindir") else None)
            servers[s] = server
        if len(servers) > 0:
            logging.info('Found %d valid server(s) in servers.conf' % len(servers))
        else:
            raise Exception('No valid server found in servers.conf')

        #parsing backup list
        self.backups = {}
        for b in backups_list:
            if not backups_conf.has_option(b, "server") or backups_conf.get(b, "server") not in servers:
                logging.warning("Server config not found for backup [%s], skipping section" % b)
                continue
            server = servers[backups_conf.get(b, "server")]
            databases = (backups_conf.get(b, "databases").split(",") if backups_conf.has_option(b, "databases") else [])
            databases = [x.strip() for x in databases]
            directory = (backups_conf.get(b, "dir") if backups_conf.has_option(b, "dir") else ".")
            file_prefix = (backups_conf.get(b, "file_prefix").replace(" ", "_")
                           if backups_conf.has_option(b, "file_prefix") else b.replace(" ", "_"))
            frequency = (backups_conf.get(b, "frequency") if backups_conf.has_option(b, "frequency") else None)
            rotation = (backups_conf.get(b, "rotation") if backups_conf.has_option(b, "rotation") else None)
            bktype = (backups_conf.get(b, "type") if backups_conf.has_option(b, "type") else "fast")
            backup = Backup(b, server, databases, directory, file_prefix, frequency, rotation, bktype)
            self.backups[b] = backup
        if len(self.backups) > 0:
            logging.info('Found %d valid backup configuration(s) in backups.conf' % len(self.backups))
        else:
            raise Exception('No valid backup configuration found in backups.conf')

    # I am assuming that the first week of a month starts with the first monday of a month...
    # I *think* my logic is OK - if Monday (0) is the start of the week, then
    # any day of the month minus its own day of week (0,1,2...) must be positive
    # if that day is on or after the first monday of the month
    @staticmethod
    def week_of_month(tgtdate):
        days_this_month = calendar.mdays[tgtdate.month]
        for i in range(1, days_this_month):
            d = datetime.date(tgtdate.year, tgtdate.month, i)
            if d.day - d.weekday() > 0:
                startdate = d
                break
            # now we can use the modulo 7 approach
        return (tgtdate - startdate).days // 7 + 1

    def start_current(self):
        now = datetime.datetime.now()
        scheduled = []
        logging.info('-------------------- START SCHEDULER --------------------')

        # looking for scheduled backups to execute
        for b in self.backups.itervalues():

            # is this a scheduled backup?
            if b.frequency is None:
                continue

            # since this script is supposed to run every hour, hourly backup are always executed
            if b.frequency == 'hour':
                scheduled.append(b)
            elif now.hour == 1:  # looking for 1AM for all other backups
                if (b.frequency == 'day'
                    or (b.frequency == 'week' and now.weekday() == 6)  # Sunday for weekly backup
                    or (b.frequency == 'month' and now.day == 1)  # 1st day of the month for monthly backup
                    or (b.frequency == 'year' and now.month == 1 and now.day == 1)  # 1st day of the year
                ):
                    scheduled.append(b)

        if not scheduled:
            logging.info("No backup to execute")
        else:
            logging.info("%d backups to execute..." % len(scheduled))

        for s in scheduled:
            filename = ""

            if s.rotation:
                filename += str(s.frequency) + "-" + str(s.rotation) + "_"
                if s.frequency == 'hour':
                    if s.rotation == 'hour':
                        filename += 'lasthour'
                    elif s.rotation == 'day':
                        filename += str(now.hour)
                    elif s.rotation == 'week':
                        filename += str(now.isoweekday()) + "_" + str(now.hour)
                    elif s.rotation == 'month':
                        filename += str(now.day) + "_" + str(now.hour)
                    elif s.rotation == 'year':
                        filename += str(now.month) + "_" + str(now.day) + "_" + str(now.hour)

                elif s.frequency == 'day':
                    if s.rotation == 'day':
                        filename += 'lastday'
                    elif s.rotation == 'week':
                        filename += str(now.isoweekday())
                    elif s.rotation == 'month':
                        filename += atr(now.day)
                    elif s.rotation == 'year':
                        filename += str(now.month) + "_" + str(now.day)

                elif s.frequency == 'week':
                    if s.rotation == 'week':
                        filename += 'lastweek'
                    elif s.rotation == 'month':
                        filename += str(self.week_of_month(now.date()))
                    elif s.rotation == 'year':
                        filename += str(now.isocalendar()[1])

                elif s.frequency == 'month':
                    if s.rotation == 'month':
                        filename += 'lastmonth'
                    elif s.rotation == 'year':
                        filename += str(now.month)

                elif s.frequency == 'year':
                    filename += 'lastyear'
            else:
                filename += now.strftime("%Y-%m-%d_%H-%M-%S")

            logging.info("------- Start scheduled backup [%s] on server [%s] -------" % (s.name, s.server.alias))
            backup = PGBackup(s.server.port, s.server.bindir, s.server.host, s.server.user, s.server.password)
            if s.databases is None:
                dbs = backup.list_dbs()
                regex = re.compile(r'^postgres$|^template[0-9]*$')
                s.databases = [x for x in dbs if not regex.search(x)]
            for db in s.databases:
                complete_filename = s.file_prefix + s.server.name + "." + db + "_" + filename
                logging.info("Filename: %s" % complete_filename)
                destination = os.path.join(s.dir, complete_filename)
                logging.info("Destination: %s" % destination)
                try: 
                    backup.backup(dbname=db, dest=destination, backup_type=s.type)
                except Exception as e:
                    logging.error("Error backing-up database {db}. Skipping.".format(db=db))
            logging.info("------- End scheduled backup [%s] on server [%s] -------\n" % (s.name, s.server.alias))

        logging.info('-------------------- END SCHEDULER --------------------\n\n')

    def start(self, backup_name):
        if backup_name in self.backups:
            bk = self.backups[backup_name]
            logging.info("------- Start MANUAL backup [%s] on server [%s] -------"
                         % (backup_name, bk.server.alias))
            backup = PGBackup(bk.server.port, bk.server.bindir, bk.server.host, bk.server.user, bk.server.password)
            if bk.databases is None:
                dbs = backup.list_dbs()
                regex = re.compile(r'^postgres$|^template[0-9]*$')
                bk.databases = [x for x in dbs if not regex.search(x)]
            for db in bk.databases:
                filename = bk.file_prefix + bk.server.name + "." + db \
                           + "_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                logging.debug("Filename: %s" % filename)
                destination = os.path.join(bk.dir, filename)
                logging.debug("Destination: %s" % destination)
                try:
                    backup.backup(dbname=db, dest=destination, backup_type=bk.type)
                except Exception as e:
                    logging.error("Error backing-up database {db}. Skipping.".format(db=db))
            logging.info("------- End MANUAL backup [%s] on server [%s] -------\n" % (backup_name, bk.server.alias))
        else:
            raise Exception('Backup [%s] not found', backup_name)


def main():
    #parsing arguments
    usage = "Usage: %prog [-l] [config_path [backup_name]]\n" \
            "If [config_path] is not specified ~/.pgbackup will be used\n" \
            "If [backup_name] is not specified scheduled backups will be executed"

    parser = optparse.OptionParser(usage)

    parser.add_option("-l", "--list", action="store_true", dest="list",
                      help="Lists servers/backups")

    options, args = parser.parse_args()

    if len(args) > 2:
        parser.error('Too many arguments')
    if len(args) > 0:
        config_path = args[0]
    else:
        config_path = "~/.pgbackup"

    try:
        scheduler = Scheduler(config_path)
        if len(args) == 2:
            backup_name = args[1]
            if options.list is True:
                pass #TODO: show backup info
            else:
                scheduler.start(backup_name)
        else:
            if options.list is True:
                pass #TODO: list servers/backups
            else:
                scheduler.start_current()
    except Exception, e:
        logging.fatal(e)


if __name__ == "__main__":
    main()
