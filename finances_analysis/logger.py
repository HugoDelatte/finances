import logging
from colorlog import ColoredFormatter
from pathlib import PurePath
import datetime as dt
from .paths import LOG


def create_logger():
    today = dt.datetime.today()
    logger = logging.getLogger('CryptoTrading')
    logger.setLevel(logging.DEBUG)
    console_log = logging.StreamHandler()
    log_path = PurePath(LOG, f'{today:%Y%m%d_%Hh%Mm%Ss}.log')
    file_log = logging.FileHandler(log_path)
    console_log.setLevel(logging.DEBUG)
    file_log.setLevel(logging.DEBUG)
    console_format = '  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s'
    file_format = '%(asctime)-15s - %(name)-8s - %(levelname)-8s | %(message)s'
    console_log.setFormatter(ColoredFormatter(console_format))
    file_log.setFormatter(logging.Formatter(file_format, '%Y-%m-%d %H:%M:%S'))
    logger.addHandler(console_log)
    logger.addHandler(file_log)
    logger.info(f'Log files are in {log_path}')

