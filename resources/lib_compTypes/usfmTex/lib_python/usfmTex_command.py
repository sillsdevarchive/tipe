#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110811
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle system process commands.  This relys a lot on the
# optparse lib.  Documentation can be found here:
# http://docs.python.org/library/optparse.html

# History:
# 20110811 - djd - Begin initial draft


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

class AddComp (Command) :
	'''Add a specific component to a project.  The component type does not
	necessarily need to be added to the project.  That will be added when the
	component is initiated.  This will only add one component at a time as
	opposed to the remove function which will remove multiple components.'''

	type = "component_add"

	def run(self, args, aProject, userConfig) :
		super(AddComp, self).run(args, aProject, userConfig)

		if len(args) :
			aProject.addNewComponent(self.options.component, self.options.type, self.options.source)

	def setupOptions(self, parser) :
		self.parser.add_option("-c", "--component", type="string", action="store", help="Add a component or group of components to the project.")
		self.parser.add_option("-t", "--type", type="string", action="store", help="Specify the component type. It needs to be valid but not present in the project.")
		self.parser.add_option("-s", "--source", type="string", action="store", help="Specify a valid source file for this component.")


class RemoveComp (Command) :
	'''Remove specific component from the current project.'''

	type = "component_remove"

	def run(self, args, aProject, userConfig) :
		super(RemoveComp, self).run(args, aProject, userConfig)

		if len(args) :
			aProject.removeComponent(self.options.component)

	def setupOptions(self, parser) :
		self.parser.add_option("-c", "--component", type="string", action="store", help="Remove a component from the current project.")



