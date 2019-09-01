import pandas as pd
from pathlib import Path, PurePath
import sqlite3
import logging
from ..hsbc.preprocessing import StatementReader
from ..processing.transaction import Transaction

logger = logging.getLogger('finances.statement')


class Statement:
    """
    Statement class which is a collection of Transactions
    """

    def __init__(self, statement_file: Path, project_folder: Path, prev_end_balance: float):
        self.statement_file = statement_file
        self.reader = StatementReader(statement_file)
        self.project_folder = project_folder
        self.prev_end_balance = prev_end_balance
        self.entity_mapping = self._get_entity_mapping_file()
        self.error_folder = Path(PurePath(Path(self.project_folder), 'error'))
        self.transaction_collection = None
        self._create_error_folder()
        self._delete_error_file()

    @property
    def mapping_error_df(self):
        """
        Mapping errors
        :return: DataFrame of the mapping errors
        """
        return pd.DataFrame([t.to_dict() for t in self.transaction_collection if t.error])

    def _get_entity_mapping_file(self):
        """
        Read and format the entity mapping file
        :return: entity mapping DataFrame
        """
        file_name = 'entity_mapping.csv'
        file_path = Path(PurePath(Path(self.project_folder), file_name))
        if not file_path.exists():
            logger.error(f'{file_name} not found'
                         f'Please create the file in {self.project_folder} root')
            raise FileNotFoundError

        entity_mapping = pd.read_csv(file_path, sep=',', header=0, usecols=['keyword', 'entity_name', 'type',
                                                                            'category', 'sub_category'])
        entity_mapping['key'] = list(map(len, entity_mapping.keyword))
        entity_mapping.sort_values(by=['key'], ascending=False, inplace=True)
        return entity_mapping

    def _create_error_folder(self):
        """
        Create the error folder containing rhe error file in the project folder
        """
        # error folder
        self.error_folder = Path(PurePath(Path(self.project_folder), 'error'))
        if not self.error_folder.exists():
            self.error_folder.mkdir()
        self.error_file = Path(PurePath(self.error_folder, f'mapping_error_{self.statement_file.name[:-4]}.csv'))

    def _delete_error_file(self):
        """
        Delete the previous error file
        """
        if self.error_file.exists():
            self.error_file.unlink()

    def _check_mapping_error(self):
        """
        Check for mapping errors and save them in the file if any
        """
        if not self.mapping_error_df.empty:
            logger.error(f'{len(self.mapping_error_df)} Entity mapping errors have been found')
            self.save_error_file()
            raise AttributeError('Entity mapping errors')

    def _check_balance_error(self):
        """
        Check if the previous ending balance is equal to the strating balance from the pdf statement
        """
        if self.prev_end_balance != self.start_balance:
            logger.error(f'Start balance and transactions amounts are different:'
                         f'Database Ending Balance: {self.prev_end_balance}'
                         f'/ Statement Starting Balance: {self.start_balance}')
            raise ValueError('Start balance and transactions amounts are different')

    def _get_end_balance(self):
        """
        Compute the ending balance of the statement
        """
        self.end_balance = round(self.start_balance + sum(t.amount for t in self.transaction_collection), 2)

    def _process(self):
        """
        Read and map each transaction from the statement
        """
        self.transaction_collection = []
        self.reader.get_statement_details()
        self.start_balance = self.reader.start_balance
        for transaction in self.reader.transaction_list:
            new_transaction = Transaction(date=transaction['date'],
                                          method=transaction['method'],
                                          method_symbol=transaction['method_symbol'],
                                          entity=transaction['entity'],
                                          amount=transaction['amount'],
                                          ccy=transaction['ccy'],
                                          account=transaction['account'])
            new_transaction.map_entity_detail(entity_mapping=self.entity_mapping)
            self.transaction_collection.append(new_transaction)
        self._check_mapping_error()
        self._check_balance_error()
        self._get_end_balance()

    def save_error_file(self):
        """
        Save the error file in the error folder
        """
        logger.error(f'Missing Mappings to complete are in {self.error_file}')
        self.mapping_error_df.to_csv(self.error_file, index=False)

    def save_to_database(self, db_cursor: sqlite3.Cursor):
        """
        Save each transaction of the statement in the database
        :param db_cursor: database cursor
        """
        self._process()
        for transaction in self.transaction_collection:
            transaction.save_to_database(db_cursor)
