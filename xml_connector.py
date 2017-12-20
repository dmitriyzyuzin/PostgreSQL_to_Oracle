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
            string_data += str(item) + '--DeLiMeTeR--'
        return string_data[:-13]

    def fill_in_table_block(self, tablename, columns_descr, primary_key, foreign_keys, rows_data):
        table = ET.SubElement(self.tables, 'table')
        table_name = ET.SubElement(table, 'table_name')
        table_name.text = str(tablename)

        # lists for FK
        fk_column_name = []
        fk_foreign_column = []
        fk_foreign_table = []
        if foreign_keys is not None:
            for _tuple in foreign_keys:
                fk_column_name.append(_tuple.column)
                fk_foreign_column.append(_tuple.foreign_column)
                fk_foreign_table.append(_tuple.foreign_table)

        # creating columns block
        columns = ET.SubElement(table, 'columns')
        for item in columns_descr:
            column = ET.SubElement(columns, 'column')
            column_name = str(item[0])
            column_name_elem = ET.SubElement(column, 'column_name')
            column_name_elem.text = str(column_name)

            # PK tag
            pk_elem = ET.SubElement(column, 'primary_key')
            if column_name == primary_key:
                pk_elem.text = 'YES'
            else:
                pk_elem.text = 'NO'

            """
            FK block. Will be
            <foreign_key>NO</foreign_key>
            or
            <foreign_key>
            ____<foreign_column></foreign_column>
            ____<foreign_table></foreign_table>
            </foreign_key>
            """
            fk_elem = ET.SubElement(column, 'foreign_key')
            if column_name in fk_column_name:
                index_in_fk_tables = fk_column_name.index(column_name)
                foreign_column_elem = ET.SubElement(fk_elem, 'foreign_column')
                foreign_column_elem.text = fk_foreign_column[index_in_fk_tables]
                foreign_table_elem = ET.SubElement(fk_elem, 'foreign_table')
                foreign_table_elem.text = fk_foreign_table[index_in_fk_tables]
            else:
                fk_elem.text = 'NO'

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
    columns = postgres.get_columns_description(table)
    primary_key = postgres.get_primary_key(table)
    foreign_keys = postgres.get_foreign_keys(table)
    rows_data = postgres.get_table_rows(table)

    exporter.fill_in_table_block(table, columns, primary_key, foreign_keys, rows_data)
# get data from postgres end


# save TODO: make saving pretty xml only with one xml-library
ET.ElementTree(exporter.top).write('postgres.xml', xml_declaration=True, encoding='utf-8', method="xml")

dom = parse('postgres.xml')
test = dom.toprettyxml()

with open('postgres.xml', 'w') as file:
    file.write(test)
