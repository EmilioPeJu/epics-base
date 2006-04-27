#!/bin/env python

import sys, re, os
from optparse import OptionParser
from dlsedmtable import edmTableBuilder					# The module that contain the table-API
from dls_generate_edm_titlebar import titlebar
from dlsxmlparserfunctions import table_handler

def gen_edm_generic_screen(out_dir,filename,title="Device - $(P)",row=[],tableHandler=table_handler("","",False)):
	##############
	# initialise #
	##############
	# dict of keywords to search for in title
	global dict
	# create the temperature-table object at offset 0, 0 with 10 pixels between rows and columns.
	global edmTable
	edmTable = edmTableBuilder(10,10,10,10)
	global D
	D = tableHandler
	global macro
	macro = {
		"temp": "label=T#<N>#,temp=$(P)$(T#<N>#)",
		"flow": "flow=$(W)$(W#<N>#),label=Flow #<N>#",
		"curr": "curr=$(P)$(C#<N>#),label=$(CT)#<N>#",
		"bpm" : "$(P):INFO:NCURR"}
	global rrow
	rrow=row

	####################
	# hardcoded fields #
	####################
	# Define the vacuum cell template:
	edmTable.tableTemplate['cellborder'] = False	# Don't want borders around each cell.
	
	if row:
		dict = {
			"motor":(0,int(D.lookup(row,"NMOTOR",emptyval=0))),
			"temp": (0,int(D.lookup(row,"NTEMP",emptyval=0))),
			"curr": (0,int(D.lookup(row,"NCURR",emptyval=0))%4),
			"flow": (0,int(D.lookup(row,"NFLOW",emptyval=0))),
			"pos":  (0,int(D.lookup(row,"NPOS",emptyval=0))),
			"pneu": (0,int(D.lookup(row,"NPNEU",emptyval=0))),
			"bpm":  (0,int(int(D.lookup(row,"NCURR",emptyval=0))/4))}
		filename=D.lookup(row,"P")+"-device-screen.edl"
	else:
		dict = {
			"motor":(0,0),
			"temp": (0,0),
			"curr": (0,0),
			"flow": (0,0),
			"pos":  (0,0),
			"pneu": (0,0),
			"bpm":  (0,0)}
		sections=filename[filename.find("-")+1:].replace(".edl","").split("+")
		filename=filename[:filename.find("-")]+"-"
		for key in dict.keys():
			for section in sections:
				if key in section:
					dict[key]=(0,int(section.replace(key,"")))
		for key in dict.keys():
			if not dict[key][1]==0:
				filename+=str(dict[key][1])+key+"+"
		filename=filename[:len(filename)-1]+".edl"

#	if os.path.isfile(out_dir+"/"+filename):
	# if file exists then do nothing
