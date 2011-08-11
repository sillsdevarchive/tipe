#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110610
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle user configuration operations.

# History:
# 20110811 - djd - Begin initial draft


###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os
from configobj import ConfigObj

# Load the local classes
from tools import *


class UserConfig (object) :

	def __init__(self, userHome, tipeHome) :
		'''Intitate the whole class'''

		self.userHome       = userHome
		self.tipeHome       = tipeHome
		self.userConfigFile = os.path.join(userHome, 'tipe.conf')
		self.userResources  = os.path.join(userHome, 'resources')
		self.createUserConfig()


	def recordProject (self, projConfig, projHome) :
		'''Add information about this project to the user's tipe.conf located in
		the home config folder.'''

		pid     = projConfig['ProjectInfo']['projectIDCode']
		pname   = projConfig['ProjectInfo']['projectName']
		ptype   = projConfig['ProjectInfo']['projectType']
		date    = projConfig['ProjectInfo']['projectCreateDate']
		if not self.isRecordedProject(pid) :

			if os.path.isfile(self.userConfigFile) :
				cf = ConfigObj(self.userConfigFile)

				# FIXME: Before we create a project entry we want to be sure that
				# the projects section already exsists.  There might be a better way
				# of doing this.
				try :
					cf['Projects'][pid] = {}
				except :
					cf['Projects'] = {}
					cf['Projects'][pid] = {}

				# Now add the project data
				cf['Projects'][pid]['projectName']          = pname
				cf['Projects'][pid]['projectType']          = ptype
				cf['Projects'][pid]['projectPath']          = projHome
				cf['Projects'][pid]['projectCreateDate']    = date
				cf.write()
				return True
			else :
				return False


	def isRecordedProject (self, pid) :
		'''Check to see if this project is recorded in the user's config'''

		return pid in self.userConfig['Projects']


	def createUserConfig (self) :
		'''Create a user config object based on the system defaults and the
		overrides in the user config file, if it exsits.  If it does not, make
		one.'''

		# Check to see if the file is there, then read it in and break it into
		# sections. If it fails, scream really loud!
		tipeXML = os.path.join(self.tipeHome, 'bin', 'tipe.xml')
		if os.path.exists(tipeXML) :
			sysXmlConfig = xml_to_section(tipeXML)
		else :
			raise IOError, "Can't open " + tipeXML

		# Now get the settings from the users tipe.conf file
		if not os.path.exists(self.userConfigFile) :
			self.initUserHome()

		# Load the conf file into an object
		tipeConfig = ConfigObj(self.userConfigFile)

		# Look for any projects that might be registered and copy the data out
		try :
			tipeProjs = tipeConfig['Projects']
		except :
			tipeProjs = None

		# Create a new conf object based on all the XML default settings
		# Then override them with any exsiting user settings.
		self.userConfig = ConfigObj(sysXmlConfig.dict()).override(tipeConfig)

		# Put back the copied data of any project information that we might have
		# lost from the XML/conf file merging.
		if tipeProjs :
			self.userConfig['Projects'] = tipeProjs

		return self.userConfig


	def initUserHome (self) :
		'''Initialize a user config file on a new install or system re-init.'''

		# Create home folders
		if not os.path.isdir(self.userHome) :
			os.mkdir(self.userHome)

		if not os.path.isdir(self.userResources) :
			os.mkdir(self.userResources)

		# Make the default global tipe.conf for custom environment settings
		if not os.path.isfile(self.userConfigFile) :
			date_time = tStamp()
			tipe = ConfigObj()
			tipe.filename = self.userConfigFile
			tipe['System'] = {}
			tipe['Folders'] = {}
			tipe['Projects'] = {}
			tipe['System']['userName'] = 'Default User'
			tipe['System']['initDate'] = date_time
			tipe['System']['writeOutUserConfFile'] = 'True'
			# Folder list
			folders = ['fonts', 'illustrations', 'admin', 'compTypes', 'projTypes']
			# System folders
			for f in folders :
				tipe['Folders']['tipe' + f] = os.path.join(self.tipeHome, 'resources', 'lib_' + f)
			# User (home) folders
			for f in folders :
				thisFolder = os.path.join(self.userHome, 'resources', 'lib_' + f)
				tipe['Folders']['user' + f] = thisFolder
				if not os.path.isdir(thisFolder) :
					os.mkdir(thisFolder)

			# Write out the user config file
			tipe.write()


