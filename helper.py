#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import os, sys, time, sqlite3, re
from json import loads, dumps


#----------------
#WORK WITH OUTPUT
#----------------



def showtable(cursor, name):
    cursor.execute(f"""SELECT * from {name}""")
    table = cursor.fetchall()
    for row in table:
        print('Traceroute', row[0],'. Date: ', row[1])
        route = loads(row[2])
        for hop in route:
            print(hop, ':', route[hop])
        print(f'Finished: {row[4]}')



def dblst(cursor):
    cursor.execute(f"""SELECT name from sqlite_master where type= 'table'""")
    lst = cursor.fetchall()
    tables = []
    for row in lst:

        if row[0] != 'sqlite_sequence':
            table = row[0]
            tables.append(table)
            print(table)

def showlasttable(cursor, name):
    cursor.execute(f"""select * from {name} order by trace_date desc limit 1""")
    row = cursor.fetchall()[0]


    print('Traceroute', row[0],'. Date: ', row[1])
    route = loads(row[2])
    for hop in route:
        print(hop, ':', route[hop])
    print(f'Finished: {row[4]}')


