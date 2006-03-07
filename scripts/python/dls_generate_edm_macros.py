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

	##############
	# initialise #
	##############
	edminitsub = "" 
	
	for row in table:
		if D.rowtype(row) == "normal" and row[3]:
			out_row = D.insert_quotes(row)
			if not edminitsub:
				dom = out_row[2][:out_row[2].find("-")]
				filename = dom + ".subst"
				edminitsub = D.filef(filename)
				text = "dom="+dom+","
				for macro in edm_base_macros:
					if D.lookup(out_row,macro)=='""' or D.lookup(out_row,macro)=="":
						text = text+macro+"='',"
					else:
						text = text+macro+"="+D.lookup(out_row,macro)+","
				edminitsub.write(text[:len(text)-1])
				print "Wrote "+filename
			filename = row[3]+'.subst'
			outfile = D.filef(filename)
			outfile.write(D.lookuplist(out_row))
			print "Wrote "+filename
	D.closef()
