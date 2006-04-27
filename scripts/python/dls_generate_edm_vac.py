#!/bin/env python
#
#	Based on exportVacuumGui.py written by Ulrik Pedersen @ Diamond - March 2006
#
#	Version 1.0 - 	29.03.2006
#					updated to use dlsxmlparserfunctions

import sys, re, os
from optparse import OptionParser
from dlsedmtable import edmTableBuilder					# The module that contain the table-API
from dlsxmlexcelparser import *
from dls_generate_edm_titlebar import *
from dlsxmlparserfunctions import table_handler

##########
# Global #
##########
filename = ""
# create the temperature-table object at offset 0, 0 with 10 pixels between rows and columns.
edmTable = edmTableBuilder(0,0,10,10)

def complete_screen(D,new_filename,domain):
	global filename
	global edmTable
	if filename:
		# print the existing table to file and start a new file
		print "Wrote "+filename
		if os.path.isfile(D.out_dir+"/"+filename):
			os.remove(D.out_dir+"/"+filename)
			D.bugprint("Replaced "+filename)
		edmTable.writeEdmScreenAuto(D.out_dir+"/"+filename)
		hutchText = filename
		if filename.find("OH")>-1:
			hutchText = "Optics Hutch "+filename[filename.find("OH")+2].replace(".","-")
		if filename.find("EH")>-1:
			hutchText = "Experiment Hutch "+filename[filename.find("EH")+2].replace(".","-")	
		if filename.find("EE")>-1:
			hutchText = "Experimental Enclosure "+filename[filename.find("EE")+2].replace(".","-")							
		if filename.find("BE")>-1:
			hutchText = "Branchline Enclosure "+filename[filename.find("BE")+2].replace(".","-")							
		# add titlebar to screen					
		titlebar(D.out_dir+"/"+filename,colour="green",htype=1,buttonText=domain,headerText=hutchText +" Vacuum Summary",tooltipFilename="generic-tooltip")
		# start new file	
		if new_filename:
			filename = new_filename
			tmpCellTemplate = edmTable.cellTemplate.copy()
			tmpTableTemplate = edmTable.tableTemplate.copy()
			edmTable = edmTableBuilder(0,0,10,10)
			edmTable.cellTemplate = tmpCellTemplate
			edmTable.tableTemplate = tmpTableTemplate
			edmTable.nextCell()
			D.bugprint("New Cell")
	else:
		# If this is the first file, just set the filename
		filename = new_filename


