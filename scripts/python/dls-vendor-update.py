#!/usr/bin/env python2.4

# dls-vendor-update [-i] <source directory> <name> <old version no> <new version no>
# Converted to Python by: Andy Foster

import os, shutil, pysvn, sys
from optparse import OptionParser


def pathcheck(client, path):
    try:
        junk = client.ls(path)
        ret  = 1
    except pysvn._pysvn.ClientError:
        ret  = 0
    return ret


def main():
    parser = OptionParser(
        "usage: %prog [-i] <source directory> <name> <old version no> <new version no>"
                         )
    parser.add_option("-i", "--ioc", action="store_true", dest="ioc",
                      help="Update a vendor IOC/support module to a new version")
    (options, args) = parser.parse_args()
    if len(args) != 4:
      parser.error("incorrect number of arguments")

    # Check the SVN_ROOT environment variable
    try:
      prefix = os.environ['SVN_ROOT']+'/diamond'
    except KeyError:
      print "SVN_ROOT environment variable must be set"
      sys.exit()

    if options.ioc:
      source = 'ioc/'+args[1]
    else:
      source = 'support/'+args[1]

    # Create an object to interact with subversion
    subversion = pysvn.Client()

    # Check for existence of this module in vendor and trunk in the repository
    exists = pathcheck( subversion, os.path.join(prefix,'vendor',source) )
    if not exists:
      print prefix+'/vendor/'+source+' does not exist'
      sys.exit()
    else:
      exists = pathcheck( subversion, os.path.join(prefix,'trunk',source) )
      if not exists:
        print prefix+'/trunk/'+source+' does not exist'
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
      print 'Vendor "current" of: '+args[1]+' is not at revision: '+args[2]
      sys.exit()

    print 'Importing: '+args[1]+' from: '+args[0]
    print 'to update from version: '+args[2]+' to version: '+args[3]

    command1 = 'dls-svn_load_dirs -t '+args[3]
    command2 = os.path.join(prefix,'vendor',source)+' current '+args[0]
    command  = command1 + ' ' + command2
    os.system(command)

    print
    print 'You probably now want to merge this update into the trunk.'
    print 'Do this by checking out the trunk, and running:'
    print 'svn merge '+os.path.join(prefix,'vendor',source,args[2])+' \\'
    print '          '+os.path.join(prefix,'vendor',source,args[2],arg[3])+' \\'
    print '          <working dir>'

if __name__ == "__main__":
  main()
