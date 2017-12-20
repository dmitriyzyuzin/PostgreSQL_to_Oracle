#!/usr/bin/python3

from collections import OrderedDict, namedtuple

import psycopg2
# TODO: remove after all tests
from database_credentials import postgresql_credentials

CONSTRAINT_SCHEMA = 'public'


class PostgresExport:
    def __init__(self, host, user, password, dbname):
        self.dbname = dbname

        try:
            self.conn = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                dbname=dbname
            )

            self.cursor = self.conn.cursor()
        except Exception:
            print('Error with connection to PostgreSQL')
            exit(-1)

    def get_columns_description(self, tablename):
        sql = "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = %s"
        self.cursor.execute(sql, (tablename,))
        columns = self.cursor.fetchall()
        if len(columns) > 0:
            return columns
        else:
            return None

    """
    
    Method return None (if no foreign keys in table)
    or
    list of namedtuples
    
    You can retrieve data this way:
    elem.column, elem.foreign_column, elem.foreign_table
    
    """
    def get_foreign_keys(self, tablename):
        sql = """SELECT
            tc.constraint_name, tc.table_name, kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
            FROM
            information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
            WHERE constraint_type = 'FOREIGN KEY' AND tc.table_name=%s"""

        self.cursor.execute(sql, (tablename,))
        foreign_keys = self.cursor.fetchall()
        if not foreign_keys:
            return None

        FK = namedtuple('FK', 'column foreign_column foreign_table')
        result = []

        for foreign_key in foreign_keys:
            _tuple = FK(foreign_key[2], foreign_key[4], foreign_key[3])
            result.append(_tuple)

        return result

    """
    Function returns None or pk for a given table
    """
    def get_primary_key(self, tablename):
        sql = """SELECT a.attname
            FROM   pg_index i
            JOIN   pg_attribute a ON a.attrelid = i.indrelid
                                 AND a.attnum = ANY(i.indkey)
            WHERE  i.indrelid = %s::regclass
            AND    i.indisprimary"""
        self.cursor.execute(sql, (tablename,))
        primary_key = self.cursor.fetchone()
        if not primary_key:
            return None

        return primary_key[0]

    def get_table_rows(self, tablename):
        sql = "SELECT * FROM " + str(tablename)
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()

        if len(rows) > 0:
            return rows
        else:
            return None

    def get_tables(self):
        sql = "SELECT table_name FROM information_schema.table_constraints" \
              " WHERE constraint_schema = %s AND constraint_catalog = %s"
        self.cursor.execute(sql, (CONSTRAINT_SCHEMA, self.dbname))
        result = self.cursor.fetchall()

        if len(result) < 0:
            return None

        tables_with_duplicates = []
        for item in result:
            tables_with_duplicates.append(item[0])

        return list(OrderedDict((x, True) for x in tables_with_duplicates).keys())


# postgres = PostgresExport('localhost', postgresql_credentials['username'],
#                           postgresql_credentials['password'], '9sem_bd_lab1')