def gen_edm_vac(table,D,domain="$(dom)"):
	##############
	# initialise #
	##############
	spaces = {}
	last_space = ""


	####################
	# hardcoded fields #
	####################
	# Define the vacuum cell template:
	global edmTable
	edmTable.addObjectType("RGAtitle", title, 50, 0);
	edmTable.addObjectType("RGAsymbol", RGAsymbol, 50, 10);
	edmTable.addObjectType("RGAstub", stub, 30, 22);
	edmTable.addObjectType("RGApipe", pipe, 30, 22);
	edmTable.addObjectType("gaugeRelatedDisplay", gaugeRelatedDisplay, 45, 65);
	edmTable.addObjectType("PIRGtitle", title, 50, 70);
	edmTable.addObjectType("PIRGsymbol", PIRGsymbol, 50, 80);
	edmTable.addObjectType("PIRGstub", stub, 30, 92);
	edmTable.addObjectType("PIRGpipe", pipe, 30, 92);
	edmTable.addObjectType("PIRGvalue", textMonitor, 30, 120);
	edmTable.addObjectType("IMGtitle", title, 50, 140);
	edmTable.addObjectType("IMGsymbol", IMGsymbol, 50, 150);
	edmTable.addObjectType("IMGstub", stub, 30, 162);
	edmTable.addObjectType("IMGpipe", pipe, 30, 162);
	edmTable.addObjectType("IMGvalue", textMonitor, 30, 190);
	edmTable.addObjectType("GaugeValue", specialTextMonitor, 25, 210);
	edmTable.addObjectType("pumpStub", pumpStub, 30, 242);
	edmTable.addObjectType("pumpSymbol", pumpSymbol, 20, 280);
	edmTable.addObjectType("pumptitle", title, 17, 315);
	edmTable.addObjectType("pumpvalue", textMonitor, 5, 330);
	edmTable.addObjectType("valveSymbol", valveSymbol, 0, 215);
	edmTable.addObjectTypeSpecial("vaSpace", vaSpace, 21, 230);
	edmTable.addObjectTypeSpecial("vaSpaceLeft", vaSpace, 0, 230);
	edmTable.addObjectType("window", window, 0, 215);
	edmTable.addObjectType("windowTitle", title, 0, 265);
	edmTable.addObjectType("aperture", aperture, 0, 215);
	edmTable.addObjectType("apertureTitle", title, 0, 265);
	edmTable.addObjectType("topLeftWall", topwall, 5, 0);
	edmTable.addObjectType("bottomLeftWall", bottomwall, 5, 260);
	edmTable.addObjectType("topRightWall", topwall, 97, 0);
	edmTable.addObjectType("bottomRightWall", bottomwall, 97, 260);
	edmTable.addObjectType("topMidWall", topwall, 57, 0);
	edmTable.addObjectType("bottomMidWall", bottomwall, 57, 260);
	edmTable.tableTemplate['cellborder'] = False	# Don't want borders around each cell.
	edmTable.tableTemplate['maxnumrows'] = 1		# Define how many rows can max be in one column.

	# Get ready to fill in the content of each cell...
	edmTable.nextCell()
	D.bugprint("New Cell")

	for row in table:
		# find space lengths
		if D.rowtype(row)=="normal":
			if D.lookup(row,"SPACE"):
				# start a new space
				spaces[D.lookup(row,"NAME")]=0
				last_space = D.lookup(row,"NAME")
			elif D.lookup(row,"GCTLR") or D.lookup(row,"IONP") or D.lookup(row,"RGA"):
				# extend length of last space
				spaces[last_space]+=1

	for row in table:
	# write files
		rowtype = D.rowtype(row)
		if rowtype=="file":
			complete_screen(D,row[1],domain)
			# print the existing table to file and start a new file
		if rowtype=="normal":
			prefix = D.lookup(row,"PREFIX")
			# add RGAs
			rowRGA=D.lookup(row,"RGA")
			if rowRGA:
				edmTable.fillCellContent("RGAstub", {})
				edmTable.fillCellContent("RGApipe", {})
				edmTable.fillCellContent("RGAsymbol", {"<DEVICE>": prefix + rowRGA})
				edmTable.fillCellContent("RGAtitle", {"<TITLE>": rowRGA})
			# add IMGs
			rowIMG=D.lookup(row,"IMG")
			if rowIMG:
				edmTable.fillCellContent("IMGstub", {})
				edmTable.fillCellContent("IMGpipe", {})
				edmTable.fillCellContent("IMGtitle", {"<TITLE>": rowIMG})
				edmTable.fillCellContent("IMGsymbol", {"<DEVICE>": prefix + rowIMG})
				edmTable.fillCellContent("IMGvalue", {"<DEVICE>": prefix + rowIMG + ":P"})
			# add PIRGs
			rowPIRG=D.lookup(row,"PIRG")
			if rowPIRG:
				edmTable.fillCellContent("PIRGstub", {})
				edmTable.fillCellContent("PIRGpipe", {})
				edmTable.fillCellContent("PIRGtitle", {"<TITLE>": rowPIRG})
				edmTable.fillCellContent("PIRGsymbol", {"<DEVICE>": prefix + rowPIRG})
				edmTable.fillCellContent("PIRGvalue", {"<DEVICE>": prefix + rowPIRG + ":P"})
			# add GCTLR
			rowGID=D.lookup(row,"GID")
			if rowGID:
				if len(rowGID)<2:
					rowGID = "0"+rowGID[0]
				edmTable.fillCellContent("gaugeRelatedDisplay", {"<ID>": rowGID, "<GCTLR_DEVICE>": prefix + D.lookup(row,'GCTLR')})
				edmTable.fillCellContent("GaugeValue", {"<DEVICE>": prefix + "GAUGE-" + rowGID + ":P"})
			# add IONP
			rowIONP=D.lookup(row,"IONP")
			if rowIONP:
				edmTable.fillCellContent("pumpStub", {})
				edmTable.fillCellContent("pumpSymbol", {"<DEVICE>": prefix + rowIONP})
				edmTable.fillCellContent("pumptitle", {"<TITLE>": rowIONP})
				edmTable.fillCellContent("pumpvalue", {"<DEVICE>": prefix + rowIONP + ":P"})
			# add VALVE
			rowVALVE=D.lookup(row,"VALVE")
			if rowVALVE:
				if rowVALVE.upper().find("WIND")>-1:
					edmTable.fillCellContent("window", {})
					edmTable.fillCellContent("windowTitle", {"<TITLE>": rowVALVE})
				elif rowVALVE.upper().find("APER")>-1:
					edmTable.fillCellContent("aperture", {})
					edmTable.fillCellContent("apertureTitle", {"<TITLE>": rowVALVE})
				else:
					edmTable.fillCellContent("valveSymbol", {"<DEVICE>": rowVALVE})
			# add space
			rowSPACE=D.lookup(row,"SPACE")
			if rowSPACE:
				vaSpaceLength = edmTable.tableTemplate['cellwidth'] - 20 + edmTable.tableTemplate['colspacing']
				cellWidth = edmTable.tableTemplate['cellwidth'] + edmTable.tableTemplate['colspacing']
				if not rowVALVE:
					edmTable.fillCellContent("vaSpaceLeft", {"<SPACE>": prefix + rowSPACE, "<WIDTH>": str(21+vaSpaceLength+spaces[D.lookup(row,"NAME")]*cellWidth-1)})
				else:
					edmTable.fillCellContent("vaSpace", {"<SPACE>": prefix + rowSPACE, "<WIDTH>": str(vaSpaceLength+spaces[D.lookup(row,"NAME")]*cellWidth-1)})
			# add WALL
			rowWALL=D.lookup(row,"WALL")
			if rowWALL[:4].upper()=="LEFT":
				edmTable.fillCellContent("topLeftWall", {})
				edmTable.fillCellContent("bottomLeftWall", {})
			if rowWALL[:5].upper()=="RIGHT":
				edmTable.fillCellContent("topRightWall", {})
				edmTable.fillCellContent("bottomRightWall", {})
			if rowWALL[:3].upper()=="MID":
				edmTable.fillCellContent("topMidWall", {})
				edmTable.fillCellContent("bottomMidWall", {})
			edmTable.nextCell()
			D.bugprint("New Cell")

	# tidy up
	complete_screen(D,"",domain)


