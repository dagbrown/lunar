#!/usr/bin/python
#

from lunar.pkgdb import pkgdb
from lunar.messages import *
from lunar.config import config
from lunar.modules import Module
from wordexp import wordexp
import re
import os

class Dependency:
    pass

def _process_depends(depends_path):
  """
  Processes the DEPENDS file in the filename
      
  Returns a list of dependency records
  """
  module = depends_path.split("/")[-2]

  depends_list = []
  params = None

  lines = file(depends_path).read().split("\n")

  backslash = False
  for line in lines:
    if backslash:
      full_line += line
    else:
      full_line = line
    if re.search("^[ \t]*$", full_line):
      backslash = False
      continue
    if line[-1] == "\\":
      line = line.strip("\\")
      backslash = True
      continue
    else:
      backslash = False
    words = wordexp(full_line)
    if words[0] == "depends":
      params = ( module, words[1], 1, "", "", "" )
    else:
      if words[0] == "optional_depends":
        params = ( module, words[1], 0, words[2], words[3], words[4] )
    if params is not None:
      depends_list.append(params)

  return depends_list

def create_depends_cache():
  """
  If the module index is newer than the dependency cache, creates a new
  dependency cache.
  """
  if pkgdb.timestamp("module_index") > pkgdb.timestamp("depends_cache"):
    verbose_msg("Generating a new depends cache...")
    pkgdb.query("drop table if exists depends_cache")
    pkgdb.query("""
      create table depends_cache (
        module text,
        dependency text,
        required boolean,
        flags_for_active text,
        flags_for_not_active text,
        reason text,
        foreign key(module) references module_index(package),
        foreign key(dependency) references module_index(package)
      )
    """)

    # massive speedup if user is using default moonbase
    if config["MOONBASE"] == "/var/lib/lunar/moonbase":
      version = Module("moonbase").installed_version()
      location = os.path.join(config["INSTALL_LOGS"],"moonbase-%s" % version)
      files = file(location).read.split("\n")
      depends_files = filter(lambda x: re.search("DETAILS$", x),files)
      if config["ZLOCAL_OVERRIDES"] == "on":
        for root, dirs, files in os.walk(os.path.join(config["MOONBASE"], "zlocal")):
          if "DEPENDS" in files:
            depends_files.append(os.path.join(root, "DEPENDS"))
    else:
      depends_files = []
      for root, dirs, files in os.walk(config["MOONBASE"]):
        if "DEPENDS" in files:
          depends_files.append(os.path.join(root,"DEPENDS"))
      if config["ZLOCAL_OVERRIDES"] != "on":
        depends_files.filter(lambda f: not re.search("zlocal", f))

    records = []
    for depfile in depends_files:
      records += _process_depends(depfile)
    # TODO put records into DB
