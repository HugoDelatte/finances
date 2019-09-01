import sqlite3
import pandas as pd
from typing import Union
from pathlib import Path

ATTRIBUTES = {'date': 'Date',
              'account': 'Account',
              'entity': 'Entity',
              'type': 'Type',
              'category': 'Category',
              'sub_category': 'Sub Category',
              'detail': 'Detail',
              'method': 'Payment Method',
              'currency': 'Currency',
              'amount': 'Amount'}


def create_db(db_cursor: sqlite3.Cursor):
    """
    Creates the Database structure
    :param db_cursor: database cursor
    """
    db_cursor.execute(
        '''
        CREATE TABLE Method(
            method_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            symbol TEXT NOT NULL UNIQUE
        );

        CREATE TABLE Entity(
            entity_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE Type(
            type_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE Category(
            category_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE Sub_category(
            sub_category_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );
        
        CREATE TABLE Account(
            account_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE Statement (
            transaction_id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            account_id INTEGER NOT NULL,
            detail TEXT NOT NULL,
            entity_id INTEGER,
            amount REAL NOT NULL,
            currency CHAR(3) NOT NULL,
            method_id INTEGER,
            type_id INTEGER,
            category_id INTEGER,
            sub_category_id INTEGER,
            FOREIGN KEY (entity_id) REFERENCES Entity (entity_id),
            FOREIGN KEY (method_id) REFERENCES Method (method_id),
            FOREIGN KEY (type_id) REFERENCES Type (type_id),
            FOREIGN KEY (category_id) REFERENCES Category (category_id),
            FOREIGN KEY (sub_category_id) REFERENCES Sub_Category (sub_category_id),
            FOREIGN KEY (account_id) REFERENCES Account (account_id)
        );
        '''
    )


def get_attr_id(db_cursor: sqlite3.Cursor, attribute: str, value: str, symbol: str = None):
    """
    Retrieve the id of the given the attribute name and its value
    :param db_cursor: database cursor
    :param attribute: the attribute name
    :param value: the attribute value
    :param symbol: the transaction symbol
    :return: id
    """
    if pd.isnull(value):
        return None
    db_cursor.execute('SELECT ' + attribute + '_id '
                                              'FROM ' + attribute.title() + ' '
                                                                            'WHERE name = ?', (value,))
    res = db_cursor.fetchone()
    if res is not None:
        return res[0]
    else:
        if symbol is None:
            db_cursor.execute('INSERT INTO ' + attribute.title() + ' (name) ' +
                              'VALUES (?)', (value,))
            return db_cursor.lastrowid
        else:
            db_cursor.execute('INSERT INTO ' + attribute.title() + ' (name, symbol) ' +
                              'VALUES (?, ?)', (value, symbol))
            return db_cursor.lastrowid


def save_transaction_to_db(db_cursor: sqlite3.Cursor, transaction):
    """
    Save a transaction to the database
    :param db_cursor: database cursor
    :param transaction: transaction
    """
    entity_id = get_attr_id(db_cursor, 'entity', transaction.entity_name)
    method_id = get_attr_id(db_cursor, 'method', transaction.method, transaction.method_symbol)
    type_id = get_attr_id(db_cursor, 'type', transaction.type)
    category_id = get_attr_id(db_cursor, 'category', transaction.category)
    account_id = get_attr_id(db_cursor, 'account', transaction.account)
    sub_category_id = get_attr_id(db_cursor, 'sub_category', transaction.sub_category)
    db_cursor.execute(
        '''
        INSERT INTO Statement
        (date, detail, entity_id, amount, method_id, type_id,
        category_id, sub_category_id, currency, account_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (transaction.date, transaction.entity, entity_id,
         transaction.amount, method_id, type_id, category_id,
         sub_category_id, transaction.currency, account_id)
    )


def get_balance(db_cursor: sqlite3.Cursor):
    """
    Get the actual Balance
    :param db_cursor: database cursor
    :return: balance
    """
    db_cursor.execute('SELECT SUM(amount) FROM Statement')
    return round(db_cursor.fetchone()[0], 2)


def get_db_last_date(db_cursor: sqlite3.Cursor):
    """
    Get the last saved transaction date
    :param db_cursor: database cursor
    :return: last saved transaction date
    """
    db_cursor.execute('SELECT MAX(date) FROM Statement')
    return db_cursor.fetchone()[0]


def load_all_transactions(database: Union[Path, str], account_name: str = None):
    """
    Load all transactions from the databse for a given account name
    :param database: the database name
    :param account_name: the account name
    :return: Dataframe of all the transactions
    """
    if account_name is None:
        account_condition = ''
    else:
        account_condition = f'''WHERE A.name = '{account_name}' '''
    con = sqlite3.connect(database)
    con.execute('pragma foreign_keys=ON')
    db_cursor = con.cursor()
    db_cursor.execute(
        f'''
        SELECT S.date, A.name, E.name, T.name,
               C.name, SC.name, S.detail, M.name, S.currency, S.amount 
              FROM Statement S
              OUTER LEFT JOIN Entity E
                  on E.entity_id = S.entity_id
              OUTER LEFT JOIN Method M
                  on M.method_id = S.method_id
              INNER JOIN Type T
                  on T.type_id = S.type_id
              OUTER LEFT JOIN Category C
                  on C.category_id = S.category_id
              OUTER LEFT JOIN Account A
                  on A.account_id = S.account_id
              OUTER LEFT JOIN Sub_category SC
                  on SC.sub_category_id = S.sub_category_id
              {account_condition}
              ;
        ''')
    res = db_cursor.fetchall()
    con.close()
    df = pd.DataFrame(res, columns=ATTRIBUTES.keys())
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df['amount'] = df['amount'].astype(float)
    return df