def main():
	usage = "usage: ./%prog [options] INPUT_XML_FILE"
	parser = OptionParser(usage)
	D = table_handler(".","",True)
	(options, args) = parser.parse_args()
	if len(args) != 1:
		D.errorprint("*** Error: Incorrect number of arguments - you must supply one input file (.xml)")

	# parse xml file
	xml = args[0]
	data = ExcelHandler()
	parse(xml, data)		
	for name, table in data.tables:
		if name=="!GUI-VA":
			gen_edm_vac(table,D)
	sys.exit(0)
	
screenProperties = '''4 0 1
beginScreenProperties
major 4
minor 0
release 1
x 50
y 50
w <WIDTH>
h <HEIGHT>
font "arial-medium-r-12.0"
ctlFont "arial-medium-r-12.0"
btnFont "arial-medium-r-12.0"
fgColor index 14
bgColor index 3
textColor index 14
ctlFgColor1 index 14
ctlFgColor2 index 0
ctlBgColor1 index 0
ctlBgColor2 index 14
topShadowColor index 1
botShadowColor index 11
showGrid
endScreenProperties
'''

RGAsymbol = '''# (Related Display)
object relatedDisplayClass
beginObjectProperties
major 4
minor 0
release 0
x 154
y 118
w 33
h 33
fgColor index 53
bgColor index 0
topShadowColor index 0
botShadowColor index 53
font "arial-medium-r-18.0"
invisible
numPvs 4
numDsps 1
displayFileName {
  0 "rga.edl"
}
menuLabel {
  0 "Gauges"
}
symbols {
  0 "device=<DEVICE>"
}
endObjectProperties

# (Symbol)
object activeSymbolClass
beginObjectProperties
major 4
minor 0
release 0
x 154
y 118
w 33
h 33
file "rga-symbol.edl"
numStates 11
minValues {
  2 1
  3 2
  4 3
  5 4
  6 5
  7 6
  8 7
  9 8
  10 9
}
maxValues {
  1 1
  2 2
  3 3
  4 4
  5 5
  6 6
  7 7
  8 8
  9 9
  10 10
}
controlPvs {
  0 "<DEVICE>:STA"
}
numPvs 1
useOriginalSize
useOriginalColors
fgColor index 14
bgColor index 0
endObjectProperties
'''

