#!/bin/env python2.4

"""
dlsreleasetree.py
Author: Tom Cobb

contains release_tree: a python representation of a tree of modules
also tree_update: a class that updates a release_tree to is most up to date consistent state
"""

import os, sys, shutil


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
		# dls specific entries:
		self.work_string = "work"
		self.prod_string = "prod"
		self.support_string = "support"
		self.ioc_string = "ioc"
		# setup variables
		self.leaves=[]
		self.path = ""
		self.name = ""
		self.epics_version = "R3.14.8.2"
		self.version = ""
		self.parent=parent
		self.macros={}
		if module_path:
			self.process_module(module_path)
		
	def copy(self):
		# return a new_tree that is a copy of self
		new_tree = release_tree(self.parent)
		new_tree.path = self.path
		new_tree.name = self.name
		new_tree.epics_version = self.epics_version
		new_tree.version = self.version
		new_tree.macros = self.macros.copy()
		for leaf in self.leaves:
			new_leaf = leaf.copy()
			new_leaf.parent = new_tree
			new_tree.leaves.append(new_leaf)
		return new_tree

	def make_path(self,prod_work,ioc_support):
		# return a path for prod/work support/ioc. E.g path("prod","ioc") = /home/diamond/R3.14.8.2/prod/ioc
		string = "/dls_sw/"
		if prod_work=="prod":
			string += self.prod_string + "/"+self.epics_version+"/"
		elif prod_work=="work":
			string += self.work_string + "/"+self.epics_version+"/"
		else:
			print >> sys.stderr, "***Error: expected prod or work, got: "+str(prod_work)
			sys.exit(0)
		if ioc_support=="ioc":
			string += self.ioc_string
		elif ioc_support=="support":
			string += self.support_string
		else:
			print >> sys.stderr, "***Error: expected ioc or support, got: "+str(ioc_support)
			sys.exit(0)
		if not os.path.isdir(string):
			print "***Warning: can't find path: "+string
		return string

	def init_module(self):
		# initialise name and version from self.path
		sections = self.path.split("/")
		if self.make_path("prod","support") in self.path:
			self.name = sections[-2]
			self.version = sections[-1]
		elif self.make_path("prod","ioc") in self.path:
			self.name = sections[-3]+"/"+sections[-2]
			self.version = sections[-1]
		elif self.make_path("work","support") in self.path:
			self.name = sections[-1]
			self.version = "work"
		elif self.make_path("work","ioc") in self.path:
			self.name = sections[-2]+"/"+sections[-1]
			self.version = "work"
		else:
			if "ioc" in self.path:
				self.name = sections[-2]+"/"+sections[-1]
			else:
				self.name = sections[-1]
			self.version = "local"

	def process_module(self,module_path):
		# read the file in
		if not os.path.isfile(module_path+"/configure/RELEASE"):
			print >> sys.stderr, "***Error: cannot find module - "+module_path+"/configure/RELEASE"
			sys.exit(0)
		if module_path[-1]=="/":
			self.path=module_path[:-1]
		else:
			self.path=module_path
		input = open(self.path+"/configure/RELEASE","r")
		lines = input.readlines()
		input.close()
		# store current working directory then go to module base
		cwd = os.getcwd()
		os.chdir(self.path)
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
		self.macros = modules
		self.init_module()
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
					if self.make_path("work","support") in modules[module] or self.make_path("work","ioc") in modules[module] or self.make_path("prod","ioc") in modules[module] or self.make_path("prod","support") in modules[module]:
						new_leaf = release_tree(parent=self)
						new_leaf.path = modules[module]
						new_leaf.init_module()
						new_leaf.version="invalid"
						self.leaves.append(new_leaf)
					print >> sys.stderr, "***Warning: can't find module: "+module+" with path: "+modules[module]
			elif not ("/"+self.name in modules[module] and (modules[module].endswith("/"+self.name) or "/"+self.name+"/" in modules[module])):
				new_leaf = release_tree(parent=self,module_path=modules[module])
				self.leaves.append(new_leaf) 
		# go back to initial place and return the values
		os.chdir(cwd)

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
					try:
						if os.path.samefile(leaf.path,path):
							flag = True
					except OSError:
						flag = True
				if not flag:
					output.append(leaf)
		return output

	def latest_version(self):
		path = self.__latest_path()
		try:
			if os.path.samefile(path,self.path):
				return ""
			else:
				return path.split("/")[-1]
		except OSError:
			return path.split("/")[-1]		
	
	def __latest_path(self):
		try:
			files = self.__possible_paths()
			return self.sort_paths(files)[0]
		except:
			return self.path

	def __possible_paths(self):
		if self.ioc_string in self.path:
			prefix = self.make_path("prod","ioc")+"/"+self.name
		else:
			prefix = self.make_path("prod","support")+"/"+self.name
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
			try:
				if os.path.samefile(path,self.path):
					return updates
				else:
					updates.append(release_tree(self.parent,path))
			except OSError:
				if os.path.isdir(path):
					updates.append(release_tree(self.parent,path))
		return updates
		
	def __repr__(self):
		return "<release_tree - "+self.name+": "+self.version+">"

	def equals(self,tree):
		output = self.name==tree.name and self.version==tree.version and len(self.leaves)==len(tree.leaves)
		for i in range(len(self.leaves)):
			output = output and self.leaves[i].equals(tree.leaves[i])
		return output

		
						
class tree_update:

	def __init__(self,tree,no_check=False):
		self.modules = {}
		self.old_tree = tree
		self.tree = tree.copy()
		for i in range(len(self.tree.leaves)):
			leaf_updates = self.tree.leaves[i].updates()+[tree.leaves[i]]
			if leaf_updates:
				self.modules[self.tree.leaves[i].name]=leaf_updates
