import os
from dlsxmlparserfunctions import *

def titlebar(filename,colour="blue",htype=1,buttonText="$(dom)",headerText="Temperature Summary",tooltipFilename="generic-tooltip"):
	incryheader = 40
	incryspacer = 10
	exitw = 95
	exith = 25
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
	i = 0
	lasty = 0
	maxy = 0
	flag = False
	while i<len(lines):
		if lines[i][:2]=="y ":
			lasty = int(lines[i][2:])
		elif lines[i][:2]=="h ":
			if flag==False:
				flag=True
			else:
				maxy = max(maxy,int(lines[i][2:])+lasty)
		i+=1
	i=0
	while not lines[i][:2]=="w ":
		output.write(lines[i])
		i += 1
	w = int(lines[i][2:])
	output.write(lines[i])
	i+=1
	while not lines[i][:2]=="h ":
		output.write(lines[i])
		i += 1
	h = int(lines[i][2:])
	i+=1
	output.write("h "+str(maxy+incryheader+incryspacer+exith+5)+"\n")
	while i < len(lines):
		if lines[i][:2]=="y ":
			output.write("y "+str(int(lines[i][2:])+incryheader)+"\n")
		else:
			output.write(lines[i])
		i+=1
	output.write(exitButton.replace('#<X>#',str(w-exitw-5)).replace('#<Y>#',str(maxy+incryheader+incryspacer)).replace('#<exitw>#',str(exitw)).replace('#<exith>#',str(exith)))
	if htype==1:
		output.write(titlebar1.replace('#<W>#',str(w)).replace("#<tooltipFilename>#",tooltipFilename).replace("#<buttonText>#",buttonText).replace("#<headerText>#",headerText).replace("#<col2>#",col2).replace("#<col1>#",col1))
	output.close()



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
