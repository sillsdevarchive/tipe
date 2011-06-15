#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110615
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle default template configuration.

# History:
# 20110615 - djd - Initial draft


###############################################################################
################################### Shell Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os
from xml.etree.ElementTree import XMLID, ElementTree
tree = ElementTree()

# Load the local classes


class ConfigTemplate (object) :

	# Intitate the whole class
	def __init__(self) : pass

		#self.home              = dir


	def readTemplate (self, template) :
		'''Read in default settings from TIPE system'''

		tree.parse(template)
		p = tree.find('section/setting')

		return p


	def writeDefaultConfig (self, template) :
		'''Write out a single config file for the project that is based on its
		parent XML file.'''

		pass




