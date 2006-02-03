#!/usr/bin/env python2.4

# dls-vendor-import [-i] <path to import from> <name> <vendor version>
# Converted to Python by: Andy Foster

import os, pysvn, sys
from optparse import OptionParser


def pathcheck(client, path):
    try:
        junk = client.ls(path)
        ret  = 1
    except pysvn._pysvn.ClientError:
        ret  = 0
    return ret


def main():
    parser = OptionParser("usage: %prog [-i] <path to import from> <name> <vendor version>")
    parser.add_option("-i", "--ioc", action="store_true", dest="ioc",
                      help="Import a vendor IOC application")
    (options, args) = parser.parse_args()
    if len(args) != 3
      parser.error("Incorrect number of arguments")

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

    Check for existence of this module in release, vendor and trunk in the repository
    error = pathcheck( subversion, os.path.join(prefix,'release',source) )
    if error:
      print prefix+'/release/'+source+' already exists'
      sys.exit()
    else
      error = pathcheck( subversion, os.path.join(prefix,'vendor',source) )
      if error:
        print prefix+'/vendor/'+source+' already exists'
        sys.exit()
      else
        error = pathcheck( subversion, os.path.join(prefix,'trunk',source) )
        if error:
          print prefix+'/trunk/'+source+' already exists'
          sys.exit()

    print 'Importing vendor source from: '+args[0]

    subversion.import_( args[0], os.path.join(prefix,'vendor',source,'current'),
                        'Import of '+args[1]+' from pristine '+args[2]+' source',
                        True )

    print 'Tagging vendor source at version: '+args[2]

    subversion.copy( os.path.join(prefix, 'vendor', source, 'current'),
                     os.path.join(prefix, 'vendor', source, args[2] )

    print 'Copying vendor source to trunk'

    subversion.copy( os.path.join(prefix, 'vendor', source, 'current'),
                     os.path.join(prefix, 'trunk',  source )

    print 'Checking out trunk...'

    subversion.checkout( os.path.join(prefix, 'trunk', source), '.' )

    print 'Please now:'
    print '(1) Edit configure/RELEASE to put in correct paths'
    print '(2) Use make to check that it builds
    print '(3) Commit with the following comment:'
    print '"'+args[1]+': changed configure/RELEASE to reflect Diamond paths"'

if __name__ == "__main__":
    main()
