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

def writeConfFiles (userConfig, projConfig, userHome, projHome) :
	'''Write out, if necessary, any conf files.  This will depend on if there
	has been any activity to necessitate this action.'''

	userConfigFile = os.path.join(userHome, userConfig['Files']['userConfFile']['name'])
	projConfigFile = os.path.join(projHome, userConfig['Files']['projConfFile']['name'])
	date_time = tStamp()
	if userConfig['System']['writeOutUserConfFile'] :
		userConfig['System']['lastEditDate'] = date_time
		userConfig['System']['writeOutUserConfFile'] = ''
		userConfig.filename = userConfigFile
		userConfig.write()

	# Don't try to write to the projConfFile if it is not there or the write
	# flag has not been set.'
	if os.path.isfile(projConfigFile) :
		print dir(projConfig)
		if userConfig['ProjectInfo']['writeOutProjConfFile'] :
			projConfig['ProjectInfo']['lastEditDate'] = date_time
			projConfig['ProjectInfo']['writeOutProjConfFile'] = ''
			projConfig.filename = projConfigFile
			projConfig.write()


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




