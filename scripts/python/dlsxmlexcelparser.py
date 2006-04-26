#!/usr/bin/env python

"""
dlsxmlexcelparser.py
Author: Peter Denison

This script is used by dls-signalparse.py to help
parse signal data from XML spreadsheets.
"""

import sys
from xml.sax import handler
from xml.sax import parse

def ExtendList(list, length, value=''):
    while len(list) < length:
        list.append(value)

class ExcelHandler(handler.ContentHandler):
    def __init__(self):
        self.chars=[]
        self.cells=[]
        self.rows=[]
        self.tables=[]
        self.data=[]
        
    def characters(self, content):
        self.chars.append(content)

    def startElement(self, name, atts):
        if name=="Cell":
            try:
                index = atts.getValue('ss:Index')
            except KeyError:
                pass
            else:
                self.cells.extend(
                    ['' for i in range(int(index) - len(self.cells) - 1)])
            self.chars=[]
        elif name=="Row":
            self.cells=[]
        elif name=="Table":
            self.rows=[]
        elif name=="Worksheet":
            self.worksheet = atts.getValue('ss:Name')
    
    def endElement(self, name):
        if name=="Cell":
            self.cells.append(''.join(self.data))
        elif name=="Row":
            self.rows.append(self.cells)
        elif name=="Table":
            self.tables.append((self.worksheet, self.rows))
        elif name=="Data":
            self.data=self.chars
            self.chars=[]

if __name__ == "__main__":
    excelHandler=ExcelHandler()
    parse(sys.argv[1], excelHandler)
    print excelHandler.tables
