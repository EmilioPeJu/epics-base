#!/usr/bin/env python2.4

"""
dls-list-branches.py [-i] <name>
Author: Peter Denison

This script is used to list the branches of a
support module or IOC application in the repository.

The -i flag is used to specify an IOC application.
"""

import sys, os, pysvn
from   optparse import OptionParser
from   dlsPyLib import *

def main():
  parser = OptionParser("usage: %prog [-i] <name>")
  parser.add_option("-i", "--ioc", action="store_true", dest="ioc",
                    help="List IOC branches")
  (options, args) = parser.parse_args()
  if len(args) != 1:
    parser.error("incorrect number of arguments")

  # Check the SVN_ROOT environment variable
  prefix = checkSVN_ROOT()
  if not prefix:
    sys.exit()

  if options.ioc:
    source = 'ioc/'+args[0]
  else:
    source = 'support/'+args[0]

  # Create an object to interact with subversion
  subversion = pysvn.Client()

  # Check for existence of this module/IOC in "trunk" in the repository
  exists = pathcheck( subversion, os.path.join(prefix,'trunk',source) )
  if not exists:
    print os.path.join(prefix,'trunk',source)+' does not exist in the repository.'
    sys.exit()

  # Check for the exitence of branches of this module/IOC
  exists = pathcheck( subversion, os.path.join(prefix,'branches',source) )
  if not exists:
    print os.path.join(prefix,'branches',source)+' does not exist in the repository.'
    sys.exit()
  else:
    branches = subversion.ls(os.path.join(prefix,'branches',source))
    for node in branches:
      print os.path.basename(node['name'])

if __name__ == "__main__":
  main()
