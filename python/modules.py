#!/usr/bin/python

import os
import re
import sys
from pkgdb import pkgdb
from create_module_index import create_module_index
from wordexp import wordexp
from config import config

if os.environ.has_key("MOONBASE"):
  moonbase = os.environ["MOONBASE"]
else:
  moonbase = "/var/lib/lunar/moonbase"

class Module:
  def __init__(self, name = ""):
    self.name = name
    results = pkgdb.query1("""
      select location, version, updated from module_index
      where package = ?
    """, self.name)
    if results is not None:
      (self.location, self.version, self.updated) = results
    else:
      (self.location, self.version, self.updated) = (None, None, None)

  def run_details(self):
    pass # implement later

  def _has_state(self, statename):
    count = pkgdb.query1("""
      select count(*) from modules_states ms
        inner join states s on ms.state_id = s.id
        where ms.module = ? and s.name = ?
    """, self.name, statename)[0]

    return count == 1

  def installed(self):
    return self._has_state("installed") or self._has_state("held")

  def held(self):
    return self._has_state("held")

  def installed_version(self):
    version = pkgdb.query1("select version from modules where package = ?", self.name )[0]
    return version

  def section(self):
    """ Returns what section a module is in, taking into account the value of ZLOCAL_OVERRIDES """
    if config["ZLOCAL_OVERRIDES"] == "on":
      for root, dirs, files in os.walk(os.path.join(moonbase, "zlocal")):
        if self.name in dirs and os.path.exists(os.path.join(root, self.name, "DETAILS")):
          return string.replace(root, moonbase, "")
    else:
      if self.location is not None:
        return self.location
      else:
        # Okay, find, try zlocal again
        for root, dirs, files in os.walk(os.path.join(moonbase, "zlocal")):
          if self.name in dirs and os.path.exists(os.path.join(root, self.name, "DETAILS")):
            return string.replace(root, moonbase, "")

  def run_details(self):
    pass # TODO
