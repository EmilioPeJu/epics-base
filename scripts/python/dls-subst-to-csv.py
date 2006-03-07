#!/bin/env python

import os, sys
from optparse import OptionParser

def handle_brackets(open_brackets):
	global i
	global lines
	j = len(open_brackets)
	# remove leading whitespace before macro names and check for "}"
	while i<len(lines):
		while ((not lines[i][j] == '\n') and (not j == 0)):
			j = lines[i].find(', ')+1
			while lines[i][j] == ' ':
				lines[i]=lines[i][:j]+lines[i][(j+1):]
		while ((not lines[i][j] == '\n') and (not j == 0)):
			j = lines[i].find(' ,')
			while lines[i][j] == ' ':
				lines[i]=lines[i][:j]+lines[i][(j+1):]
		lines[i]=lines[i].replace('"','"""')
		if not lines[i].find('}')==-1:
			break
		lines[i]=lines[i].replace('\n','')
		i+=1
	j = lines[i].find('}')-1
	while lines[i][j] == ' ':
		lines[i]=lines[i][:j]+lines[i][(j+1):]
		j-=1
	lines[i]=lines[i].replace('}',',}')
	i+=1

def handle_comment():
	global i
	global lines
	# skip comments and format comment pattern titles (anything starting with "##{")
	while(i<len(lines)and (lines[i].startswith('#') or lines[i]=='\n')):
		if lines[i].startswith('##{'):
			handle_brackets('##{')
		i+=1

def handle_file():
	global i
	global lines
	# substitute file for "!file," and look and delete the next "{"
	if not lines[i].startswith('file'):
		print ('Line %d: Expecting "file"' % (i+1))
		sys.exit()
	lines[i]=lines[i].replace('file','!file,')
	if lines[i].find("{")==-1:
		i+=1
		handle_comment()
		if not lines[i].startswith('{'):
			print ('Line %d: Expecting "{" after "file" keyword' % (i+1))
			sys.exit()
	lines[i]=lines[i].replace('{','')
	lines[i]=lines[i].replace('\n','')
	i+=1
	handle_comment()

def handle_pattern():
	global i
	global lines
	# substitute "!{" for "pattern" and look for and remove the next "{"
	handle_comment()
	if not lines[i].startswith('pattern'):
		print ('Line %d: Expecting "pattern"' % (i+1))
		sys.exit()
	if lines[i].find('{')==-1:
		lines[i]=lines[i].replace('\n','')
		lines[i]=lines[i].replace('pattern','!{,')
		handle_comment()
		j=lines[i].find('{')
		if j == -1:
			print ('Line %d: Expecting "{" after pattern' % (i+1))
			sys.exit()
		lines[i] = lines[i][:j]+lines[i][:(j+1)]
	lines[i]=lines[i].replace('{','')
	lines[i]=lines[i].replace('pattern','!{,')
	handle_brackets('!{')
	handle_comment()

def handle_subst():
	global i
	global lines
	# format each line of the macro substitution
	handle_comment()
	if not lines[i].startswith('{'):
		print ('Line %d: Expecting "{" for beginning of substitution' % (i+1))
		sys.exit()
	while (lines[i].startswith('{') and i<len(lines)):
		lines[i]=lines[i].replace('{','{,')
		handle_brackets('{')
		handle_comment()
	if not lines[i].startswith('}'):
		print ('Line %d: Expecting "}" for end of substitution' % (i+1))
		sys.exit()
	lines[i]=lines[i].replace('}','!endfile')
	i+=1


def main():
	parser = OptionParser("usage: %prog [options] input-file")
	parser.add_option("-f", "--file", dest="filename", metavar="FILE", help="The csv output filename (default is <input-file>.csv)")
	(options, args) = parser.parse_args()
	if len(args) != 1:
		parser.error("incorrect number of arguments")
	
	global subst_file
	subst_file = args[0]
	if options.filename:
		csv_file = options.filename
	else:
		csv_file = subst_file.replace('substitutions','csv')

	input = open(subst_file,'r')
	output = open(csv_file,'w')
	global lines	
	lines = input.readlines()
	if lines == [] or lines == '':
		print "Empty input file"
		sys.exit()
	
	global i
	i=len(lines)-1
	while i>0:
		lines[i] = (lines[i].replace('\t',' ')).strip()+'\n'
		i-=1
	while i<len(lines):
		handle_comment()
		if i>= len(lines):
			break
		handle_file()
		handle_pattern()
		handle_subst()

	output.writelines(lines)
	output.close()
	os.system("unix2dos %s" % (csv_file))
	os.system("echo %s converted to %s" % (subst_file,csv_file))

if __name__ == "__main__":
    main()
