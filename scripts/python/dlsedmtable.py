#!/usr/bin/env python

## \file edmTable.py
#	
#	Generates a table-structure of user defined EDM objects.
#
#	Ulrik Pedersen, Diamond
#	Version 1: January 2005
#	Version 1.1: March 2006 (UKP)
#				- First release (to /home/up45/bin/scripts )
#	Ver. 1.2 - 02.03.2006 (UKP)
#				- Added size of screen to tableTemplate
#				- Added automatic generation of screenProperties when using writeEdmScreen(outputfile)
#
#	Ver. 1.3 - 06.03.2006 (UKP)
#				- Errors and warnings changed to print to stderr instead of stdout
#				- Exit gracefully (sys.exit(1)) when a file does not want to open.
#				- changed module name from edmtable to dlsedmtable to fit DLS naming "convension".
#				- first release to makeDlsApp (first release to DLS svn environment).
#				- Moved three edm-strings from global file to be part of edmTableBuilder class.
#				  (strings: EDMscreenProperties, moduleLine and cellBorder)
#

import sys, re

## \class edmTableBuilder
#	This class will handle writing a table-style edm file with objects that can be
#	specified by the user (through another script)
# 	\var tableTemplate 'maxnumrows' integer value - is the maximum number of rows in the table. The default is 4 but can be set to whatever.
class edmTableBuilder:

	## @var cellTemplate A template for the cells.
	cellTemplate = {}
	
	## A structure where the module builds each cell with data filled in.
	#	This structure is only used internally in the module.
	cellContent = ()
	
	##	A structure the class uses to maintain the data for the whole table.
	#	This structure is only used internally in the module.
	tableContent = ()
	
	## Dictionary that contains the settings for the table.
	#	Use this structure to read (and possibly write - only recommended in few cases) the settings of the table.<BR>
	#	Available keys:
	#	- 'xoffset' (read only)
	#	- 'yoffset' (read only)
	#	- 'cellwidth' (read only)
	#	- 'cellheight' (read only)
	#	- 'colspacing' (read only)
	#	- 'rowspacing' (read only)
	#	- 'maxnumrows' write integer here to set the maximum number of rows in the table (default: 4)
	#	- 'modulelines' write False or integer value to define if module lines should be drawn between forced columnchanges. The
	#						 integer number sets the width of the line (in pixels) (default: False -> no lines)
	#	- 'cellborder' write True or False to set whether there should be drawn borders around each cell (mainly for debugging purpose) (default: False)
	tableTemplate = {}
	cellPointer = {}

## Constructor for the edmTableBuilder class.
#	\param xoffset an integer value, defining the global horizontal offset of the table (in pixels - the upper left corner)
#	\param yoffset an integer value, defining the global vertical offset of the table (in pixels - the upper left corner)
#	\param colspacing an integer value, defining the space between columns in the table (in pixels)
#	\param rowspacing an integer value, defining the space between rows in the table.
	def __init__(self, xoffset, yoffset, colspacing, rowspacing):
		self.tableTemplate['xoffset'] = xoffset
		self.tableTemplate['yoffset'] = yoffset
		self.tableTemplate['cellwidth'] = 0
		self.tableTemplate['cellheight'] = 0
		self.tableTemplate['colspacing'] = colspacing
		self.tableTemplate['rowspacing'] = rowspacing
		self.tableTemplate['maxnumrows'] = 4
		self.tableTemplate['modulelines'] = False
		self.tableTemplate['cellborder'] = True
		self.tableTemplate['screenSizeX'] = xoffset
		self.tableTemplate['screenSizeY'] = yoffset
		self.cellPointer['x'] = 0
		self.cellPointer['y'] = 0
		self.cellPointer['rownum'] = 0
		self.cellPointer['colnum'] = 0
		self.cellPointer['tableWidth'] = 0
		self.cellPointer['tableHeight'] = 0
		
