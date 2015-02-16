#/usr/bin/python

import sqlite3 as sqlite
import os

if os.environ.has_key("MODULE_STATUS"):
    status_db = os.environ["MODULE_STATUS"]
else:
    status_db = "/var/state/lunar/packages.db"

class PkgDB:
    def __init__(self):
        self.db = sqlite.connect(status_db)

    def query(self, query, *params):
        cursor = self.db.cursor()

        cursor.execute(query, params)
        return cursor.fetchall()

    def query1(self, query, *params):
        cursor = self.db.cursor()

        cursor.execute(query, params)
        return cursor.fetchone()

    def set_timestamp(self, name):
        cursor = self.db.cursor()
        cursor.execute("""
                create table if not exists timestamps (
                    name text unique primary key,
                    time timestamp default current_timestamp not null
                )
        """)
        print name
        cursor.execute("select count(*) from timestamps where name = ?", (name,) )
        if cursor.fetchone()[0] == 0:
            print "insert"
            cursor.execute("insert into timestamps (name) values ( ? )", (name,) )
        else:
            print "update"
            cursor.execute("update timestamps set time = current_timestamp where name = ?", (name,))
        self.db.commit()

    def compare_timestamps(self, name1, name2):
        cursor = self.db.cursor()

        cursor.execute("""
            select (
                select time from timestamps where name = ?
            ) > (
                select time from timestamps where name = ?
            )
        """, (name1, name2) )

        if cursor.fetchone()[0] == 1:
            return 1
        else:
            cursor.execute("""
                select (
                    select time from timestamps where name = ?
                ) < (
                    select time from timestamps where name = ?
                )
            """, (name1, name2) )
            if cursor.fetchone()[0] == 1:
                return -1
            else:
                return 0

pkgdb=PkgDB()

if __name__ == '__main__':
    import sys
    results = pkgdb.query(sys.argv[1],*tuple(sys.argv[2:]))
    for result in results:
        print "|".join(result)
