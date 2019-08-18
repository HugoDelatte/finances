import logging
import pandas as pd
from typing import Dict
import sqlite3
from finances_analysis.utils.database import save_transaction_to_db

logger = logging.getLogger('finances_analysis.transaction')


class Transaction:
    def __init__(self, date: str, method: str, method_symbol: str, entity: str, amount: float,
                 entity_mapping: pd.DataFrame):
        self.date = date
        self.method = method
        self.method_symbol = method_symbol
        self.entity = entity
        self.amount = amount
        self.entity_mapping = entity_mapping
        self.type = None
        self.entity_name = None
        self.category = None
        self.sub_category = None
        self.mapping_error = None
        self.error = False

    def get_entity_detail(self):
        entity_detail_list = []
        for row in self.entity_mapping.itertuples():
            if self.entity.lower().find(row.keyword.lower()) > -1:
                entity_detail_list.append(row)

        if len(entity_detail_list) == 0:
            logger.error(f'Entity mapping is missing for {self}')
            self.mapping_error = dict(transaction=self,
                                      error='Entity mapping is missing')
            return

        if len(entity_detail_list) > 1:
            logger.warning(f'More than one entity mapping have been found for {self}.'
                           f'The mapping with the most keyword characters has been chosen')
            for i, entity_detail in enumerate(entity_detail_list):
                logger.warning(f'      {i} ----> {entity_detail.keyword}')
        return entity_detail_list[0]

    def is_mapping_error(self, entity_detail: Dict):
        if entity_detail is None:
            self.error = True
            return self.error
        if self.amount > 0:
            if entity_detail['type'] == 'Expense':
                logger.error(f'type and amount are inconsistent for: {self}')
                self.mapping_error = dict(transaction=self,
                                          error='type and amount are inconsistent')
                self.error = True
                return self.error
        else:
            if entity_detail['type'] == 'Income' or entity_detail['type'] == 'Expense Reimbursement':
                logger.error(f'type and amount are inconsistent for: {self}')
                self.mapping_error = dict(transaction=self,
                                          error='type and amount are inconsistent')
                self.error = True
                return self.error
        self.error = False
        return self.error

    def map_entity_detail(self):
        entity_detail = self.get_entity_detail()
        if not self.is_mapping_error(entity_detail):
            self.type = entity_detail.type
            self.entity_name = entity_detail.entity_name
            self.category = entity_detail.category
            self.sub_category = entity_detail.sub_category

    def save_to_database(self, db_cursor: sqlite3.Cursor):
        save_transaction_to_db(db_cursor, self)

    def __str__(self):
        return (f'date: {self.date}'
                f' | method: {self.method}'
                f' | entity: {self.entity}'
                f' | amount: {self.amount}')
