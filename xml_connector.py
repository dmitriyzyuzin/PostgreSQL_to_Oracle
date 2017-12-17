#!/usr/bin/python3

import xml.etree.ElementTree as ET
from xml.dom.minidom import Node, parse

from database_credentials import postgresql_credentials
from postgres import PostgresExport


class ExportXml:

    def __init__(self, dbname):
        self.top = ET.Element('top')
        self.database = ET.SubElement(self.top, 'database')
        self.database.text = str(dbname)

        self.tables = ET.SubElement(self.top, 'tables')

    @staticmethod
    def convert_tuple_to_string_data(tuple):
        string_data = ''
        for item in tuple:
            string_data += str(item) + ','
        return string_data[:-1]

    def fill_in_table_block(self, tablename, columns_descr, rows_data):
        table = ET.SubElement(self.tables, 'table')
        table_name = ET.SubElement(table, 'table_name')
        table_name.text = str(tablename)

        # creating columns block
        columns = ET.SubElement(table, 'columns')
        for item in columns_descr:
            column = ET.SubElement(columns, 'column')
            column_name = ET.SubElement(column, 'column_name')
            column_name.text = str(item[0])

            data_type = ET.SubElement(column, 'data_type')
            data_type.text = str(item[1])
            is_nullable = ET.SubElement(column, 'is_nullable')
            is_nullable.text = str(item[2])

        # backup data from rows
        rows_elem = ET.SubElement(table, 'rows')
        for item in rows_data:
            row_elem = ET.SubElement(rows_elem, 'row')
            row_elem.text = self.convert_tuple_to_string_data(item)


exporter = ExportXml('9sem_bd_lab1')

# get data from postgres begin
postgres = PostgresExport('localhost', postgresql_credentials['username'],
                          postgresql_credentials['password'], '9sem_bd_lab1')
tables_list = postgres.get_tables()
for table in tables_list:
    columns = postgres.get_table_description(table)
    rows_data = postgres.get_table_rows(table)

    exporter.fill_in_table_block(table, columns, rows_data)
# get data from postgres end


# save TODO: make saving pretty xml only with one xml-library
ET.ElementTree(exporter.top).write('postgres.xml', xml_declaration=True, encoding='utf-8', method="xml")

dom = parse('postgres.xml')
test = dom.toprettyxml()

with open('postgres.xml', 'w') as file:
    file.write(test)