PIRGsymbol = '''# (Symbol)
object activeSymbolClass
beginObjectProperties
major 4
minor 0
release 0
x 154
y 190
w 33
h 33
file "mks937aPirg-symbol.edl"
numStates 17
minValues {
  2 1
  3 2
  4 3
  5 4
  6 5
  7 6
  8 7
  9 8
  10 9
  11 10
  12 11
  13 12
  14 13
  15 14
  16 15
}
maxValues {
  1 1
  2 2
  3 3
  4 4
  5 5
  6 6
  7 7
  8 8
  9 9
  10 10
  11 11
  12 12
  13 13
  14 14
  15 15
  16 16
}
controlPvs {
  0 "<DEVICE>:STA"
}
numPvs 1
useOriginalSize
useOriginalColors
fgColor index 14
bgColor index 0
endObjectProperties
'''

IMGsymbol = '''# (Symbol)
object activeSymbolClass
beginObjectProperties
major 4
minor 0
release 0
x 154
y 262
w 33
h 33
file "mks937aImg-symbol.edl"
numStates 17
minValues {
  2 1
  3 2
  4 3
  5 4
  6 5
  7 6
  8 7
  9 8
  10 9
  11 10
  12 11
  13 12
  14 13
  15 14
  16 15
}
maxValues {
  1 1
  2 2
  3 3
  4 4
  5 5
  6 6
  7 7
  8 8
  9 9
  10 10
  11 11
  12 12
  13 13
  14 14
  15 15
  16 16
}
controlPvs {
  0 "<DEVICE>:STA"
}
numPvs 1
useOriginalSize
useOriginalColors
fgColor index 14
bgColor index 0
endObjectProperties
'''

pumpSymbol = '''# (Related Display)
object relatedDisplayClass
beginObjectProperties
major 4
minor 0
release 0
x 122
y 366
w 33
h 33
fgColor index 14
bgColor index 0
topShadowColor index 0
botShadowColor index 14
font "arial-medium-r-18.0"
invisible
numPvs 4
numDsps 1
displayFileName {
  0 "digitelMpcIonpControl.edl"
}
symbols {
  0 "device=<DEVICE>"
}
endObjectProperties

# (Symbol)
object activeSymbolClass
beginObjectProperties
major 4
minor 0
release 0
x 122
y 366
w 33
h 33
file "digitelMpcIonp-symbol.edl"
numStates 10
minValues {
  2 1
  3 2
  4 3
  5 4
  6 5
  7 6
  8 7
  9 8
}
maxValues {
  1 1
  2 2
  3 3
  4 4
  5 5
  6 6
  7 7
  8 8
  9 9
}
controlPvs {
  0 "<DEVICE>:STA"
}
numPvs 1
useOriginalSize
useOriginalColors
fgColor index 14
bgColor index 0
endObjectProperties
'''


gaugeRelatedDisplay = '''# (Related Display)
object relatedDisplayClass
beginObjectProperties
major 4
minor 0
release 0
x 154
y 158
w 50
h 140
fgColor index 53
bgColor index 0
topShadowColor index 0
botShadowColor index 53
font "arial-medium-r-18.0"
invisible
numPvs 4
numDsps 2
displayFileName {
  0 "mks937aGauge.edl"
  1 "mks937a.edl"
}
menuLabel {
  0 "Gauges"
  1 "Controller"
}
symbols {
  0 "id=<ID>"
  1 "device=<GCTLR_DEVICE>"
}
endObjectProperties
'''

title = '''# (Static Text)
object activeXTextClass
beginObjectProperties
major 4
minor 1
release 0
x 154
y 102
w 38
h 12
font "arial-medium-r-10.0"
fgColor index 14
bgColor index 0
useDisplayBg
value {
  "<TITLE>"
}
autoSize
endObjectProperties
'''

textMonitor = '''# (Text Monitor)
object activeXTextDspClass:noedit
beginObjectProperties
major 4
minor 1
release 0
x 154
y 174
w 72
h 16
controlPv "<DEVICE>"
format "exponential"
font "arial-medium-r-10.0"
fgColor index 14
bgColor index 0
useDisplayBg
autoHeight
precision 3
nullColor index 0
smartRefresh
fastUpdate
showUnits
newPos
objType "monitors"
endObjectProperties
'''

