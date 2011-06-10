#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110610
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project infrastructure tasks.

# History:
# 20110610 - djd - Initial draft


###############################################################################
################################### Shell Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os


class Project (object) :

	def __init__(self) : pass

#        self._placeholder = ""
#        self._processLogObject = []


	def checkProject (self, here) :
		'''Check to see if all the project assets are present wherever "here"
		is.  At a bare minimum we must have a project.conf file.  This will
		return Null if that is not found.'''

		# First check for a .project.conf file
		if not os.path.isfile(here + "/.project.conf") :
			return

		# From this point we will check for and add all the necessary project
		# assets.  Anything that is missing will be replaced by a default
		# version of the asset.

		return True


	def makeProject (self, here) :
		'''Create a new publishing project.'''

		self.makeProjectConfigFile(here)


	def makeProjectConfigFile (self, here) :
		'''Create a fresh, default project configuration file wherever "here"
		is.'''

		writeObject = codecs.open(here + "/.project.conf", "w", encoding='utf_8')

		writeObject.write('[TIPE]\n')
		writeObject.write('version = 0.0.1\n')
		writeObject.close()

