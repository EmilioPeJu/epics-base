#!/bin/env python

import os, sys
from optparse import OptionParser

class subst_to_csv:

	def __init__(self,in_file,out_file=None,ioc=""):
		self.in_file = open(in_file,"r")
		self.ioc = ioc
		self.counter = 1
		if out_file:
			out_filename = out_file
		else:
			out_filename = in_file.replace(".substitutions","")+".csv"
		self.out_file = open(out_filename,"w")
		self.process_lines(self.in_file.readlines())
		self.in_file.close()
		self.out_file.close()
		os.system("unix2dos %s" % (out_filename))
		os.system("echo %s converted to %s" % (in_file,out_filename))
					
	def process_lines(self,lines,flag=None):
		if len(lines):
			line = lines[0]
		else:
			return
		if line=="\n" or line[0] == "#":
			if not(line=="\n" and (flag in ["subst","pattern"])):
				self.out_file.write(line)
			self.counter += 1
			self.process_lines(lines[1:],flag)
		elif flag and flag[0]=="{":
			if "{" in line:
				self.process_lines([line[line.find("{")+1:].strip()+"\n"]+lines[1:],flag=flag[1:])
			else:
				print >> sys.stderr, "*** Error: expected { after",flag[1:],"statement, line",self.counter
				sys.exit()
		elif flag =="pattern":
			if "pattern" in line:
				self.process_lines([line[line.find("pattern")+7:].strip()+"\n"]+lines[1:],flag="{patternval")
			else:
				print >> sys.stderr, "*** Error: expected pattern keyword, line",self.counter
				sys.exit()
		elif flag =="patternval":
			if "}" in line:
				self.counter += 1
				vals = [x.replace('"','').replace("'","").strip() for x in line.replace("}","").split(",")]
				self.out_file.write("NAME,DESCRIPTION,IOC,"+str.join(",",vals)+"\n")
				self.process_lines(lines[1:],flag="subst")
			else:
				self.counter += 1
				self.process_lines([line.strip()+lines[1]]+lines[2:],flag="patternval")
		elif flag == "subst":
			if line.find("{")>-1:
				sections = line[line.find("{")+1:].strip().split("}")
				if len(sections)==1:
					self.counter += 1
					self.process_lines([line.strip()+lines[1]]+lines[2:],flag="subst")
				elif len(sections)==2:
					vals = [x.replace('"','').replace("'","").strip() for x in sections[0].split(",")]	
					self.out_file.write(",,"+self.ioc+","+str.join(",",vals)+"\n")
					self.counter+=1
					if sections[1].strip():
						self.process_lines([sections[1].strip()+"\n"]+lines[1:],flag="subst")
					else:
						self.process_lines(lines[1:],flag="subst")
				else:
					print >> sys.stderr, "*** Error: expected subst, line",self.counter
					sys.exit()					
			elif line.find("}")>-1:
				self.process_lines([line[line.find("}")+1:]]+lines[1:],flag=None)
			else:
				print >> sys.stderr, "*** Error: expected {, line",self.counter
				sys.exit()				
		elif line[:4] == "file":
			self.out_file.write("FILE:,"+line.split()[1].strip()+"\n")
			if "{" in line[line.find("file"):]:
				self.process_lines(["{\n"]+lines[1:],flag="{pattern")
			else:
				self.counter += 1
				self.process_lines(lines[1:],flag="{pattern")

def main():
	parser = OptionParser("usage: %prog [options] input-file")
	parser.add_option("-f", "--file", dest="filename", metavar="FILE", help="The csv output filename (default is <input-file>.csv)")
	parser.add_option("-i", "--ioc", dest="ioc", metavar="IOC", help="The ioc (defailt is extraced from filename)")
	(options, args) = parser.parse_args()
	sys.setrecursionlimit(10000)
	if len(args) != 1:
		parser.error("incorrect number of arguments")
	if options.ioc:
		ioc = options.ioc
	else:
		ioc = args[0].split(".")[0]
	if options.filename:
		subst_to_csv(args[0],out_file=options.filename,ioc=ioc)
	else:
		subst_to_csv(args[0],ioc=ioc)

if __name__ == "__main__":
    main()
