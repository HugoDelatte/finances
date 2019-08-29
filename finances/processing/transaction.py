import logging
import pandas as pd
import sqlite3
from ..utils.database import save_transaction_to_db

logger = logging.getLogger('finances.transaction')


class Transaction:
    def __init__(self, date: str, method: str, method_symbol: str, entity: str, amount: float, ccy: str,
                 account: str):
        self.date = date
        self.method = method
        self.method_symbol = method_symbol
        self.entity = entity
        self.amount = amount
        self.ccy = ccy
        self.account = account
        self.type = None
        self.entity_name = None
        self.category = None
        self.sub_category = None
        self.mapping_error = None
        self.error = False

    def get_entity_detail(self, entity_mapping: pd.DataFrame):
        entity_detail_list = []
        for row in entity_mapping.itertuples():
            if self.entity.lower().find(row.keyword.lower()) > -1:
                entity_detail_list.append(row)

        if len(entity_detail_list) == 0:
            logger.error(f'Entity mapping is missing for {self}')
            self.mapping_error = 'Entity mapping is missing'
            return

        if len(entity_detail_list) > 1:
            logger.warning(f'More than one entity mapping have been found for {self}.'
                           f'The mapping with the most keyword characters has been chosen')
            for i, entity_detail in enumerate(entity_detail_list):
                logger.warning(f'      {i} ----> {entity_detail.keyword}')
        return entity_detail_list[0]

    def is_mapping_error(self, entity_detail):
        if entity_detail is None:
            self.error = True
            return True
        return False

    def map_entity_detail(self, entity_mapping: pd.DataFrame):
        entity_detail = self.get_entity_detail(entity_mapping)
        if not self.is_mapping_error(entity_detail):
            self.entity_name = entity_detail.entity_name
            self.category = entity_detail.category
            self.sub_category = entity_detail.sub_category
            if entity_detail.type == 'Expense' and self.amount > 0:
                self.type = 'Expense Reimbursement'
            elif entity_detail.type == 'Income' and self.amount < 0:
                self.type = 'Income Refund'
            else:
                self.type = entity_detail.type

    def save_to_database(self, db_cursor: sqlite3.Cursor):
        save_transaction_to_db(db_cursor, self)

    def __str__(self):
        return (f'date: {self.date}'
                f' | method: {self.method}'
                f' | entity: {self.entity}'
                f' | amount: {self.amount}')

    def to_dict(self):
        fields = ['date', 'method', 'entity', 'amount', 'mapping_error']
        return {attr: getattr(self, attr) for attr in fields}
