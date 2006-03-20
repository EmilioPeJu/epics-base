#!/usr/bin/env python
#
#	exportVacuumGui.py
#	
#	Ulrik Pedersen @ Diamond - March 2006
#
#	Version 1.0 - 	03.03.2006
#					released to /home/up45/bin/scripts
#
#	Version 1.1 - 	03.03.2006
#					removed annoying output.
#
#	Ver. 1.2 - 	06.03.2006 (UKP)
#				- Added graceful exit and stderr output when file error occurs.
#
#	Ver. 1.3 -	06.03.2006 (UKP)
#				- Moved all VacuumCellObjects into this file.
#				
#	Ver. 1.4 -	06.03.2006 (UKP)
#				- added support for empty and comment rows.
#				- first version released to makeDlsApp subversion.
#				- renamed to dlsGenerateEdmVacuumGui.py
#				- removed prefix in fron of valve to support FE valves.
#
# Ver. 1.5 -  06.03.2006 (TMC)
#				- titlebar now added using dls_generate_edm_titlebar
#				- FUDGE: added output directory


import sys, optparse, re
from optparse import OptionParser
from dlsedmtable import edmTableBuilder					# The module that contain the table-API
#from vacuumCellObjects import *							# The file where the EDM objects are defined
from dlsxmlexcelparser import *
from dls_generate_edm_titlebar import *

def gen_edm_vac(spreadSheetData,out_dir="."):

	# create the temperature-table object at offset 0, 0 with 10 pixels between rows and columns.
	edmTable = edmTableBuilder(0,0,10,10)

	# Define the vacuum cell template:
	edmTable.addObjectType("RGAtitle", title, 50, 0);
	edmTable.addObjectType("RGAsymbol", RGAsymbol, 50, 10);
	edmTable.addObjectType("RGAstub", stub, 30, 22);
	edmTable.addObjectType("RGApipe", pipe, 30, 22);
	edmTable.addObjectType("gaugeRelatedDisplay", gaugeRelatedDisplay, 45, 65);
	edmTable.addObjectType("PIRGtitle", title, 50, 70);
	edmTable.addObjectType("PIRGsymbol", PIRGsymbol, 50, 80);
	edmTable.addObjectType("PIRGstub", stub, 30, 92);
	edmTable.addObjectType("PIRGpipe", pipe, 30, 92);
	edmTable.addObjectType("PIRGvalue", textMonitor, 45, 120);
	edmTable.addObjectType("IMGtitle", title, 50, 140);
	edmTable.addObjectType("IMGsymbol", IMGsymbol, 50, 150);
	edmTable.addObjectType("IMGstub", stub, 30, 162);
	edmTable.addObjectType("IMGpipe", pipe, 30, 162);
	edmTable.addObjectType("IMGvalue", textMonitor, 45, 190);
	edmTable.addObjectType("GaugeValue", specialTextMonitor, 45, 210);
	edmTable.addObjectType("pumpStub", pumpStub, 30, 242);
	edmTable.addObjectType("pumpSymbol", pumpSymbol, 20, 260);
	edmTable.addObjectType("pumptitle", title, 20, 295);
	edmTable.addObjectType("pumpvalue", textMonitor, 20, 310);
	edmTable.addObjectType("valveSymbol", valveSymbol, 0, 215);
	edmTable.addObjectTypeSpecial("vaSpace", vaSpace, 21, 232);
	edmTable.addObjectType("beWindow", beWindow, 0, 215);
	edmTable.addObjectType("beWindowTitle", title, 0, 260);

	edmTable.tableTemplate['cellborder'] = False	# Don't want borders around each cell.
	edmTable.tableTemplate['maxnumrows'] = 1		# Define how many rows can max be in one column.

	# Get ready to fill in the content of each cell...
	edmTable.nextCell()

	header = True
	hutchNumber = 0
	rowIndex = {}
#	print "here!"
	for name, table in spreadSheetData.tables:
		if name == "!GUI-VA":
#			print "Parsing sheet: " + name
			for i, row in enumerate(table):
				
				#ignore empty rows
				if len(row) == 0:
					continue
