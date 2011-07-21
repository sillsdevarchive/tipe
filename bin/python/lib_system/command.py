#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110721
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle system process commands.

# History:
# 20110721 - djd - Begin initial draft


###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os
from optparse import OptionParser

# Load the local classes

commands = {}

class MetaCommand(type) :

	def __init__(c, namestring, t, d) :
		global commands
		super(MetaCommand, c).__init__(namestring, t, d)
		if c.type :
			commands[c.type] = c.__call__()

class Command (object) :
	'''Documentation goes here'''
	__metaclass__ = MetaCommand
	type = None

	# Intitate the whole class
	def __init__(self) :
		self.parser = OptionParser(self.__doc__)
		self.setupOptions(self.parser)

	def run(self, args) :
		(self.options, self.args) = self.parser.parse_args(args = args)

	def setupOptions(self, parser) :
		pass

	def help(self) :
		self.parser.print_help()

class Setup (Command) :
	'''Setup creates a new object'''
	type = "setup"

	def run(self, args) :
		super(Setup, self).run(args)
		# do something here, options are in self.options

	def setupOptions(self, parser) :
		self.parser.add_option("-d", "--dir", action="store", help="Create project in this directory")

class Run () :
	'''Documentation goes here'''

	def __init__(self) :
		pass


class Help (Command) :
	'''Documentation goes here'''
	type = "help"

	def run(self, args) :
		global commands
		if len(args) :
			cmd = commands[args[0]]
			cmd.help()
		else :
			for c in commands.keys() :
				print c

###############################################################################
####################### TIPE System Command Classes ###########################
###############################################################################

# Here go all the command classes that TIPE knows how to use.  If it isn't
# defined here, it will not work.  The documentation for each command goes in
# the command so when the user types 'help' followed by the command they will
# get whatever documentation there is for that command.


class ChangeSettings (object) :
	'''Documentation goes here'''

	def changeSystemSetting (self, argv) :
		'''Change specific global system default settings in TIPE.'''

		if self.changeSystemDefault(argv) :
			self.writeToLog('MSG', 'Setting changed.')


class GUIManager (object) :
	'''Documentation goes here'''

	def tipeManager (self, argv) :
		'''Usage: tipeManager | Start the TIPE Manager GUI'''

		self.terminal('SORRY: Manager GUI has not been implemented yet.')


class CreateProject (object) :
	'''Documentation goes here'''

	def newProject (self, argv) :
		'''Usage: newProject ProjectType [ProjectName] | Setup a new project in the
		current directory.'''

		if self.makeProject(argv) :
				self.writeToLog('MSG', 'Created new project at: ' + os.getcwd(), 'project.newProject()')


class RemoveProject (object) :
	'''Documentation goes here'''

	def removeProject (self) :
		'''Usage: removeProject ProjectType | Remove an existing project in
		the current directory.'''

		if self.removeProject() :
				self.writeToLog('MSG', 'Removed project at: ' + os.getcwd(), 'project.removeProject()')


class RestoreProject (object) :
	'''Documentation goes here'''

	def restoreProject (self) :
		'''Usage: restorProject -pid | Restore an existing project in
		the current directory.'''

		if self.restoreProject() :
				self.writeToLog('MSG', 'Restored project at: ' + os.getcwd(), 'project.restoreProject()')


class Render (object) :
	'''Documentation goes here'''

	def render(self, argv) :
		'''Usage: render [compID] | Render the current component.'''

		mod = 'tipe.render()'

		# First check our project setup and try to auto correct any problems that
		# might be caused from missing project assets.  This can include files
		# like.sty, .tex, .usfm, and folders, etc.
		if not self.checkProject(aProject.self) :
			self.writeToLog('ERR', 'No project found!', mod)
			return

		aDoc = self.getDoc(argv[0])
		if not aDoc :
			self.writeToLog('ERR', 'Component [' + argv[0] + '] not found in project', mod)
			return

		#FIXME: What does this next line do?
		aDoc.render()

		# Create the makefile for processing this particular component.  This is
		# done every time TIPE is run.
		if aDoc.createMakefile(thisComponent, command) :
			if runMake() :
				self.writeToLog('MSG', 'Process completed successful!', mod)
			else :
				self.writeToLog('ERR', 'Process did not complete successfuly. Check logs for more information.', mod)

		# Collect the results and report them in the log

		return True
