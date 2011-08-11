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
from sys_command import Command

###############################################################################
########################### Command Classes Go Here ###########################
###############################################################################
# Insert the commands you want visable to the system here in the order you want
# them to appear when listed.

class AddCompType (Command) :
	'''Add a component type to a project.'''

	type = "add_component"

	def run(self, args, aProject, userConfig) :
		super(AddCompType, self).run(args, aProject, userConfig)
		if len(args) :
			ct = args[1]
			if ct in aProject.componentTypeList :
				if aProject.addComponentType(ct) :
					aProject.writeToLog('LOG', 'Added [' + ct + '] component type to project.', 'bookTex_command.AddCompType')
				else :
					aProject.writeToLog('ERR', 'Failed to add component type [' + ct + '] to project.', 'bookTex_command.AddCompType')
			else :
				aProject.writeToLog('ERR', 'Invalid component type: [' + ct + ']', 'bookTex_command.AddCompType')

	def setupOptions(self, parser) :
		self.parser.add_option("-t", "--type", type="string", action="store", help="The type of component to be added to the project.")


class ChangeProjSettings (Command) :
	'''Change a system setting.'''

	type = "project_change"

	def run(self, aProject, args) :
		super(ChangeProjSettings, self).run(aProject, args)
		aProject.changeProjectSetting()



	def setupOptions(self, parser) :
		self.parser.add_option("--projectName", action="store", help="Change the name of the current project.")
		self.parser.add_option("--projectID", action="store", help="Change the ID code of the current project.")


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
