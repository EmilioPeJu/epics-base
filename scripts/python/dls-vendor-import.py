#!/usr/bin/env python2.4

"""
dls-vendor-import [-i] <source> <name> <version>
Converted to Python and IOC option added by: Andy Foster

This script is used to import, to the repository, a support module
or IOC application given to Diamond by a vendor. The script imports
the code from <source> to:

"vendor/support or ioc/<name>/current"

in the repository. It creates a tag in the repository called <version>.
It also copies the code to the trunk and then checks the code out
into the current directory.

The -i flag specifies that we are importing an IOC application.
For an IOC application, <source> is expected to be of the form:
<beamLine/Technical Area> e.g. BL18I/MO
"""

import os, pysvn, sys
from   optparse import OptionParser
from   dlsPyLib import *

def main():
  parser = OptionParser("usage: %prog [-i] <source> <name> <version>")
  parser.add_option("-i", "--ioc", action="store_true", dest="ioc",
                    help="Import a vendor IOC application")
  (options, args) = parser.parse_args()
  if len(args) != 3:
    parser.error("Incorrect number of arguments")

  # Check the SVN_ROOT environment variable
  prefix = checkSVN_ROOT()
  if not prefix:
    sys.exit()

  if options.ioc:
    cols = args[0].split('/')
    if len(cols) > 1:
      BL_TO_IMPORT = 'ioc/' + cols[0]
      TA_TO_IMPORT = cols[1]
    else:
      print 'Missing Technical Area in source path'
      sys.exit()

    colsDest  = args[1].split('/')
    destName  = colsDest[0]
    source    = 'ioc/' + destName + '/' + TA_TO_IMPORT
    dirOnDisk = destName + '/' + TA_TO_IMPORT
  else:
    source    = 'support/' + args[1]
    dirOnDisk = args[1]

  # Create an object to interact with subversion
  subversion = pysvn.Client()

  log_message = 'Importing vendor source from: '+args[0]

  def get_log_message():
    return True, log_message

  subversion.callback_get_log_message = get_log_message

  # Check for existence of this module in release, vendor and trunk in the repository

  exists = pathcheck( subversion, os.path.join(prefix,'release',source) )
  if exists:
    print os.path.join(prefix,'release',source) + ' already exists'
    sys.exit()
  else:
    exists = pathcheck( subversion, os.path.join(prefix,'vendor',source) )
    if exists:
      print os.path.join(prefix,'vendor',source) + ' already exists'
      sys.exit()
    else:
      exists = pathcheck( subversion, os.path.join(prefix,'trunk',source) )
      if exists:
        print os.path.join(prefix,'trunk',source) + ' already exists'
        sys.exit()

  if os.path.isdir(dirOnDisk):
    print 'Cannot checkout to: "' + dirOnDisk + '"' + ' as this directory already exists'
    sys.exit()

  print 'Importing vendor source from: '+args[0]

  subversion.import_( args[0], os.path.join(prefix,'vendor',source,'current'),
                      'Import of '+dirOnDisk+' from pristine '+args[2]+' source',
                      True )

  print 'Tagging vendor source at version: '+args[2]

  subversion.copy( os.path.join(prefix, 'vendor', source, 'current'),
                   os.path.join(prefix, 'vendor', source,  args[2] ) )

  if options.ioc:
    exists = pathcheck( subversion, os.path.join(prefix,'trunk','ioc',destName) )
    if not exists:
      subversion.mkdir( os.path.join(prefix, 'trunk', 'ioc', destName),
                        '"Created ioc/" + destName + " trunk area"' )

  print 'Copying vendor source to trunk'
  print
  print os.path.join(prefix, 'vendor', source, 'current')
  print 'to'
  print os.path.join(prefix, 'trunk', source)
  print

  subversion.copy( os.path.join(prefix, 'vendor', source, 'current'),
                   os.path.join(prefix, 'trunk', source) )

  print 'Checking out trunk...' + os.path.join(prefix, 'trunk', source) + ' to ' + dirOnDisk

  subversion.checkout( os.path.join(prefix, 'trunk', source), dirOnDisk )

  print ''
  print 'Please now:'
  print '(1) Edit configure/RELEASE to put in correct paths'
  print '(2) Use make to check that it builds'
  print '(3) Commit with the following comment:'
  print '"'+dirOnDisk+': changed configure/RELEASE to reflect Diamond paths"'
  print ''

if __name__ == "__main__":
  main()
