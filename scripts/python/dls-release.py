#!/usr/bin/env python2.4

"""
dls-release [-i -b <branch> -e <epicsVer>] <name> <tag>
Converted to Python and IOC option added by: Andy Foster

This script is used to release a support module or IOC
application, <name>, to the 'prod' tree. The released
software is tagged as <tag> in the release area of the
repository.

The -i flag specifies a release of an IOC application.

The -b flag tells the script to release from a branch
rather than from the trunk.

The -e flag specifies which EPICS version 'prod' area
the release should be made to.
"""

import os, pysvn, sys
from   optparse import OptionParser
from   dlsPyLib import *

def main():
  parser = OptionParser("usage: %prog [-i -b <branch> -e <EPICS version>] <name> <tag>")
  parser.add_option("-i", "--ioc", action="store_true", dest="ioc",
                    help="Release an IOC application")
  parser.add_option("-b", "--branch", action="store", type="string", dest="branch",
                    help="Release from a branch")
  parser.add_option("-e", "--epicsVer", action="store", type="string", dest="epicsVer",
                    help="Release into \"/home/diamond/epicsVer/prod\"")
  (options, args) = parser.parse_args()
  if len(args) < 2 or len(args) > 3:
    parser.error("Incorrect number of arguments")

  # Check the SVN_ROOT environment variable
  prefix = checkSVN_ROOT()
  if not prefix:
    sys.exit()

  if( not options.epicsVer ):
    epicsVer = 'R3.14.7'
  else:
    epicsVer = options.epicsVer

  if( not options.ioc and not options.branch ):
    srcDir  = 'trunk/support/'+args[0]
    relDir1 = 'release/support/'
    diskDir = 'support'
    bflag   = 0
  elif( not options.ioc and options.branch ):
    srcDir  = 'branches/support/'+args[0]+'/'+options.branch
    relDir1 = 'release/support/'
    diskDir = 'support'
    bflag   = 1
  elif( options.ioc and options.branch ):
    srcDir  = 'branches/ioc/'+args[0]+'/'+options.branch
    relDir1 = 'release/ioc/'
    diskDir = 'ioc'
    bflag   = 1
  elif( options.ioc and not options.branch ):
    srcDir  = 'trunk/ioc/'+args[0]
    relDir1 = 'release/ioc/'
    diskDir = 'ioc'
    bflag   = 0
  else:
    print 'Should NEVER see this'

  relDir = relDir1+args[0]

  # Create an object to interact with subversion
  subversion = pysvn.Client()

  log_message = 'Releasing ' +args[0]+ ' at version ' +args[1]

  def get_log_message():
    return True, log_message

  subversion.callback_get_log_message = get_log_message

  # Check for the existence of this module in "trunk" and "branches" in the repository

  exists = pathcheck( subversion, os.path.join(prefix, srcDir) )
  if not exists:
    print os.path.join(prefix, srcDir)+ ' does not exist in the repository.'
    sys.exit()

  # Check for the existence of a directory in the repository, into which tagged 
  # releases of this module can be made. If it is not present, create it.

  relD = relDir1
  for ss in args[0].split('/'):
    relD = relD + ss + '/'
    exists = pathcheck( subversion, os.path.join(prefix,relD) )
    if not exists:
      subversion.mkdir(os.path.join(prefix,relD), 
                       'Created: '+os.path.join(prefix,relD))

  # Check for existence of a release of this module with the same tag

  exists = pathcheck( subversion, os.path.join(prefix,relDir,args[1]) )
  if exists:
    print 'Repository already contains the ' +args[1]+ ' release of ' +args[0]
    print 'Please choose a different name and try again'
    sys.exit()

  if not bflag:
    print 'Releasing "' + args[0] + '" from trunk, at version "' + args[1] + '"'
  else:
    print 'Releasing "' + args[0] + '" from branch, "' + options.branch + '", at version "' + args[1] + '"'

  subversion.copy( os.path.join(prefix, srcDir), os.path.join(prefix, relDir, args[1]) )

  # Check for the existence of the correct directory tree on disk, into which
  # the release should be checked out. If the directory tree is not present, create it.

  baseStr = '/'
  prodDir = os.path.join( '/home/diamond', epicsVer, 'prod', diskDir, args[0] )
  for ss in prodDir.split('/'):
    baseStr = os.path.join( baseStr, ss )
    stat    = os.access(baseStr, os.F_OK)
    if not stat:
      os.mkdir(baseStr)

#  subversion.export(  os.path.join(prefix,relDir, args[1]),       os.path.join(baseStr,args[1]) )
  subversion.checkout(os.path.join(prefix,relDir, args[1]), os.path.join(baseStr,args[1]) )

  print 'Building release...'
  stat = os.chdir(os.path.join(baseStr,args[1]))
#  os.system('make')

if __name__ == "__main__":
  main()
