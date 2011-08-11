#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110811
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project infrastructure tasks.

# History:
# 20110811 - djd - Initial draft


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, sys

# Load the local classes
from usfmTex_command import Command
from project import Project


###############################################################################
############################ Define Global Functions ##########################
###############################################################################

# These root level functions work at a fundamental level of the system


###############################################################################
################################## Begin Class ################################
###############################################################################

class UsfmTex (Project) :

	def __init__(self, projConfig, userConfig, projHome, userHome, tipeHome) :
		'''Initialize this class.'''

		# Make it available to the Project Class with this
		super(UsfmTex, self).__init__(projConfig, userConfig, projHome, userHome, tipeHome)

		# Set class vars
		self._projConfig = projConfig
		self._userConfig = userConfig
		self.projHome = projHome
		self.userHome = userHome
		self.tipeHome = tipeHome




###############################################################################
############################# Begin Main Functions ############################
###############################################################################


	def addComponent (self, comp) :
		'''Add a component to the current project.'''


		print "Adding component type", comp

		self.initComponent(comp)

		return True


	def initComponent (self, comp) :
		'''Initialize a component in this project.  This will put all the files
		in place for this type of component so it can be rendered.'''

		print "initializing this component:", comp



