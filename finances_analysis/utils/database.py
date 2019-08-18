# -*- coding: utf-8 -*-

import pandas as pd


def create_db(c):
    c.execute('''CREATE TABLE Method(
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


def get_attr_id(c, attribute, value, symbol=None):
    if pd.isnull(value):
        return None
    c.execute('SELECT ' + attribute + '_id '
              'FROM ' + attribute.title() + ' '
              'WHERE name = ?', (value,))
    res = c.fetchone()
    if res is not None:
        return res[0]
    else:
        if symbol is None:
            c.execute('INSERT INTO ' + attribute.title() + ' (name) ' +
                      'VALUES (?)', (value,))
            return c.lastrowid
        else:
            c.execute('INSERT INTO ' + attribute.title() + ' (name, symbol) ' +
                      'VALUES (?, ?)', (value, symbol))
            return c.lastrowid


def save_transaction_to_db(c, trans):
    entity_id = get_attr_id(c, 'entity', trans.entity_name)
    method_id = get_attr_id(c, 'method', trans.method_name,
                            trans.method_symbol)
    type_id = get_attr_id(c, 'type', trans.type)
    category_id = get_attr_id(c, 'category', trans.category)
    sub_category_id = get_attr_id(c, 'sub_category', trans.sub_category)
    c.execute('''INSERT INTO Statement
              (date, detail, entity_id, amount, method_id, type_id,
              category_id, sub_category_id)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (trans.date, trans.detail,
              entity_id, trans.amount, method_id, type_id, category_id,
              sub_category_id))


def balance(c):
    c.execute('''SELECT SUM(amount)
              FROM Statement''')
    return round(c.fetchone()[0],2)


def last_date(c):
    c.execute('''SELECT MAX(date)
              FROM Statement''')
    return c.fetchone()[0]



