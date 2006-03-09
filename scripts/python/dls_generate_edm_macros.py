#!/bin/env python

import os, sys
from dlsxmlparserfunctions import *

# write edm macro substitutions files
def gen_edm_macros(table,D):

	####################
	# hardcoded fields #
	####################
	# macros that are passed to edm on the commandline
	edm_base_macros=["EMOTOR","ELO","ELOLO","ETEMP","ECURR"]
	# will load the macros for the monochromator at startup to get around the 255 char macro limit
	base_macro_devices=["DCM","PGM"]

	########
	# Init #
	########
	rows_to_do = []
	
	for row in table:
		if D.rowtype(row) == "normal" and row[3]:
			out_row = D.insert_quotes(row)
			if row[0][:3] not in base_macro_devices:
				# write edm subs for a normal row to file
				filename = row[3]+'.subst'
				outfile = D.filef(filename)
				text = D.lookuplist(out_row,base_macro_devices=base_macro_devices)
				outfile.write(text)
				D.bugprint(filename+": "+text)
				print "Wrote "+filename
			else:
				# add it to list of rows to do
				rows_to_do += [out_row]
	if not rows_to_do:
		D.errorprint("Spreadsheet does not contain a device in "+str(base_macro_devices))
	out_row = rows_to_do[0]
	dom = out_row[2][:out_row[2].find("-")]
	filename = dom + ".subst"
	edminitsub = D.filef(filename)
	text = "dom="+dom+","
	for macro in edm_base_macros:
		if D.lookup(out_row,macro)=='""' or D.lookup(out_row,macro)=="":
			text = text+macro+"='',"
		else:
			text = text+macro+"="+D.lookup(out_row,macro)+","
	# print edm init substitutions
	edminitsub.write(text[:len(text)-1])
	D.bugprint(filename+": "+text[:len(text)-1])
	other_text = D.lookuplist(out_row,header_row=D.unsubbed_edm_row,base_macro_devices=base_macro_devices)
	if other_text:
		edminitsub.write(","+other_text)
		D.bugprint(filename+": "+other_text)
	print "Wrote "+filename
	# print the unsubbed macros for devices in rows_to_do
	for out_row in rows_to_do:
		filename = out_row[3]+'.subst'
		outfile = D.filef(filename)
		text=D.lookuplist(out_row,header_row=D.subbed_edm_row,base_macro_devices=base_macro_devices)
		outfile.write(text)
		D.bugprint(filename+": "+text)
		print "Wrote "+filename
	D.closef()
