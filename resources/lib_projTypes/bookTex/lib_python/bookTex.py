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
		super(BookTex, self).__init__(projConfig, userConfig, projHome, userHome, tipeHome)
		# Set all the initial paths and locations




###############################################################################
############################# Begin Main Functions ############################
###############################################################################


	def addComponentType (self, ctype) :
		'''Add a component type to the current project.  Before doing so, it
		must varify that the requested component type is valid to add to this
		type of project.'''


		print "Adding component type", ctype

		self.initComponentType(ctype)

		return True


	def initComponentType (self, ctype) :
		'''Initialize a component type in this project.  This will copy all the
		necessary files and folders into the project to support the processing
		of this component type.'''

		print "init component type", ctype


