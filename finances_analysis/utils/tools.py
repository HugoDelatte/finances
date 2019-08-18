import datetime as dt

def extract_characters(box):
    return [sub_elem for elem in box for sub_elem in elem]


def to_date(date_str, format='%d %b %y'):
    return dt.datetime.strptime(date_str, format).date()


def to_date_str(date):
    return date.strftime('%Y-%m-%d')


def statement_file_date(file):
    return dt.datetime.strptime(file.name[11:-4], '%Y-%m').date()


def to_float(string):
    return float(string.replace(',', ''))