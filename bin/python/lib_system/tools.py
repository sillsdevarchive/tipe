#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110721
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This module will hold all the miscellaneous functions that are shared with
# many other scripts in the system.

# History:
# 20110728 - djd - Begin initial draft


###############################################################################
################################## Tools Class ################################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, sys
from datetime import *
from xml.etree import ElementTree
from configobj import ConfigObj, Section


###############################################################################
############################ Functions Begin Here #############################
###############################################################################


############################## Settings Functions #############################


def isRecordedProject (userConfigFile, pid) :
	'''Check to see if this project is recorded in the user's config'''

	if os.path.isfile(userConfigFile) :
		cf = ConfigObj(userConfigFile)
		try :
			return pid in cf['Projects']
		except :
			pass


def recordProject (userConfigFile, projConfig, projHome) :
	'''Add information about this project to the user's tipe.conf located in
	the home config folder.'''

	pid     = projConfig['ProjectInfo']['projectIDCode']
	pname   = projConfig['ProjectInfo']['projectName']
	ptype   = projConfig['ProjectInfo']['projectType']
	date    = projConfig['ProjectInfo']['projectCreateDate']
	if not isRecordedProject(userConfigFile, pid) :

		if os.path.isfile(userConfigFile) :
			cf = ConfigObj(userConfigFile)

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


def mergeProjConfig (projConfig, projHome, userHome, tipeHome) :
	'''Retrun a merge project config object from a valid project config file'''

	# Find out what kind of project this is
	oldProjConfig = projConfig
	projType = oldProjConfig['ProjectInfo']['projectType']
	compTypes = oldProjConfig['ProjectInfo']['projectComponentTypes']
	compInfo = ConfigObj()
	compInfo['Components'] = {}
	for comp in compTypes :
		try :
			compInfo['Components'][comp] = {}
			compInfo['Components'][comp].merge(oldProjConfig['Components'][comp])
		except :
			pass

	# Load in the project type XML default settings
	projXmlConfig = getProjSettings(userHome, tipeHome, projType)
	# Create a new conf object based on all the XML default settings
	# Then override them with any exsiting project settings.
	newProjConfig = ConfigObj(projXmlConfig.dict()).override(oldProjConfig)
	newProjConfig.merge(compInfo)

	return newProjConfig


def getProjInitSettings (userHome, tipeHome, projType) :
	'''Get the project initialisation settings from the project type init xml
	file.'''

	tipeProjInitXML     = os.path.join(tipeHome, 'resources', 'lib_projTypes', projType, projType + '_init.xml')
	userProjInitXML     = os.path.join(userHome, 'resources', 'lib_projTypes', projType, projType + '_init.xml')

	res = getXMLSettings(tipeProjInitXML)
	if os.path.isfile(userProjInitXML) :
		return overrideSettings(res, userProjInitXML)
	else :
		return res


def getCompInitSettings (userHome, tipeHome, compType) :
	'''Get the project initialisation settings from the project type init xml
	file.  Then, if it exsits, override these settings with the version found in
	the user area.'''

	tipeCompInitXML     = os.path.join(tipeHome, 'resources', 'lib_compTypes', compType, compType + '_init.xml')
	userCompInitXML     = os.path.join(userHome, 'resources', 'lib_compTypes', compType, compType + '_init.xml')

	res = getXMLSettings(tipeCompInitXML)
	if os.path.isfile(userCompInitXML) :
		return overrideSettings(res, userCompInitXML)
	else :
		return res


def getProjSettings (userHome, tipeHome, projType) :
	'''Get the default settings out of a project type xml description file.'''

	tipeProjXML     = os.path.join(tipeHome, 'resources', 'lib_projTypes', projType, projType + '.xml')
	userProjXML     = os.path.join(userHome, 'resources', 'lib_projTypes', projType, projType + '.xml')

	res = getXMLSettings(tipeProjXML)
	if os.path.isfile(userProjXML) :
		return overrideSettings(res, userProjXML)
	else :
		return res


def getCompSettings (userHome, tipeHome, compType) :
	'''Get the default settings out of a project type xml description file.'''

	tipeCompXML     = os.path.join(tipeHome, 'resources', 'lib_compTypes', compType, compType + '.xml')
	userCompXML     = os.path.join(userHome, 'resources', 'lib_compTypes', compType, compType + '.xml')

	res = getXMLSettings(tipeCompXML)
	if os.path.isfile(userCompXML) :
		return overrideSettings(res, userCompXML)
	else :
		return res


def getXMLSettings (xmlFile) :
	'''Get settings from an XML file.'''

	if  os.path.exists(xmlFile) :
		return xml_to_section(xmlFile)
	else :
		raise IOError, "Can't open " + xmlFile


