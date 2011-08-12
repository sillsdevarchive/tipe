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

class AddComps (Command) :
	'''Add specific components (one or more) to a project.  The component type
	modules should already exist for this component.'''

	type = "component_add"

	def run(self, args, aProject, userConfig) :
		super(AddComps, self).run(args, aProject, userConfig)

		comps = []
		if len(args) :
			# Build a list of components to add from the command line
			for comp in args :
				if comp != '-c' :
					comps.append(comp)

		aProject.addNewComponents(comps)


	def setupOptions(self, parser) :
		self.parser.add_option("-c", "--component", type="string", action="append", help="Add a component or group of components to the project.")


class RemoveComps (Command) :
	'''Remove specific components (one or more) from the current project.'''

	type = "component_remove"

	def run(self, args, aProject, userConfig) :
		super(RemoveComps, self).run(args, aProject, userConfig)

		comps = []
		if len(args) :
			# Build a list of components to remove from the command line
			for comp in args :
				if comp != '-c' :
					comps.append(comp)

		aProject.removeComponents(comps)

	def setupOptions(self, parser) :
		self.parser.add_option("-c", "--component", type="string", action="append", help="Remove a component or group of components from the project.")