#				print "### Updated",self.tree.leaves[i].name,"from",self.tree.leaves[i].version,"to",leaf_updates[0].version
				self.tree.leaves[i]=leaf_updates[0]
		if no_check:
			return
		clashes = self.tree.clashes(ignore_warnings=True)
		agenda = []
		counter = 0
		while clashes:
			if agenda:
				name = agenda.pop()
				if not name in self.modules.keys():
					flat_leaves = self.tree.flatten()
					flag = False
					for leaf in flat_leaves:
						if leaf.name == name:
							print leaf
							agenda.append(leaf.parent.name)
							flag = True
					if not flag:
						print "*** Warning - Can't find a consistent set, the following clashes need to be resolved"
						for key in clashes.keys():
							text = ": "
							for leaf in clashes[key]:
								text += leaf.parent.name + ": " + leaf.parent.version + " has " + leaf.version + ", " 
							print >> sys.stderr, key+text
						return
				elif not self.revert(name):
					if clashes.has_key(name):
						for leaf in clashes[name]:
							if not leaf.parent.name == self.tree.name:
								agenda.append(leaf.parent.name)
					else:
						print "*** Warning - Can't find a consistent set, the following clashes need to be resolved"
						for key in clashes.keys():
							text = ": "
							for leaf in clashes[key]:
								text += leaf.parent.name + ": " + leaf.parent.version + " has " + leaf.version + ", " 
							print >> sys.stderr, key+text
						return
			else:	
				clash = clashes[clashes.keys()[0]]
				duplicates = self.__duplicates(clash)
				if duplicates:
					agenda.append(duplicates)
				else:
					agenda += self.fix_clash(clash)
			clashes = self.tree.clashes(ignore_warnings=True)
			counter+=1
			if counter > 300:
				print >> sys.stderr, "***Error: Maximum recursion depth reached. Check you don't have duplicate entries in your configure/RELEASE. Clashes still remain:"
				for key in clashes.keys():
					text = ": "
					for leaf in clashes[key]:
						text += leaf.parent.name + ": " + leaf.parent.version + " has " + leaf.version + ", " 
					print >> sys.stderr, key+text
				sys.exit()
		
	def fix_clash(self,leaves):
		clash_name = leaves[0].name
		# set minimum path
		min_leaf_path = self.tree.sort_paths([x.path for x in leaves])[-1]
		out_names = []
		for leaf in leaves:
			if leaf.path==min_leaf_path:
				min_leaf = leaf.copy()
				min_leaf.parent = self.tree
				if not leaf.parent == self.tree:
					for i in range(len(self.tree.leaves)):
						if self.tree.leaves[i].name == clash_name:
							self.tree.leaves[i] = min_leaf
			elif not leaf.parent == self.tree:
				out_names.append(leaf.parent.name)
		return out_names
	
	def __duplicates(self,leaves):
		dict = {}
		for name in [x.parent.name for x in leaves]:
			if name in dict.keys():
				dict[name]+=1
			else:
				dict[name]=1
		for key in dict.keys():
			if dict[key]>1:
				return key
		return 0
	
	def revert(self,name):
		upgrades = self.modules[name]
		index = -1
		for i in range(len(self.tree.leaves)):
			if self.tree.leaves[i].name == name:
				index = i
		if not index == -1:
			for i in range(len(upgrades)):
				if upgrades[i].path==self.tree.leaves[index].path and i+1<len(upgrades):
#					print "### Reverted",name,"to",upgrades[i+1].version
					self.tree.leaves[index] = upgrades[i+1]
					return 1
		return 0
		
	def changes(self):
		output = {}
		file = open(self.tree.path+"/configure/RELEASE","r")
		lines = file.readlines()
		file.close()
		for i in range(len(self.old_tree.leaves)):
			if not self.old_tree.leaves[i].version == self.tree.leaves[i].version:
				for j in range(len(lines)):
					if ("/"+self.old_tree.leaves[i].name+"\n" in lines[j] or "/"+self.old_tree.leaves[i].name+"/" in lines[j]) and (self.old_tree.leaves[i].version in lines[j] or self.old_tree.leaves[i].version.upper() in lines[j] or self.old_tree.leaves[i].version=="invalid") and "#" not in lines[j][:4]:
						macros = {}
						out_line = lines[j]
						while "$(" in out_line:
							index = out_line.find("$(")
							macro = out_line[index+2:index+out_line[index:].find(")")]
							macros[self.tree.macros[macro]]=macro
							out_line = out_line.replace("$("+macro+")",self.tree.macros[macro])
						out_line = out_line.replace(self.old_tree.leaves[i].path,self.tree.leaves[i].path)
						for macro_sub in macros.keys():
							out_line = out_line.replace(macro_sub,"$("+macros[macro_sub]+")")
						output[lines[j]]=out_line
		return output
	
	def print_changes(self):
		changes = self.changes()
		message = ""
		for old_line in changes.keys():
			message+= "Change: "+old_line+"To:     "+changes[old_line]
		print message
		
	
	def write_changes(self):
		changes = self.changes()
		shutil.copy(self.tree.path+"/configure/RELEASE",self.tree.path+"/configure/RELEASE~")
		print "Backup written to",self.tree.path+"/configure/RELEASE~."
		file = open(self.tree.path+"/configure/RELEASE","r")
		lines = file.readlines()
		file.close()
		file = open(self.tree.path+"/configure/RELEASE","w")
		for line in lines:
			if changes.has_key(line):
				file.write(changes[line])
			else:
				file.write(line)
		file.close()
		print "Changes written to",self.tree.path+"/configure/RELEASE."

	
