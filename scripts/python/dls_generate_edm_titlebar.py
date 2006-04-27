#!/bin/env python

import os
from optparse import OptionParser
from dlsxmlparserfunctions import *

def titlebar(filename,colour="blue",htype=1,buttonText="$(dom)",headerText="Temperature Summary",buttonPV="$(P):NAME",headerPV="$(P):NAME.DESC",tooltipFilename="generic-tooltip"):

	####################
	# hardcoded fields #
	####################
	incryheader = 30
	incryspacer = 10
	incrxspacer = 10
	exitw = 95
	exith = 25
	min_title_width = 210

	##############
	# initialise #
	##############	
	i = 0
	lasty = 0
	maxy = 0
	lastx = 0
	maxx = 0
	lastw = 0
	lasth = 0
	points = []
	
	# Flag used to ignore initial screen size
	flag = False

	if colour=="blue":
		col1 = "48"
		col2 = "49"
	else:
		col1 = "53"
		col2 = "54"

	input = open(filename,"r")
	lines = input.readlines()
	input.close()
	output = open(filename,"w")

	# 1st iteration to find max x and y
	while i<len(lines):
		if lines[i][:2]=="x ":
			lastx = int(lines[i][2:])
		elif lines[i][:2]=="y ":
			lasty = int(lines[i][2:])
		elif lines[i][:2]=="w ":
			lastw = int(lines[i][2:])
			if flag==True:
				maxx = max(maxx,lastw+lastx)
		elif lines[i][:2]=="h ":
			lasth = incryheader + int(lines[i][2:])
			if flag==False:
				flag=True
			else:
				maxy = max(maxy,lasth+lasty)
				# add the bottom right point to the list of points to determine where the exit button goes
				points.append((lastx+lastw,lasty+lasth))
		i+=1
	i=0
	
	# 2nd interation to find width and height, then modify each y value to make room for header
	while not lines[i][:2]=="w ":
		output.write(lines[i])
		i += 1
	w = max(int(lines[i][2:]),min_title_width)
	i+=1
	while not lines[i][:2]=="h ":
		output.write(lines[i])
		i += 1
	i+=1
	exit_button_x = max(maxx + incrxspacer,min_title_width) - exitw - 5
	exit_button_y = maxy + incryspacer - exith - 5
	for x,y in points:
		if x > exit_button_x-incrxspacer and y > exit_button_y-incryspacer:
			exit_button_y = y +incryspacer
	w = exit_button_x+exitw+5
	h = exit_button_y+exith+5
	output.write("w "+str(w)+"\n")
	output.write("h "+str(h)+"\n")
	while i < len(lines):
		if lines[i][:2]=="y ":
			output.write("y "+str(int(lines[i][2:])+incryheader)+"\n")
		else:
			output.write(lines[i])
		i+=1
	output.write(exitButton.replace('#<X>#',str(exit_button_x)).replace('#<Y>#',str(exit_button_y)).replace('#<exitw>#',str(exitw)).replace('#<exith>#',str(exith)))
	output.write(eval("titlebar"+str(htype)).replace('#<W>#',str(w)).replace("#<tooltipFilename>#",tooltipFilename).replace("#<buttonText>#",buttonText).replace("#<headerText>#",headerText).replace("#<buttonPV>#",buttonPV).replace("#<headerPV>#",headerPV).replace("#<col2>#",col2).replace("#<col1>#",col1))
	output.close()


def main():
	usage = """usage: ./%prog [options] <input_screen_filename>
Adds a titlebar and exit button to the screen saving it under the same filename"""
	parser = OptionParser(usage)
	D = table_handler(".","",True)
	(options, args) = parser.parse_args()
	if len(args) != 1:
		D.errorprint("*** Error: Incorrect number of arguments - run the program with --help for help")
	titlebar(args[0])


exitButton = """# (Exit Button)
object activeExitButtonClass
beginObjectProperties
major 4
minor 1
release 0
x #<X>#
y #<Y>#
w #<exitw>#
h #<exith>#
fgColor index 46
bgColor index 3
topShadowColor index 1
botShadowColor index 11
label "EXIT"
font "arial-medium-r-18.0"
3d
endObjectProperties

"""


