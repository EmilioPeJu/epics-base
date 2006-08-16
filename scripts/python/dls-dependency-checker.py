#!/bin/env python2.4

"""
dls-dependency-checker.py
Author: Tom Cobb

Checks a module for clashes and suggests an updated configure/RELEASE file if updates exist
"""

import os, sys, signal, string, new
from optparse import OptionParser
from qt import *
from dlsreleasetree import *

def nothing():
	"just to poll the python interpreter"
	pass

def uiload(filename, ns = {}):
    "run pyuic to compile form into new namespace"
    from subprocess import Popen, PIPE
    pyuic = Popen(["pyuic", filename], stdout = PIPE, stderr = PIPE)
    (stdout, stderr) = pyuic.communicate()
    if pyuic.returncode != 0:
        raise Exception(stderr)
    exec stdout in ns
    return ns

def catchbreak():
	"poll the interpreter 1s period to catch ctrl-C"
	background = QTimer(qApp)
	QObject.connect(background, SIGNAL("timeout()"), nothing)
	background.start(1000)
	# this signal handler is only serviced inside the python interpreter
	signal.signal(signal.SIGINT, lambda *args: qApp.exit())

class ButtonListItem(QListViewItem):
	"List view item with Diamond mouseover colours"
	def paintCell(self, painter, cg, column, width, align):
		# taken from Diamon web page css
		grp = QColorGroup(cg)
		grp.setColor(QColorGroup.Base, self.base_color)
		grp.setColor(QColorGroup.Text, self.text_color)
		QListViewItem.paintCell(self, painter, grp, column, width, align)

def init_tree_view(list_view,tree):
	list_view.tree = tree
	list_view.clashes = tree.clashes(ignore_warnings=True)
	list_view.setRootIsDecorated(True)
	list_view.setSorting(-1)
	# bind functions to instances of select, mousein, mouseout
	list_view.select = new.instancemethod(tree_view_select, list_view, QListView)
	list_view.mousein = new.instancemethod(tree_view_mousein, list_view, QListView)
	list_view.mouseout = new.instancemethod(tree_view_mouseout, list_view, QListView)
	# connect event handlers
	QObject.connect(list_view, SIGNAL("clicked(QListViewItem *)"), list_view.select)
	QObject.connect(list_view, SIGNAL("onItem(QListViewItem *)"), list_view.mousein)
	QObject.connect(list_view, SIGNAL("onViewport()"), list_view.mouseout)
	build_gui_tree(list_view,tree)
	list_view.setOpen(list_view.child,True)
	return list_view

def build_gui_tree(list_view,tree,parent=None):
	if parent:
		child = ButtonListItem(parent, tree.name+": "+tree.version)
	else:
		child = ButtonListItem(list_view, tree.name+": "+tree.version)
		list_view.child = child
	child.tree = tree
	child.setSelectable(False)
	child.text_color = Qt.black
	child.base_color = QColor(212,216,236) #normal
	open_parents = False
	if tree.latest_version():
		child.text_color = Qt.white
		child.base_color = QColor(23,125,23) #update available - green
		open_parents = True
	if tree.name in list_view.clashes.keys():
		if not tree.latest_version():
			child.text_color = Qt.black
			child.base_color = QColor(225,225,125) #clash in module with same name 
			open_parents = True
		else:
			child.text_color = Qt.white
			child.base_color = QColor(125,23,23) #clash - red
			open_parents = True
	if open_parents: 
		temp_ob = child
		while temp_ob.parent():
			list_view.setOpen(temp_ob.parent(),True)
			temp_ob = temp_ob.parent()
	for leaf in tree.leaves:
		build_gui_tree(list_view,leaf,child)
								
def tree_view_select(self, item):
	# print the current cell
	if item:
		print str(item.tree)
			
def tree_view_mouseout(self):
	# deselect items
	self.top.statusBar().message("")
			
def tree_view_mousein(self, item):
	# highlight item
	text = item.tree.name+" - current: "+item.tree.version
	if item.tree.latest_version():
		text += ", latest: "+item.tree.latest_version()
	self.top.statusBar().message(text)

def make_write_function(update):
	def function():
		response=QMessageBox.question(None,"Write Changes","Would you like to write your changes to configure/RELEASE?",QMessageBox.Yes,QMessageBox.No)
		if response == QMessageBox.Yes:
			update.write_changes()
	return function

def release_tree_gui():
	parser = OptionParser("usage: %prog [options] <module_path>")
#	parser.add_option("-t", action="store_true", dest="text", help="Use the text-based command line browser")
	(options, args) = parser.parse_args()
	if len(args) != 1:
		if len(args) == 0:
			path = os.getcwd()
		else:
			print >> sys.stderr, "***Error: Incorrect number of arguments. Type %prog -h for help"
			sys.exit()
	else:
		path = args[0]
		
	namespace = uiload(os.path.dirname(sys.argv[0])+"/dls-dependency-checker.ui")
	app = QApplication([])
	top = namespace["Form1"]
	top = top()
	tree = release_tree(None,path)
	top.setCaption("Tree Browser - "+tree.name+": "+tree.version+", Epics:"+tree.epics_version)
	left = init_tree_view(top.listView1,tree)
	left.top = top
	update = tree_update(tree)
	changes = update.changes()
	write_function = make_write_function(update)
	if changes:
		middle = init_tree_view(top.listView2,update.tree)
		middle.top = top
		QObject.connect(top.write2, SIGNAL("clicked()"), write_function)
		QObject.connect(top.print2, SIGNAL("clicked()"), update.print_changes)
	else:
		top.listView2.setEnabled(False)
		top.print2.setEnabled(False)
		top.write2.setEnabled(False)
	update_no_check = tree_update(tree,no_check=True)
	changes = update_no_check.changes()
	write_function2 = make_write_function(update_no_check)
	if changes and not update.tree.equals(update_no_check.tree):
		right = init_tree_view(top.listView3,update_no_check.tree)
		right.top = top
		QObject.connect(top.write3, SIGNAL("clicked()"), write_function2)
		QObject.connect(top.print3, SIGNAL("clicked()"), update_no_check.print_changes)
	else:
		top.listView3.setEnabled(False)
		top.print3.setEnabled(False)
		top.write3.setEnabled(False)
#	top.setSize(1000,900)
	top.show()
	app.setMainWidget(top)
	catchbreak()
	app.exec_loop()
														
if __name__ == "__main__":
	release_tree_gui()
