#!/usr/bin/env python
import os
import logging
import optparse
import random
import string
from tempfile import NamedTemporaryFile

from pgbackup import PGBackup
from utils import PGServer

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')


def pgmove(source_server, source_db, dest_server, dest_db, drop_source=False, mode="new"):
    source = PGBackup(source_server.port, source_server.bindir, source_server.host,
                      source_server.user, source_server.password)
    destination = PGBackup(dest_server.port, dest_server.bindir, dest_server.host,
                           dest_server.user, dest_server.password)

    #initalize temp file
    f = NamedTemporaryFile(delete=False)
    f.close()

    logging.info("Starting operations on [{server}] server".format(server=source_server.alias))
    source_dbs = source.list_dbs()
    #looking for source db
    if source_db not in source_dbs:
        raise Exception("Database [{db}] not found on [{server}] server. Aborting."
                        .format(db=source_db, server=source_server.alias))
    #checking superuser capabilities
    if not source.is_superuser(source_db):
        logging.warning("User [{user}] is not superuser on [{server}] server, this can cause inconsistencies"
                        .format(user=source_server.user, server=source_server.alias))
    #dump source database
    logging.info("Dumping db [{db}] on [{server}] server...".format(db=source_db, server=source_server.alias))
    source.sql_dump(dbname=source_db, dest=f.name)

    logging.info("Starting operations on [{server}] server".format(server=dest_server.alias))
    destination_dbs = destination.list_dbs()
    temp_dest_db = destination.get_maintenance_db(dest_db)
    #checking superuser capabilities on destination server
    if not destination.is_superuser(temp_dest_db):
        logging.warning("User [{user}] is not superuser on [{server}] server, restore may fail"
                        .format(user=dest_server.user, server=dest_server.alias))
    #abort if mode is new and server exists otherwise create
    if mode == "new":
        if dest_db in destination_dbs:
            raise Exception("Database [{db}] is already present on [{server}] server. Aborting."
                            .format(db=dest_db, server=dest_server.alias))
        else:
            destination.pg_command(temp_dest_db, "CREATE DATABASE {database}".format(database=dest_db))
    #abort if mode is add and server does not exists
    elif mode == "add" and dest_db not in destination_dbs:
        raise Exception("Database [{db}] not found on [{server}] server. Aborting."
                        .format(db=dest_db, server=dest_server.alias))
    #create database if mode is create and server does not exists
    elif mode == "create" and dest_db not in destination_dbs:
        destination.pg_command(temp_dest_db, "CREATE DATABASE {database}".format(database=dest_db))
    #if mode is clean and destination exists create a temporary database to restore the data
    #after restore original db is dropped and temp db renamed
    elif mode == "clean":
        dest_db_orig = None
        if dest_db in destination_dbs:
            dest_db_orig = dest_db
            #create random database
            dest_db = ''.join(random.choice(string.ascii_lowercase) for x in range(8))
            while dest_db in destination_dbs:
                dest_db = ''.join(random.choice(string.ascii_lowercase) for x in range(8))
            destination.pg_command(temp_dest_db, "CREATE DATABASE {database}".format(database=dest_db))

    #restoring on destination database
    logging.info("Restoring db [{db}] on [{server}] server...".format(db=dest_db, server=dest_server.alias))
    restore_errors = False
    logging.debug(destination.pg_file(dbname=dest_db, file=f.name))
    if destination.stderr.strip() > 0:
        restore_errors = True
    logging.info("Restore complete!")

    #if we restored on a temporary db now we can drop the original destination and rename
    if mode == "clean" and dest_db_orig is not None:
        destination.drop_db(dest_db_orig)
        logging.info("Renaming db [{database}] to [{original}]...".format(database=dest_db, original=dest_db_orig))
        destination.pg_command(temp_dest_db, "ALTER DATABASE {database} RENAME TO {original}"
                                             .format(database=dest_db, original=dest_db_orig))

    #dropping source db if requested to do so and there where no errors
    if drop_source:
        if restore_errors:
            logging.info("The database restoration produced error messages. "
                         "Source db [{db}] will NOT be dropped!".format(db=source_db))
        else:
            logging.info("Dropping [{db}] db...".format(db=source_db))
            source.drop_db(source_db)

    #delete tmp file
    logging.info("Deleting temp file...")
    os.unlink(f.name)


