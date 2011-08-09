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


def mergeProjConfig (projConfig, projHome, userHome, tipeHome) :
	'''Retrun a merge project config file from a valid project config file'''

	# Find out what kind of project this is
	oldProjConfig = projConfig
	projType = oldProjConfig['ProjectInfo']['projectType']
	# Load in the project type XML default settings
	projXmlConfig = getDefaultProjSettings(projHome, userHome, tipeHome, projType)
	# Create a new conf object based on all the XML default settings
	# Then override them with any exsiting project settings.
	return ConfigObj(projXmlConfig.dict()).override(oldProjConfig)


def getDefaultProjSettings (projHome, userHome, tipeHome, projType) :

	tipeProjXML     = os.path.join(tipeHome, 'resources', 'lib_projTypes', projType, projType + '.xml')
	userProjXML     = os.path.join(userHome, 'resources', 'lib_projTypes', projType, projType + '.xml')

	# Check first to see if this project type exsits in the user area.  That
	# project def. will get priority over system defs.  We use one or the other,
	# not both.
	if  os.path.exists(tipeProjXML) :
		res = xml_to_section(tipeProjXML)
	else :
		raise IOError, "Can't open " + tipeProjXML

	# The user overrides are not required
	try :
		if os.path.exists(userProjXML) :
			res = xml_to_section(userProjXML)
	except :
		pass

	# Return the final results of the conf settings
	return res


def writeConfFiles (userConfig, projConfig, userHome, projHome) :
	'''Write out, if necessary, any conf files.  This will depend on if there
	has been any activity to necessitate this action.'''

	userConfigFile = os.path.join(userHome, userConfig['Files']['userConfFile']['name'])
	projConfigFile = os.path.join(projHome, userConfig['Files']['projConfFile']['name'])
	stamp = tStamp()

	# There should always be a userConfig so if the write flag is set we will
	# write
	if userConfig['System']['writeOutUserConfFile'] :
		userConfig['System']['lastEditDate'] = stamp
		userConfig['System']['writeOutUserConfFile'] = ''
		userConfig.filename = userConfigFile
		userConfig.write()

	# There may not always be a valid (populated) projConfig so we need to try
	# to find the write flag first to see if we are going to write to it.
	try :
		if projConfig['ProjectInfo']['writeOutProjConfFile'] :
			projConfig['ProjectInfo']['lastEditDate'] = stamp
			projConfig['ProjectInfo']['writeOutProjConfFile'] = ''
			projConfig.filename = projConfigFile
			projConfig.write()

	except :
		# FIXME: Should I be doing something else here?
		pass


def xml_to_section(fname) :
	'''Read in our default settings from the XML system settings file'''

	# Read in our XML file
	doc = ElementTree.parse(fname)
	# Create an empty dictionary
	data = {}
	# Extract the section/key/value data
	xml_add_section(data, doc)
	# Convert the extracted data to a configobj and return
	return ConfigObj(data)


def xml_add_section(data, doc) :
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
				data[s.find('key').text] = [val.split(',')]
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

def override_section(self, aSection) :
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
	aProject._userConfig['System']['tipeEditDate'] = ts
	aProject._userConfig['System']['writeOutUserConfFile'] = True
	aProject.tipeEditDate = ts



def recordProject (tipeUserConfFile, projHome, pname, ptype, pid, date) :
	'''Add information about this project to the user's tipe.conf located in
	the home config folder.'''

	mod = 'project.recordProject()'
	if os.path.isfile(tipeUserConfFile) :
		cf = ConfigObj(tipeUserConfFile)

		# FIXME: Before we create a project entry we want to be sure that
		# the projects section already exsists.  There might be a better way
		# of doing this.
		try :
			cf['Projects'][pid] = {}
		except :
			cf['Projects'] = {}
			cf['Projects'][pid] = {}

		# Now add the project data
		cf['Projects'][pid]['projectName'] = pname
		cf['Projects'][pid]['projectType'] = ptype
		cf['Projects'][pid]['projectPath'] = projHome
		cf['Projects'][pid]['createDate'] = date
		cf.write()
		return True
	else :
		return False


def isRecordedProject (userConfFile, pid) :
	'''Check to see if this project is recorded in the user's config'''

	if os.path.isfile(userConfFile) :
		cf = ConfigObj(userConfFile)

		try :
			isConfPID = cf['Projects'][pid]
			return True
		except :
			return False



#def safeConfig(dir, fname, tipedir, setting, projconf = None) :
#    '''This is the main function for reading in the XML data and overriding
#    default settings with the current project settings.  This works with both
#    the project.conf file and the components.conf files.'''

#    # Check to see if the file is there, then read it in and break it into
#    # sections. If it fails, scream really loud!
#    f = os.path.join(tipedir, fname)
#    if os.path.exists(f) :
#        res = xml_to_section(f)
#    else :
#        raise IOError, "Can't open " + f

#    # If this is a live project it should have been passed a valid project.conf
#    # object.  Otherwise, the default settings from the XML will be good enough
#    # to get going.
#    if not projconf : projconf = res
#    f = projconf['System']['FileNames'][setting]

#    # If dealing with a components we'll use the same process but just create an
#    # empty object if no components have been defined for the project or a
#    # project doesn't exist.
#    if fname == 'components.xml' :
#        if os.path.exists(f) :
#            conf = override_components(res, f)
#        else :
#            conf = ConfigObj()
#    else :
#        if os.path.exists(f) :
#            conf = override(res, f)
#        else :
#            conf = res

#    return (conf, res)




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