## Add new objects to the cell-template.
#  Objects are graphical entities of any sort: buttons, related displays or what ever EDM supports.
#	When a new object type is added to the cell template through this function the cell measurements is recalculated to fit exactly
#  the new object as well as the existing objects.
#  \param objName an indicator of what type of object is added (could be for instance: "button", "more-button" or "my-text-box")
#  \param objTxtDef the EDM object itself. A text string with all the attributes that EDM uses defined. Tags of a user-defined
#				  format should be added to indicate where some sort of substitution should be added (for instance: <PV-NAME> or <BUTTON-LABEL>).
#				  All coordinate placement values that might be defined in the object is ignored and replaced by this script.
#  \param xCoord relative X-coordinate in the cell (In integer pixels. Must be > 0)
#  \param yCoord relative Y-coordinate in the cell (In integer pixels. Must be > 0)
	def addObjectType(self, objName, objTxtDef, xCoord, yCoord):
		# extract the width and height of the object:
		startPos = objTxtDef.find("\nw ") + len("\nw ")
		if (startPos < 0):
			print (sys.stderr, "*** WARNING: it seems there is no width defined for object \'" + objName + "\'")
			return
		objWidth = int(objTxtDef[startPos:objTxtDef.find("\n", startPos)])
		startPos = objTxtDef.find("\nh ") + len("\nh ")
		if (startPos < 0):
			print (sys.stderr, "*** WARNING: it seems there is no height defined for object \'" + objName + "\'")
			return
		objHeight = int(objTxtDef[startPos:objTxtDef.find("\n", startPos)])
		
		# Add the data to the objects data:
		self.cellTemplate[objName] = [objTxtDef, xCoord, yCoord, objWidth, objHeight]
		
		# Calculate the new cell width and height to fit all objects:
		if ((xCoord + objWidth) > self.tableTemplate['cellwidth']):
			self.tableTemplate['cellwidth'] = xCoord + objWidth
		if ((yCoord + objHeight) > self.tableTemplate['cellheight']):
			self.tableTemplate['cellheight'] = yCoord + objHeight
		
## Add special new objects to the cell-template.
#  Objects are graphical entities of any sort: buttons, related displays or what ever EDM supports.
#	When a new object type is added to the cell template through this function the cell measurements is NOT recalculated (as is the case in 
#	addObjectType() ), thus enabling bjects that might not fit inside a cell - like vacuum spaces that can be long enough to go across 
#	multiple cells.
#  \param objName an indicator of what type of object is added (could be for instance: "button", "more-button" or "my-text-box")
#  \param objTxtDef the EDM object itself. A text string with all the attributes that EDM uses defined. Tags of a user-defined
#				  format should be added to indicate where some sort of substitution should be added (for instance: <PV-NAME> or <BUTTON-LABEL>).
#				  All coordinate placement values that might be defined in the object is ignored and replaced by this script.
#  \param xCoord relative X-coordinate in the cell (In integer pixels. Must be > 0)
#  \param yCoord relative Y-coordinate in the cell (In integer pixels. Must be > 0)
	def addObjectTypeSpecial(self, objName, objTxtDef, xCoord, yCoord):
		# Add the data to the objects data:
		self.cellTemplate[objName] = [objTxtDef, xCoord, yCoord, -1, -1]

	
## Instanciate cells by filling out the user defined tags in a given object.
#	The order of which objects are filled in will effect the layering of objects on the screen: objects filled in first will be put in the
#	'lowest' layer on the screen.
#  \param objName name of the object to do tag-substitution on.
#  \param dictReplacement dictionary of tag-substitutions: the key is defined to be the tag to replace and the value is the new substitution string.
#	Note: the dictionary parameter must have both keys and values of type string!
	def fillCellContent(self, objName, dictReplacement):
		if not self.cellTemplate.has_key(objName):
			print >> std.err, "*** WARNING: There is no \'" + objName + "\' object in the cell you defined! No replacements will take place. (fillCellContent())"
			return
		
		tmpObjString = self.cellTemplate[objName][0]
		replacementTags = dictReplacement.keys()
		for tag in replacementTags:
			if (tmpObjString.find(tag) < 0):
				print >> sys.stderr, "*** WARNING: TAG: \'" + tag + "\' was not found in object \'" + objName + "\' - no replacement of this tag done... (fillCellContent())"
				break
#			print "Replace: " + tag + " with: " + dictReplacement[tag]
			tmpObjString = tmpObjString.replace(tag, dictReplacement[tag]) + "\n"
			
		# Insert the correct x and y coordinates for the object in question...
		substitutionStr = "x " + str(self.cellPointer['x'] + self.cellTemplate[objName][1])
		regexp = re.compile(r'^[xX].*', re.MULTILINE)
		tmpObjString = regexp.sub(substitutionStr, tmpObjString)
		substitutionStr = "y " + str(self.cellPointer['y'] + self.cellTemplate[objName][2])
		regexp = re.compile(r'^[yY].*', re.MULTILINE)
		tmpObjString = regexp.sub(substitutionStr, tmpObjString)
			
		# Add the newly expanded object to the cell content:
		self.cellContent += (tmpObjString,)

## Prepares an empty placeholder for a filling in the tags in the objects, defined in a cell.
#  This function should be called once before starting to fill out cells \sa fillCellContent() and then once, after filling in each cell.
	def nextCell(self):
#		if (len(self.cellContent) == 0):		# if this is the first call when starting a new table...
		if (self.cellPointer['colnum'] == 0):		# if this is the first call when starting a new table...
