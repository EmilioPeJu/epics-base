#!/bin/env python

import os, sys
from optparse import OptionParser

def main():
	parser = OptionParser("usage: %prog [options] input-file")
	parser.add_option("-f", "--file", dest="filename", metavar="FILE", help="The substitutions output filename (default is <input-file>.substitutions)")
	(options, args) = parser.parse_args()
	if len(args) != 1:
		parser.error("incorrect number of arguments")
	
	global subst_file
	csv_file = args[0]
	if options.filename:
		subst_file = options.filename
	else:
		subst_file = csv_file.replace('csv','substitutions')

	# reformat csv files and cat them into a substitution file
	os.system(r'''cat %s | dos2unix | sed -e s/\!file[\ ]*,/file\ / | sed -e s/\!\{[\ ]*,[\ ]*/{\\npattern\ {\ / | sed -e s/\{[\ ]*,[\ ]*/\\t\{\ / | sed -e s/\,[\ ]*\}/}/ | sed -e s/\!endfile/\}/ | sed -e s/,,[,]*$// | sed -e s/\"\#/\#/ | sed -e s/\"$// > %s'''% (csv_file,subst_file))
	input = open(subst_file,'r')
	lines = input.readlines()
	input.close()
	i = 0
	while i<len(lines):
		lines[i]=lines[i].replace('"""','"')	
		i+=1
	output = open(subst_file,'w')
	output.writelines(lines)
	output.close()
	print ('Exported %s to %s' % (csv_file,subst_file))


if __name__ == "__main__":
    main()
