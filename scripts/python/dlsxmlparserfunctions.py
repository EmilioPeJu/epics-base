#!/bin/env python

import sys,os, re

class table_handler:

	####################
	# hardcoded fields #
	####################
	ioc_row = 2
	smallest_row = 3

	##############
	# initialise #
	##############
	out_dir = "."
	ioc = ""
	bug = False
	# name_dict[column_title]=(index,prefix,defval)
	name_dict = {}
	name_row = []
	prefix_row = []
	def_row = []
	edm_row = []
	unsubbed_edm_row = []
	subbed_edm_row = []
	files = {}
	extra_lookup = {}
	unsubbed_names = {}

	# init
	def __init__(self, out_dir, ioc, bug):
		self.out_dir = out_dir
		self.ioc = ioc
		self.bug = bug
	
	# print text if bug-fixing flag is set
	def bugprint(self,text):
		if self.bug:
			print text

	# print error text
	def errorprint(self,text):
		print>>sys.stderr, text
		sys.exit(1)

	# return type of row. Do default operation on row if dodefaction
	def rowtype(self,row,dodefaction=True):
		if row == []:
			# empty rows have no def action
			self.bugprint("Found Empty row")
			return "empty"
		elif row[0][:1]=='#':
			# comments have no def action
			self.bugprint("Found Comment row")
			return "comment"
		elif row[0][:4]=="NAME":
			self.bugprint("Found NAME row")
			if dodefaction:
				# create name_dict with new name row
				self.name_row = self.trim(row)
				self.prefix_row = []
				self.def_row = []
				self.name_dict = {}
				i = 0
				while i<len(self.name_row):
					self.name_dict[self.name_row[i]]=(i,"","")
					i +=1
			return "name"
		elif row[0][:4]=='EDM_':
			self.bugprint("Found EDM row")
			if dodefaction:
				# create edm_row
				self.edm_row = self.trim(row)
				self.unsubbed_edm_row = self.edm_row[:]
				self.subbed_edm_row = [""]*len(self.edm_row)
			return "edm"
		elif row[0][:6]=='PREFIX':
			self.bugprint("Found PREFIX row")
			if dodefaction:
				# create name_dict with new prefix row
				self.prefix_row = self.trim(row)
				self.name_dict = {}
				i = 0
				while i<len(self.name_row):
					self.name_dict[self.name_row[i]]=(i,self.safeindex(self.prefix_row,i),self.safeindex(self.def_row,i))
					i +=1		
			return "prefix"
		elif row[0][:7]=='DEFAULT':
			self.bugprint("Found DEFAULT row")
			if dodefaction:
				# create name_dict with new def row
				self.def_row = self.trim(row)
				self.name_dict = {"NAME": (0,"","")}
				i = 1
				while i<len(self.name_row):
					self.name_dict[self.name_row[i]]=(i,self.safeindex(self.prefix_row,i),self.safeindex(self.def_row,i))
					i +=1
			return "default"	
		elif row[0][:4]=='FILE':
			self.bugprint("Found File "+row[1]+" row")
			# file has no default action
			return "file"
		elif row[0][:5]=='SMODE':
			self.bugprint("Found SMODE row")
			# smode returns the current simulation mode: SMODE:SIM if simulation or SMODE:REAL if reaf
			if row[1][:3].upper()=="SIM":
				return "SMODE:SIM"
			else:
				return "SMODE:REAL"
		elif len(row) < self.smallest_row or row[self.ioc_row]=="":
			self.bugprint("Found Empty row")
			# empty rows have no def action
			return "empty"
		elif self.ioc not in self.lookup(row,"IOC"):
			self.bugprint("Found Not In IOC row")
			# filter out rows not in current ioc
			return "notinioc"
		else:
			self.bugprint("Found Normal row")
			# normal rows have no default action
			return "normal"

	# lookup a value from a dictionary dict.
	# if the result and defval are "" then return emptyval. replace '""' with "" 
	def lookup(self,row,key,dict="",emptyval=""):
		if not dict:
			dict = self.name_dict
		params = dict.get(key)
		output = ""
		if not params and key == "P":
			params = dict.get("device")
		if not params and key == "device":
			params = dict.get("P")
		if params:
			index,prefix,defval = params
			if index >= len(row) or row[index] == "":
				output = defval	
			else:
				output = row[index]
			if output == "" or output == '""':
				if emptyval:
					return emptyval
				else:
					return ""
			if prefix:
				return prefix+output
			else:
				return output
		else:
			return emptyval

	# lookup list generates a text string from the row if the header exists in the header row
	#	if edm_subs is set then substitute '""' for "''"
	def lookuplist(self,row,header_row="",edm_subs=True,base_macro_devices=[]):
		if not header_row:
			header_row = self.edm_row
		i = 0
		out_text = ""
		while i < len(row):
			if self.safeindex(header_row,i) and row[i] and not header_row[i][:4]=="EDM_":
				cell = row[i]
				if edm_subs and cell=='""':
					cell = "''"
				out_text = out_text + header_row[i] + "=" + cell + ","
				if row[0][:3] not in base_macro_devices:
					self.unsubbed_edm_row[i]=""
					self.subbed_edm_row[i]=self.edm_row[i]
			i += 1
		return out_text[:len(out_text)-1]

	# returns "" if index outside range
	def safeindex(self,row,i):
		if i<len(row):
			return row[i]
		else:
			return ""

	# start a new file if it doesn't exist, then write to it
	def filef(self,filename,readonly=True):
		if not self.files.has_key(filename):
			if os.path.isfile(self.out_dir+"/"+filename):
				os.rename(self.out_dir+"/"+filename,self.out_dir+"/"+filename+".bak")
				print "Backed up "+filename+" to "+filename+".bak"
			out_file = open (self.out_dir+"/"+filename,"w")
			self.files[filename] = (out_file,filename,readonly)
			return out_file
		else:
			f,filename,r=self.files[filename]
			return f

	# open file for reading
	def openf(self,filename):
		return open(self.out_dir+"/"+filename,"r")
	
	# close all files
	def closef(self):
		for (f,filename,r) in self.files.values():
			f.close()
			if r:
				os.chmod(self.out_dir+"/"+filename,0555)
		self.bugprint("All files closed")
		files = {}

	# insert quotes in a file
	def insert_quotes(self,list):
		i = 0
		new_list = list[:]
		while i<len(new_list):
			if not new_list[i]=='""':
				new_list[i]=new_list[i].replace("'","")
				new_list[i]=new_list[i].replace('"',"")
				if new_list[i].find(" ")>-1:
					new_list[i]='"'+new_list[i]+'"'
			i+=1
		return new_list

	# return comma seperated version of list
	def strlist(self,list,stripcomments=True):
		i = 0
		output = ""
		while i<len(list):
			if not(stripcomments and list[i][:1]=="#"):
				output = output + list[i] + ","
			i += 1
		return output[:len(output)-1]

	# trim whitespace from rows
	def trim(self,row):
		i = len(row)-1
		while row[i]=="":
			i-=1
		if row[0][:6]=="PREFIX" or row[0][:4]=="EDM_" or row[0][:7]=="DEFAULT":
			return [""]+row[1:i+1]
		else:
			return row[:i+1]
