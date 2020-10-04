#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
import subprocess
import os, sys, time, sqlite3, re
from json import loads, dumps
import dns.resolver

FILEPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tracerouting.py')
IPLIST = 'ipaddresses.txt'
DATABASE = 'tracerouting2.db'

RESULTCODE = {
    '0': 'NO CHANGE',
    '1': 'CHANGE',
    '2': 'DB ERROR',
    '3': 'ENTRY IS NOT FOUND',
    '5': 'TRACEROUTE ERROR'
}




def targetlist():

    targetList = []
    with open(IPLIST) as f:
        for line in f:
            string = line.rstrip()
            if string != '':
                correct, ip = checkIP(string)
                if correct == True:
                    l = [string, ip]
                    targetList.append(l)


    return targetList



def resolver_hostname(reNormalIp, target):

    try: 
        l = dns.resolver.resolve(target, 'A')
        for row in l:
            
            ip = row.to_text()
            if reNormalIp.findall(ip):
                return ip




    except dns.resolver.NoNameservers as e:
        print(e)

    except dns.resolver.NXDOMAIN as e:
        print(e)

    except Exception as e:
        print(e)





def exister(tablename, strRoute):


    cursor.execute(f"""SELECT ip_list FROM {tablename} order by trace_date desc limit 1 """)
    row = cursor.fetchall()

    exist = -1
    try:
        if row[0][0]:
            if row[0][0] == strRoute:
                print(RESULTCODE['0'])
                exist = 0
            else:
                print(RESULTCODE['1'])
                exist = 1
            
        else:
            print(RESULTCODE['3'])
            exist = 3
        
    except IndexError:
        print(RESULTCODE['3'])
        exist = 3

    return exist

def traceExec(ip: str) -> subprocess.Popen:


    cmd = f'python3 {FILEPATH} {ip}'.split()
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    return p


def parser(blockResult):

    print('-'*25)



    for block in blockResult.split('\n\n')[:-1]:
        header = block.split('\n')[0]
        body = block.split('\n')[1:]
        print(header)

        if body != ['']:

            timeLst = []
            hopLst = {}
            for hop in body:
                hopLst[hop.split(' ')[0]] = hop.split(' ')[1]
                timeLst.append(hop.split(' ')[2])

            yield header, hopLst, timeLst





def createtablename(target):

    tablename = 'traceroute_' + target
    tablename = tablename.replace('.', '_')
    tablename = tablename.replace('-', '_')

    try:
        cursor.execute(f"""create table if not exists {tablename}(id INTEGER PRIMARY KEY autoincrement, trace_date string, ip_list string, avg_time integer, descr string)""")


    except Exception as e:
        print('UNKNOWN ERROR. IMPOSSIBLE TO CREATE TABLE')
        print(e)

        return None
    
    return tablename


def analizer(tablename, newtrace):

    cursor.execute(f"""SELECT ip_list FROM {tablename} order by trace_date desc limit 1 """)

    oldtrace = loads(cursor.fetchall()[0][0])



    iter_number = max(*[int(x) for x in oldtrace.keys()], *[int(x) for x in newtrace.keys()])
    for hop_number in range(1, iter_number):

        hop_number = str(hop_number)
        
        if not hop_number in oldtrace or hop_number in newtrace:
            continue
        else:

            if hop_number in oldtrace and hop_number in newtrace:
                if not oldtrace[hop_number] == newtrace[hop_number]:
                    print(hop_number,': ', oldtrace[hop_number], ' changed on ', newtrace[hop_number])

            if hop_number not in oldtrace:
                print('detected new hop ', hop_number,': ', newtrace[hop_number])

            if int(hop_number) not in newtrace:
                print('missed the hop ', hop_number,': ', oldtrace[hop_number])






def dbwritter(targetName, hopLst, targetIp, timeLst, nowTime):

    strRoute = dumps(hopLst)
    strTime = dumps(timeLst)
    tablename = createtablename(targetName) #создание таблицы

    if not tablename:
        return False


    exist = exister(tablename, hopLst)  #проверка на соответсвие последней трессировки
    
    descr = False

    if hopLst[max(hopLst, key=hopLst.get)] == targetIp:
        descr = True
    else:
        descr = False


    if exist == 0:
        cursor.execute(f"""SELECT id FROM {tablename} WHERE ip_list = '{strRoute}' order by trace_date desc limit 1""")
        newid = cursor.fetchall()[0][0]
        cursor.execute(f"""UPDATE {tablename} SET avg_time = "{strTime}" WHERE id = {newid}""")
        conn.commit()
        return True


    elif exist == 1:
        analizer(tablename, hopLst)
        cursor.execute(f"""INSERT INTO  {tablename} (trace_date, ip_list, avg_time, descr) VALUES ('{nowTime}', '{strRoute}', '{strTime}', '{descr}')""")
        conn.commit()
        return True


    elif exist == 3 or exist == -1:
        cursor.execute(f"""INSERT INTO  {tablename} (trace_date, ip_list, avg_time, descr) VALUES ('{nowTime}', '{strRoute}', '{strTime}', '{descr}')""")
        conn.commit()
        return True


def checkIP(target):

    reIp = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    reNormalIp = re.compile(r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$')
    reDel = re.compile(r'([^a-zA-Z0-9_.-])')



    target = target.replace(' ', '')
    target = reDel.sub('', target)




    if not reIp.findall(target):

        ip = resolver_hostname(reNormalIp, target)
        
        if not ip:
            print(f'UNABLE TO GET IP FROM HOST: {target}')
            return False, target
        

        else:
            print(f'From host {target} got IP {ip}')
            return True, ip

            



    else:
        for row in target.split('.'):
            if int(row) == 255:
                print(f'Broadcast IP {target}')
                return False, target
        if reNormalIp.findall(target):
            return True, target

        else:
            print(f'Uncorrect IP: {target}')
            return False, target




def tracerouting(targetList):

    blockSize: int = 4 # Parallel traceroute count
    blockResult: str = ''

    for idx in range(0, len(targetList), blockSize):
        nowTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        processes: list = []


        for target in targetList[idx:idx+4]:
            processes.append(traceExec(target[1]))



        for p in processes:
            stdout, stderr = p.communicate()
            blockResult += stdout.decode() + '\n'

        for targetIp, hopLst, timeLst in parser(blockResult):


            for target in targetList:
                if target[1] == targetIp:
                    targetName = target[0]


            if dbwritter(targetName, hopLst, targetIp, timeLst, nowTime) == True:
                pass
            else:
                continue
    





def startprocess(cur, con, oneip = None):
    global cursor
    global conn
    cursor = cur
    conn = con
    if oneip:
        correct, ip = checkIP(oneip)
        if correct == True:
            tracerouting([oneip, ip])

    else:
        targetList = targetlist()
        tracerouting(targetList)






def connection():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    return conn, cursor


def main():
    conn, cursor = connection()
    print(f'Connecting with DB {conn}')
    startprocess(cursor, conn)

if __name__ == '__main__':
	sys.exit(main())

