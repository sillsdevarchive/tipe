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
print "starting to load"
from bookTex_command import Command

from project import Project
#from project import bookTex

#from book import Book
#from xml.etree import ElementTree

#print dir(Project)

###############################################################################
############################ Define Global Functions ##########################
###############################################################################

# These root level functions work at a fundamental level of the system


###############################################################################
################################## Begin Class ################################
###############################################################################

class BookTex (Project) :

	def __init__(self, aProject) :

		# Set all the initial paths and locations

		self.aProject = aProject



###############################################################################
############################# Begin Main Functions ############################
###############################################################################


	def addComponentTypexxxxxxxxx (self, ctype) :
		'''Add a component type to the current project.  Before doing so, it
		must varify that the requested component type is valid to add to this
		type of project.'''


		print "Adding compnent type", ctype

		self.initComponentType(ctype)

		return True


	def initComponentType (self, ctype) :
		'''Initialize a component type in this project.  This will copy all the
		necessary files and folders into the project to support the processing
		of this component type.'''

		print "init compnent type", ctype


