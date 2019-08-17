# -*- coding: utf-8 -*-

import os
import datetime as dt
import pandas as pd
import pdfminer.pdfparser
import pdfminer.layout
import pdfminer.pdfinterp
import pdfminer.converter
import sqlite3
import sys
from pandas.tseries.offsets import Day
from finances_analysis.utils import database as db

CHAR_HEIGHT = 10
CHAR_WIDTH = 5/8
COL = {
    'date': 100,
    'payment_type': 130,
    'detail': 300,
    'paid_out': 400,
    'paid_in': 500,
    'balance': 600
    }

METHOD = {
    'ATM': 'Cash Machine',
    'BP': 'Bill Payment',
    'CHQ': 'Cheque',
    'CIR': 'Cirrus / Maestro card / Eurocheque',
    'CR':	'Credit',
    'DD':	'Direct Debit',
    'DIV': 'Dividend',
    'DR':	'Debit',
    'MAE': 'Maestro Debit Card',
    'SO':	'Standing Order',
    'TRF': 'Transfer',
    'VIS': 'Visa debit card',
    ')))': 'Contactless debit card',
    'PIM': 'Pay-In Machine'
}

TEXT_ELEMENTS = [
    pdfminer.layout.LTTextBox,
    pdfminer.layout.LTTextBoxHorizontal,
    pdfminer.layout.LTTextLine,
    pdfminer.layout.LTTextLineHorizontal
    ]


MAPPING = pd.read_csv(DIR + '/mapping.csv', sep=',', header=0,
                      usecols=['keyword', 'entity_name', 'type', 'category',
                               'sub_category'])
# sort by keyword lenght
MAPPING['key'] = list(map(len, MAPPING.keyword))
MAPPING.sort_values(by=['key'], ascending=False, inplace=True)

database = DIR + '/finance.db'


class Char:
    def __init__(self, lt_char):
        self.x0 = round(lt_char.x0, 2)
        self.x1 = round(lt_char.x1, 2)
        self.y0 = round(lt_char.y0, 2)
        self.y1 = round(lt_char.y1, 2)
        self.box = (self.x0, self.y0, self.x1, self.y1)
        self.height = round(lt_char.height, 2)
        self.width = round(lt_char.width, 2)
        self.text = lt_char.get_text()
        self.row = None
        self.get_col()

    def __str__(self):
        return (self.text + ': ' + str(self.box) + ' row:' + str(self.row) +
                ' col:' + str(self.col))

    def get_col(self):
        if self.x0 < COL['date']:
            self.col = 0
            self.col_name = 'date'
        elif self.x0 < COL['payment_type']:
            self.col = 1
            self.col_name = 'payment_type'
        elif self.x0 < COL['detail']:
            self.col = 2
            self.col_name = 'detail'
        elif self.x0 < COL['paid_out']:
            self.col = 3
            self.col_name = 'paid_out'
        elif self.x0 < COL['paid_in']:
            self.col = 4
            self.col_name = 'paid_in'
        else:
            self.col = 5
            self.col_name = 'balance'


class String:
    def __init__(self, row, col, col_name):
        self.row = row
        self.col = col
        self.col_name = col_name
        self.text = ''

    def clean(self):
        if self.text != '':
            if self.text[0] == ' ':
                self.text = self.text[1:]

    def __str__(self):
        return (self.text + ': row:' + str(self.row) +
                ' col:' + str(self.col) + ' col_name:' + str(self.col_name))


class Transaction:
    def __init__(self, date, method_symbol, detail, amount):
        self.date = date
        self.date_str = to_date_str(date)
        self.method_symbol = method_symbol
        self.method_name = METHOD[self.method_symbol]
        self.detail = detail
        self.amount = amount

    def update(self, detail, amount):
        self.detail = ' '.join((self.detail, detail))
        self.amount = amount

    def find_mapping_keyword(self):
        result = []
        for row in MAPPING.itertuples():
            if self.detail.lower().find(row.keyword.lower()) > -1:
                result.append(row)
        return result

    def print_occurrence_keyword(self, keyword_result):
        if len(keyword_result) > 1:
            print('---------------------------')
            print(self)
            for i, trans in enumerate(keyword_result):
                print(str(i) + ' ----> ' + trans.keyword)
        elif len(keyword_result) == 0:
            print('---------------------------')
            print(self)

    def map_attr(self, check=False):
        result = self.find_mapping_keyword()
        if len(result) > 0:
            if len(result) > 1:
                self.print_occurrence_keyword(result)
            if self.amount > 0:
                if result[0].type == 'Expense':
                    raise IndexError('type and amount are inconsistent for:' +
                                     str(self))
            else:
                if (result[0].type == 'Income' or
                        result[0].type == 'Expense Reimbursement'):
                    raise IndexError('type and amount are inconsistent for:' +
                                     str(self))
            self.type = result[0].type
            self.entity_name = result[0].entity_name
            self.category = result[0].category
            self.sub_category = result[0].sub_category
        elif len(result) == 0:
            if check:
                print(str(self))
                return(vars(self))
            else:
                raise IndexError('no match found for: ' + str(self))

    def __str__(self):
        return(str(vars(self)))


def find(trans_list, attr, value):
    return [trans for trans in trans_list if
            getattr(trans, attr) == value]


def extract_characters(box):
    return [subelem for elem in box for subelem in elem]


def to_date(date_str, format='%d %b %y'):
    return dt.datetime.strptime(date_str, format).date()


