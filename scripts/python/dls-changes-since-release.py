#!/usr/bin/env python2.4

"""
dls-checkout-module.py
Author: Tom Cobb

This script is used to check for changes in a support or ioc module since its last release"""

import sys, os, pysvn
from optparse import OptionParser
from dlsPyLib import *

def sort_paths(files):
	order = []
	# order = (1st,2nd,3rd,4th,path)
	# e.g. ./4-5dls1-3 = (4,5,1,3,./4-5dls1-3)
	for path in files:
		try:
			version = path.split("/")[-1]
			split = [x.split("-") for x in version.split("dls")]
			if len(split)>1:
				splitcd = split[1]
			else:
				splitcd = [0,0]
			splitab = split[0]
			if len(splitab)>1:
				b = int(splitab[1])
			else:
				b = 0
			a = int(splitab[0])
			if len(splitcd)>1:
				d = int(splitcd[1])
			else:
				d = 0
			c = int(splitcd[0])
			order.append((a,b,c,d,path))
		except:
			order.append((0,0,0,0,path))
	order.sort()
	order.reverse()
	return [x[4] for x in order]

def main():
	parser = OptionParser("usage: %prog [options] <MODULE_NAME>")
	parser.add_option("-i", "--ioc", action="store_true", dest="ioc", help="Check an IOC application")
	(options, args) = parser.parse_args()
	if len(args)!=1:
		parser.error("incorrect number of arguments")

	# Check the SVN_ROOT environment variable
	prefix = checkSVN_ROOT()
	if not prefix:
		sys.exit()

	if options.ioc:
		cols = args[0].split('/')
		if len(cols) > 1:
			source = 'ioc/' + args[0]
		else:
			print 'Missing Technical Area under Beamline'
			sys.exit()
	else:
		source = 'support/' + args[0]

	# Create an object to interact with subversion
	subversion = pysvn.Client()

	# Check for existence of this module in various places in the repository
	exists = pathcheck( subversion, os.path.join(prefix,'trunk',source) )
	if not exists:
		print 'Repository does not contain the "'+source+'" module'
		sys.exit()
	last_trunk_rev = subversion.info2(os.path.join(prefix,"trunk",source),recurse=False)[0][1]["last_changed_rev"].number

	exists = pathcheck( subversion, os.path.join(prefix,'release',source) )
	if not exists:
		print 'Repository does not contain a release of the "'+source+'" module'
		sys.exit()
	last_release_rev = subversion.info2(os.path.join(prefix,"release",source),recurse=False)[0][1]["last_changed_rev"].number


	last_release_num = sort_paths([x["name"] for x in subversion.ls(os.path.join(prefix,"release",source))])[0].split("/")[-1]
	
	if last_trunk_rev > last_release_rev:
		print args[0]+" ("+last_release_num+"): Outstanding changes. Release = r"+str(last_release_rev)+", Trunk = r"+str(last_trunk_rev) 
	else:
		print args[0]+" ("+last_release_num+"): Up to date." 

if __name__ == "__main__":
	main()
