#!/bin/env python

import os, sys
from dlsxmlparserfunctions import *

####################
# hardcoded fields #
####################

##############
# initialise #
##############
device = {}

# see if a group needs subs done
def group(D,lines,start):
	i = start
	vis = ""
	counter = 1
	while i<len(lines) and counter > 0:
		i += 1
		if lines[i][:10]=="beginGroup":
			counter+=1
		if lines[i][:8]=="endGroup":
			counter-=1
	end = i
	while i<len(lines) and not lines[i][:19]=="endObjectProperties":
		line = lines[i]
		while line[:9]=='''visPv "#<''':
			macro = line[9:line.find(">#")]
			if macro.find("=")>-1:
				if not vis:
					vis = "dummy"
				D.extra_lookup[macro[:macro.find("=")]]=macro[macro.find("=")+1:]
			else:
				vis = macro
			line=line[:7]+line[11+len(macro):]
		i+=1
	if vis:
		write_vis_object(D,lines,start,end,macro)
		output.writelines(lines[end:i])
	else:
		output.writelines(lines[start:i])
	return i
	
# replace tags in a given group
def write_vis_object(D,lines,start,end,vis):
	i = start
	while i < end:
		line_out = lines[i]
		while line_out.find("#<")>-1:
			macro = line_out[line_out.find("#<")+2:line_out.find(">#")]
			if D.extra_lookup.has_key(macro):
				subst = D.extra_lookup[macro]
			elif not device.has_key(vis):
				D.unsubbed_names[vis]=filename
				break
			else:
				if D.unsubbed_names.has_key(vis):
					del D.unsubbed_names[vis]
				subst = D.lookup(device[vis],macro)
			line_out = line_out.replace("#<"+macro+">#",subst)
			D.bugprint("Replaced %s with %s in %s" %(macro,subst,lines[i]))
		global output
		output.writelines([line_out])
		i+=1
			
# parse table, create device dictionary, parse input file
def gen_edm_autofill(table,D,filename_in):
	global filename
	filename = filename_in
	for row in table:
		if D.rowtype(row)=="normal":
			device[row[0]]=row
	D.bugprint(os.listdir("."))
	D.bugprint("is a listing of '.'")
	input = open(D.out_dir+"/"+filename,"r")
	lines = input.readlines()
	input.close()
	global output
	output = 	open(D.out_dir+"/"+filename,"w")
	i = 0
	while i < len(lines):
		if lines[i][:10]=="beginGroup":
			i = group(D,lines,i)
		output.writelines([lines[i]])
		i+=1 
	print "Wrote "+ filename
	output.close()

