#!/bin/env python

import os, sys
from dlsxmlparserfunctions import *
#from dls_generate_edm_optimized_screen import gen_edm_optimized_screen
from dls_generate_edm_generic_screen import gen_edm_generic_screen

####################
# hardcoded fields #
####################
RELEASE_file=""

##############
# initialise #
##############
device = {}

# see if a group needs subs done
def group(D,lines,start,overview,optimized):
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
		write_vis_object(D,lines,start,end,macro,overview,optimized)
		output.writelines(lines[end:i])
	else:
		output.writelines(lines[start:i])
	return i
	
# replace tags in a given group
def write_vis_object(D,lines,start,end,vis,overview,optimized):
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
				if macro=="FILE" and overview:
					if subst=="autogen":
						subst=gen_edm_generic_screen(D.out_dir,subst,title=vis+" - $(P)",row=device[vis],tableHandler=D)
					elif subst[:7]=="autogen":
						subst=gen_edm_generic_screen(D.out_dir,subst,title="Device - $(P)",tableHandler=D)
					if optimized:
					# lines for optimizing screens
					#	out_file=D.lookup(device[vis],"P")+"-optimized-screen.edl"
					#	opt_title=D.lookup(device[vis],"NAME")+" - "+D.lookup(device[vis],"P"
					#	gen_edm_optimized_screen(subst,RELEASE_file,D.out_dir+"/"+out_file,D.lookuplist(device[vis]),title=opt_title)
						subst=out_file
			line_out = line_out.replace("#<"+macro+">#",subst)
			D.bugprint("Replaced %s with %s in %s" %(macro,subst,lines[i]))
		global output
		output.writelines([line_out])
		i+=1
			
# parse table, create device dictionary, parse input file
def gen_edm_autofill(table,D,filename_in,overview=False,optimized=False):
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
			i = group(D,lines,i,overview,optimized)
		output.writelines([lines[i]])
		i+=1 
	print "Wrote "+ filename
	output.close()

