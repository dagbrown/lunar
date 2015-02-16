#!/usr/bin/python

import os
import sqlite3
import re
import sys
from pkgdb import pkgdb

if os.environ.has_key("MOONBASE"):
    moonbase = os.environ["MOONBASE"]
else:
    moonbase = "/var/lib/lunar/moonbase"

def create_module_index():
    details = []
    if moonbase == "/var/lib/lunar/moonbase":
        fh = file(os.environ["INSTALL_LOGS"]+"/moonbase-"+installed_version("moonbase"))
        for line in fh.read().split("\n"):
            if re.search('DETAILS$', line):
                details.append(line)
    else:
        for root, dirs, files in os.walk(moonbase):
            for f in files:
                if f == "DETAILS":
                    details.append(os.path.join(root, f))

    records=[]
    i=1
    tot=len(details)
    for mod in details:
        ind = index_record(mod)
        if ind is not None:
            records.append(index_record(mod))
            sys.stderr.write("({}/{})\r".format(i,tot))
            i = i + 1
    # records = [ index_record(mod) for mod in details]
    sys.stderr.write("\n");

    cursor = pkgdb.db.cursor() # this abstraction leaky as hell yo
    cursor.execute("drop table if exists module_index")
    cursor.execute("create table module_index (package text primary key, location text, version text, updated text)")
    for rec in records:
        try:
            cursor.execute("insert into module_index values ( ?, ?, ?, ? )", rec)
        except sqlite3.IntegrityError: # ignore duplicates
            pass
    pkgdb.db.commit()

def index_record(details):
    version=None
    updated=None
    fh = file(details)
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
    cursor = pkgdb.db.cursor()

    version = pkgdb.query1("select version from modules where package = ?", mod )
    return version[0]

if __name__ == '__main__':
    sys.stderr.write("Creating module index...\n");
    create_module_index()
