#!/usr/bin/python2
# -*- coding: utf_8 -*-
# version: 20110609
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This class will handle processes dealing with managing project components.

# History:
# 20110609 - djd - Initial draft


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, sys
from configobj import ConfigObj

# Import supporting local classes
import tools
from error_manager import *
from datetime import *

# Instantiate local classes
error_manager = ErrorManager()

class ComponentManager (object) :

	# Intitate the whole class
	def __init__(self) :

		self._sources = self.getSourcesObject()
		self._placeholder = ""
#        self._processLogObject = []


	def getSourcesObject (self) :
		'''This will simply create a souces setting objects based on the .source
		settings file found in the root of the project.'''

		if os.path.isfile(os.getcwd() + "/.source") :
			# Load in the source object from our project
			return ConfigObj(os.getcwd() + "/.source", encoding='utf_8')


