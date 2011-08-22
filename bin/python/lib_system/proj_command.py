#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110721
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project level commands.  This relys on the optparse
# lib.  Documentation can be found here:
# http://docs.python.org/library/optparse.html


# History:
# 20110721 - djd - Begin initial draft


###############################################################################
################################# Command Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

from optparse import OptionParser
from sys_command import Command, commands


###############################################################################
########################### Command Classes Go Here ###########################
###############################################################################
# Insert the commands you want visable to the system here in the order you want
# them to appear when listed.


class ChangeProjSettings (Command) :
	'''Change a system setting.'''

	type = "project_settings_change"

	def run(self, aProject, args) :
		super(ChangeProjSettings, self).run(aProject, args)
		aProject.changeProjectSetting(self.options.pname, self.options.pid)

	def setupOptions(self, parser) :
		self.parser.add_option("-n", "--pname", action="store", help="Change the name of the current project.")
		self.parser.add_option("-i", "--pid", action="store", help="Change the ID code of the current project.")


class PreProcess (Command) :
	'''Preprocess a component'''

	type = "component_preprocess"

	def run(self, args, aProject, userConfig) :
		super(PreProcess, self).run(args, aProject, userConfig)
		if len(args) :
			aProject.preProcessComp(self.options.component)

	def setupOptions(self, parser) :
		self.parser.add_option("-c", "--component", type="string", action="store", help="Preprocess a component in the project.")


class AddComp (Command) :
	'''Add a component to a project.'''

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
	'''Remove a component from a project.'''

	type = "component_remove"

	def run(self, args, aProject, userConfig) :
		super(RemoveComp, self).run(args, aProject, userConfig)
		if len(args) :
			aProject.removeComponent(self.options.component)

	def setupOptions(self, parser) :
		self.parser.add_option("-c", "--component", type="string", action="store", help="Add a component or group of components to the project.")



