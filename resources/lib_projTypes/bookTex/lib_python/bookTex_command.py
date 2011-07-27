#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110727
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle system process commands.  This relys a lot on the
# optparse lib.  Documentation can be found here:
# http://docs.python.org/library/optparse.html

# History:
# 20110727 - djd - Begin initial draft


###############################################################################
################################# Command Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os
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
	'''The main command object class.'''

	__metaclass__ = MetaCommand
	type = None

	# Intitate the whole class
	def __init__(self) :
		self.parser = OptionParser(self.__doc__)
		self.setupOptions(self.parser)

	def run(self, aProject, args) :
		(self.options, self.args) = self.parser.parse_args(args = args)

	def setupOptions(self, parser) :
		pass

	def help(self) :
		self.parser.print_help()


###############################################################################
########################### Command Classes Go Here ###########################
###############################################################################
# Insert the commands you want visable to the system here in the order you want
# them to appear when listed.


class ChangeProjSettings (Command) :
	'''Change a system setting.'''

	type = "project_change"

	def run(self, aProject, args) :
		super(ChangeProjSettings, self).run(aProject, args)
		aProject.changeProjectSetting(args[0][2:], args[1])

	def setupOptions(self, parser) :
#        self.parser.add_option("--userName", action="store", help="Change the system user name.")
#        self.parser.add_option("--language", action="store", help="Change the interface language.")
#        self.parser.add_option("--loglimit", action="store", help="Set the number of lines the log file is allowed to have.")
		pass


# This is an example command class
#class Setup (Command) :
#    '''Setup creates a new object'''
#    type = "setup"
#    def run(self, aProject, args) :
#        super(Setup, self).run(aProject, args)
#        # do something here, options are in self.options
#
#    def setupOptions(self, parser) :
#        self.parser.add_option("-d", "--dir", type="string", action="store", help="Create project in this directory")


###############################################################################
########################### Draft Command Classes #############################
###############################################################################


class Render (Command) :
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
