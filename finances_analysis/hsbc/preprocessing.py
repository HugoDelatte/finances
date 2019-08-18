from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams, LTTextBoxHorizontal, LTChar
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfinterp import PDFPageInterpreter
from pathlib import Path
from typing import Iterator, Union
from finances_analysis.utils.tools import to_float, extract_characters, to_date_str, to_date
from finances_analysis.hsbc.vars import COL, CHAR_HEIGHT, CHAR_WIDTH, METHOD


class Char:
    """
    Class representing a character from the HSBC statement
    """

    def __init__(self, lt_char: LTChar):
        self.x0 = round(lt_char.x0, 2)
        self.x1 = round(lt_char.x1, 2)
        self.y0 = round(lt_char.y0, 2)
        self.y1 = round(lt_char.y1, 2)
        self.box = (self.x0, self.y0, self.x1, self.y1)
        self.height = round(lt_char.height, 2)
        self.width = round(lt_char.width, 2)
        self.text = lt_char.get_text()
        self.row = None
        self.col = None
        self.col_name = None
        self.get_col()

    def __str__(self):
        return (f'text: {self.text}'
                f' | box: {self.box}'
                f' | row: {self.row}'
                f' | col: {self.col}')

    def get_col(self):
        if self.x0 < COL['date']:
            self.col = 0
            self.col_name = 'date'
        elif self.x0 < COL['payment_type']:
            self.col = 1
            self.col_name = 'payment_type'
        elif self.x0 < COL['entity']:
            self.col = 2
            self.col_name = 'entity'
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
    """
    Class representing a string from the HSBC statement
    """

    def __init__(self, row: int, col: int, col_name: str):
        self.row = row
        self.col = col
        self.col_name = col_name
        self.text = ''

    def clean(self):
        if self.text != '':
            if self.text[0] == ' ':
                self.text = self.text[1:]

    def __str__(self):
        return (f'text: {self.text}'
                f' | row: {self.row}'
                f' | col: {self.col}'
                f' | col_name: {self.col_name}')


class StatementReader:
    def __init__(self, file: Union[str, Path]):
        self.start_balance = None
        self.transaction_list = []
        self.f = open(file, 'rb')
        resource_manager = PDFResourceManager()
        params = LAParams()
        self.device = PDFPageAggregator(resource_manager, laparams=params)
        self.interpreter = PDFPageInterpreter(resource_manager, self.device)

    def read_statement(self):
        # Process each page contained in the statement.
        page_list = []
        for page in PDFPage.get_pages(self.f):
            str_list = self.read_page(page)

            page_list.append(str_list)
        return page_list

    def read_page(self, page: Iterator[PDFPage]):
        characters = []
        self.interpreter.process_page(page)
        layout = self.device.get_result()
        for box in layout:
            if isinstance(box, LTTextBoxHorizontal):
                characters.extend(extract_characters(box))
        # Create list of characters
        char_list = [Char(char) for char in characters if
                     isinstance(char, LTChar)]
        char_list = sorted(char_list, key=lambda char: char.y0, reverse=True)
        # Attribute a row number to each character
        char_list[0].row = 0
        for i in range(1, len(char_list)):
            if (char_list[i - 1].y0 - char_list[i].y0) > CHAR_HEIGHT / 2:
                char_list[i].row = char_list[i - 1].row + 1
            else:
                char_list[i].row = char_list[i - 1].row
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
                    if (char_list[i].x0 - char_list[i - 1].x1) > CHAR_WIDTH:
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
        str_list = iter(sorted(str_list, key=lambda x: (x.row, x.col)))
        return str_list

    def get_statement_details(self):
        page_list = self.read_statement()
        for str_list in page_list:
            self.get_transaction_details(str_list)

    def get_transaction_details(self, str_list: Iterator[String]):
        while True:
            string = next(str_list, None)
            if string is None:
                break
            # First BALANCE BROUGHT FORWARD
            elif string.text == 'BALANCE BROUGHT FORWARD':
                string = next(str_list)
                if self.start_balance is None:
                    # Some time, there is a '.' in the first line so we pass it
                    if string.text == '.':
                        string = next(str_list)
                    self.start_balance = to_float(string.text)
                string = next(str_list)
                # Last BALANCE BROUGHT FORWARD
                while string.text != 'BALANCE CARRIED FORWARD':
                    current_row = string.row
                    new_transaction = False
                    date = None
                    method_symbol = None
                    entity = None
                    amount = 0
                    while string.row == current_row:
                        if string.text == 'BALANCE CARRIED FORWARD':
                            break
                        if string.col_name == 'date':
                            date = to_date_str(to_date(string.text))
                        elif string.col_name == 'payment_type':
                            method_symbol = string.text
                            new_transaction = True
                        elif string.col_name == 'entity':
                            entity = string.text
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
                            if date is None:
                                prev_transaction = self.transaction_list[-1]
                                date = prev_transaction['date']
                            transaction = dict(date=date,
                                               method=METHOD[method_symbol],
                                               method_symbol=method_symbol,
                                               entity=entity,
                                               amount=amount)
                            self.transaction_list.append(transaction)
                        else:
                            prev_transaction = self.transaction_list[-1]
                            prev_transaction['amount'] = amount
                            prev_transaction['entity'] = ' '.join((prev_transaction['entity'], entity))
                            self.transaction_list[-1] = prev_transaction
                else:
                    break

    def close_statement(self):
        self.f.close()
        self.device.close()
