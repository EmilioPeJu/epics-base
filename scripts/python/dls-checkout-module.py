#!/usr/bin/env python2.4

"""
dls-checkout-module.py [-i -b <branch>] <name>
Author: Peter Denison

This script is used to checkout a support module or
IOC application from the trunk or a branch in the
repository. The support module or IOC application
is checked out into the users current directory.

The -i flag is used to specify an IOC application.
The -b flag tells the script to checkout from a
branch rather than the trunk.
"""

import sys, os, pysvn
from   optparse import OptionParser
from   dlsPyLib import *

def main():
  parser = OptionParser("usage: %prog [-i -b <branch>] <name>")
  parser.add_option("-i", "--ioc", action="store_true", dest="ioc",
                    help="Checkout an IOC application")
  parser.add_option("-b", "--branch", action="store", type="string", dest="branch",
                    help="Checkout from a branch rather than from the trunk")
  (options, args) = parser.parse_args()
  if len(args) < 1 or len(args) > 2:
    parser.error("incorrect number of arguments")

  # Check the SVN_ROOT environment variable
  prefix = checkSVN_ROOT()
  if not prefix:
    sys.exit()

  if options.ioc:
    cols = args[0].split('/')
    if len(cols) > 1:
      source = 'ioc/' + args[0]
    else:
      print 'Missing Technical Area under Beamline'
      sys.exit()
  else:
    source = 'support/' + args[0]

  # Create an object to interact with subversion
  subversion = pysvn.Client()

  # Check for existence of this module in various places in the repository
  exists =  pathcheck( subversion, os.path.join(prefix,'trunk',source) )
  if not exists:
    print 'Repository does not contain the "'+source+'" module'
    sys.exit()

  if options.branch:
    branch = options.branch
    exists = pathcheck( subversion, os.path.join(prefix,'branches',source) )
    if not exists:
      print 'Module "'+source+'" has no branches'
      sys.exit()

    exists = pathcheck( subversion, os.path.join(prefix,'branches',source,branch) )
    if not exists:
      print 'Module "'+source+'" does not contain a branch called: "'+branch+'"'
      sys.exit()
    subtree = 'branches'
  else:
    branch  = ''
    subtree = 'trunk'

  print 'Checking out: '+os.path.join(prefix,subtree,source,branch)+'...'
  subversion.checkout(os.path.join(prefix,subtree,source,branch), os.path.join(args[0],branch))


if __name__ == "__main__":
  main()
