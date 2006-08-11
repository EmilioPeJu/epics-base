#!/bin/env python

"""
dlsreleasetree.py
Author: Tom Cobb

contains a python representation of a tree of modules
"""

import os, sys
from optparse import OptionParser

class release_tree:

	#############
	# Variables #	
	#############
	# leaves: list of release_tree leaves
	# path: path to current module
	# name: module name (e.g. Mr1394)
	# epics_version: epics version, (e.g. R3.14.8.2)
	# version: current version (number, work or local)
	# parent: parent node
	
	def __init__(self,parent,module_path=None):
		self.leaves=[]
		self.path = ""
		self.name = ""
		self.epics_version = "R3.14.8.2"
		self.version = ""
		self.parent=parent
		if module_path:
			self.process_module(module_path)

	def copy(self):
		new_tree = release_tree(self.parent)
		new_tree.path = self.path
		new_tree.name = self.name
		new_tree.epics_version = self.epics_version
		new_tree.version = self.version
		for leaf in self.leaves:
			new_leaf = leaf.copy()
			new_leaf.parent = new_tree
			new_tree.leaves.append(new_leaf)
		return new_tree

	def process_module(self,module_path):
		if not os.path.isfile(module_path+"/configure/RELEASE"):
			print >> sys.stderr, "***Error: module does not exist - "+module_path
			sys.exit(0)
		if module_path[-1]=="/":
			self.path=module_path[:-1]
		else:
			self.path=module_path
		sections = self.path.split("/")
		if "prod" in self.path:
			if "ioc" in self.path:
				self.name = sections[-3]+"/"+sections[-2]
			else:
				self.name = sections[-2]
			self.version = sections[-1]
		elif "work" in self.path:
			if "ioc" in self.path:
				self.name = sections[-2]+"/"+sections[-1]
			else:
				self.name = sections[-1]
			self.version = "work"
		else:
			if "ioc" in self.path:
				self.name = sections[-2]+"/"+sections[-1]
			else:
				self.name = sections[-1]
			self.version = "local"
		self.process_release(self.path+"/configure/RELEASE")

	def process_release(self,RELEASE_filename):
		# check for existence of modules here
		# number of times to recursively substitute macros in RELEASE
		retries = 5
		# read the file in
		input = open(RELEASE_filename,"r")
		lines = input.readlines()
		input.close()
		# store current working directory then go to module base
		cwd = os.getcwd()
		os.chdir(RELEASE_filename.replace("/configure/RELEASE",""))
		# strip the modules from lines
		self.__make_leaves(lines)
		# go back to initial place and return the values
		os.chdir(cwd)


	def __make_leaves(self,lines):
		modules = {"TOP":"."}
		module_order = []
		retries = 5
		# list of definitions that are not support modules
		ignore_list = ["TEMPLATE_TOP","EPICS_BASE"]
		for line in lines:
			if line and not line[0]=="#" and line.find("=")>-1:
				list = line.split("=")
				if list[0].strip() == "EPICS_BASE":
					self.epics_version = list[1].strip().split("/")[3]
				elif not list[0].strip() in ignore_list:
					modules[list[0].strip()]=list[1].strip()
					module_order.append(list[0].strip())
		while retries>0:
			unsubbed_macros = []
			for macro in modules.keys():
				if modules[macro].find("$(")>-1:
					unsubbed_macros.append(macro)
			if not unsubbed_macros:
				break
			for unsubbed_macro in unsubbed_macros:
				for macro in modules.keys():
					modules[unsubbed_macro]=modules[unsubbed_macro].replace("$("+macro+")",modules[macro])
			retries-=1
		for module in module_order:
			if (self.parent and module==self.parent.name) or module=="TOP" or modules[module]=="." or not os.path.isfile(modules[module]+"/configure/RELEASE"):
				if not os.path.isdir(modules[module]) and modules[module].upper() not in ["YES","NO","TRUE","FALSE"] and "python" not in modules[module]:
					print >> sys.stderr, "***Warning: can't find "+modules[module]
			else:
				new_leaf = release_tree(parent=self,module_path=modules[module])
				self.leaves.append(new_leaf) 

	def flatten(self,include_self=True):
		if include_self:
			output = [self]
		else:
			output = []
		for tree in self.leaves:
			flattened_list = tree.flatten()
			for leaf in flattened_list:
				flag = False
				for path in [x.path for x in output]:
					if os.path.samefile(leaf.path,path):
						flag = True
				if not flag:
					output.append(leaf)
		return output

	def __latest_version(self):
		path = self.__latest_path()
		if os.path.samefile(path,self.path):
			return "-"
		else:
			return path.split("/")[-1]
	
	def __latest_path(self):
		try:
			files = self.__possible_paths()
			return self.sort_paths(files)[0]
		except:
			return self.path

	def __possible_paths(self):
		if "ioc" in self.path:
			prefix = "/home/diamond/"+self.epics_version+"/prod/ioc/"+self.name
		else:
			prefix = "/home/diamond/"+self.epics_version+"/prod/support/"+self.name
		if os.path.isdir(prefix):
			files = [prefix + "/" + x for x in os.listdir(prefix)]
		else:
			files = []
		if self.path in files:
			return files
		else:
			return [self.path]+files
			
	def sort_paths(self,files):
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
	
	def clashes(self,ignore_warnings=False):
		leaves = self.flatten()
		modules = {}
		clashes = {}
		for leaf in leaves:
			if modules.has_key(leaf.name):
				modules[leaf.name]+=[leaf]
			else:
				modules[leaf.name]=[leaf]
		for module in modules.values():
			if len(module)>1:
				if not ignore_warnings:
					print >> sys.stderr, "*** Warning: releases do not form a consistent set:"
				clashes[module[0].name]=[]
				for leaf in module:
					if not ignore_warnings:
						print >> sys.stderr, leaf.parent.name + " " + leaf.parent.version + " defines " + leaf.name + " as " + leaf.path
					clashes[leaf.name].append(leaf)
		return clashes
					
					
	def updates(self):
		paths = self.sort_paths(self.__possible_paths())
		updates = []
		for path in paths:
			if os.path.samefile(path,self.path):
				return updates
			else:
				updates.append(release_tree(self.parent,path))
		print >> sys.stderr, "*** Error: badly formed path "+self.path
		sys.exit()
		
	def __repr__(self):
		output = """##############################
# Module: """+self.name+"""
# Version: """+self.version+"""
##############################
Number	Module		Current		Latest
"""
		for i in range(len(self.leaves)):
			if len(self.leaves[i].name) >= len("\t".expandtabs()):
				output += str(i)+"\t"+self.leaves[i].name+"\t"
			else:
				output += str(i)+"\t"+self.leaves[i].name+"\t\t"
			if len(self.leaves[i].version) >= len("\t".expandtabs()):
				output += self.leaves[i].version+"\t"+self.leaves[i].__latest_version()+"\n"
			else:
				output += self.leaves[i].version+"\t\t"+self.leaves[i].__latest_version()+"\n"
		return output
		
