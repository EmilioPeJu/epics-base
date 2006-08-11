#!/bin/env python

"""
dls-check-ioc-updates.py
Author: Tom Cobb

Checks an ioc for updates to its modules and fixes them if prompted
"""

import os, sys, shutil
from optparse import OptionParser
from dlsreleasetree import *

class tree_update:

	def __init__(self,tree):
		self.modules = {}
		self.tree = tree.copy()
		for i in range(len(self.tree.leaves)):
			leaf_updates = self.tree.leaves[i].updates()+[tree.leaves[i]]
			if leaf_updates:
				self.modules[self.tree.leaves[i].name]=leaf_updates
				print "### Updated",self.tree.leaves[i].name,"from",self.tree.leaves[i].version,"to",leaf_updates[0].version
				self.tree.leaves[i]=leaf_updates[0]
		clashes = self.tree.clashes(ignore_warnings=True)
		agenda = []
		while clashes:
			if agenda:
				name = agenda.pop()
#				print "### Trying module "+name
				if not name in self.modules.keys():
					flat_leaves = self.tree.flatten()
					flag = False
					for leaf in flat_leaves:
						if leaf.name == name:
							agenda.append(leaf.parent.name)
							flag = True
					if not flag:
						print "*** Warning - Can't find a consistent set, the following clashes need to be resolved"
						return
				elif not self.revert(name):
					for leaf in clashes[name]:
						if not leaf.parent.name == self.tree.name:
							agenda.append(leaf.parent.name)
			else:	
				clash = clashes[clashes.keys()[0]]
				duplicates = self.__duplicates(clash)
				if duplicates:
					agenda.append(duplicates)
				else:
#					print "### Trying to fix "+clash[0].name
					agenda += self.fix_clash(clash)
			clashes = self.tree.clashes(ignore_warnings=True)
		
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
					print "### Reverted",name,"to",upgrades[i+1].version
					self.tree.leaves[index] = upgrades[i+1]
					return 1
		return 0
	
def release_tree_parser():
	parser = OptionParser("usage: %prog [options] <module_path>\n\nUse this script to check for updates on an IOC")
	parser.add_option("-w", action="store_true", dest="write", help="Write changes to configure/RELEASE (and backup to RELEASE~)")
	(options, args) = parser.parse_args()
	if len(args) != 1:
		print >> sys.stderr, "***Error: Incorrect number of arguments. Type %prog -h for help"
		sys.exit(1)
	tree = release_tree(None,args[0])
	update_tree = tree_update(tree)
	new_tree = update_tree.tree
	new_tree.clashes()
	if options.write:
		shutil.copy(args[0]+"/configure/RELEASE",args[0]+"/configure/RELEASE~")
	file = open(args[0]+"/configure/RELEASE","r")
	lines = file.readlines()
	file.close()
	if tree == new_tree:
		print "No consistent update combination found"
	else:
		print "*********************"
		print "* Suggested Changes *"
		print "*********************"
		for i in range(len(tree.leaves)):
			if not tree.leaves[i].version == new_tree.leaves[i].version:
				print "Upgrade: "+new_tree.leaves[i].name+" to "+new_tree.leaves[i].version
				for j in range(len(lines)):
					if (tree.leaves[i].name+"\n" in lines[j] or tree.leaves[i].name+"/" in lines[j]) and (tree.leaves[i].version in lines[j] or tree.leaves[i].version.upper() in lines[j]) and "#" not in lines[j][:4]:
						out_line = lines[j].split("=")[0]+"= "+new_tree.leaves[i].path
						print "Change : "+lines[j]+"To     : "+out_line
						lines[j]=out_line.replace("\n","")+"\n"
				print "********"
							
	if options.write:
		file = open(args[0]+"/configure/RELEASE","w")		
		file.writelines(lines)
		print "Suggested changes written to "+args[0]+"/configure/RELEASE, backup saved as "+args[0]+"/configure/RELEASE~"
		file.close()
				
	
		
if __name__ == "__main__":
	release_tree_parser()