def overrideSettings (settings, overrideXML) :
	'''Override the settings in an object with another like object.'''

	settings = xml_to_section(overrideXML)

	return settings


def writeProjConfFile (projConfig, projHome) :
	'''Write out only the project config file.'''

	projConfigFile = os.path.join(projHome, '.project.conf')
	stamp = tStamp()

	# There may not always be a valid (populated) projConfig so we need to try
	# to find the write flag first to see if we are going to write to it.
	try :
		if projConfig['ProjectInfo']['writeOutProjConfFile'] :
			projConfig['ProjectInfo']['projectLastEditDate'] = stamp
			projConfig['ProjectInfo']['writeOutProjConfFile'] = ''
			projConfig.filename = projConfigFile
			projConfig.write()

	except :
		# FIXME: Should I be doing something else here?
		pass


def writeUserConfFile (userConfig, userHome) :
	'''Write out only the user config file.'''

	userConfigFile = os.path.join(userHome, 'tipe.conf')
	stamp = tStamp()

	# There should always be a userConfig so if the write flag is set we will
	# write to it.
	if userConfig['System']['writeOutUserConfFile'] :
		userConfig['System']['lastEditDate'] = stamp
		userConfig['System']['writeOutUserConfFile'] = ''
		userConfig.filename = userConfigFile
		userConfig.write()


def writeConfFiles (userConfig, projConfig, userHome, projHome) :
	'''Write out, if necessary, to all the conf files.  This will depend on if
	there has been any activity to necessitate this action.'''

	writeProjConfFile(projConfig, projHome)
	writeUserConfFile(userConfig, userHome)


def xml_to_section (fname) :
	'''Read in our default settings from the XML system settings file'''

	# Read in our XML file
	doc = ElementTree.parse(fname)
	# Create an empty dictionary
	data = {}
	# Extract the section/key/value data
	xml_add_section(data, doc)
	# Convert the extracted data to a configobj and return
	return ConfigObj(data)


def xml_add_section (data, doc) :
	'''Subprocess of xml_to_section().  Adds sections in the XML to conf
	object that is in memory.  It acts only on that object and does not return
	anything.'''

	# Find all the key and value in a setting
	sets = doc.findall('setting')
	for s in sets :
		val = s.find('value').text
		# Need to treat lists special but type is not required
		if s.find('type').text == 'list' :
			if val :
				data[s.find('key').text] = val.split(',')
			else :
				data[s.find('key').text] = []
		else :
			data[s.find('key').text] = val

	# Find all the sections then call this same function to grab the keys and
	# values all the settings in the section
	sects = doc.findall('section')
	for s in sects :
		nd = {}
		data[s.find('sectionID').text] = nd
		xml_add_section(nd, s)


def override_section (self, aSection) :
	'''Overrides settings by using the XML defaults and then merging those with
	items in the configobj that match.'''

	# Look for the key and value in object of items created from itself
	for k, v in self.items() :
		if k in aSection :
			if isinstance(v, dict) and isinstance(aSection[k], dict) :
				v.override(aSection[k])
			elif not isinstance(v, dict) and not isinstance(aSection[k], dict) :
				self[k] = aSection[k]
	# Return the overridden object
	return self


# This will reasign the standard ConfigObj function that works much like ours
# but not quite what we need for working with XML as one of the inputs.
Section.override = override_section


def reportSysConfUpdate (aProject) :
	'''Mark the project/system config object as changed so the next time a write
	command is called on it it will write out the changes.  This normally
	happens at the end of a process.'''

	ts = tStamp()
	aProject._userConfig['System']['lastEditDate'] = ts
	aProject._userConfig['System']['writeOutUserConfFile'] = True
	aProject.lastEditDate = ts


############################### Terminal Output ###############################

def terminal (msg) :
	'''Send a message to the terminal with a little formating to make it
	look nicer.'''

	# Output the message and wrap it if it is over 60 chars long.
	print wordWrap(msg, 60)


def wordWrap (text, width) :
	'''A word-wrap function that preserves existing line breaks
		and most spaces in the text. Expects that existing line
		breaks are linux style newlines (\n).'''

	def func(line, word) :
		nextword = word.split("\n", 1)[0]
		n = len(line) - line.rfind('\n') - 1 + len(nextword)
		if n >= width:
			sep = "\n"
		else:
			sep = " "
		return '%s%s%s' % (line, sep, word)
	text = text.split(" ")
	while len(text) > 1:
		text[0] = func(text.pop(0), text[0])
	return text[0]


def tStamp () :
	'''Create a simple time stamp for logging and timing purposes.'''

	date_time, secs = str(datetime.now()).split(".")

	return date_time