#			print "First cell to fill in."
			self.cellPointer['x'] = self.tableTemplate['xoffset']
			self.cellPointer['y'] = self.tableTemplate['yoffset']
			self.cellPointer['rownum'] = 0
			self.cellPointer['colnum'] = 1
			self.cellContent = ()
		else:
		
			# Add the cell border (rectangle) to the cell string:
			if (self.tableTemplate['cellborder']):
				regexp = re.compile('<XCOORD>', re.MULTILINE)
				tmpBorderStr = regexp.sub(str(self.cellPointer['x']), self.cellBorder)
				regexp = re.compile('<YCOORD>', re.MULTILINE)
				tmpBorderStr = regexp.sub(str(self.cellPointer['y']), tmpBorderStr)
				regexp = re.compile('<HEIGHT>', re.MULTILINE)
				tmpBorderStr = regexp.sub(str(self.tableTemplate['cellheight']), tmpBorderStr)
				regexp = re.compile('<WIDTH>', re.MULTILINE)
				tmpBorderStr = regexp.sub(str(self.tableTemplate['cellwidth']), tmpBorderStr)
				
				tmpCellString = tmpBorderStr
			else:
				# define (and reset) the string that will be used to add the whole cell info for the duration of this funcion call.
				tmpCellString = ""

			for objStr in self.cellContent:
				tmpCellString += objStr	

			# Clear the cellContent to be ready for filling in the next cell	
			self.cellContent = ()

			# Add the full cell-string (which includes all objects with tags filled in) to the entire table (a tuple-array)	
			self.tableContent += (tmpCellString,)
			
			# Update the size of the table
			if (self.cellPointer['y'] + self.tableTemplate['cellheight'] - self.tableTemplate['yoffset']) > self.cellPointer['tableHeight']:
				self.cellPointer['tableHeight'] = self.cellPointer['y'] + self.tableTemplate['cellheight'] - self.tableTemplate['yoffset']
			if (self.cellPointer['x'] + self.tableTemplate['cellwidth'] - self.tableTemplate['xoffset']) > self.cellPointer['tableWidth']:
				self.cellPointer['tableWidth'] = self.cellPointer['x'] + self.tableTemplate['cellwidth'] - self.tableTemplate['xoffset']
				
			# Update the size of the screen
			self.tableTemplate['screenSizeX'] = self.tableTemplate['xoffset'] + self.cellPointer['tableWidth']
			self.tableTemplate['screenSizeY'] = self.tableTemplate['yoffset'] + self.cellPointer['tableHeight']
			
			# update the cellPointer to point to the starting point of the new cell:
			if (self.cellPointer['rownum'] == self.tableTemplate['maxnumrows'] - 1):
				self.cellPointer['y'] = self.tableTemplate['yoffset']
				self.cellPointer['x'] += (self.tableTemplate['cellwidth'] + self.tableTemplate['colspacing'])
				self.cellPointer['rownum'] = 0
				self.cellPointer['colnum'] += 1
			else :
				self.cellPointer['y'] += (self.tableTemplate['cellheight'] + self.tableTemplate['rowspacing'])
				self.cellPointer['rownum'] += 1
				

	## Forces a column change when filling in the table.
	#	Can be used to start ensure different 'modules' or 'components' get their own columns.
	#	This method should be used before the first cell in the new column is filled out.
	#	\param extraColSpacing integer value that adds an extra space (in pixels) between forced columns. Thus enabling
	#	seperation of 'modules' or 'components' in the table.
	def forceNewCol(self, extraColSpacing):
		if (self.cellPointer['rownum'] != 0):