def to_date_str(date):
    return date.strftime('%Y-%m-%d')


def file_date(file_name):
    return dt.datetime.strptime(file_name[11:-4], '%Y-%m').date()


def to_float(string):
    return float(string.replace(',', ''))


def read_doc(file):
    start_balance = None
    trans = []
    f = open(file, 'rb')
    parser = pdfminer.pdfparser.PDFParser(f)
    doc = pdfminer.pdfparser.PDFDocument()
    parser.set_document(doc)
    doc.set_parser(parser)
    doc.initialize('')
    resource = pdfminer.pdfinterp.PDFResourceManager()
    params = pdfminer.layout.LAParams()
    device = pdfminer.converter.PDFPageAggregator(resource, laparams=params)
    interpreter = pdfminer.pdfinterp.PDFPageInterpreter(resource, device)
    # Process each page contained in the document.
    for page in doc.get_pages():
        characters = []
        interpreter.process_page(page)
        layout = device.get_result()
        for box in layout:
            if isinstance(box, pdfminer.layout.LTTextBoxHorizontal):
                characters.extend(extract_characters(box))
        # Create list of characters
        char_list = [Char(char) for char in characters if
                     isinstance(char, pdfminer.layout.LTChar)]
        char_list = sorted(char_list, key=lambda char: char.y0, reverse=True)
        # Attribute a row number to each character
        char_list[0].row = 0
        for i in range(1, len(char_list)):
            if (char_list[i-1].y0 - char_list[i].y0) > CHAR_HEIGHT/2:
                char_list[i].row = char_list[i-1].row + 1
            else:
                char_list[i].row = char_list[i-1].row
        char_list = sorted(char_list, key=lambda char: (char.row, char.x0))
        # Create list of strings
        str_list = []
        previous_row = char_list[0].row
        previous_col = char_list[0].col
        i = 1
        while i < len(char_list):
            current_row = char_list[i].row
            current_col = char_list[i].col
            current_col_name = char_list[i].col_name
            string = String(current_row, current_col, current_col_name)
            while True and i < len(char_list):
                if (char_list[i].row == previous_row and
                        char_list[i].col == previous_col):
                    if (char_list[i].x0 - char_list[i-1].x1) > CHAR_WIDTH:
                        string.text = ' '.join((string.text,
                                                char_list[i].text))
                    else:
                        string.text = ''.join((string.text, char_list[i].text))
                else:
                    previous_row = char_list[i].row
                    previous_col = char_list[i].col
                    string.clean()
                    str_list.append(string)
                    break
                i = i + 1
        str_list = iter(sorted(str_list,
                               key=lambda string: (string.row, string.col)))
        # Create list of transactions
        while True:
            string = next(str_list, None)
            if string is None:
                break
            # First BALANCE BROUGHT FORWARD
            elif string.text == 'BALANCE BROUGHT FORWARD':
                string = next(str_list)
                if start_balance is None:
                    # Some time, there is a '.' in the firt line so we pass it
                    if string.text == '.':
                        string = next(str_list)
                    start_balance = to_float(string.text)
                string = next(str_list)
                # Last BALANCE BROUGHT FORWARD
                while string.text != 'BALANCE CARRIED FORWARD':
                    current_row = string.row
                    new_transaction = False
                    method_symbol = None
                    detail = None
                    amount = 0
                    while string.row == current_row:
                        if string.text == 'BALANCE CARRIED FORWARD':
                            break
                        if string.col_name == 'date':
                            date = to_date(string.text)
                        elif string.col_name == 'payment_type':
                            method_symbol = string.text
                            new_transaction = True
                        elif string.col_name == 'detail':
                            detail = string.text
                        elif string.col_name == 'paid_out':
                            amount = amount - to_float(string.text)
                        elif string.col_name == 'paid_in':
                            amount = amount + to_float(string.text)
                        elif string.col_name == 'balance':
                            pass
                        else:
                            raise ValueError('col name not found')
                        string = next(str_list)
                    else:
                        if new_transaction:
                            trans.append(Transaction(date, method_symbol,
                                                     detail, amount))
                        else:
                            trans[-1].update(detail, amount)
                else:
                    break
    f.close()
    return (trans, start_balance)


con = sqlite3.connect(database)
con.execute('pragma foreign_keys=ON')
c = con.cursor()

last_date = (to_date(db.last_date(c), '%Y-%m-%d') - Day(6)).date()
statments_path = DIR + '/Statments/'
file_list = os.listdir(statments_path)
file_list = [f for f in file_list if f.startswith('statements') and
             f.endswith('.pdf') and file_date(f) > last_date]
file_list = sorted(file_list, key=file_date)
end_balance = db.balance(c)
transaction = []
for file in file_list:
    print('------------------------' + file + '------------------------')
    trans, start_balance = read_doc(statments_path + file)
    if start_balance != end_balance:
        raise ValueError('Start balance and transactions '
                         'amounts are differents')
    transaction.extend(trans)
    end_balance = round(start_balance + sum(t.amount for t in trans), 2)

missing_trans = []
for trans in transaction:
    missing = trans.map_attr(check=True)
    if missing:
        missing_trans.append(missing)
missing_trans = pd.DataFrame(missing_trans)

if missing_trans.empty:
    for trans in transaction:
        print(trans.date_str)
        trans.map_attr()
        db.add_transaction(c, trans)

    con.commit()
    con.close()
else:
    missing_trans.to_csv(DIR + '/missing.csv')
    raise IndexError('Transaction mapping are missing')
