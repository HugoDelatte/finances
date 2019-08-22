import sqlite3
import logging
import datetime as dt
from finances.utils.logger import create_logger
from pathlib import Path, PurePath
from pandas.tseries.offsets import Day
from finances.utils.database import create_db, get_db_last_date, get_balance
from finances.utils.tools import to_date, statement_file_date
from finances.processing.statement import Statement


def get_statement_file(statements_folder: Path, last_date: dt.date):
    statement_file_list = []
    for statement_file in Path(statements_folder).iterdir():
        if statement_file.name[:10] == 'statements' and statement_file.suffix == '.pdf':
            if statement_file_date(statement_file) > last_date:
                statement_file_list.append(statement_file)
    statement_file_list = sorted(statement_file_list, key=statement_file_date)
    return statement_file_list


def archive_statements(project_folder: str, database_name: str, statements_folder: str):
    create_logger(Path(project_folder))
    logger = logging.getLogger('finances.archiver')
    if not Path(project_folder).exists():
        logger.error(f'folder: {project_folder} not found')
        raise FileNotFoundError
    database = Path(PurePath(project_folder, database_name))
    if Path(database).exists():
        logger.info('Connecting to Database')
        con = sqlite3.connect(database)
        con.execute('pragma foreign_keys=ON')
        db_cursor = con.cursor()
    else:
        logger.info(f'No Database found for path {database}'
                    f'--> Creating New Database')
        con = sqlite3.connect(database)
        con.execute('pragma foreign_keys=ON')
        db_cursor = con.cursor()
        create_db(db_cursor)

    last_database_date = (to_date(get_db_last_date(db_cursor), '%Y-%m-%d') - Day(6)).date()
    statement_file_list = get_statement_file(Path(statements_folder), last_database_date)
    prev_end_balance = get_balance(db_cursor)
    for statement_file in statement_file_list:
        statement = Statement(statement_file, Path(project_folder), prev_end_balance)
        statement.save_to_database(db_cursor)
    con.commit()
    con.close()


dir = ('C:/Users/hugo/OneDrive/Documents/SynologyDrive/Administrative/'
       'Finances/HSBC/Financial Analysis')

archive_statements(dir, 'finance.db', dir + '/Statments/')
project_folder=dir
database_name='finance.db'
statements_folder=dir + '/Statments/'