from argparse import *
from os.path import isfile, isdir

import textwrap
import logging
from typing import Optional

import orjson
from database import models, database
from server import httpServer

SUBPARSER_NAME = "command"
VERBOSE_NAME = "loglevel"


def load_bd(db_name, db_user, db_pass, db_host, model) -> Optional[database.DB]:
    if model == 'postgresql':
        logging.info("Using PostgreSQL model")
        logging.info("Trying to connect to database '%s:%s'", db_host, db_name)
        model = models.PostgreSQLModel(db_name, db_user, db_pass, db_host)
    else:
        logging.info("Using SQLite model")
        logging.info("Trying to connect to database '%s'", db_name)
        model = models.SQLLiteModel(db_name)

    if not model.connected():
        logging.error("Connection failed with following error")
        logging.error(model.error())
        return None
    else:
        logging.info("Connection established!")

    db = database.DB(model)
    return db


def migrate(db_name, db_user, db_pass, db_host, model, input, skip_db) -> bool:
    db = load_bd(db_name, db_user, db_pass, db_host, model)
    if db is None:
        return False

    if not isdir(input):
        logging.error("Unable to locate directory %s'", input)
        return False

    result_file = input + '/result.json'
    if not isfile(result_file):
        logging.error("Unable to open result file %s'", result_file)
        return False
    else:
        logging.info("File exists!")

    logging.info("Reading file...")
    with open(result_file, "r") as f:
        data = f.read()
        logging.info("Read %iKbs bytes of data from file", len(data) / 1024)
        logging.info("Parsing file...")
        parsed = orjson.loads(data)
        logging.info("Parsed %i root keys", len(parsed))

    if not skip_db:
        db.create_databases()
    else:
        logging.info("Skipping database creation...")

    db.fill_databases(parsed, input)
    return True


def server(db_name, db_user, db_pass, db_host, model, port, hostname, limit_messages) -> bool:
    db = load_bd(db_name, db_user, db_pass, db_host, model)
    if db is None:
        return False

    if limit_messages is not None:
        logging.info('Limit value set to %s', limit_messages)
        db.limit_messages = limit_messages

    logging.info('Caching database messages')
    db.get_messages()
    logging.info('Cache ready!')


    try:
        httpServer.run_server(db, hostname, int(port))
    except Exception as ex:
        logging.error('Server crushed with error: %s', str(ex))
        return False

    return True


def setup_parsers() -> ArgumentParser:
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
    parser.description = textwrap.dedent('''
          Display statistics of your Telegram Data. 
        To display data you need to convert your Telegram's export into internal-utility 
        format. To do so use 'migrate' subcommand. It will read data from export and 
        store it to a database (currently is PostgreSQL or SQLite3 database), To use 
        PostgresSQL you need to manually install it. To install it on linux devices try:
        
        > sudo apt install postgresql
        
        If you`re forgot or don't know your PostgresSQL password try next:
        
        > sudo -u postgres psql
        And type in opened terminal: '\password postgres'
        In this terminal you can also create database: 'create database <database-name>;
        
        SQLite already shipped with Python3.
        
        Use 'server' subcommand to start a local web-server where statistics will be 
        shown.''')

    parser.add_argument('-v', '--verbose', help="Be verbose", action="store_const", dest=VERBOSE_NAME, const=True)

    parser.add_argument('--database', dest='db_name', help='PostgreSQL database name OR SQLite database file name', default='database', )
    parser.add_argument('--user', dest='db_user', help='PostgreSQL user name', default='postgres')
    parser.add_argument('--password', dest='db_pass', help='PostgreSQL user password', default='1234')
    parser.add_argument('--host', dest='db_host', help='PostgreSQL host (usually localhost)', default='localhost')
    parser.add_argument('--postgresql', dest='model', help='Use PostgreSQL model (should be installed PIP package '
                                                            'and PostgreSQL on your computer)',
                         action="store_const",
                         const='postgresql')
    parser.add_argument('--sqlite', dest='model', help='Use SQLite3 model (should be installed PIP package)',
                         action="store_const",
                         const='sqlite', default=True)

    subparsers = parser.add_subparsers(dest=SUBPARSER_NAME)
    subparsers.required = True

    migrate = subparsers.add_parser('migrate',
                                    formatter_class=RawDescriptionHelpFormatter,
                                    help='Migrates Telegram output JSON file to PostgreSQL database')
    migrate.description = textwrap.dedent('''\
             Migrates Telegram output JSON file to a selected database that is 
           required for further work of this''')

    migrate.add_argument(dest='input', help='Path to Telegram\'s output directory where LARGE Json stored')
    migrate.add_argument('--skip-database-creation', dest='skip_db', help='Skips database creation (for ADVANCED users)',
                         action="store_const",
                         const=True)

    server = subparsers.add_parser('server',
                                   formatter_class=RawDescriptionHelpFormatter,
                                   help='Starts simple server to view statistics')
    server.description = textwrap.dedent('''\
          Starts web-server with a selected port and host name. This requires
        converted database to work. Use 'migrate' command to do so.''')

    server.add_argument('-p', '--port', dest='port', help='Port to start a web-server (default: 8000)', default='8000')
    server.add_argument('-n', '--hostname', dest='hostname', help='Host name of a web-server (default: localhost)', default='localhost')
    server.add_argument('--limitmessages', dest='limit_messages', help='Account only part of all messages (from start).'
                                                                       ' Takes all if parameter is not specified',
                        default=None)

    return parser


def main():
    parser = setup_parsers()
    kwargs = vars(parser.parse_args())

    logging.basicConfig(format='%(asctime)-15s | %(funcName)-7s | %(levelname)s:  %(message)s',
                        level=logging.INFO if kwargs.pop(VERBOSE_NAME) else logging.ERROR)

    subroutine_name = kwargs.pop(SUBPARSER_NAME)
    logging.info("Running '%s' subroutine", subroutine_name)

    exit(0 if globals()[subroutine_name](**kwargs) else 1)


if __name__ == '__main__':
    main()