specialTextMonitor = '''# (Text Monitor)
object activeXTextDspClass:noedit
beginObjectProperties
major 4
minor 1
release 0
x 154
y 302
w 72
h 16
controlPv "<DEVICE>"
format "exponential"
font "arial-bold-r-10.0"
fgColor index 14
bgColor index 53
autoHeight
precision 3
nullColor index 0
showUnits
newPos
objType "monitors"
endObjectProperties
'''

stub = '''# (Rectangle)
object activeRectangleClass
beginObjectProperties
major 4
minor 0
release 0
x 138
y 270
w 20
h 8
lineColor index 35
fill
fillColor index 35
lineWidth 0
endObjectProperties
'''

pipe = '''# (Rectangle)
object activeRectangleClass
beginObjectProperties
major 4
minor 0
release 0
x 130
y 126
w 8
h 70
lineColor index 35
fill
fillColor index 35
lineWidth 0
endObjectProperties
'''

pumpStub = '''# (Rectangle)
object activeRectangleClass
beginObjectProperties
major 4
minor 0
release 0
x 130
y 342
w 8
h 42
lineColor index 35
fill
fillColor index 35
lineWidth 0
endObjectProperties
'''

topwall = '''# (Rectangle)
object activeRectangleClass
beginObjectProperties
major 4
minor 0
release 0
x 0
y 0
w 10
h 210
lineColor index 14
fill
fillColor index 13
lineWidth 0
endObjectProperties
'''

bottomwall='''# (Rectangle)
object activeRectangleClass
beginObjectProperties
major 4
minor 0
release 0
x 0
y 260
w 10
h 65
lineColor index 14
fill
fillColor index 13
lineWidth 0
endObjectProperties
'''

valveSymbol = '''# (Related Display)
object relatedDisplayClass
beginObjectProperties
major 4
minor 0
release 0
x 199
y 193
w 20
h 40
fgColor index 14
bgColor index 0
topShadowColor index 0
botShadowColor index 14
font "arial-medium-r-18.0"
invisible
numPvs 4
numDsps 1
displayFileName {
  0 "vacuumValve.edl"
}
symbols {
  0 "device=<DEVICE>"
}
endObjectProperties

# (Symbol)
object activeSymbolClass
beginObjectProperties
major 4
minor 0
release 0
x 252
y 190
w 20
h 40
file "vacuumValve-symbol.edl"
numStates 6
minValues {
  0 99
  2 1
  3 2
  4 3
  5 4
}
maxValues {
  0 100
  1 1
  2 2
  3 3
  4 4
  5 5
}
controlPvs {
  0 "<DEVICE>:STA"
}
numPvs 1
useOriginalColors
fgColor index 14
bgColor index 0
endObjectProperties
'''

vaSpace = '''# (Group)
object activeGroupClass
beginObjectProperties
major 4
minor 0
release 0
x 136
y 222
w <WIDTH>
h 10

beginGroup

# (Related Display)
object relatedDisplayClass
beginObjectProperties
major 4
minor 0
release 0
x 136
y 222
w <WIDTH>
h 10
fgColor index 14
bgColor index 0
topShadowColor index 0
botShadowColor index 14
font "arial-medium-r-18.0"
invisible
numPvs 4
numDsps 1
displayFileName {
  0 "space.edl"
}
symbols {
  0 "device=<SPACE>"
}
endObjectProperties

# (Rectangle)
object activeRectangleClass
beginObjectProperties
major 4
minor 0
release 0
x 136
y 222
w <WIDTH>
h 10
lineColor index 35
fill
fillColor index 83
lineWidth 0
alarmPv "<SPACE>:STA"
endObjectProperties

endGroup

endObjectProperties

'''

window = '''
# (Rectangle)
object activeRectangleClass
beginObjectProperties
major 4
minor 0
release 0
x 200
y 296
w 20
h 42
lineColor index 25
fill
fillColor index 25
endObjectProperties
'''
aperture = '''
# (Symbol)
object activeSymbolClass
beginObjectProperties
major 4
minor 0
release 0
x 252
y 190
w 21
h 40
file "symbols-vacuum-aperture-symbol.edl"
numStates 2
minValues {
  0 -1
  1 0
}
maxValues {
  0 0
  1 1
}
controlPvs {
  0 ""
}
numPvs 1
useOriginalColors
fgColor index 14
bgColor index 0
endObjectProperties
'''

if __name__ == "__main__":
	main()
