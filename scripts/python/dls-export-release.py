#!/usr/bin/env python2.4

"""
dls-export-release [-i] <name> <tag> <epicsVer>
Written by: Andy Foster

This script is used to export the release of <name>
called <tag> to the <epicsVer> "prod" tree.
The release, <tag>, must already exist in the repository.
This will have been created originally with "dls-release.py".
<name> can be a support module or IOC application.

This script solves the problem of making multiple releases to
different EPICS "prod" trees without creating multiple tags 
in the repository. There should not be multiple tags for a given
release since the same code should compile for different
EPICS versions.

This script makes no changes to the repository.

The -i flag specifies to export a release of an IOC application.
For an IOC application, <name> is expected to be of the form:
<beamLine/Technical Area> e.g. BL18I/MO
"""

import os, pysvn, sys
from   optparse import OptionParser
from   dlsPyLib import *

def main():
  parser = OptionParser("usage: %prog [-i] <name> <tag> <epicsVer>")
  parser.add_option("-i", "--ioc", action="store_true", dest="ioc",
                    help="Export a release of an IOC application")
  (options, args) = parser.parse_args()
  if len(args) < 3:
    parser.error("Incorrect number of arguments")

  # Check the SVN_ROOT environment variable
  prefix = checkSVN_ROOT()
  if not prefix:
    sys.exit()

  epicsVer = args[2]
  if( epicsVer != 'R3.13.9' and epicsVer != 'R3.14.7' and epicsVer != 'R3.14.8.2' ):
    print 'The EPICS version must be one of: R3.13.9, R3.14.7 or R3.14.8.2'
    sys.exit()

  if options.ioc:
    cols = args[0].split('/')
    if len(cols) < 2:
      print 'Missing Technical Area under Beam Line'
      sys.exit()
    relDir  = 'release/ioc/' + args[0]
    diskDir = 'ioc'
  else:
    relDir  = 'release/support/' + args[0]
    diskDir = 'support'

  # Create an object to interact with subversion
  subversion = pysvn.Client()

  # Check for the existence of the tagged release of this module

  exists = pathcheck( subversion, os.path.join(prefix,relDir,args[1]) )
  if not exists:
    print 'Repository does not contain the ' +args[1]+ ' release of ' +args[0]
    sys.exit()

  # Check for the existence of the correct directory tree on-disk, into which
  # the release should be checked out. If the directory tree is not present, create it.

  baseStr = '/'
  prodDir = os.path.join( '/home/diamond', epicsVer, 'prod', diskDir, args[0] )
  for ss in prodDir.split('/'):
    baseStr = os.path.join( baseStr, ss )
    stat    = os.access(baseStr, os.F_OK)
    if not stat:
      os.mkdir(baseStr)

  # Check if this release already exists on-disk
  stat = os.access(os.path.join(baseStr, args[1]), os.F_OK)
  if stat:
    print 'Release: "' + os.path.join(baseStr, args[1]) + '"'
    print 'already exisits on-disk!'
    sys.exit()

  print 'Checking out: ' + os.path.join(relDir,args[1])

  subversion.checkout(os.path.join(prefix,relDir,args[1]), os.path.join(baseStr,args[1]) )

  print 'Building release...'
  stat = os.chdir(os.path.join(baseStr,args[1]))
  os.system('make')

if __name__ == "__main__":
  main()
