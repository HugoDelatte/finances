import logging
from colorlog import ColoredFormatter
from pathlib import Path, PurePath
import datetime as dt


def create_logger(project_folder: Path = None):
    today = dt.datetime.today()
    logger = logging.getLogger('finances')
    logger.setLevel(logging.INFO)
    # Console logger
    console_log = logging.StreamHandler()
    console_log.setLevel(logging.INFO)
    console_format = '  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s'
    console_log.setFormatter(ColoredFormatter(console_format))
    logger.addHandler(console_log)
    if project_folder is not None:
        # File logger
        log_folder = create_log_folder(project_folder)
        clear_old_logs(log_folder, keep_log_days=5)
        log_path = PurePath(log_folder, f'{today:%Y%m%d_%Hh%Mm%Ss}.log')
        file_log = logging.FileHandler(log_path)
        file_log.setLevel(logging.DEBUG)
        file_format = '%(asctime)-15s - %(name)-8s - %(levelname)-8s | %(message)s'
        file_log.setFormatter(logging.Formatter(file_format, '%Y-%m-%d %H:%M:%S'))
        logger.addHandler(file_log)
        logger.info(f'Log files are in {log_path}')


def create_log_folder(project_folder: Path):
    # error folder
    log_folder = Path(PurePath(Path(project_folder), 'log'))
    if not log_folder.exists():
        log_folder.mkdir()
    return log_folder


def clear_old_logs(log_folder: Path, keep_log_days: int):
    today = dt.datetime.today().date()
    for log_file in log_folder.iterdir():
        if log_file.suffix == '.log':
            if log_file_date(log_file) < today - dt.timedelta(days=keep_log_days):
                log_file.unlink()


def log_file_date(log_file: Path):
    return dt.datetime.strptime(log_file.name[:10], '%Y%m%d').date()
