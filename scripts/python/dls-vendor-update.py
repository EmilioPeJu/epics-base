#!/usr/bin/env python2.4

"""
dls-vendor-update [-i] <source> <name> <old> <new>
Converted to Python and IOC option added by: Andy Foster

This script updates a vendor support module or IOC application
called <name>, from <old> version to <new> version, using the
code from <source>.

The script allows a history to be maintained between versions of
the repository when files are added, deleted or renamed between
vendor imports.

The -i flag specifies that we are updating an IOC application.
For an IOC application, <source> is expected to be of the form:
<beamLine/Technical Area> e.g. BL18I/MO
"""

import os, shutil, pysvn, sys
from   optparse import OptionParser
from   dlsPyLib import *

def main():
  parser = OptionParser("usage: %prog [-i] <source> <name> <old> <new>")
  parser.add_option("-i", "--ioc", action="store_true", dest="ioc",
                    help="Update a vendor IOC application to a new version")
  (options, args) = parser.parse_args()
  if len(args) != 4:
    parser.error("incorrect number of arguments")

  # Check the SVN_ROOT environment variable
  prefix = checkSVN_ROOT()
  if not prefix:
    sys.exit()

  if options.ioc:
    cols = args[0].split('/')
    if len(cols) > 1:
      BL_TO_UPDATE = 'ioc/' + cols[0]
      TA_TO_UPDATE = cols[1]
    else:
      print 'Missing Technical Area in source path'
      sys.exit()

    colsDest  = args[1].split('/')
    destName  = colsDest[0]
    source    = 'ioc/' + destName + '/' + TA_TO_UPDATE
    dirOnDisk = destName + '/' + TA_TO_UPDATE
  else:
    source    = 'support/' + args[1]
    dirOnDisk = args[1]

  # Create an object to interact with subversion
  subversion = pysvn.Client()

  # The directory tree we are importing from must not contain any
  # .svn directories, otherwise "dls-svn_load_dirs" will fail with
  # a non-obvious error.

  found = 0
  for path, subdirs, files in os.walk(args[0]):
    for tt in subdirs:
      if tt == '.svn': 
        found = 1
        break

  if found == 1:
    print 'An .svn directory has been found in "' + args[0] + '"'
    print 'cannot update from here!'
    sys.exit()

  # Check for existence of this module in vendor and trunk in the repository

  exists = pathcheck( subversion, os.path.join(prefix,'vendor',source) )
  if not exists:
    print os.path.join(prefix,'vendor',source) + ' does not exist'
    sys.exit()
  else:
    exists = pathcheck( subversion, os.path.join(prefix,'trunk',source) )
    if not exists:
      print os.path.join(prefix,'trunk',source) + ' does not exist'
      sys.exit()

  exists = pathcheck( subversion, os.path.join(prefix,'vendor',source, args[2]) )
  if not exists:
    print 'Repository does not contain version: '+args[2]+' of module: '+args[1]
    sys.exit()

  exists = pathcheck( subversion, os.path.join(prefix,'vendor',source, args[3]) )
  if exists:
    print 'Repository already contains version: '+args[3]+' of module: '+args[1]
    sys.exit()

  diffs = subversion.diff( '/tmp/svn',
                           os.path.join(prefix,'vendor',source,'current'),
                           pysvn.Revision( pysvn.opt_revision_kind.head ),
                           os.path.join(prefix,'vendor',source,args[2]),
                           pysvn.Revision( pysvn.opt_revision_kind.head ),
                           True, True, True )

  if diffs:
    print 'Vendor "current" of: ' + source +' is not at revision: ' + args[2]
    sys.exit()

  print 'Importing: '+args[1]+' from: '+args[0]
  print 'to update from version: '+args[2]+' to version: '+args[3]

  command1 = 'dls-svn_load_dirs -t ' + args[3]
  command2 = os.path.join(prefix,'vendor',source)+' current ' + args[0]
  command  = command1 + ' ' + command2 + ' >& /dev/null'

  print ''
  print 'Running command: '
  print command
  print ''

  os.system(command)

  print
  print 'You probably now want to merge this update into the trunk.'
  print 'Do this by issuing the following commands:'
  print
  print 'svn checkout ' + os.path.join(prefix, 'trunk', source) + ' ' + dirOnDisk
  print
  print 'svn merge ' + os.path.join(prefix, 'vendor', source, args[2]) + ' ' + os.path.join(prefix, 'vendor', source, args[3]) + ' ' + dirOnDisk
  print

if __name__ == "__main__":
  main()