def main():
    usage = "usage: %prog [options] source_database destination_database\n" \
            "Moves a database between postgres instances.\n"

    parser = optparse.OptionParser(usage)

    parser.add_option("-d", "--drop-source-db", dest="drop_source", type="choice",
                      choices=["true", "false"],
                      default="false",
                      help="[true|false] (default false) Drop source database after successful migration")
    parser.add_option("-m", "--mode", dest="mode", type="choice",
                      choices=["new", "add", "create", "clean"],
                      default="new",
                      help="[new|add|create|clean] (default new) -- "
                           "[new]: fails if destination db already exists -- "
                           "[add]: adds content to an existing db (fails if db does not exists) -- "
                           "[create]: creates destination db if not exists, adds if exists -- "
                           "[clean]: clean (drops) destination db if exists")

    parser.add_option("-B", "--source-bin-dir", dest="sbindir", type="string",
                      help="Source PostgreSQL executalbes dir (psql, pg_dump, pg_dumpall, ...)")
    parser.add_option("-P", "--source-port", dest="sport", type="int",
                      default="5432",
                      help="Source PostgreSQL server port (default 5432)")
    parser.add_option("-A", "--source-address", dest="shost", type="string",
                      help="Source PostgreSQL server address (hostname)")
    parser.add_option("-U", "--source-user", dest="suser", type="string",
                      help="Source PostgreSQL username")
    parser.add_option("-S", "--source-password", dest="spassword", type="string",
                      help="Source PostgreSQL password")

    parser.add_option("-b", "--destination-bin-dir", dest="dbindir", type="string",
                      help="Destination PostgreSQL executalbes dir (psql, pg_dump, pg_dumpall, ...)")
    parser.add_option("-p", "--destination-port", dest="dport", type="int",
                      default="5432",
                      help="Destination PostgreSQL server port (default 5432)")
    parser.add_option("-a", "--destination-address", dest="dhost", type="string",
                      help="Destination PostgreSQL server address (hostname)")
    parser.add_option("-u", "--destination-user", dest="duser", type="string",
                      help="Destination PostgreSQL username")
    parser.add_option("-s", "--destination-password", dest="dpassword", type="string",
                      help="Destination PostgreSQL password")

    options, args = parser.parse_args()

    if len(args) != 2:
        parser.error('Number of arguments do not match (must be two)')
    source_db = args[0]
    dest_db = args[1]

    if options.drop_source is None or options.drop_source != "true":
        options.drop_source = False
    else:
        options.drop_source = True
    if options.mode is None:
        options.mode = "new"

    if options.sbindir is None:
        options.sbindir = ""
    if options.shost is None:
        options.shost = ""
    if options.suser is None:
        options.suser = ""
    if options.spassword is None:
        options.spassword = ""
    sserver = PGServer(name="Source", port=options.sport, user=options.suser, password=options.spassword,
                       host=options.shost, bindir=options.sbindir)

    if options.dbindir is None:
        options.dbindir = ""
    if options.dhost is None:
        options.dhost = ""
    if options.duser is None:
        options.duser = ""
    if options.dpassword is None:
        options.dpassword = ""
    dserver = PGServer(name="Destination", port=options.dport, user=options.duser, password=options.dpassword,
                       host=options.dhost, bindir=options.dbindir)

    #start backup
    try:
        pgmove(sserver, source_db, dserver, dest_db, options.drop_source, options.mode)
    except Exception, e:
        logging.critical(e)


if __name__ == "__main__":
    main()
