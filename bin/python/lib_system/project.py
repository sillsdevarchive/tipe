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
from datetime import *
from configure import *
configure = Configure()

# Local classes
from report import *
report = Report()

class Project (object) :

	def __init__(self) :

		self._sysConfig = configure.getSystem()
		self._version = self._sysConfig['System']['systemVersion']
		self._projectFile = self._sysConfig['System']['projectFile']


	def checkProject (self, here) :
		'''Check to see if all the project assets are present wherever "here"
		is.  At a bare minimum we must have a project.conf file.  This will
		return Null if that is not found.'''

		# First check for a .project.conf file
		if not os.path.isfile(here + "/" + self._projectFile) :
			return

		# From this point we will check for and add all the necessary project
		# assets.  Anything that is missing will be replaced by a default
		# version of the asset.

		# Check for the base set of folders

		# Check for key settings files

		return True


	def makeProject (self, here, settings="") :
		'''Create a new publishing project.'''

		# A new project only needs to have a project.conf file.  The rest is
		# made with the check project file the first time a component is
		# processed.  However, if the project.conf file already exists we will
		# abandon the process
		if not os.path.isfile(here + "/" + self._projectFile) :
			if self.makeProjectConfigFile(here, settings) :
				return True
		else :
			report.writeToLog('ERR', 'report.makeProject: project.conf file already exists')


	def makeProjectConfigFile (self, here, settings="") :
		'''Create a fresh, default project configuration file wherever "here"
		is.'''

		date_time, secs = str(datetime.now()).split(".")
		writeObject = codecs.open(here + "/" + self._projectFile, "w", encoding='utf_8')
		writeObject.write('[TIPE]\n')
		writeObject.write('version = ' + self._version + '\n')
		writeObject.write('created = ' + date_time + '\n')
		writeObject.close()

		return True



