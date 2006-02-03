#!/usr/bin/env python2.4

"""
dls-list-modules.py [-i]
Converted to Python and IOC option added by: Andy Foster

This script returns a list of all the support modules
or IOC applications in the repository.

The -i flag is used to specify a listing of the
IOC applications.
"""

import os, pysvn, sys
from   optparse import OptionParser
from   dlsPyLib import *

def main():
  parser = OptionParser("usage: %prog [-i]")
  parser.add_option("-i", "--ioc", action="store_true", dest="ioc",
                    help="List IOC applications")
  (options, args) = parser.parse_args()
  if options.ioc:
    if len(args) != 0 and len(args) != 1:
      parser.error("This script takes either 0 or 1 argument")
      sys.exit()
    if len(args) == 0:
      source = 'ioc'
    else:
      source = 'ioc/' + args[0]
  else:
    source = 'support'
    if len(args) != 0:
      parser.error("This script takes no arguments")
      sys.exit()

  # Check the SVN_ROOT environment variable
  prefix = checkSVN_ROOT()
  if not prefix:
    sys.exit()

  # Create an object to interact with subversion
  subversion = pysvn.Client()

  # Check for the existence of "source" in the repository
  exists = pathcheck( subversion, os.path.join(prefix,'trunk',source) )
  if not exists:
    print os.path.join(prefix,'trunk',source)+' does not exist in the repository.'
    sys.exit()
  else:
    modules = subversion.ls(os.path.join(prefix,'trunk',source))
    for node in modules:
      print os.path.basename(node['name'])

if __name__ == "__main__":
  main()
