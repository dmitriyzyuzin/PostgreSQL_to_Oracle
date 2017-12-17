#!/usr/bin/python3

import psycopg2
from database_credentials import postgresql_credentials


class PostgresExport:
    def __init__(self, host, user, password, dbname):
        try:
            conn = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                dbname=dbname
            )

            self.cursor = conn.cursor()
        except Exception:
            print('Error with connection to PostgreSQL')
            exit(-1)

    def export_database_to_xml(self):
        pass

    def get_tables(self):
        sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        self.cursor.execute(sql)

        tables = []
        for item in self.cursor.fetchall():
            tables.append(item[0])
        return tables

    def get_table_description(self, tablename):
        sql = "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = %s"
        self.cursor.execute(sql, (tablename,))
        columns = self.cursor.fetchall()
        if len(columns) > 0:
            return columns
        else:
            return None

    def get_table_rows(self, tablename):
        sql = "SELECT * FROM " + str(tablename)
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()

        if len(rows) > 0:
            return rows
        else:
            return None