#		return

	big_boxes = dict["motor"][1]+dict["pneu"][1]
	small_boxes = dict["temp"][1]+dict["curr"][1]+dict["flow"][1]+dict["bpm"][1]
	total_boxes = big_boxes+int((small_boxes+7)/8)
	
	if total_boxes in [1,2,3,4]:
		trigger = total_boxes -1
		boxes_per_row = 1
	elif total_boxes in [5,6,7,8]:
		trigger = total_boxes - (total_boxes+1)%2 -1
		boxes_per_row = 2
	elif total_boxes in [9,12]:
		trigger = total_boxes - (total_boxes+2)%3 -1
		boxes_per_row = 3
	elif total_boxes in [11,16]:
		trigger = total_boxes - (total_boxes+3)%4 -1
		boxes_per_row = 4
	else:
		trigger = total_boxes - (total_boxes+4)%5 -1
		boxes_per_row = 5

	edmTable.tableTemplate['maxnumrows'] = boxes_per_row
	current_box = 0
	total_boxes = trigger + boxes_per_row

	if big_boxes==0:
		n = int((small_boxes-1)/4)+1
		if n==0:
			D.errorprint("***Error - cannot create screen with no contents: "+filename)
		m = int((small_boxes-1)/n)+1
		edmTable.tableTemplate['maxnumrows'] = 1
		for i in range(m):
			edmTable.nextCell()
			make_small_boxes_for_range(n)
		current_box += 1
	else:
		edmTable.addObjectType("motorBox", motorBox, 0, 0);
		edmTable.addObjectType("posBox", posBox, 0, 0);
		edmTable.addObjectType("pneuBox", pneuBox, 0, 0);
	while current_box < big_boxes:
		edmTable.nextCell()
		current_box += 1
		if current_box <= dict["pos"][1]:
			edmTable.fillCellContent("posBox", {"#<mp>#": D.expand(row,"$(MP"+str(current_box)+")"), "#<p>#": D.expand(row,"$(P"+str(current_box)+"1)")})
		elif current_box <= dict["motor"][1]:
			edmTable.fillCellContent("motorBox", {"#<motor>#": D.expand(row,"$(P)$(M"+str(current_box)+")")})
		else:
			edmTable.fillCellContent("pneuBox", {"#<pneu>#": D.expand(row,"$(P)$(N"+str(current_box-dict["motor"][1])+")")})
	while current_box < trigger:
		edmTable.nextCell()
		current_box += 1
		make_small_boxes_for_range(8)
	while current_box	< total_boxes:
		edmTable.nextCell()
		ctemp,ntemp = dict["temp"]
		cflow,nflow = dict["flow"]
		ccurr,ncurr = dict["curr"]
		boxes_to_do=ntemp+nflow+ncurr-ctemp-cflow-ccurr
		if boxes_to_do<(total_boxes-current_box)*4:
			make_small_boxes_for_range(4)
		else:
			make_small_boxes_for_range(8)
		current_box += 1			
	print "Wrote "+filename
	if os.path.isfile(out_dir+"/"+filename):
		os.remove(out_dir+"/"+filename)
	edmTable.nextCell()
	global screenProperties
	newscreenProperties = screenProperties
	regexp = re.compile('#<WIDTH>#', re.MULTILINE)
	newscreenProperties = regexp.sub(str(edmTable.cellPointer['tableWidth']), newscreenProperties)
	regexp = re.compile('#<HEIGHT>#', re.MULTILINE)
	newscreenProperties = regexp.sub(str(edmTable.cellPointer['tableHeight']), newscreenProperties)
	newscreenProperties = newscreenProperties.replace('#<TITLE>#',title)
	edmTable.writeEdmScreen(out_dir+"/"+filename, newscreenProperties)
	titlebar(out_dir+"/"+filename,htype=2)
	return filename

def make_small_boxes_for_range(n):
	global dict
	global edmTable
	for i in range(n):
		ctemp,ntemp = dict["temp"]
		cflow,nflow = dict["flow"]
		ccurr,ncurr = dict["curr"]
		cbpm, nbpm  = dict["bpm"]
		if ntemp+nflow+ncurr+nbpm-ctemp-cflow-ccurr-cbpm==0:
			break
		if ctemp<ntemp: 
			make_small_box("temp",i,ctemp+1)
			dict["temp"]=(ctemp+1,ntemp)
		elif cflow<nflow: 
			make_small_box("flow",i,cflow+1)
			dict["flow"]=(cflow+1,nflow)
		elif ccurr<ncurr: 
			make_small_box("curr",i,ccurr+1)
			dict["curr"]=(ccurr+1,ncurr)
		elif cbpm<nbpm: 
			make_small_box("bpm",i,cbpm+1)
			dict["bpm"]=(cbpm+1,nbpm)

def make_small_box(string,i,cstring):
	global edmTable
	global D
	global rrow
	global macro
	x = int(i/4)*100
	y = i%4*30
	edmTable.addObjectType(string+"Box"+str(cstring), eval(string+"Box"), x, y)
	edmTable.fillCellContent(string+"Box"+str(cstring), {"#<N>#": str(cstring), "#<"+string+">#": D.expand(rrow,macro[string].replace("#<N>#",str(cstring)))},suppress_warnings=True)	

def main():
	usage = "usage: ./%prog [options] OUT_FILENAME"
	parser = OptionParser(usage)
	(options, args) = parser.parse_args()
	if len(args) != 1:
		print("*** Error: Incorrect number of arguments - you must supply one output filename")
		sys.exit(0)
	gen_edm_generic_screen(".",args[0])
	os.system("edm -eolc "+args[0])

	
screenProperties = '''4 0 1
beginScreenProperties
major 4
minor 0
release 1
x 50
y 50
w #<WIDTH>#
h #<HEIGHT>#
font "arial-medium-r-18.0"
ctlFont "arial-medium-r-18.0"
btnFont "arial-medium-r-18.0"
fgColor index 14
bgColor index 3
textColor index 14
ctlFgColor1 index 14
ctlFgColor2 index 0
ctlBgColor1 index 0
ctlBgColor2 index 14
topShadowColor index 0
botShadowColor index 14
title #<TITLE>#
showGrid
snapToGrid
gridSize 5
disableScroll
endScreenProperties
'''

