#!/usr/bin/env python2.4
#
# Author: Andy Foster
#

import os, shutil, pysvn, sys
from optparse import OptionParser

def pathcheck(client, path):
    try:
        junk = client.ls(path)
        ret  = 1
    except pysvn._pysvn.ClientError:
        ret  = 0
    return ret

def workingCopy(client):
    try:
      info = client.info('.')
      ret  = 1
    except pysvn._pysvn.ClientError:
      ret  = 0
    return ret


def main():
    parser = OptionParser("usage: %prog [options] module-name")
    parser.add_option("-i", "--ioc", action="store_true", dest="ioc",
                      help="start new ioc application, not support module")
    (options, args) = parser.parse_args()
    if len(args) != 1:
      parser.error("incorrect number of arguments")

    # Check the SVN_ROOT environment variable
    try:
        prefix = os.environ['SVN_ROOT']+'/diamond'
    except KeyError:
        print "SVN_ROOT environment variable must be set"
        sys.exit()

    source = 'support/'+args[0]
    if options.ioc:
        source = 'ioc/'+args[0]
 
    # Create an object to interact with subversion
    subversion = pysvn.Client()

    # Check for existence of this module in release, vendor and trunk in the repository
    error = pathcheck( subversion, os.path.join(prefix,'release',source) )
    if error:
      print prefix+'/release/'+source+' already exists'
      sys.exit()
    else:
      error = pathcheck( subversion, os.path.join(prefix,'vendor',source) )
      if error:
        print prefix+'/vendor/'+source+' already exists'
        sys.exit()
      else:
        error = pathcheck( subversion, os.path.join(prefix,'trunk',source) )
        if error:
          print prefix+'/trunk/'+source+' already exists'
          sys.exit()

    error = workingCopy( subversion )
    if error:
      print 'Currently in a working copy under revision control, please move'
      print 'to another directory and try again'
      sys.exit()

    if os.path.isdir(args[0]):
      print args[0] + ' already exists in this directory.'
      print 'Please choose another name or move elsewhere'
      sys.exit()

    print 'Making clean directory structure for ' + args[0]

    os.mkdir(args[0])
    os.chdir(args[0])
    command = 'makeBaseApp.pl -t diamond ' + args[0]
    os.system(command)

    if options.ioc:
      command = 'makeBaseApp.pl -i -t diamond ' + args[0]
      os.system(command)

    os.chdir('..')
    print 'Import ' +args[0]+ ' into ' +os.path.join(prefix,'trunk',source)
    subversion.import_( args[0], os.path.join(prefix,'trunk',source), 
                        'Initial structure of new ' +args[0], recurse=True )
    shutil.rmtree(args[0])
    print 'checkout ' +args[0]+ ' from ' +os.path.join(prefix,'trunk',source)
    subversion.checkout(os.path.join(prefix, 'trunk', source), args[0])

    print
    print 'Please now edit "' +args[0]+ '/configure/RELEASE" to put in correct'
    print 'paths for dependencies.'
    print 'You can also add dependencies to "' +args[0]+ '/' +args[0]+ 'App/src/Makefile"'
    print 'and "' +args[0]+ '/' +args[0]+ 'App/Db/Makefile" if appropriate.'

if __name__ == "__main__":
  main()
