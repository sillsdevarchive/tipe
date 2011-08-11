#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110728
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project infrastructure tasks.

# History:
# 20110728 - djd - Initial draft


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, sys
#from datetime import *
#from configobj import ConfigObj, Section

# Load the local classes
from bookTex_command import Command
from project import Project


###############################################################################
############################ Define Global Functions ##########################
###############################################################################

# These root level functions work at a fundamental level of the system


###############################################################################
################################## Begin Class ################################
###############################################################################

class BookTex (Project) :

	def __init__(self, projConfig, userConfig, projHome, userHome, tipeHome) :
		'''Initialize this class.'''

		# Make it available to the Project Class with this
		super(BookTex, self).__init__(projConfig, userConfig, projHome, userHome, tipeHome)

		# Set class vars
		self._projConfig = projConfig
		self._userConfig = userConfig
		self.projHome = projHome
		self.userHome = userHome
		self.tipeHome = tipeHome




###############################################################################
############################# Begin Main Functions ############################
###############################################################################


	def addComponentType (self, ctype) :
		'''Add a component type to the current project.  Before doing so, it
		must varify that the requested component type is valid to add to this
		type of project.'''

		compTypeList = []
		compTypeList = self._projConfig['ProjectInfo']['projectComponentTypes']
		if not ctype in compTypeList :
			compTypeList.append(ctype)
			self._projConfig['ProjectInfo']['projectComponentTypes'] = compTypeList
			self._projConfig['ProjectInfo']['writeOutProjConfFile'] = True
		else :
			self.writeToLog('MSG', 'Component type: [' + ctype + '] already exsits.', 'bookTex.addComponentType()')

		print "Adding component type", ctype

		self.initComponentType(ctype)

		return True


	def initComponentType (self, ctype) :
		'''Initialize a component type in this project.  This will copy all the
		necessary files and folders into the project to support the processing
		of this component type.'''

		print "init component type", ctype


#    def loadComponents (self) :
#        '''Load all the components for a project.'''
#
#        # Start by loading all the component types for this project.
#        self.loadComponentTypes()
#
#        # Load Components
#        print 'Loading project components. (Not working!)'
#
#        return True
#
#
#    def loadComponentTypes (self) :
#        '''Load the component type classes for this project.'''
#
#        print 'Loading project component types. (Not working!)'
#
#        return True
