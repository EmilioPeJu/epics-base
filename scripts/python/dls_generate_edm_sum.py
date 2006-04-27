#!/usr/bin/env python

import os, sys
from dlsxmlparserfunctions import *
from dls_generate_edm_titlebar import *
from dlsedmtable import *


# write edm summary
# for vtype = "xxx", assume existence of xxxTooltip, xxxRD, xxxSymbol, xxxLabel, tempVal and exitButton in edmobjects
# also assume rows labelled X1 .. X[n] in table with NXXX=n
# output a summary screen with a standard blue header and a list of vtype with device headers and an exit button
def gen_edm_sum(xml_table,D,filename,dom,title,vtype="temp",aspectratio=0.65):

	####################
	# hardcoded fields #
	####################
	# create the temperature-table object at offset 100, 100 with 10 pixels between rows and columns.
	table = edmTableBuilder(0,0,2,2)
	# Add and name the EDM objects to the cell template with their (cell) offset
	table.addObjectType(vtype+"Tooltip", Tooltip.replace("#<VTYPE>#",vtype), 11, 1)
	table.addObjectType("deviceTooltip", deviceTooltip, 11, 1)
	table.addObjectType(vtype+"RD", RD, 11, 1)
	table.addObjectType(vtype+"Symbol", eval(vtype+"Symbol"), 84, 4)
	table.addObjectType("Label", Label, 14, 6)
	table.addObjectType("tempVal", tempVal, 42, 6)
	table.addObjectType("Text_title", Text_title, 14, 4)	
	table.tableTemplate['cellborder'] = False	# Don't want borders around each cell.
	cell_width = 110
	done_devices = []
	nvtype = "N"+vtype.upper()

	##############
	# initialise #
	##############
	totalv = 0
	maxv = 0
	nvtypev = 0
	height = 0
	x = 1
	y = 1
	table.nextCell()

	# find the table height in number of blocks
	for row in xml_table:
		if D.rowtype(row)=="normal":
			totalv = totalv + int(D.lookup(row,nvtype))
			maxtemp = max(maxv,int(D.lookup(row,nvtype)))
	height = max(int(totalv**aspectratio)+2,maxv+2)
	table.tableTemplate['maxnumrows'] = height		# Define how many rows can max be in one column.
	for row in xml_table:
		if D.rowtype(row)=="normal":
			nvtypev = int(D.lookup(row,nvtype))
			if nvtypev > 0:
				p = D.lookup(row,"P")
				skip_list = []
				for i in range(int(D.lookup(row,"NFLOW"))):
					wn = D.lookup(row,"W")+D.lookup(row,"W"+str(i))
					if wn in done_devices:
						skip_list.append(wn)
					else:
						done_devices.append(wn)
				if vtype=="temp" or not len(skip_list) == int(D.lookup(row,"NFLOW")):
					i = 1
					if y + nvtypev + 1 > height:
						table.forceNewCol(0)
						x += 1
						y = 1
						D.bugprint("forcing new column for " + p)
					D.bugprint("writing cell header for "+p)
					if not y==1:
						table.nextCell()
						y +=1 					
					table.fillCellContent("Text_title", {"#<NAME>#": D.lookup(row,"NAME")})
					table.fillCellContent(vtype+"RD", {"#<P>#": p,"#<FILE>#": D.lookup(row,"FILE")})
					table.fillCellContent("deviceTooltip", {"#<P>#": p})
					table.nextCell()
					y += 1
					while not i > nvtypev:
						vn = D.lookup(row,vtype[:1].upper()+str(i))
						vPV = p + vn
						table.fillCellContent(vtype+"Tooltip", {})
						table.fillCellContent(vtype+"RD", {"#<P>#": p,"#<FILE>#":D.lookup(row,"FILE")})
						if vtype == "temp":
							table.fillCellContent("Label", {"$(label)": vtype[:1].upper()+str(i)})						
							table.fillCellContent(vtype+"Val", {"$("+vtype+")": vPV})
							table.fillCellContent("tempSymbol", {"$(temp)": vPV})
						elif D.lookup(row,"W")+D.lookup(row,"W"+str(i)) not in skip_list:
							table.fillCellContent("Label", {"$(label)": "Flow "+str(i)})
							table.fillCellContent("flowSymbol", {"$(flow)": D.lookup(row,"W")+D.lookup(row,"W"+str(i))})
						D.bugprint("writing cell for "+vtype+" "+str(i))
						i += 1
						table.nextCell()
						y += 1
	
	global screenProperties
	# Get the size of the entire table and create an EDM screen where the table will fit exactly
	regexp = re.compile('#<WIDTH>#', re.MULTILINE)
	screenProperties = regexp.sub(str(table.cellPointer['tableWidth']), screenProperties)
	regexp = re.compile('#<HEIGHT>#', re.MULTILINE)
	screenProperties = regexp.sub(str(table.cellPointer['tableHeight']), screenProperties)
	screenProperties = screenProperties.replace('#<SCREEN_TITLE>#',dom+" - "+title)
	
	# Finally write the screen to a file
	if os.path.isfile(D.out_dir+"/"+filename):
		os.remove(D.out_dir+"/"+filename)
		D.bugprint("Replaced "+filename)
	table.writeEdmScreen(D.out_dir+"/"+filename, screenProperties)

	# Now add a header and exit button to this file
	if vtype == "temp":
		headerText = "Temperature Summary"
	else:
		headerText = "Water Flow Summary"
	titlebar(D.out_dir+"/"+filename,"blue",1,"$(dom)",headerText,"generic-tooltip")
	
	print "Wrote "+filename

