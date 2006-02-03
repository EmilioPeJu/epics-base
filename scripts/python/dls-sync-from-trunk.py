#!/usr/bin/env python2.4

# dls-sync-from-trunk [-i]
# Converted to Python by: Andy Foster

import os, pysvn, sys, shutil
from optparse import OptionParser


def workingCopy(client):
    try:
      entry = client.info('.')
      ret   = entry
    except pysvn._pysvn.ClientError:
      ret   = 0
    return ret


def main():
    parser = OptionParser("usage: %prog [-i]")
    parser.add_option("-i", "--ioc", action="store_true", dest="ioc",
                      help="Synchronise working copy of a branch with the trunk")
    (options, args) = parser.parse_args()
    if len(args) != 0
      parser.error("There are no arguments to this script")

    # Check the SVN_ROOT environment variable
    try:
      prefix = os.environ['SVN_ROOT']+'/diamond'
    except KeyError:
      print "SVN_ROOT environment variable must be set"
      sys.exit()

    if options.ioc:
      source = 'ioc/'
    else:
      source = 'support/'

    # Create an object to interact with subversion
    subversion = pysvn.Client()

    # Check that we are currently in a working copy of a branch
    # Extract the module name and the branch name
    entry = workingCopy(subversion)
    if entry:
      line = entry.url
      if line.find('branches') >= 0:
        ll         = line.split('/')
        moduleName = ll[len(ll)-2]
        branchName = ll[len(ll)-1]
      else:
        parser.error('You must run this script in a working copy of a feature branch')
        sys.exit()
    else:
      parser.error('You must run this script in a working copy of a feature branch')
      sys.exit()

    prop_list = subversion.propget( 'dls:synced-from-trunk', 
                                    os.path.join(prefix,'branches',source,branchName), 
                                    pysvn.Revision(pysvn.opt_revision_kind.head), 
                                    False )
    if not prop_list:
      print 'The "dls:synced-from-trunk" property is not set for this branch'
      sys.exit()

    merge_from = prop_list[os.path.join(prefix,'branches',source,branchName)]
    if not merge_from:
      print 'Merge revision information not available'
      sys.exit()
    
    subversion.merge( os.path.join(prefix,'trunk',source,moduleName), merge_from,
                      os.path.join(prefix,'trunk',source,moduleName), HEAD,
                      '.', False, True )

    # Checkout the latest version of the module from the trunk to find out
    # the number of HEAD
    tempdir        = /tmp/svn
    subversion.checkout( os.path.join(prefix,'trunk',source,moduleName), tempdir )
    entry          = subversion.info(tempdir)
    trunk_revision = entry.revision.number
    shutil.rmtree(tempdir)

    # Update the "dls:synced-from-trunk" property which tells us how far up the trunk
    # we have merged into this branch.

    subversion.propset( 'dls:synced-from-trunk', trunk_revision, '.',
                        pysvn.Revision(pysvn.opt_revision_kind.working), False )