def release_tree_parser():
	parser = OptionParser("usage: %prog [options] <module_path>")
	(options, args) = parser.parse_args()
	if len(args) != 1:
		print >> sys.stderr, "***Error: Incorrect number of arguments. Type %prog -h for help"
		sys.exit(1)
	print "******************************"
	print "* Interactive object viewer  *"
	print "******************************"
	commands = """Commands:
q   quit
f   print flattened list of modules
..  go to parent module
.   refresh the tree
0   go to module 0
1   go to module 1, etc...
"""
	print commands
	release_file = release_tree(None,args[0])
	path = []
	print release_file
	while True:
		command = raw_input("Please enter a command:")
		if command=="..":
			if release_file.parent:
				release_file=release_file.parent
				path = path[:-1]
				print
				print release_file
			else:
				print "Error: this module has no parent"
		elif command==".":
			release_file = release_tree(None,args[0])
			for number in path:
				release_file = release_file.leaves[number]
			print release_file	
		elif command=="q":
			return
		elif command=="f":
			for m in release_file.flatten():
				print m.name,m.version
		else:
			try:
				number=int(command)
				release_file=release_file.leaves[number]
				path.append(number)
				print
				print release_file
			except:
				print commands
		
		
if __name__ == "__main__":
	release_tree_parser()
