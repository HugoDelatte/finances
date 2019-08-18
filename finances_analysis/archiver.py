import sqlite3
import logging
from pathlib import Path, PurePath
from pandas.tseries.offsets import Day
from finances_analysis.utils.database import create_db, last_date, balance
from finances_analysis.utils.tools import to_date, statement_file_date
from finances_analysis.processing.statement import Statement

logger = logging.getLogger('finances_analysis.archiver')


def get_statement_file(statements_folder, last_date):
    statement_file_list = []
    for statement_file in Path(statements_folder).iterdir():
        if statement_file.name[:10] == 'statements' and statement_file.suffix == '.pdf':
            if statement_file_date(statement_file) > last_date:
                statement_file_list.append(statement_file)
    statement_file_list = sorted(statement_file_list, key=statement_file_date)
    return statement_file_list


def archive_statements(project_folder, database_name, statements_folder):
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

    last_database_date = (to_date(last_date(last_date), '%Y-%m-%d') - Day(6)).date()
    statement_file_list = get_statement_file(statements_folder, last_database_date)
    prev_end_balance = balance(last_date)
    for statement_file in statement_file_list:
        statement = Statement(statement_file, project_folder, prev_end_balance)
        statement.save_to_database(db_cursor)
    con.commit()
    con.close()




project_folder = ('C:/Users/hugo/OneDrive/Documents/SynologyDrive/Administrative/'
       'Finances/HSBC/Financial Analysis')
database_name = 'finance.db'
statements_folder = project_folder + '/Statments/'

