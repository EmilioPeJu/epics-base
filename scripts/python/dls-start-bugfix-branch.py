#!/usr/bin/env python2.4

"""
dls-start-bugfix-branch [-i] <name> <release> <branch>
Converted to Python and IOC option added by: Andy Foster

This script is used to start a new bug fix branch for either
a support module or IOC application, in the repository.
The script creates a branch called <branch>, from release <release>,
of support module or IOC application, <name>.
A bug fix branch is started after a release has been made and we
need to patch that release.

The -i flag specifies that we are creating an IOC application
bug fix branch.
"""

import os, pysvn, sys
from   optparse import OptionParser
from   dlsPyLib import *

def main():
  parser = OptionParser("usage: %prog [-i] <name> <release name> <branch name>")
  parser.add_option("-i", "--ioc", action="store_true", dest="ioc",
                    help="Start a branch from release for an IOC")
  (options, args) = parser.parse_args()
  if len(args) != 3:
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

  log_message = ''

  def get_log_message():
    return True, log_message

  subversion.callback_get_log_message = get_log_message

  # Check for existence of this module in the release area of the repository
  exists = pathcheck( subversion, os.path.join(prefix,'release',source) )
  if not exists:
    print os.path.join(prefix,'release',source) + ' does not exist'
    sys.exit()

  # Check for existence of this particular release of this module in the repository
  exists = pathcheck( subversion, os.path.join(prefix,'release',source,args[1]) )
  if not exists:
    print os.path.join(prefix,'release',source,args[1]) + ' does not exist'
    sys.exit()

  where = args[2].find(args[1])
  if where == -1:
    branchName = args[2] + args[1]
  else:
    branchName = args[2]

  if os.path.isdir(branchName):
    print 'A directory called "' + branchName + '" already exists in this directory.'
    print 'Please choose another name or move elsewhere'
    sys.exit()

  # Check for existence of branches/<name> directory in the repository
  exists = pathcheck( subversion, os.path.join(prefix,'branches',source) )
  if not exists:
    print 'Creating ' +args[0]+ ' branches area'
    subversion.mkdir(os.path.join(prefix,'branches',source),
                     '"Created " +args[0]+ " branches area"')

  # Check for existence of branches/<name>/<branch name> in the repository
  exists = pathcheck( subversion, os.path.join(prefix,'branches',source,branchName) )
  if exists:
    print 'The branch "' + branchName + '" already exists in the repository'
    sys.exit()

  print 'Creating bugfix branch from "' + args[1] + '" release of "' + args[0] + '" called "' + branchName + '"'
  subversion.copy( os.path.join(prefix, 'release', source, args[1]),
                   os.path.join(prefix, 'branches', source, branchName) )

  print 'Checking out working directory...'
  subversion.checkout( os.path.join(prefix, 'branches', source, branchName), branchName )

  print
  print 'Created a working directory from this new branch: ' + branchName

if __name__ == "__main__":
  main()
