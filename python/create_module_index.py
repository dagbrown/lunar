#!/usr/bin/python

import os
import sqlite3
import re

moonbase=os.environ["MOONBASE"]

status_db=os.environ["MODULE_STATUS"]

def create_module_index():
    details = []
    if moonbase == "/var/lib/lunar/moonbase":
        fh = file.open(os.environ["INSTALL_LOGS"]+"/moonbase-"+installed_version("moonbase"))
        details = [re.match("/DETAILS$", line) for line in fh.read().split("\n")]
    else:
        for root, dirs, files in os.walk(moonbase):
            for file in files:
                if file == "DETAILS":
                    details.append(os.path.join(root, file))

    records=[]
    i=1
    tot=len(details)
    for mod in details:
        records.append(index_record(mod))
        print "({}/{})\r".format(i,tot),
        i = i + 1
    # records = [ index_record(mod) for mod in details]
    print

    conn = sqlite3.connect(status_db)
    cursor = conn.cursor()
    cursor.execute("drop table if exists module_index")
    cursor.execute("create table module_index (package text primary key, location text, version text, updated text)")
    for rec in records:
        cursor.execute("insert into module_index values ( ?, ?, ?, ? )", rec)
    conn.commit()
    conn.close()

def index_record(details):
    version=None
    updated=None
    for line in file(details).read().split("\n"):
        if re.search("=",line):
            (name,junk,value) = line.replace(" ","").partition("=")
            if name == "VERSION":
                version = value
            if name == "UPDATED":
                updated = value
    mod = os.path.basename(os.path.dirname(details))
    location = os.path.dirname(os.path.dirname(details)).replace(moonbase + "/", "")
    return (mod, location, version, updated)

def installed_version(mod):
    conn = sqlite3.connect(status_db)
    cursor = conn.cursor()
    t = ( mod, )

    cursor.execute("select * from modules where package = ?", t)
    version = cursor.fetchone()
    conn.close()
    return version

if __name__ == '__main__':
    print "Creating module index..."
    create_module_index()
