#!/bin/env python

import os, sys
from optparse import OptionParser
from dlsxmlexcelparser import *
from dls_generate_Db_sim import *
from dls_generate_Db_info import *
from dls_generate_Db_subst import *
from dlsxmlparserfunctions import table_handler

####################
# hardcoded fields #
####################
# suffix for temp, flow, overview input and output suffixes
out_dir="."
sim_suffix=".sim.substitutions.autogen"
info_suffix=".0info.substitutions.autogen"
subst_suffix=".substitutions.autogen"
mo_table_name="!GUI-MO"

##############
# initialise #
##############
ioc = ""
bug = False

# print text if bug-fixing flag is set
def bugprint(text):
	global bug
	if bug:
		print text

# print error text
def errorprint(text):
	print>>sys.stderr, text
	sys.exit(1)

# import xml file and call relevant script
def main():
	global out_dir
	global sim_suffix
	global info_suffix
	global subst_suffix
	global mo_table_name
	global ioc
	global bug

	parser = OptionParser("usage: %prog [options] <xml-file>")
	parser.add_option("-s", action="store_true", dest="sim", help="Exports a simulation of temps, currents and flows to <ioc>"+sim_suffix)
	parser.add_option("-n", action="store_true", dest="info", help="Exports a substitution file containing all the info fields and alarm summary to <ioc>"+info_suffix)
	parser.add_option("-u", action="store_true", dest="subst", help="Exports a substitution file from all '!...' tables (except !GUI-xx) to <ioc>-<table_name>"+subst_suffix)
	parser.add_option("-i", "--ioc", dest="ioc", metavar="IOC", help="Filter output on IOC (if IOCfield contains <ioc> process row)")
	parser.add_option("-d", "--dir", dest="dir", metavar="DIR", help="The output directory (default is %s)"%out_dir)
	parser.add_option("-b", action="store_true", dest="bug", help="Turns on bug-fixing messages")

	# parse arguments
	(options, args) = parser.parse_args()
	if len(args) != 1:
		errorprint("Incorrect number of arguments. Type %prog -h for help")

	# parse xml file
	xml = args[0]
	data = ExcelHandler()
	parse(xml, data)		

	# set the output directory
	if options.dir:
		out_dir = options.dir

	# set the ioc filter
	bug = options.bug
	if options.ioc:
		ioc = options.ioc
		bugprint("Outputting results for ioc: "+ioc)

	# create a row_handler object containing the defaults
	Table_handler = table_handler(out_dir,ioc,bug)
	
	# process each sheet in the xml file
	print """-----------------------------------------------------------------------------
Creating Db files from: %s
-----------------------------------------------------------------------------""" % xml
	for name,table in data.tables:
		if name==mo_table_name:
			mo_table = table
	for name,table in data.tables:
		bugprint("Processing sheet: "+name)
		if name.find(" ")>-1:
			errorprint("Sheet names must not contain spaces: %s" % name)
		if name==mo_table_name:
			if options.sim:
				bugprint("Creating simulation substitution file")
				gen_Db_sim(table,Table_handler,ioc+sim_suffix)
			if options.info:
				bugprint("Creating info substitution file")
				gen_Db_info(table,Table_handler,ioc+info_suffix)	
		elif name[:1]=="!" and not name[:4]=="!GUI":	
			if options.subst:
				bugprint("Creating substitution file "+name)
				gen_Db_subst(table,mo_table,Table_handler,ioc+'.'+name[1:]+subst_suffix)
	
	# close output files
	Table_handler.closef()

if __name__ == "__main__":
    main()
