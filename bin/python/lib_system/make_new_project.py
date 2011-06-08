#!/usr/bin/python2
# -*- coding: utf_8 -*-
# version: 20110608
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This script will setup a new project for the user by asking
# questions for project parameters, then taking that data
# and pushing to the Makefile which runs the system. This
# will setup the project. After that it will produce a script
# just for that specific project which will allow the user
# run processes without having to input project parameters
# each time.

# History:
# 20110608 - djd - Initial refactor from ptxplus


#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the modules we need for this process

import os, shutil, codecs, tarfile

# Import supporting local classes
import tools


#############################################################
#################### Main Module Defined ####################
#############################################################

class MakeNewProject (object) :


	def main (self, projType, newFolderName) :
		'''Create a new project at the specified path.'''


		# Just in case it isn't already a full path
		newProjectPath = os.path.abspath(newFolderName)
		fileLib = os.environ.get('TIPE_BASE') + "/resources/lib_sysFiles"

		# Check to see if we support this type of publication
		if projType in tools.getSystemSettingsObject()['System']['pubTypeList'] and projType != 'dictionary' :
			# To make a project all we really need is the .conf file
			if projType in tools.getSystemSettingsObject()['System']['pubTypeList'] :
				if not os.access(newProjectPath + "/." + projType + ".conf", os.R_OK) :
					shutil.copy(fileLib + "/." + projType + ".conf", newProjectPath + "/." + projType + ".conf")

			# Now to give the user a clue as to what happened we will
			# write out a little new project readme file with enough
			# info to guide them on to the next step.
			if not os.path.isfile (newProjectPath + "/README") :
				shutil.copy(fileLib + "/README", newProjectPath + "/README")

			else :
				userMessage("ERRR: The project type: [" + projType + "] is unknown. Process halted!")
				sys.exit(1)

			tools.userMessage('INFO: Created new project at: ' + newProjectPath)
		else :
			tools.userMessage('ERRR: The [' + projType + '] publication type is not supported.')



# This starts the whole process going
def doIt(pathToProject, projType) :

	thisModule = MakeNewProject()
	return thisModule.main(pathToProject, projType)