motorBox = '''
# (Embedded Window)
object activePipClass
beginObjectProperties
major 4
minor 1
release 0
x 10
y 10
w 190
h 110
fgColor index 14
bgColor index 0
topShadowColor index 0
botShadowColor index 14
displaySource "menu"
filePv "LOC\\\dummy=i:0"
setSize
sizeOfs 5
numDsps 1
displayFileName {
  0 "motor-embed-small.edl"
}
menuLabel {
  0 "0"
}
symbols {
  0 "motor=#<motor>#"
}
noScroll
endObjectProperties
'''

pneuBox = '''
# (Embedded Window)
object activePipClass
beginObjectProperties
major 4
minor 1
release 0
x 10
y 10
w 190
h 110
fgColor index 14
bgColor index 0
topShadowColor index 0
botShadowColor index 14
displaySource "menu"
filePv "LOC\\\dummy=i:0"
setSize
sizeOfs 5
numDsps 1
displayFileName {
  0 "generic-pneumatic.edl"
}
menuLabel {
  0 "0"
}
symbols {
  0 "box-label=Pneumatic Controls,device=#<pneu>#"
}
noScroll
endObjectProperties
'''

posBox = '''
# (Embedded Window)
object activePipClass
beginObjectProperties
major 4
minor 1
release 0
x 10
y 10
w 190
h 110
fgColor index 14
bgColor index 0
topShadowColor index 0
botShadowColor index 14
displaySource "menu"
filePv "LOC\\\dummy=i:0"
setSize
sizeOfs 5
numDsps 1
displayFileName {
  0 "positioner-1pos.edl"
}
menuLabel {
  0 "0"
}
symbols {
  0 "MP=#<mp>#,P1=#<p>#"
}
noScroll
endObjectProperties
'''

tempBox='''
# (Embedded Window)
object activePipClass
beginObjectProperties
major 4
minor 1
release 0
x 10
y 130
w 90
h 20
fgColor index 14
bgColor index 0
topShadowColor index 0
botShadowColor index 14
displaySource "menu"
filePv "CALC\\\{A>=#<N>#?1:0\}($(P):INFO:NTEMP)"
setSize
sizeOfs 5
numDsps 2
displayFileName {
  0 "generic-blank.edl"
  1 "generic-temp.edl"
}
menuLabel {
  0 "0"
  1 "1"
}
symbols {
  1 "#<temp>#"
}
noScroll
endObjectProperties
'''

bpmBox='''
# (Group)
object activeGroupClass
beginObjectProperties
major 4
minor 0
release 0
x 465
y 685
w 95
h 25

beginGroup

# (Related Display)
object relatedDisplayClass
beginObjectProperties
major 4
minor 0
release 0
x 465
y 685
w 95
h 25
fgColor index 43
bgColor index 3
topShadowColor index 1
botShadowColor index 11
font "arial-bold-r-14.0"
buttonLabel "BPM"
numPvs 4
numDsps 1
displayFileName {
  0 "BLdiag-BPM-small"
}
endObjectProperties

endGroup

visPv "#<bpm>#"
visInvert
visMin "0"
visMax "4"
endObjectProperties
'''

flowBox='''
# (Embedded Window)
object activePipClass
beginObjectProperties
major 4
minor 1
release 0
x 10
y 160
w 90
h 20
fgColor index 14
bgColor index 0
topShadowColor index 0
botShadowColor index 14
displaySource "menu"
filePv "CALC\\\{A>=#<N>#?1:0\}($(P):INFO:NFLOW)"
setSize
sizeOfs 5
numDsps 2
displayFileName {
  0 "generic-blank.edl"
  1 "generic-flow.edl"
}
menuLabel {
  0 "0"
  1 "1"
}
symbols {
  1 "#<flow>#"
}
noScroll
endObjectProperties
'''

currBox='''
# (Embedded Window)
object activePipClass
beginObjectProperties
major 4
minor 1
release 0
x 10
y 190
w 90
h 20
fgColor index 14
bgColor index 0
topShadowColor index 0
botShadowColor index 14
displaySource "menu"
filePv "CALC\\\{A>=#<N>#?1:0\}($(P):INFO:NCURR)"
setSize
sizeOfs 5
numDsps 2
displayFileName {
  0 "generic-blank.edl"
  1 "generic-curr.edl"
}
menuLabel {
  0 "0"
  1 "1"
}
symbols {
  1 "#<curr>#"
}
noScroll
endObjectProperties
'''

if __name__ == "__main__":
	main()
