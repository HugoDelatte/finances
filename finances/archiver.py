import sqlite3
import logging
import datetime as dt
from pathlib import Path, PurePath
from pandas.tseries.offsets import Day
from .utils.logger import create_logger
from .database.database import create_db, get_db_last_date, get_balance
from .utils.tools import to_date, statement_file_date
from .processing.statement import Statement


def get_statement_file(statements_folder: Path, last_date: dt.date):
    """
    Find the pdf statements from the statement folder from a given date to the last available date
    :param statements_folder: statement folder
    :param last_date: date of the last statement saved in the database
    :return: the path of the statements files
    """
    statement_file_list = []
    for statement_file in Path(statements_folder).iterdir():
        if statement_file.name[:10] == 'statements' and statement_file.suffix == '.pdf':
            if statement_file_date(statement_file) > last_date:
                statement_file_list.append(statement_file)
    statement_file_list = sorted(statement_file_list, key=statement_file_date)
    return statement_file_list


def archive_statements(project_folder: str, database_name: str, statements_folder: str):
    """
    Archive each given statement in the Database
    :param project_folder: the project folder
    :param database_name: the database name
    :param statements_folder: the statement folder
    """
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

    for statement_file in statement_file_list:
        prev_end_balance = get_balance(db_cursor)
        statement = Statement(statement_file, Path(project_folder), prev_end_balance)
        statement.save_to_database(db_cursor)
        con.commit()
        logger.info(f'{statement_file.name}: SUCCESS')
    con.close()
