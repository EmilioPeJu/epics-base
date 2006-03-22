#!/usr/bin/env python2.4

"""
dls-start-feature-branch [-i] <name> <branch>
Converted to Python and IOC option added by: Andy Foster

This script is used to start a new feature branch in the
repository. The script starts a new feature branch, called
<branch>, in the repository, for the support module or
IOC application called <name>.

This script should be used to create all branches which are
not for bug fixes to existing releases.

The -i flag is used to specify that we want to start a branch
of an IOC application.
"""

import os, pysvn, shutil, sys
from   optparse import OptionParser
from   dlsPyLib import *

def main():
  parser = OptionParser("usage: %prog [-i] <name> <branch name>")
  parser.add_option("-i", "--ioc", action="store_true", dest="ioc",
                    help="Start a feature branch from the trunk for an IOC")
  (options, args) = parser.parse_args()
  if len(args) != 2:
    parser.error("incorrect number of arguments")

  # Check the SVN_ROOT environment variable
  prefix = checkSVN_ROOT()
  if not prefix:
    sys.exit()

  if options.ioc:
    source = 'ioc/'+args[0]
    # Allow for individual technical areas to be specified
    if ("/" in args[0] ):
      n = args[0].rfind("/")
      source   = 'ioc'
      blName   = args[0][0:n]
      techArea = args[0][n+1:]
    else:
      n = -1
  else:
    source = 'support/'+args[0]
    n = -1

  # Create an object to interact with subversion
  subversion = pysvn.Client()

  log_message = ''

  def get_log_message():
    return True, log_message

  subversion.callback_get_log_message = get_log_message

  # Check for existence of this module in trunk in the repository
  exists = pathcheck( subversion, os.path.join(prefix,'trunk',source) )
  if not exists:
    print prefix+'/trunk/'+source+' does not exist'
    sys.exit()

  if os.path.isdir(args[1]):
    print args[1] + ' already exists in this directory.'
    print 'Please choose another name or move elsewhere'
    sys.exit()

  # Check for existence of branches/<ioc or support>/<beamline>/<technical area> 
  # directory tree in the repository
  if n != -1:
    exists = pathcheck( subversion, os.path.join(prefix,'branches',source,blName) )
    if not exists:
      print 'Creating ' +blName+ ' branches area'
      subversion.mkdir(os.path.join(prefix,'branches',source,blName),
                       '"Created " +blName+ " branches area"')
    exists = pathcheck( subversion, os.path.join(prefix,'branches',source,blName,techArea) )
    if not exists:
      print 'Creating ' +techArea+ ' branches area'
      subversion.mkdir(os.path.join(prefix,'branches',source,blName,techArea),
                       '"Created " +techArea+ " branches area"')
    source = 'ioc' + '/' + blName +  '/' + techArea

  # Check for existence of branches/<name>/<branch name> in the repository
  exists = pathcheck( subversion, os.path.join(prefix,'branches', source, args[1]) )
  if not exists:
    print 'Creating branch of ' +args[0]+ ' called ' +args[1]
    subversion.copy( os.path.join(prefix, 'trunk', source),
                     os.path.join(prefix, 'branches', source, args[1]) )
  else:
    print 'A branch called "' +args[1]+ '" already exists in the repository'
    print 'Please choose a different name and try again'
    sys.exit()

  tempdir = '/tmp/svn'
  subversion.checkout( os.path.join(prefix, 'branches', source, args[1]), tempdir )

  entry = subversion.info(tempdir)

  # Find the revision number from "info" and set the property "dls:synced-from-trunk"
  # to this value. This property tells us how far up the trunk we have merged into
  # this branch.

  print 'Setting "dls:synced-from-trunk" property for this branch'
  subversion.propset( 'dls:synced-from-trunk', str(entry.revision.number),
                      tempdir, pysvn.Revision(pysvn.opt_revision_kind.working), False )

  mess = args[0]+ '/' +args[1]+ ': Setting synced-from-trunk property'
  subversion.checkin( tempdir, mess, True )
  shutil.rmtree(tempdir)

  print

  # Is the current directory a working SVN directory?
  isWC = workingCopy(subversion)
  if isWC:
    if isWC.url == os.path.join(prefix,'trunk',source):
      status_list = subversion.status( '.', True, True, True, True )
      modified    = 0
      for x in status_list:
        if str(x.repos_text_status) == 'modified':
          modified = 1
          print 'The file "' +x.path+ '" has been modified in the trunk,'
          print 'therefore cannot switch this working SVN directory to the new branch'
          print
          print 'To create a working directory from the new branch'
          print 'change directories and run:'
          print 'svn checkout '+os.path.join(prefix,'branches',source,args[1])

      if not modified:
        print 'This is an SVN working directory for: "' +os.path.join(prefix,'trunk',source)+ '"'
        ans = raw_input('Do you want to switch this working directory onto the new branch? ')
        if( ans == 'y' or ans == 'Y' or ans == 'yes' or ans == 'Yes' ):
          print 'Switching this working directory to the new branch ' +args[1]
          subversion.switch( '.', os.path.join(prefix,'branches',source,args[1]),
                             True, pysvn.Revision( pysvn.opt_revision_kind.head ) )
        else:
          print 'NOT switching this working directory to the new branch'
          print
          print 'To create a working directory from this new branch,'
          print 'change directories and run:'
          print 'svn checkout '+os.path.join(prefix,'branches',source,args[1])
    else:
      print 'This is an SVN working directory but not for: "' +os.path.join(prefix,'trunk',source)+ '"'
      print
      print 'To create a working directory from this new branch,'
      print 'change directories and run:'
      print 'svn checkout '+os.path.join(prefix,'branches',source,args[1])
  else:
    print 'Checking out: ' + os.path.join(prefix,'branches',source,args[1]) + '...'
    subversion.checkout(os.path.join(prefix,'branches',source,args[1]), args[1])

if __name__ == "__main__":
  main()
