#!/usr/bin/env python2.4

"""
dls-start-new-module.py [-i] <name>
Author: Andy Foster

This script is used to start a new support module or
IOC application. It checks to see if <name> exists in
the repository. If it does not exist, this script runs
"makeBaseApp", using the "dls" template, to create the
support module or IOC application in the current directory.
For IOC applications, the "opi" directory is removed.
The resulting directory structure is then imported into
the repository, the users local copy is deleted and the
new support module or IOC application is checked out of
the repository, leaving the user with a working copy.

The -i flag is used to specify an IOC application.
For an IOC application <name> is expected to be of
the form "Beamline/Technical Area/IOC number"
i.e. BL02I/VA/03. The IOC number can be omitted, in
which case, it defaults to "01".
"""

import os, shutil, pysvn, sys
from   optparse import OptionParser
from   dlsPyLib import *

def main():
  parser = OptionParser("usage: %prog [-i] <name>")
  parser.add_option("-i", "--ioc", action="store_true", dest="ioc",
                    help="start new IOC application")
  (options, args) = parser.parse_args()
  if len(args) != 1:
    parser.error("incorrect number of arguments")

  # Check the SVN_ROOT environment variable
  prefix = checkSVN_ROOT()
  if not prefix:
    sys.exit()

  cols = args[0].split('/')

  if options.ioc:
    if len(cols) < 2 or cols[1] == '':
      print "Technical Area must be non-blank"
      sys.exit()
    beamLine      = cols[0]
    technicalArea = cols[1]
    if len(cols) == 3 and cols[2] != '':
      iocNumber = cols[2]
    else:
      iocNumber = '01'

    svnBlToCreate  = 'ioc/' + beamLine
    svnAppToCreate = svnBlToCreate + '/' + technicalArea
    diskDir        = beamLine + '/' + technicalArea
    appName        = beamLine + '-' + technicalArea + '-' + 'IOC' + '-' + iocNumber
  else:
    svnAppToCreate = 'support/' + cols[0]
    diskDir        = cols[0]
    appName        = cols[0]

  # Create an object to interact with subversion
  subversion = pysvn.Client()

  # Check for existence of this module in release, vendor and trunk in the repository
  exists = pathcheck( subversion, os.path.join(prefix,'release',svnAppToCreate) )
  if exists:
    print prefix + '/release/' + svnAppToCreate + ' already exists'
    sys.exit()
  else:
    exists = pathcheck( subversion, os.path.join(prefix,'vendor',svnAppToCreate) )
    if exists:
      print prefix + '/vendor/' + svnAppToCreate + ' already exists'
      sys.exit()
    else:
      exists = pathcheck( subversion, os.path.join(prefix,'trunk',svnAppToCreate) )
      if exists:
        print prefix + '/trunk/' + svnAppToCreate + ' already exists'
        sys.exit()

  error = workingCopy( subversion )
  if error:
    print 'Currently in a working copy under revision control, please move'
    print 'to another directory and try again'
    sys.exit()

  if os.path.isdir(diskDir):
    print diskDir + ' already exists in this directory.'
    print 'Please choose another name or move elsewhere'
    sys.exit()

  print 'Making clean directory structure for ' + diskDir

  currentDir = os.getcwd()
  baseStr    = './'
  for ss in diskDir.split('/'):
    baseStr = os.path.join( baseStr, ss )
    stat    = os.access(baseStr, os.F_OK)
    if not stat:
      os.mkdir(baseStr)

  os.chdir(diskDir)

  command = 'makeBaseApp.pl -t dls ' + appName
  os.system(command)

  if options.ioc:
    command = 'makeBaseApp.pl -i -t dls ' + appName
    os.system(command)
    # IOC applications do not need the "opi" directory
    # Choose the appropriate Makefile
    os.chdir( appName + 'App' )
    shutil.rmtree('opi')

  os.chdir(currentDir)

  print 'Import ' + diskDir + ' into ' + os.path.join(prefix,'trunk',svnAppToCreate)

  subversion.import_( diskDir, os.path.join(prefix,'trunk',svnAppToCreate),
                        'Initial structure of new ' + diskDir, recurse=True )

  shutil.rmtree(diskDir)

  print 'checkout ' + diskDir + ' from ' + os.path.join(prefix,'trunk',svnAppToCreate)

  subversion.checkout(os.path.join(prefix, 'trunk', svnAppToCreate), diskDir)

  print
  print 'Please now edit "' + diskDir + '/configure/RELEASE" to put in correct paths for dependencies.'
  print 'You can also add dependencies to "' + diskDir + '/' + appName + 'App/src/Makefile"'
  print 'and "' + diskDir + '/' + appName + 'App/Db/Makefile" if appropriate.'


if __name__ == "__main__":
  main()