titlebar1 = """# (Group)
object activeGroupClass
beginObjectProperties
major 4
minor 0
release 0
x 0
y 0
w #<W>#
h 30

beginGroup

# (Related Display)
object relatedDisplayClass
beginObjectProperties
major 4
minor 0
release 0
x 0
y 0
w #<W>#
h 30
fgColor index 14
bgColor index 3
topShadowColor index 0
botShadowColor index 14
font "arial-medium-r-18.0"
xPosOffset 5
yPosOffset 5
button3Popup
invisible
buttonLabel "tooltip"
numPvs 4
numDsps 1
displayFileName {
  0 "#<tooltipFilename>#"
}
setPosition {
  0 "button"
}
endObjectProperties

# (Rectangle)
object activeRectangleClass
beginObjectProperties
major 4
minor 0
release 0
x 0
y 0
w #<W>#
h 30
lineColor index 3
fill
fillColor index 3
endObjectProperties

# (Lines)
object activeLineClass
beginObjectProperties
major 4
minor 0
release 1
x 0
y 3
w #<W>#
h 24
lineColor index 11
fillColor index 0
numPoints 3
xPoints {
  0 0
  1 #<W>#
  2 #<W>#
}
yPoints {
  0 27
  1 27
  2 3
}
endObjectProperties

# (Static Text)
object activeXTextClass
beginObjectProperties
major 4
minor 1
release 0
x 0
y 3
w #<W>#
h 24
font "arial-bold-r-16.0"
fontAlign "center"
fgColor index 14
bgColor index #<col1>#
value {
  "#<headerText>#"
}
endObjectProperties

# (Lines)
object activeLineClass
beginObjectProperties
major 4
minor 0
release 1
x 0
y 3
w #<W>#
h 24
lineColor index 1
fillColor index 0
numPoints 3
xPoints {
  0 0
  1 0
  2 #<W>#
}
yPoints {
  0 27
  1 3
  2 3
}
endObjectProperties

endGroup

endObjectProperties

# (Group)
object activeGroupClass
beginObjectProperties
major 4
minor 0
release 0
x 0
y 0
w 50
h 31

beginGroup

# (Circle)
object activeCircleClass
beginObjectProperties
major 4
minor 0
release 0
x 2
y 2
w 48
h 29
lineColor index 11
fillColor index 63
lineWidth 2
endObjectProperties

# (Circle)
object activeCircleClass
beginObjectProperties
major 4
minor 0
release 0
x 0
y 0
w 48
h 29
lineColor index 1
fillColor index 63
lineWidth 2
endObjectProperties

# (Circle)
object activeCircleClass
beginObjectProperties
major 4
minor 0
release 0
x 2
y 2
w 47
h 27
lineColor index #<col2>#
fill
fillColor index #<col1>#
lineWidth 3
endObjectProperties

# (Circle)
object activeCircleClass
beginObjectProperties
major 4
minor 0
release 0
x 12
y 6
w 4
h 3
lineColor index 1
fill
fillColor index 0
lineWidth 2
endObjectProperties

# (Static Text)
object activeXTextClass
beginObjectProperties
major 4
minor 1
release 0
x 0
y 0
w 50
h 30
font "arial-bold-r-14.0"
fontAlign "center"
fgColor index 14
bgColor index 0
useDisplayBg
value {
  "#<buttonText>#"
}
endObjectProperties

endGroup

endObjectProperties

"""

titlebar2 ='''# (Group)
object activeGroupClass
beginObjectProperties
major 4
minor 0
release 0
x 25
y 0
w #<W>#
h 30
beginGroup

# (Related Display)
object relatedDisplayClass
beginObjectProperties
major 4
minor 0
release 0
x 0
y 0
w #<W>#
h 30
fgColor index 14
bgColor index 3
topShadowColor index 0
botShadowColor index 14
font "arial-medium-r-18.0"
xPosOffset 5
yPosOffset 5
button3Popup
invisible
buttonLabel "tooltip"
numPvs 4
numDsps 1
displayFileName {
  0 "#<tooltipFilename>#"
}
setPosition {
  0 "button"
}
endObjectProperties

# (Rectangle)
object activeRectangleClass
beginObjectProperties
major 4
minor 0
release 0
x 15
y 0
w #<W>#
h 30
lineColor index 3
fill
fillColor index 3
endObjectProperties

# (Lines)
object activeLineClass
beginObjectProperties
major 4
minor 0
release 1
x 0
y 3
w #<W>#
h 24
lineColor index 11
fillColor index #<col1>#
fill
numPoints 3
xPoints {
  0 0
  1 #<W>#
  2 #<W>#
}
yPoints {
  0 27
  1 27
  2 3
}
endObjectProperties

# (Textupdate)
object TextupdateClass
beginObjectProperties
major 10
minor 0
release 0
x 15
y 3
w #<W>#
h 24
controlPv "#<headerPV>#"
fgColor index 14
fgAlarm
bgColor index 48
fill
font "arial-bold-r-14.0"
fontAlign "center"
endObjectProperties

# (Lines)
object activeLineClass
beginObjectProperties
major 4
minor 0
release 1
x 0
y 3
w #<W>#
h 24
lineColor index 1
fillColor index 0
numPoints 3
xPoints {
  0 0
  1 0
  2 #<W>#
}
yPoints {
  0 27
  1 3
  2 3
}
endObjectProperties

endGroup

endObjectProperties

# (Group)
object activeGroupClass
beginObjectProperties
major 4
minor 0
release 0
x 0
y 0
w 50
h 30

beginGroup

# (Related Display)
object relatedDisplayClass
beginObjectProperties
major 4
minor 0
release 0
x 4
y 4
w 42
h 24
fgColor index 14
bgColor index 0
topShadowColor index 0
botShadowColor index 14
font "arial-medium-r-18.0"
invisible
buttonLabel "Engineering drawing"
numPvs 4
numDsps 1
displayFileName {
  0 "generic-help"
}
symbols {
  0 "draw=$(P).png"
}
endObjectProperties

# (Circle)
object activeCircleClass
beginObjectProperties
major 4
minor 0
release 0
x 2
y 2
w 48
h 29
lineColor index 11
fillColor index 63
lineWidth 2
endObjectProperties

# (Circle)
object activeCircleClass
beginObjectProperties
major 4
minor 0
release 0
x 0
y 0
w 48
h 29
lineColor index 1
fillColor index 63
lineWidth 2
endObjectProperties

# (Circle)
object activeCircleClass
beginObjectProperties
major 4
minor 0
release 0
x 2
y 2
w 47
h 27
lineColor index 49
fill
fillColor index 48
lineWidth 3
endObjectProperties

# (Circle)
object activeCircleClass
beginObjectProperties
major 4
minor 0
release 0
x 12
y 6
w 4
h 3
lineColor index 1
fill
fillColor index 0
lineWidth 2
endObjectProperties

# (Textupdate)
object TextupdateClass
beginObjectProperties
major 10
minor 0
release 0
x 0
y 0
w 50
h 30
controlPv "#<buttonPV>#"
fgColor index 14
fgAlarm
bgColor index 0
font "arial-bold-r-14.0"
fontAlign "center"
endObjectProperties

endGroup

endObjectProperties
'''

if __name__ == "__main__":
	main()
