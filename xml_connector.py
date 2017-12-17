#!/usr/bin/python3

import xml.etree.ElementTree as ET


class ExportXml:

    def __init__(self, dbname):
        self.top = ET.Element('top')
        self.database = ET.SubElement(self.top, 'database')
        self.database.text = str(dbname)

        self.tables = ET.SubElement(self.top, 'tables')

    def fillInTableBlock(self, tablename):
        table = ET.SubElement(self.tables, 'table')
        table_name = ET.SubElement(table, 'table_name')
        table_name.text = str(tablename)

        columns = ET.SubElement(table, 'columns')
        for i in range(5):
            column = ET.SubElement(columns, 'column')
            column_name = ET.SubElement(column, 'column_name')
            column_name.text = 'column_name{}'.format(str(i))


exporter = ExportXml('test_db')
exporter.fillInTableBlock('table1')
print(ET.tostring(exporter.top))


# ET.ElementTree(top).write('test.xml', xml_declaration=True, encoding='utf-8', method="xml")
