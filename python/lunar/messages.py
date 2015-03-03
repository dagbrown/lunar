#!/usr/bin/python
#                                                          #
#  messages - lunar message display functions              #
#                                                          #
############################################################
#                                                          #
# this WAS the subroutines of a source based Linux distro, #
# calls Sorcerer GNU/Linux, or SGL. SGL is no longer       #
# available with GPL license. Since this script was taken  #
# before licensing scheme change, no legal problems I      #
# guess.                                                   #
#                                                          #
# the code is re-written for Lunar. The previous Copyright #
# notices are kept; just in case some code is left :=)     #
# Kagan Kongar <kongar@tsrsb.org.tr>, 20020519             #
#                                                          #
############################################################
#                                                          #
# Copyright 2001 by Kyle Sallee                            #
#                                                          #
# Parts Copyrighted Hendrik Visage 2002 under GPLv2        #
#                                                          #
# Parts Copyrighted Kagan Kongar 2002 under GPLv2          #
#                                                          #
############################################################
#                                                          #
# moved to messages.lunar by sofar 2003                    #
# rewritten in Python by dagbrown 2015                     #
#                                                          #
############################################################

from sys import stdin, stdout, stderr
from select import select
from lunar.config import config
import inspect

# ANSI color escape sequences
colors = [ "black", "red", "green", "yellow", 
           "blue", "violet", "cyan", "white" ]

def foreground(color):
  return "\033[3%dm" % colors.index(color)

def background(color):
  return "\033[4%dm" % colors.index(color)

def bold():
  return chr(27)+"[1m"

def reset():
  return chr(27)+"[0m"

module_color    = foreground("white")+bold()+background("black")
version_color   = module_color
query_color     = foreground("yellow")+bold()
lrm_color       = query_color
check_color     = foreground("cyan")
resurrect_color = foreground("green")+bold()
file_color      = foreground("green")+bold()
symlink_color   = foreground("cyan")+bold()
problem_color   = foreground("red")+bold()
message_color   = foreground("cyan")
default_color   = reset()

def error_message(*args):
  """ Send an error message to stderr """
  stderr.write(" ".join([str(i) for i in list(args)])+"\n")

def message(*args):
  """ Send a normal message to stdout """
  if config["SILENT"] is not None:
    print " ".join([str(i) for i in list(args)])

def verbose_message(*args):
  """ Send a message to stderr if VERBOSE is on """
  if config["VERBOSE"] == "on":
    stderr.write(" ".join([str(i) for i in list(args)])+"\n")

def _lineno():
  return inspect.currentframe().f_back.f_back.f_lineno

def _filename():
  return inspect.currentframe().f_back.f_back.co_filename

def _function():
  return inspect.currentframe().f_back.f_back.function.__name__

def debug_message(*args):
  """ Output a message for debugging purposes """
  if config("LUNAR_DEBUG") is not None:
    if int(config["LUNAR_DEBUG"]) > 2:
      stderr.write("{}:{}: in {}: ".format(_filename,_lineno,
        _function) + " ".join([str[i] for i in list(args)]) + "\n")
  # if LUNAR_DEBUG > 5, it goes to a log file with a massive dump
  # of the entire configuration.  Do that later

def verbose_msg(*args):
    pass  # TODO

def query(question, default = "n", module = None):
  """
  Asks a yes/no query.  If the config flag SILENT is set, always
  return the default value.  If no default value is given, the
  default default is "n".
  """
  if config["SILENT"] is None:
    response = ""
    while response == "":
      if module is not None:
        print module_color + module + default_color+ ": ",
      print "{}{} [{}]{} ".format(query_color, question,
          default,default_color),
      stdout.flush()
      i, o, e = select( [stdin], [], [], int(config["PROMPT_DELAY"]) )
      if i:
        response = stdin.readline().strip()
      else:
        response = default
      if response[0] == 'y' or response[0] == 'Y':
        return True
      if response[0] == 'n' or response[0] == 'N':
        return False
      response = ""
  else:
    if default == "y" or default == "Y":
      return True
    if default == "n" or default == "N":
      return False
    raise TypeError

