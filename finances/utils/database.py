import sqlite3
import pandas as pd
from finances.processing.transaction import Transaction


def create_db(db_cursor: sqlite3.Cursor):
    db_cursor.execute('''CREATE TABLE Method(
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

             CREATE TABLE Statement (
              transaction_id INTEGER PRIMARY KEY,
              date TEXT NOT NULL,
              detail TEXT NOT NULL,
              entity_id INTEGER,
              amount REAL NOT NULL,
              method_id INTEGER,
              type_id INTEGER,
              category_id INTEGER,
              sub_category_id INTEGER,
              FOREIGN KEY (entity_id)
                  REFERENCES Entity (entity_id),
              FOREIGN KEY (method_id)
                  REFERENCES Method (method_id),
              FOREIGN KEY (type_id)
                  REFERENCES Type (type_id),
              FOREIGN KEY (category_id)
                  REFERENCES Category (category_id),
              FOREIGN KEY (sub_category_id)
                  REFERENCES Sub_Category (sub_category_id)
              );''')


def get_attr_id(db_cursor: sqlite3.Cursor, attribute: str, value: str, symbol: str = None):
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


def save_transaction_to_db(db_cursor: sqlite3.Cursor, trans: Transaction):
    entity_id = get_attr_id(db_cursor, 'entity', trans.entity_name)
    method_id = get_attr_id(db_cursor, 'method', trans.method, trans.method_symbol)
    type_id = get_attr_id(db_cursor, 'type', trans.type)
    category_id = get_attr_id(db_cursor, 'category', trans.category)
    sub_category_id = get_attr_id(db_cursor, 'sub_category', trans.sub_category)
    db_cursor.execute('''INSERT INTO Statement
              (date, detail, entity_id, amount, method_id, type_id,
              category_id, sub_category_id)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (trans.date, trans.entity,
                                                   entity_id, trans.amount, method_id, type_id, category_id,
                                                   sub_category_id))


def balance(db_cursor: sqlite3.Cursor):
    db_cursor.execute('''SELECT SUM(amount)
              FROM Statement''')
    return round(db_cursor.fetchone()[0], 2)


def get_db_last_date(db_cursor: sqlite3.Cursor):
    db_cursor.execute('''SELECT MAX(date)
              FROM Statement''')
    return db_cursor.fetchone()[0]