screenProperties = '''4 0 1
beginScreenProperties
major 4
minor 0
release 1
x 100
y 100
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
title "#<SCREEN_TITLE>#"
showGrid
snapToGrid
gridSize 5
disableScroll
endScreenProperties
'''

Tooltip='''# (Related Display)
object relatedDisplayClass
beginObjectProperties
major 4
minor 0
release 0
x 0
y 0
w 96
h 26
fgColor index 14
bgColor index 0
topShadowColor index 0
botShadowColor index 14
font "arial-medium-r-18.0"
xPosOffset -30
yPosOffset -50
button3Popup
invisible
numPvs 4
numDsps 1
displayFileName {
  0 "generic-#<VTYPE>#-tooltip"
}
setPosition {
  0 "button"
}
endObjectProperties
'''

RD='''# (Related Display)
object relatedDisplayClass
beginObjectProperties
major 4
minor 0
release 0
x 0
y 0
w 96
h 26
fgColor index 14
bgColor index 0
topShadowColor index 0
botShadowColor index 14
font "arial-medium-r-12.0"
invisible
buttonLabel "component screen"
numPvs 4
numDsps 1
displayFileName {
  0 "#<FILE>#"
}
symbols {
  0 "@#<P>#.subst"
}
endObjectProperties
'''

tempSymbol='''# (Symbol)
object activeSymbolClass
beginObjectProperties
major 4
minor 0
release 0
x 70
y 0
w 20
h 20
file "symbols-traffic-light-symbol.edl"
numStates 4
minValues {
  0 -1
  2 4
  3 3
}
maxValues {
  1 3
  2 5
  3 4
}
controlPvs {
  0 "$(temp).STAT"
}
numPvs 1
useOriginalSize
useOriginalColors
fgColor index 3
bgColor index 0
endObjectProperties
'''

flowSymbol='''# (Symbol)
object activeSymbolClass
beginObjectProperties
major 4
minor 0
release 0
x 70
y 0
w 20
h 20
file "symbols-traffic-light-symbol.edl"
truthTable
numStates 4
minValues {
  0 -1
  1 3
  2 2
}
maxValues {
  1 4
  2 3
  3 2
}
controlPvs {
  0 "$(flow):LO"
  1 "$(flow):LOLO"
}
numPvs 2
useOriginalSize
useOriginalColors
fgColor index 3
bgColor index 0
endObjectProperties
'''

tempVal='''# (Text Monitor)
object activeXTextDspClass:noedit
beginObjectProperties
major 4
minor 1
release 0
x 25
y 2
w 40
h 18
controlPv "$(temp)"
font "arial-bold-r-14.0"
fontAlign "right"
fgColor index 14
bgColor index 0
useDisplayBg
limitsFromDb
nullColor index 0
useHexPrefix
showUnits
newPos
objType "monitors"
endObjectProperties
'''

Label='''# (Static Text)
object activeXTextClass
beginObjectProperties
major 4
minor 1
release 0
x 0
y 2
w 60
h 18
font "arial-bold-r-14.0"
fgColor index 14
bgColor index 0
useDisplayBg
value {
  "$(label):"
}
endObjectProperties
'''

Text_title='''# (Static Text)
object activeXTextClass
beginObjectProperties
major 4
minor 1
release 0
x 0
y 0
w 90
h 20
font "arial-bold-r-14.0"
fontAlign "center"
fgColor index 14
bgColor index 0
useDisplayBg
value {
  "#<NAME>#"
}
endObjectProperties
'''

deviceTooltip='''# (Related Display)
object relatedDisplayClass
beginObjectProperties
major 4
minor 0
release 0
x 0
y 0
w 96
h 26
fgColor index 14
bgColor index 0
topShadowColor index 0
botShadowColor index 14
font "arial-medium-r-12.0"
xPosOffset -70
yPosOffset 90
button3Popup
invisible
buttonLabel "tooltip"
numPvs 4
numDsps 1
displayFileName {
  0 "symbols-tooltip-symbol"
}
setPosition {
  0 "button"
}
symbols {
  0 "P=#<P>#"
}
endObjectProperties
'''
