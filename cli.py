from tracer import startprocess, checkIP
from helper import dblst, showtable, showlasttable
import cmd, sqlite3
import os, sys

FILEPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tracerouting.py')
IPLIST = 'ipaddresses.txt'



RESULTCODE = {
    '0': 'NO CHANGE',
    '1': 'CHANGE',
    '2': 'DB ERROR',
    '3': 'ENTRY IS NOT FOUND',
    '5': 'TRACEROUTE ERROR'
}


DATABASE = 'tracerouting2.db'
def connection():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    return conn, cursor

conn, cursor = connection()
print(f'Connecting with DB {conn}')

class MyCLI(cmd.Cmd):
    """Simple command processor example."""
    def do_start(self, person):
        startprocess(cursor, conn)

    def do_traceroute(self, oneip):
        if not oneip:
            print('Input target')
        else:
            startprocess(cursor, conn, oneip)

    def do_showlast(self, name):
        if not name:
            print('Input tablename')
        else:
            showlasttable(cursor, name)
        
    def do_show(self, name):
        if not name:
            print('Input tablename')
        else:
            showtable(cursor, name)


    def do_list(self, person):
        dblst(cursor)


    def do_qq(self, line):
        print('Good Bie!')
        return True

    def postloop(self):
        print()

if __name__ == '__main__':
    MyCLI().cmdloop()

