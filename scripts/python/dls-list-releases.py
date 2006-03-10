#!/usr/bin/env python2.4

"""
dls-list-releases.py [-i] <name>
Author: Andy Foster

This script is used to list the releases of a
support module or IOC application in the repository.

The -i flag is used to specify an IOC application.
"""

import sys, os, pysvn
from   optparse import OptionParser
from   dlsPyLib import *

def main():
  parser = OptionParser("usage: %prog [-i] <name>")
  parser.add_option("-i", "--ioc", action="store_true", dest="ioc",
                    help="List IOC releases")
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

  # Check for the exitence of releases of this module/IOC
  exists = pathcheck( subversion, os.path.join(prefix,'release',source) )
  if not exists:
    print os.path.join(prefix,'release',source)+' does not exist in the repository.'
    sys.exit()
  else:
    releases = subversion.ls(os.path.join(prefix,'release',source))
    for node in releases:
      print os.path.basename(node['name'])

if __name__ == "__main__":
  main()