#			print "force a column-change"
			self.cellPointer['rownum'] = 0
			self.cellPointer['y'] = self.tableTemplate['yoffset']
			self.cellPointer['x'] += (self.tableTemplate['cellwidth'] + self.tableTemplate['colspacing'])
		if (self.cellPointer['colnum'] != 0):
			self.cellPointer['x'] += extraColSpacing
			if (self.tableTemplate['modulelines']):
				self.tableContent += (self.__getModuleLine(-((extraColSpacing + self.tableTemplate['colspacing'])/2)), )
		self.cellPointer['colnum'] += 1
		
	#	Setup a module-line by inserting coordinates (method is for internal use only!)
	#	This method is only used internally in the module.
	#	\param xOffset the space between the columns and this line (in pixels)
	#	\return string containing a defined EDM line with coordinates to fit between two columns.
	def __getModuleLine(self, xOffset):
		# Insert the correct x and y coordinates, line width and height for the object in question...
		lineHeight = (self.tableTemplate['cellheight'] + self.tableTemplate['rowspacing']) * self.tableTemplate['maxnumrows']
		lineWidth = self.tableTemplate['modulelines']
		regexp = re.compile('<XCOORD0>', re.MULTILINE)
		tmpModuleLineStr = regexp.sub(str(self.cellPointer['x'] + xOffset), self.moduleLine)
		regexp = re.compile('<XCOORD1>', re.MULTILINE)
		tmpModuleLineStr = regexp.sub(str(self.cellPointer['x'] + xOffset + lineWidth - 1), tmpModuleLineStr)
		regexp = re.compile('<YCOORD0>', re.MULTILINE)
		tmpModuleLineStr = regexp.sub(str(self.cellPointer['y']), tmpModuleLineStr)
		regexp = re.compile('<YCOORD1>', re.MULTILINE)	
		tmpModuleLineStr = regexp.sub(str(self.cellPointer['y'] + lineHeight), tmpModuleLineStr)
		regexp = re.compile('<HEIGHT>', re.MULTILINE)
		tmpModuleLineStr = regexp.sub(str(lineHeight), tmpModuleLineStr)
		regexp = re.compile('<WIDTH>', re.MULTILINE)
		tmpModuleLineStr = regexp.sub(str(lineWidth), tmpModuleLineStr)
		return tmpModuleLineStr

	
	## Deletes all template objects in the defined cell.
	#  Enables a full re-design of the cell-template.
	def clearCellTemplate(self):
		self.cellTemplate = {}
	
	## Removes a given object (like a button or related display) from the cell template.
	#	The function is the opposite equivalent to addObjectType(). This function is not really necessary since you can just
	#	not fill in the object you don't want to use (with fillCellContent()) since the object will then not show up in the cell.
	#	\param objName the name (string) of the object to remove from the template.
	def removeObjectType(self, objName):
		del self.cellTemplate[objName]

	## Writes the currently defined screen to a file.
	#	\param fileName the full name (and path) to a text file where the screen will be written to.
	#	If the file exists it will be overwritten without notice.
	#	\param edmFileHeader a string which is printed as first thing in the file. This string should contain
	#	the 'screen properties' of the EDM screen (defining screen size and stuff...)
	def writeEdmScreen(self, fileName, edmFileHeader):
		try:
			#print "Opening file and redirecting stdout..."
			fileHandle = open(fileName, 'w')
		except IOError:
#			print "*** Error: could not open file: " + fileName + " for writing."
			print >> sys.stderr, "*** Error (dlsedmtable module): could not open file: " + fileName + " for writing."
			sys.exit(1)
		sys.stdout = fileHandle
			
		print edmFileHeader
		for cell in self.tableContent:
			print cell

		sys.stdout.close()
		sys.stdout = sys.__stdout__
		#print "Done - EDM file written!"

	## Writes the currently defined screen to a file, making sure the resulting screen will be exactly 
	#	big enough to fit the table incl. offset.
	#	\param fileName the full name (and path) to a text file where the screen will be written to.
	#	If the file exists it will be overwritten without notice.
	def writeEdmScreenAuto(self, fileName):
		try:
			#print "Opening file and redirecting stdout..."
			fileHandle = open(fileName, 'w')
		except IOError:
#			print "*** Error: could not open file: " + fileName + " for writing."
			print >> sys.stderr, "*** Error (dlsedmtable module): could not open file: " + fileName + " for writing."
			sys.exit(1)
		sys.stdout = fileHandle
			
		# Get the size of the entire table and create an EDM screen where the table will fit exactly
		regexp = re.compile('<WIDTH>', re.MULTILINE)
		tmpScreenProperties = regexp.sub(str(self.tableTemplate['screenSizeX']), self.EDMscreenProperties)
		regexp = re.compile('<HEIGHT>', re.MULTILINE)
		tmpScreenProperties = regexp.sub(str(self.tableTemplate['screenSizeY']), tmpScreenProperties)
	
		print tmpScreenProperties
		for cell in self.tableContent:
			print cell

		sys.stdout.close()
		sys.stdout = sys.__stdout__
		#print "Done - EDM file written!"

	## Gets the full, defined EDM screen table.
	#	\return a string, containing the full EDM table.
	def getEdmScreen(self):
		returnStr = ""
		for cell in self.tableContent:
			returnStr += cell
		return returnStr
		
	EDMscreenProperties = '''4 0 1
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

	moduleLine = '''# (Lines)
object activeLineClass
beginObjectProperties
major 4
minor 0
release 1
x <XCOORD0>
y <YCOORD0>
w 5
h <HEIGHT>
lineColor index 14
fillColor index 0
lineWidth <WIDTH>
numPoints 2
xPoints {
  0 <XCOORD0>
  1 <XCOORD0>
}
yPoints {
  0 <YCOORD0>
  1 <YCOORD1>
}
endObjectProperties
'''
	cellBorder = '''# (Rectangle)
object activeRectangleClass
beginObjectProperties
major 4
minor 0
release 0
x <XCOORD>
y <YCOORD>
w <WIDTH>
h <HEIGHT>
lineColor index 14
fillColor index 0
endObjectProperties
'''

