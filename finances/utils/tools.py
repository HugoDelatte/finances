import datetime as dt
from pathlib import Path
from typing import Iterator
from pdfminer.layout import LTTextBoxHorizontal


def extract_characters(box: Iterator[LTTextBoxHorizontal]):
    return [sub_elem for elem in box for sub_elem in elem]


def to_date(date_str, date_format: str = '%d %b %y'):
    return dt.datetime.strptime(date_str, date_format).date()


def to_date_str(date: dt.datetime):
    return date.strftime('%Y-%m-%d')


def statement_file_date(file: Path):
    return dt.datetime.strptime(file.name[11:-4], '%Y-%m').date()


def to_float(string: str):
    return float(string.replace(',', ''))
