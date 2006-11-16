#!/bin/env python2.4

import os, subprocess, datetime, pysvn, sys
from   optparse import OptionParser
from   dlsPyLib import *

def main():
	
	# override epics_version if set
	try:
		epics_version = os.environ['DLS_EPICS_RELEASE']
	except KeyError:
		try:
			epics_version = os.environ['EPICS_RELEASE']
		except KeyError:
			epics_version = 'R3.14.8.2'

	# set default variables
	out_dir = "/dls_sw/work/etc/build/queue"
	build_script = "dls-build-release.py"
	test_dir = "/dls_sw/work/etc/build/test"

	# command line options
	parser = OptionParser("usage: %prog [options] <MODULE_NAME> <RELEASE#>")
	parser.add_option("-i", "--ioc", action="store_true", dest="ioc", help="Release an IOC application")
	parser.add_option("-b", "--branch", action="store", type="string", dest="branch", help="Release from a branch")
	parser.add_option("-e", "--epics_version", action="store", type="string", dest="epics_version", help="Force an epics version, default is "+epics_version)
	parser.add_option("-d", "--dir", action="store", type="string", dest="out_dir", help="Set the output directory, default is "+out_dir)
	(options, args) = parser.parse_args()
	if len(args)!=2:
		parser.error("incorrect number of arguments")

	# set variables
	module = args[0]
	release_number = args[1]
	if options.epics_version:
		epics_version = options.epics_version
	prod_dir = "/dls_sw/prod/"+epics_version
	if options.out_dir:
		out_dir = options.out_dir
		
	# print messages
	if not options.branch:
		print 'Releasing '+module+" "+release_number+" from trunk using epics "+epics_version+" ..."
	else:
		print 'Releasing '+module+" "+release_number+" from branch "+options.branch+" using epics "+epics_version+" ..."

	# setup svn				
	prefix = os.environ['SVN_ROOT']
	if not prefix:
		print >> sys.stderr, "***Error: SVN_ROOT is not set in the environment"
		sys.exit(1)
	subversion = pysvn.Client()	
	log_message = 'Releasing ' +module+ ' at version ' +release_number
	def get_log_message():
		return True, log_message
	subversion.callback_get_log_message = get_log_message	
	
	# setup svn directories
	if options.ioc:
		support = "ioc"
	else:
		support = "support"
	if options.branch:
		src_dir = os.path.join("diamond/trunk",support,module,options.branch)
	else:
		src_dir = os.path.join("diamond/trunk",support,module)
	rel_dir = os.path.join("diamond/release",support,module)
	
	
	# check for existence of directories	
  	if not pathcheck(subversion, os.path.join(prefix, src_dir)):
		print >> sys.stderr, "***Error: "+os.path.join(prefix, src_dir)+' does not exist in the repository.'
		sys.exit(1)
	if not pathcheck(subversion, os.path.join(prefix, rel_dir, release_number)):
		# check out to test area
		print "Doing test build, logging in "+ os.path.join(test_dir,module.split("/")[-1])+"/build.log ..."
		os.chdir(test_dir)
		os.system("rm -rf "+module.split("/")[-1])
		os.system("svn co "+os.path.join(prefix, src_dir)+" > /dev/null")
		os.chdir(module.split("/")[-1])
		os.system("mv configure/RELEASE configure/RELEASE.svn")
		os.system("""sed -e 's,^ *EPICS_BASE *=.*$,'"EPICS_BASE=/dls_sw/epics/"""+epics_version+"""/base," -e 's,^ *SUPPORT *=.*$,'"SUPPORT=/dls_sw/prod/"""+epics_version+"""/support," -e 's,^ *WORK *=.*$,'"#WORK=commented out to prevent prod modules depending on work modules," configure/RELEASE.svn > configure/RELEASE""")
		success = os.system("make &> build.log")
		if success == 0:
			os.chdir("..")
			os.system("rm -rf "+module.split("/")[-1])
			print "Test build successful, continuing with release"
		else:
			print >> sys.stderr, "***Error: module will not build. Please check module does not depend on work"
			sys.exit(1)
		# copy the source to the release directory
		dirs = rel_dir.split("/")
		for i in range(1,len(dirs)+1):
			# make sure all directories exist
			if not pathcheck(subversion, os.path.join(prefix,*dirs[:i])):
				subversion.mkdir(os.path.join(prefix,*dirs[:i]),'Created: '+os.path.join(prefix,*dirs[:i]))
		subversion.copy(os.path.join(prefix, src_dir), os.path.join(prefix, rel_dir, release_number))
		print "Created release in svn directory: "+os.path.join(prefix,rel_dir,release_number)
	elif os.path.isdir(os.path.join(prod_dir,support,module,release_number)):
		# if release exists in prod and prod then fail with an error
		print >> sys.stderr, "***Error: "+module+" "+release_number+" already exists in "+os.path.join(prod_dir,support)
		sys.exit(1)
		
	# find out which user wants to release
	user = os.getlogin()
	
	# generate the filename
	now = datetime.datetime.now()
	filename = now.strftime("%Y-%m-%d_%H-%M-%S_")+user+".sh"
	
	# check filename isn't already in use
	while os.path.isfile(filename):
		filename = filename.replace(".sh","_1.sh")

	# create the build request
	f = open(os.path.join(out_dir,filename),"w")
	f.write("""#!/usr/bin/env bash

# Script for building a diamond production module.

epics_version="""+epics_version+"""
svn_dir="""+rel_dir+"""
build_dir="""+os.path.join(prod_dir,support,module)+"""
version="""+release_number+r"""

# Set up environment
DLS_EPICS_RELEASE=$epics_version
DLS_DEV=1
source /dls_sw/etc/profile
SVN_ROOT=http://serv0002.cs.diamond.ac.uk/repos/controls

# Checkout module
mkdir -p $build_dir						|| ( echo Can not mkdir $build_dir; exit 1 )
cd $build_dir							  || ( echo Can not cd to $build_dir; exit 1 )
svn checkout $SVN_ROOT/$svn_dir/$version   || ( echo Can not check out  $svn_dir/$version; exit 1 )
cd $version

# Modify configure/RELEASE
mv configure/RELEASE configure/RELEASE.svn || ( echo Can not rename configure/RELEASE; exit 1 )
sed -e 's,^ *EPICS_BASE *=.*$,'"EPICS_BASE=/dls_sw/epics/$epics_version/base,"   \
	-e 's,^ *SUPPORT *=.*$,'"SUPPORT=/dls_sw/prod/$epics_version/support," \
	-e 's,^ *WORK *=.*$,'"#WORK=commented out to prevent prod modules depending on work modules," \
configure/RELEASE.svn > configure/RELEASE  || ( echo Can not edit configure/RELEASE; exit 1 )

# Build
timestamp=$(date +%Y%m%d-%H%M%S)
error_log=build_${timestamp}.err
build_log=build_${timestamp}.log
{
	make 4>&1 1>&3 2>&4 |
	tee $error_log
} >$build_log 3>&1
if [ $(stat -c%s $error_log) -ne 0 ] ; then
	cat $error_log | mail -s "Build Errors: """+module+' '+release_number+'" '+user+"""@rl.ac.uk
fi """)
	f.close()
	print "Build request file created: "+os.path.join(out_dir,filename)
	print module+" "+release_number+" will be exported and built by the build server shortly"
	
if __name__ == "__main__":
	main()
