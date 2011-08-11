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
	'''Add a component type to a project.'''

	type = "component_add"

	def run(self, args, aProject, userConfig) :
		super(AddComp, self).run(args, aProject, userConfig)
		if len(args) :
			ct = args[1]

			print 'Adding a component'

	def setupOptions(self, parser) :
		self.parser.add_option("-c", "--component", type="string", action="store", help="Add a component to the project.")



