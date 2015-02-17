#!/usr/bin/python

import os
from pkgdb import pkgdb
from config import config
from modules import Module

class GetOutOfLoop(exception):
  pass

if os.environ.has_key("MOONBASE"):
    moonbase = os.environ["MOONBASE"]
else:
    moonbase = config["MOONBASE"]

def list_sections():
  """ Return a list of all the moonbase's sections """
  check_module_index()

  sections = [t[0] for t in pkgdb.query("select distinct(location) from module_index")]
  
  for root, dirs, files in os.walk(os.path.join(moonbase, "zlocal")):
    for f in files:
      if f == "DETAILS":
        print dirs
        print root
        sections.append(re.subst("^"+moonbase+"/","",os.path.dirname(root)))
  sections=list(set(sections))
  sections.sort()

  return sections

def list_modules(section):
  """ Return a list of all modules in a specific section """
  modules = [ t[0] for t in pkgdb.query("select package from module_index where location = ?", section) ]
  if len(modules) == 0:
    for root, dirs, files in os.walk(os.path.join(moonbase, section)):
      for f in files:
        if f == "DETAILS":
          modules.append(os.path.basename(root))
  return modules

def list_moonbase():
  """ Return a list of all the modules in the moonbase """
  # not entirely sure why it was implemented this way, but at least "alien"
  # modules like in zlocal are still included
  sections=list_sections()
  modules=[]
  for section in sections:
    modules += list_modules(section)
  return modules

def list_installed():
  """ Return a list of installed (or held) modules """
  return [t[0] for t in pkgdb.query("""
      select distinct m.package
           from modules_states ms
           inner join modules m on ms.module = m.package
           inner join states s on ms.state_id = s.id
           where s.name = 'installed'""")]

def create_module_index():
  """ Creates an index table of module|section|version|updated """
  details = []
  if moonbase == "/var/lib/lunar/moonbase":
    fh = file(os.environ["INSTALL_LOGS"]+"/moonbase-"+Module("moonbase").installed_version())
    for line in fh.read().split("\n"):
      if re.search('DETAILS$', line):
        details.append(line)
  else: # go spelunking around someone's custom moonbase
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
  """ Runs the DETAILS file of a module, returns information about it
      in a format suitable for adding to the index database """
  # TODO refactor this into the modules module
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

def check_module_index():
  """ Checks if the index is up-to-date compared to the moonbase """
  if pkgdb.query1("select count(*) from module_index")[0] == 0 or \
      pkgdb.query1("select count(*) from depends_cache")[0] == 0:
    create_module_index()
    create_depends_cache()
  module_index_timestamp = pkgdb.timestamp("module_index")
  depends_cache_timestamp = pkgdb.timestamp("depends_cache")
  try:
    for root, dirs, files in os.walk(moonbase):
      for f in files:
        if f == "DETAILS":
          stat=os.stat(os.path.join(root,f))
          if time.localtime(stat.mtime) > module_index_timestamp:
            create_module_index
            raise GetOutOfLoop
  except GetOutOfLoop:
    pass
  try:
    for root, dirs, files in os.walk(moonbase):
      for f in files:
        if f == "DETAILS":
          stat=os.stat(os.path.join(root,f))
          if time.localtime(stat.mtime) > depends_cache_timestamp:
            create_depends_cache
            raise GetOutOfLoop
  except GetOutOfLoop:
    pass

def create_depends_cache():
  pass
