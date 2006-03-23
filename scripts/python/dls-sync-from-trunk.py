#!/usr/bin/env python2.4

"""
dls-sync-from-trunk.py
Converted to Python by: Andy Foster
 
This script will syncronise a local working copy of a feature
branch, for a support module or IOC application, with the latest
version on the trunk. Note that the current directory must be a
local working copy of the featuer branch. The first time this
script is run, it will update the local working copy with the
changes committed to trunk since the feature branch was created.
After this, it will update the local working copy with the changes
committed to trunk since the last time this script was run.

No changes are made to the repository as a result of running this
script. The only changes will be to files in the local working
copy of the branch. All changes in the local working copy should
be checked and any conflicts resolved. These changes then need to
be committed back to the feature branch.

The script takes no arguments!

"""

import os, shutil, pysvn, sys
from   dlsPyLib import *

def main():

  # Check the SVN_ROOT environment variable
  prefix = checkSVN_ROOT()
  if not prefix:
    sys.exit()

  # Create an object to interact with subversion
  subversion = pysvn.Client()

  # Check that we are currently in a working copy of a branch
  # Extract the module name and the branch name
  isWC = workingCopy(subversion)
  if isWC:
    line = isWC.url
    if line.find('branches') >= 0:
      L           = line.split('/')
      L[len(L)-1] = ''
      K           = '/'.join(L)
    else:
      print 'You must run this script in a working copy of a feature branch'
      sys.exit()
  else:
    print 'You must run this script in a working copy of a feature branch'
    sys.exit()

  prop_list = subversion.propget( 'dls:synced-from-trunk', '.',
                                   pysvn.Revision(pysvn.opt_revision_kind.working), False )
  if not prop_list:
    print 'The "dls:synced-from-trunk" property is not set for this branch'
    sys.exit()

  merge_from = prop_list['']
  if not merge_from:
    print 'Merge revision information not available'
    sys.exit()

  print 'merging from version = ' + merge_from + ' to HEAD'

  subversion.merge( K.replace('branches','trunk'),
                    pysvn.Revision( pysvn.opt_revision_kind.number, merge_from ),
                    K.replace('branches','trunk'),
                    pysvn.Revision( pysvn.opt_revision_kind.head ), 
                    '.', True, True )

  # Checkout the latest version of the module from the trunk to find out
  # the new number of HEAD

  tempdir        = '/tmp/svn'
  subversion.checkout( K.replace('branches','trunk'), tempdir )
  entry          = subversion.info(tempdir)
  trunk_revision = entry.revision.number
  shutil.rmtree(tempdir)

  # Update the "dls:synced-from-trunk" property which tells us how far up the trunk
  # we have merged into this branch.

  print 'Set new HEAD version number in branch = ', trunk_revision

  subversion.propset( 'dls:synced-from-trunk', str(trunk_revision), '.',
                      pysvn.Revision(pysvn.opt_revision_kind.working), False )
  print 'Finished...'

if __name__ == "__main__":
  main()
