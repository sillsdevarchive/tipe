#!/usr/bin/python2
# -*- coding: utf_8 -*-
# version: 20110608
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This script will update the .project.conf file with new
# settings from the master .project.conf file. This enables
# changes to be propagated to the projects downstream. However,
# this isn't necessarialy a fool-proof method. With a big
# enough changes the original .project.conf file may need to
# be edited by hand.
#
# This process would normally be done after a system update
# the first time the project is run. It will check the version
# stamp in the .project.conf file and see if it matches the
# current version. If not, it will run the update, otherwise
# nothing happens.

# History:
# 20110608 - djd - Initial refactor from ptxplus


#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, sys, shutil
from configobj import ConfigObj

# Import supporting local classes
import tools

class UpdateProjectSettings (object) :


	def main (self) :

		basePath = os.environ.get('TIPE_BASE')
		settings = tools.getSettingsObject()
		# Before we do anything we need to check to see if the
		# the version is not the same.
		try :
			curVer = settings['System']['General']['systemVersion']

		except :
			curVer = 0
			tools.userMessage("Errr: Could not determine the current system version. Hopefully this update will fix that problem. Setting current version to 0")

		if settings['System']['systemVersion'] != curVer :

			# First make a backup copy of our original .project.conf
			bakSettingsProjectFile = tools.getProjectConfigFileName() + '~'
			settingsProjectFile = tools.getProjectConfigFileName()
			shutil.copy(settingsProjectFile, bakSettingsProjectFile)
			oldSettings = ConfigObj(bakSettingsProjectFile,encoding='utf-8')

			# Get the system defaul .conf file
			systemProjectConfFile = basePath + "/resources/lib_sysFiles/" + tools.getProjectConfigFileName()
			tempMasterConfFile = os.getcwd() + "/" + tools.getProjectConfigFileName()

			if os.path.isfile(tempMasterConfFile) != True :
				tools.userMessage("Errr: Could not update project, [" + tempMasterConfFile + "] not found")
			else :
				# Copy into the project folder
				shutil.copy(systemProjectConfFile, tempMasterConfFile)
				# Load in the object
				masterSettings = ConfigObj(tempMasterConfFile,encoding='utf-8')

				# Now we will do a simple merge and overwrite the users projet \
				# settings over our copy of the new settings
				masterSettings.merge(oldSettings)

				# Set it to the right version
				masterSettings['System']['General']['systemVersion'] = settings['System']['systemVersion']

				# Now we will write out the results to our new master copy
				masterSettings.write()

				tools.userMessage("Info: Version numbers did not match, project was updated from: " + curVer + " to: " + masterSettings['System']['General']['systemVersion'])
				return True
		else :
#            tools.userMessage("Info: Version numbers between the system and the project matched. Project was not updated.")
			return False



# This starts the whole process going
def doIt() :

	thisModule = UpdateProjectSettings()
	return thisModule.main()