#				print "+++++++++ " + row[0] +" len: " + str(len(row))
				
				# Ignore comments (check if the first row starts with a #)
				if re.compile(r'^[\#].*').match(row[0]):
					continue

				if header:
					if row[0] == "NAME":
						header = False
						colIndex = 0
						for cell in row:
							rowIndex[cell] = colIndex
							colIndex += 1
					continue

				# if we reach a wall....
				# here should either be a switch to another file (ie start a new table with the same template)
				# or just draw some sort of 'wall'...
				if row[0] == "FILE:":
					if hutchNumber > 0:
						if row[1] == "end":
#							print "the end..."
							edmTable.fillCellContent("beWindow", {})
							edmTable.fillCellContent("beWindowTitle", {"<TITLE>": "Be Window"})
							edmTable.nextCell()

							# Create an EDM screen where the table will fit exactly
	#						print "tablesize: " + str(edmTable.tableTemplate['screenSizeX']) + "x" +  str(edmTable.tableTemplate['screenSizeY'])
	#						print "CellPointer: " + str(edmTable.cellPointer['x']) + "x" +  str(edmTable.cellPointer['y'])
						print "Writing screen to file: " + outputFile
						edmTable.writeEdmScreenAuto(out_dir+"/"+outputFile)
						text = outputFile
						if outputFile.find("OH")>-1:
							text = "Optics Hutch "+outputFile[outputFile.find("OH")+2]
						if outputFile.find("EH")>-1:
							text = "Experiment Hutch "+outputFile[outputFile.find("EH")+2]	
						if outputFile.find("EE")>-1:
							text = "Experimental Enclosure "+outputFile[outputFile.find("EE")+2]							
						if outputFile.find("BE")>-1:
							text = "Branchline Enclosure "+outputFile[outputFile.find("BE")+2]							
						
						titlebar(out_dir+"/"+outputFile,colour="green",htype=1,buttonText="$(dom)",headerText=text +" Vacuum Summary",tooltipFilename="generic-tooltip")
	
						tmpCellTemplate = edmTable.cellTemplate.copy()
						tmpTableTemplate = edmTable.tableTemplate.copy()
						edmTable = edmTableBuilder(0,0,10,10)
						edmTable.cellTemplate = tmpCellTemplate
						edmTable.tableTemplate = tmpTableTemplate
						
						# Get ready to fill in the content of each cell...
						edmTable.nextCell()
					if row[1]:
						outputFile = row[1]
					hutchNumber += 1
					if len(row) <= 2:
						continue		
					
				if row[rowIndex['PREFIX']]:
					prefix = row[rowIndex['PREFIX']]
				else:
					prefix = ""
				
				if row[rowIndex['RGA']]:
					edmTable.fillCellContent("RGAstub", {})
					edmTable.fillCellContent("RGApipe", {})
					edmTable.fillCellContent("RGAsymbol", {"<DEVICE>": prefix + row[rowIndex['RGA']]})
					edmTable.fillCellContent("RGAtitle", {"<TITLE>": row[rowIndex['RGA']]})
					
				if row[rowIndex['IMG']]:	
					edmTable.fillCellContent("gaugeRelatedDisplay", {"<DOMAIN>": "BL16B", "<ID>": row[rowIndex['GID']], "<GCTLR_DEVICE>": prefix + row[rowIndex['GCTLR']]})
					
					edmTable.fillCellContent("PIRGstub", {})
					edmTable.fillCellContent("PIRGpipe", {})
					edmTable.fillCellContent("PIRGtitle", {"<TITLE>": row[rowIndex['PIRG']]})
					edmTable.fillCellContent("PIRGsymbol", {"<DEVICE>": prefix + row[rowIndex['PIRG']]})
					edmTable.fillCellContent("PIRGvalue", {"<DEVICE>": prefix + row[rowIndex['PIRG']] + ":P"})
					
					edmTable.fillCellContent("IMGstub", {})
					edmTable.fillCellContent("IMGpipe", {})
					edmTable.fillCellContent("IMGtitle", {"<TITLE>": row[rowIndex['IMG']]})
					edmTable.fillCellContent("IMGsymbol", {"<DEVICE>": prefix + row[rowIndex['IMG']]})
					edmTable.fillCellContent("IMGvalue", {"<DEVICE>": prefix + row[rowIndex['IMG']] + ":P"})

					edmTable.fillCellContent("GaugeValue", {"<DEVICE>": prefix + "GAUGE-" + row[rowIndex['GID']] + ":P"})

				if row[rowIndex['IONP']]:
					edmTable.fillCellContent("pumpStub", {})
					edmTable.fillCellContent("pumpSymbol", {"<DEVICE>": prefix + row[rowIndex['IONP']]})
					edmTable.fillCellContent("pumptitle", {"<TITLE>": row[rowIndex['IONP']]})
					edmTable.fillCellContent("pumpvalue", {"<DEVICE>": prefix + row[rowIndex['IONP']] + ":P"})

				if row[rowIndex['SPACE']]:
					vaSpaceLength = edmTable.tableTemplate['cellwidth'] - 20 + edmTable.tableTemplate['colspacing']
					cellWidth = edmTable.tableTemplate['cellwidth'] + edmTable.tableTemplate['colspacing']
					nextRow = 1
					spaceEndReached = False
					while (not spaceEndReached):
						if len(table[i+nextRow]) <= 1:		# Check and ignore if the row is (almost) empty
							nextRow += 1
							continue
						if re.compile(r'^[\#].*').match(table[i+nextRow][0]):	# check and ignore if the row is a comment
							nextRow += 1
							continue
							
						spaceStr = table[i+nextRow][rowIndex['SPACE']]
						if spaceStr == "end":
							spaceEndReached = True
						elif table[i+nextRow][rowIndex['NAME']] == "FILE:":
							nextRow += 1
						elif not spaceStr:
							nextRow += 1
							vaSpaceLength += cellWidth
						else:
							spaceEndReached = True

					edmTable.fillCellContent("vaSpace", {"<SPACE>": prefix + row[rowIndex['SPACE']], "<WIDTH>": str(vaSpaceLength-1)})
					
				if len(row) >= rowIndex['VALVE']:
					if row[rowIndex['VALVE']]:
						if row[rowIndex['VALVE']].upper().find("WIND")>-1:
							edmTable.fillCellContent("beWindow", {})
							edmTable.fillCellContent("beWindowTitle", {"<TITLE>": row[rowIndex['VALVE']]})
						elif row[rowIndex['VALVE']].upper().find("APER")>-1:
							edmTable.fillCellContent("beWindow", {})
							edmTable.fillCellContent("beWindowTitle", {"<TITLE>": row[rowIndex['VALVE']]})
						else:
							edmTable.fillCellContent("valveSymbol", {"<DEVICE>": row[rowIndex['VALVE']]})
						
				edmTable.nextCell()
	return

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
w 70
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
  0 "dom=<DOMAIN>, id=<ID>"
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
h 22
lineColor index 35
fill
fillColor index 35
lineWidth 0
endObjectProperties
'''

wall = '''# (Rectangle)
object activeRectangleClass
beginObjectProperties
major 4
minor 0
release 0
x 1185
y 95
w 15
h <HEIGHT>
lineColor index 63
fill
fillColor index 48
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

beWindow = '''
# (Rectangle)
object activeRectangleClass
beginObjectProperties
major 4
minor 0
release 0
x 200
y 296
w 10
h 42
lineColor index 38
fill
fillColor index 38
endObjectProperties
'''


if __name__ == "__main__":
	usage = "usage: ./%prog [options] INPUT_XML_FILE"
	parser = OptionParser(usage)
	(options, args) = parser.parse_args()
	if len(args) != 1:
#		parser.error("*** Error: Incorrect number of arguments - you must supply one input file (.xml)")
		print >> sys.stderr, "*** Error: Incorrect number of arguments - you must supply one input file (.xml)"
		sys.exit(1)

	# read in the arguments
	inputFile = args[0]
	try:
		fileHandle = open(inputFile, 'r')
	except IOError:
		print >> sys.stderr, "*** ERROR: could not open file: " + inputFile + " for reading."
		sys.exit(1)
	fileHandle.close()

	xmlData = ExcelHandler()
	parse(inputFile, xmlData)
	gen_edm_vac(xmlData)
	sys.exit(0)
	


