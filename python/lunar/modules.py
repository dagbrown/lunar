#!/usr/bin/python

import os
import re
import sys
import string
from lunar.pkgdb import pkgdb
from wordexp import wordexp
from lunar.config import config

class NonexistentModuleError(Exception):
  pass

class Module:
  def __init__(self, name, details=True):
    """ Creates a Module object and grabs its details from its DETAILS file """
    self.name = name
    results = pkgdb.query1("""
      select location, version, updated from module_index
      where package = ?
    """, self.name)
    if results is not None:
      (self.location, self.version, self.updated) = results
    else:
      (self.location, self.version, self.updated) = (None, None, None)
    if details:
      self.run_details()

  def _has_state(self, statename):
    """ Check to see if a module has a specific state """
    count = pkgdb.query1("""
      select count(*) from modules_states ms
        inner join states s on ms.state_id = s.id
        where ms.module = ? and s.name = ?
    """, self.name, statename)[0]

    return count == 1

  def installed(self):
    """ Check if module is installed """
    return self._has_state("installed") or self._has_state("held")

  def held(self):
    """ Check if module has been held """
    return self._has_state("held")

  def exiled(self):
    """ Check if module has been exiled """
    return self._has_state("exiled")

  def enforced(self):
    """ Check if module is enforced """
    return self._has_state("enforced")

  def expired(self):
    return self.details["UPDATED"] > self.updated

  def installed_version(self):
    """ Return the installed version of module """
    version = pkgdb.query1("select version from modules where package = ?", self.name )[0]
    return version

  def section(self):
    """ Returns what section a module is in, taking into account the value of ZLOCAL_OVERRIDES """
    if config["ZLOCAL_OVERRIDES"] == "on":
      for root, dirs, files in os.walk(os.path.join(config["MOONBASE"], "zlocal")):
        if self.name in dirs and os.path.exists(os.path.join(root, self.name, "DETAILS")):
          return string.replace(root, config["MOONBASE"], "")
      return self.location
    else:
      if self.location is not None:
        return self.location
      else:
        # Okay, find, try zlocal again
        for root, dirs, files in os.walk(os.path.join(config["MOONBASE"], "zlocal")):
          if self.name in dirs and os.path.exists(os.path.join(root, self.name, "DETAILS")):
            return string.replace(root, config["MOONBASE"], "")

  def install_log(self):
    logpath = os.path.join(config["INSTALL_LOGS"], "{}-{}".format(self.name,self.installed_version()))
    try:
      return file(logpath).read()
    except IOError:
      return ""

  def _expand_params(self,text):
    """ Expands potential variables in a candidate string """
    candidates = re.findall(r"\${?(\w+)", text)

    if len(candidates) == 0: # nothing to do, just return the text
      return text

    # If it's been defined by module details, use that
    # If it's been defined by lunar config, use that
    # Finally, if it's in the environment, use tha
    deletethese = []
    for candidate in candidates:
      if self.details.has_key(candidate):
        os.environ[candidate] = self.details[candidate]
        deletethese += [ candidate ]
      else:
        if config[candidate] is not None:
          os.environ[candidate] = config[candidate]
          deletethese += [ candidate ]
    try:
        returnval = wordexp(text)[0]
    except RuntimeError:
        returnval = text
    for d in deletethese:
      if os.environ.has_key(d):
        del os.environ[d]
    return returnval

  def run_details(self):
    """ Loads up the values defined in the module's DETAILS file """
    self.details={}
    section = self.section()
    if section is not None:
      fullpath = os.path.join(config["MOONBASE"],
          self.section(),
          self.name,
          "DETAILS")
      description_flag=False
      self.description = ""
      print fullpath
      lines=file(fullpath, "r").read().split("\n")
      for line in lines:
        if re.search('^ *$',line):
          continue
        if re.search('^ *#', line):
          continue
        if description_flag and line != "EOF":
          self.description += "\n" + line
        if description_flag and line == "EOF":
          self.description += "\n"
          description_flag = False
        if re.search("cat *\<\< *EOF$", line):
          description_flag=True
        try:
          line.index("=")
          variable, value = line.split("=", 1)
          variable=wordexp(variable)[0]
          value = self._expand_params(value)
          self.details[variable] = value
        except ValueError:
          pass
    else:
      raise NonexistentModuleError
