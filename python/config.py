#!/usr/bin/python

from wordexp import wordexp
import re
import os

class Config:
  def __init__(self, config="/etc/lunar/config"):
    """
    Load up the configuration from /etc/lunar/config
    or whatever alternative location you give it
    """
    self.config = {}

    lines=file(config,"r").read().split("\n")

    for line in lines:
      if re.search("^ *$", line):
        continue
      if re.search('^ *#.*$', line):
        continue
      words=wordexp(line)
      if len(words) == 0:
        next
      if words[0] == 'export':
        env, value = words[1].split("=")
        os.environ[env]=value
      else:
        variable, value = words[0].split("=")
        self.config[variable] = value

  def __getitem__(self, item):
    if self.config.has_key(item): 
      return self.config[item]
    else:
      return None

config = Config()
