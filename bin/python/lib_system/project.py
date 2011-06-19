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
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, sys, fileinput
from datetime import *
from configobj import ConfigObj, Section


# Load the local classes
from component import Component
from book import Book
from xml.etree import ElementTree


###############################################################################
############################ Define Global Functions ##########################
###############################################################################

# FIXME: XML issues
#   1) Merge may not be working.  When a setting is updated it doesn't seem to
#   want to write out
#   2) Lists are not being written to the conf file as lists but as strings
#   3) Settings found in the conf file are not overriding the defaults in some cases.


def xml_to_section(fname) :
	'''Read in our default settings from the XML system settings file'''

	doc = ElementTree.parse(fname)
	data = {}
	xml_add_section(data, doc)
	return ConfigObj(data)


def xml_add_section(data, doc) :
	'''Subprocess of xml_to_section().  Adds sections in the XML to conf
	object.'''

	sets = doc.findall('setting')
	for s in sets :
		data[s.attrib['id']] = s.find('default').text
	sects = doc.findall('section')
	for s in sects :
		nd = {}
		data[s.attrib['id']] = nd
		xml_add_section(nd, s)


def override(sysConfig, fname) :
	'''Subprocess of override_components().  The purpose is to override default
	settings taken from the TIPE system (sysConfig) file with those found in the
	project.conf file (projConfig).'''

	# Read in the project.conf file and create an object
	projConfig = ConfigObj(fname)

	# Recall this function to override the default settings
	sysConfig.override(projConfig)

	# How does this work? Really, how the changed object get passed back?


def override_components(aConfig, fname) :
	'''Overrides component settings that we got from the default XML system
	settings file.'''
	projConfig = ConfigObj(fname)
	for s, v in projConfig.items() :
		old = ConfigObj(aConfig['defaults'].dict())
		old.override(v)
		aConfig[s] = ConfigObj(old)

	# Do we want to pass aConfig back to something?


def override_section(self, aSection) :
	for k, v in self.items() :
		if k in aSection :
			if isinstance(v, dict) and isinstance(aSection[k], dict) :
				v.override(aSection[k])
			elif not isinstance(v, dict) and not isinstance(aSection[k], dict) :
				self[k] = v


# This will reasign the standard ConfigObj function.
Section.override = override_section


def safeConfig(dir, fname, tipedir, setting, projconf = None) :
	'''This is the main function for reading in the XML data and overriding
	default settings with the current project settings.'''

	# Check to see if the file is there, then read it in and break it into
	# sections. If it fails, return None
	f = os.path.join(tipedir, fname + '.xml')
	if os.path.exists(f) :
		res = xml_to_section(f)
	else :
		return None

	# If this is a live project it should have been passed a valid project.conf
	# object.  Otherwise, the default settings from the XML will be good enough
	# to get going.
	if not projconf : projconf = res
	f = projconf['System']['FileNames'][setting]

# I think the above needs to change as we only have one xml and conf file to deal with.

	#
	if fname == 'component' and os.path.exists(f) :
		override_components(res, f)
	elif os.path.exists(f) :
		override(res, f)
	return res


###############################################################################
################################## Begin Class ################################
###############################################################################

class Project (object) :

	def __init__(self, dir, tipedir) :

		self.home                   = dir

		# Load project config files
		self._sysConfig             = safeConfig(dir, "project", tipedir, 'projConfFile')
		self._components            = {}

		if self._sysConfig :
			self.initLogging(self.home)
			self.version            = self._sysConfig['System']['systemVersion']
			self.isProject          = self._sysConfig['System']['isProject']
			self.projConfFile       = os.path.join(self.home, self._sysConfig['System']['FileNames']['projConfFile'])
			self.errorLogFile       = os.path.join(dir, self._sysConfig['System']['FileNames']['errorLogFile'])
			self.logLineLimit       = self._sysConfig['System']['logLineLimit']
			self.textFolder         = os.path.join(self.home, self._sysConfig['System']['FolderNames']['textFolder'])
			self.processFolder      = os.path.join(self.home, self._sysConfig['System']['FolderNames']['processFolder'])
			self.reportFolder       = os.path.join(self.home, self._sysConfig['System']['FolderNames']['reportFolder'])


	def initLogging (self, dir) :
		'''Initialize the log file system.'''

		self.report = Report(
			logFile         = os.path.join(dir, self._sysConfig['System']['FileNames']['logFile']) if self._sysConfig else None,
			errFile         = os.path.join(dir, self._sysConfig['System']['FileNames']['errorLogFile']) if self._sysConfig else None,
			debug           = self._sysConfig and self._sysConfig['System']['debugging'],
			isProject       = self._sysConfig and self._sysConfig['System']['isProject'])


	def checkProject (self, home) :
		'''Check to see if all the project assets are present wherever "home"
		is.  At a bare minimum we must have a project.conf file.  This will
		return Null if that is not found.'''

		mod = 'project.checkProject()'

		# Look to see if all three conf files exist
		if os.path.isfile(self.projConfFile) :
			# From this point we will check for and add all the necessary project
			# assets.  Anything that is missing will be replaced by a default
			# version of the asset.
			self.initProject(home)

			# Check for key settings files

			return True


	def initProject (self, home) :
		'''Initialize a new project by creating all necessary components.'''

		mod = 'project.initProject()'
		for key, value in self._sysConfig['System']['FolderNames'].iteritems() :
			thisFolder = os.path.join(home, value)
			if not os.path.isdir(thisFolder) :
				os.mkdir(thisFolder)
				self.writeToLog('LOG', 'Created folder: ' + value, mod)


	def makeProject (self, home, settings="") :
		'''Create a new publishing project.'''

		mod = 'project.makeProject()'
		# A new project only needs to have the necessary configuration files.
		# The rest is made with the check project file the first time a
		# component is processed.  However, if these files already exists we
		# will abandon the process
		if not os.path.isfile(self.projConfFile) :
			date_time, secs = str(datetime.now()).split(".")
			self._sysConfig['System']['isProject'] = True
			self._sysConfig['System']['projCreateDate'] = date_time
			self.initLogging(home)
			self.initProject(home)
			return True
		else :
			self.writeToLog('ERR', 'Conf files already exists', mod)
			return False


	def getDoc (self, name) :
		'''Create a document object.'''
#        # FIXME: I think this needs more work and thought.
		if name == "Book" :
			return self._book
		try :
			return self._components[name]
		except KeyError :
			return None


	def initFiles (self, idCode) :
		'''Initialize all the necessary files for a given component.'''

		# Discover the type of component it is

		# Loop through all the component files in the projectConf file.

		pass


	def addNewComponent(self, name) :
		'''Add a new component to the project.'''

		self._compsConfig[name].initialisedefaultcomponentvaluessomehow()
		aComp = self.addComponent(name)
		aComp.initFiles()


	def addComponent(self, name) :
		'''Append a component to the bindingOrder list and add it to the
		project.conf file, often called by addNewComponent().'''

		aComp = Component(self, self._compsConfig[name], name)
		self._components[aComp.name] = aComp
		return self._sysConfig.addComponent(aComp)

	# These are Report mod functions that are exposed to the project class
	def terminal(self, msg) : self.report.terminal(msg)
	def terminalCentered(self, msg) : self.report.terminalCentered(msg)
	def writeToLog(self, code, msg, mod) : self.report.writeToLog(code, msg, mod)
	def trimLog(self, logLineLimit) : self.report.trimLog(logLineLimit)


###############################################################################
############################### Reporting Class ###############################
###############################################################################


class Report (object) :

	# Intitate the whole class
	def __init__(self, logFile = None, errFile = None, debug = False, isProject = True) :

		self._debugging         = False
		self._logFile           = logFile
		self._errorLogFile      = errFile
		self._debugging         = debug
		self._isProject         = isProject


	def terminal (self, msg) :
		'''Send a message to the terminal with a little formating to make it
		look nicer.'''

		# Output the message and wrap it if it is over 60 chars long.
		print self.wordWrap(msg, 60)


	def terminalCentered (self, msg) :
		'''This will try to center text on a 60 char-long line.  If it is more
		than that it will wrap the text.'''

		if len(msg) < 60 :
			print self.centerText(msg, 60)
		else :
			print self.wordWrap(msg, 60)


	def error (self, msg, dest='t') :
		'''Report error to log and/or terminal.'''

		# Output to terminal if indicated
		if dest == "t" :
			self.terminal(msg)


	def wordWrap (self, text, width) :
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

	#FIXME: This doesn't work yet
	def centerText (self, text, width) :
		'''As long as the length of the text does not exceed the width of the line.
		This will center the text in the line and leave white space before and
		after.'''

	#    return '{:^' + str(width) + '}'.format(text)
		return '{:*^60}'.format('text')


###############################################################################
################################# Logging routines ############################
###############################################################################

# These have to do with keeping a running log file.  Everything done is recorded
# in the log file and that file is trimmed to a length that is specified in the
# system settings.  Everything is channeled to the log file but depending on
# what has happened, they are classed in three levels:
#   1) Common event going to log and terminal
#   2) Warning event going to log and terminal if debugging is turned on
#   3) Error event going to the log and terminal

	def writeToLog (self, code, msg, mod = None) :
		'''Send an event to the log file. and the terminal if specified.
		Everything gets written to the log.  Whether a message gets written to
		the terminal or not depends on what type (code) it is.  There are four
		codes:
			MSG = General messages go to both the terminal and log file
			LOG = Messages that go only to the log file
			WRN = Warnings that go to the terminal and log file
			ERR = Errors that go to both the terminal and log file.'''

		# Build the mod line
		if mod :
			mod = mod + ': '
		else :
			mod = ''

		# Write out everything but LOG messages to the terminal
		if code != 'LOG' :
			self.terminal(code + ' - ' + msg)

		# If there is not project, why bother?
		if self._isProject :
			# When are we doing this?
			date_time, secs = str(datetime.now()).split(".")

			# Build the event line
			if code == 'ERR' :
				eventLine = '\"' + date_time + '\", \"' + code + '\", \"' + mod + msg + '\"'
			else :
				eventLine = '\"' + date_time + '\", \"' + code + '\", \"' + msg + '\"'

			# Do we need a log file made?
			if not os.path.isfile(self._logFile) or os.path.getsize(self._logFile) == 0 :
				writeObject = codecs.open(self._logFile, "w", encoding='utf_8')
				writeObject.write('TIPE event log file created: ' + date_time + '\n')
				writeObject.close()

			# Now log the event to the top of the log file using preAppend().
			self.preAppend(eventLine, self._logFile)

			# Write errors and warnings to the error log file
			if code == 'WRN' and self._debugging :
				self.writeToErrorLog(eventLine)

			if code == 'ERR' :
				self.writeToErrorLog(eventLine)

		return


	def writeToErrorLog (self, eventLine) :
		'''In a perfect world there would be no errors, but alas there are and
		we need to put them in a special file that can be accessed after the
		process is run.  The error file from the previous session is deleted at
		the begining of each new run.'''

		# Because we want to read errors from top to bottom, we don't pre append
		# them to the error log file.
		if not os.path.isfile(self._errorLogFile) :
			writeObject = codecs.open(self._errorLogFile, "w", encoding='utf_8')
		else :
			writeObject = codecs.open(self._errorLogFile, "a", encoding='utf_8')

		# Write and close
		writeObject.write(eventLine + '\n')
		writeObject.close()

		return


	def trimLog (self, logLineLimit = 1000) :
		'''Trim the system log file.  This will take an existing log file and
		trim it to the amount specified in the system file.'''

		# Of course this isn't needed if there isn't even a log file
		if os.path.isfile(self._logFile) :

			# Read in the existing log file
			readObject = codecs.open(self._logFile, "r", encoding='utf_8')
			lines = readObject.readlines()
			readObject.close()

			# Process only if we have enough lines
			if len(lines) > logLineLimit :
				writeObject = codecs.open(self._logFile, "w", encoding='utf_8')
				lineCount = 0
				for line in lines :
					if logLineLimit > lineCount :
						writeObject.write(line)
						lineCount +=1

				writeObject.close()

		return


	def preAppend (self, line, file_name) :
		'''Got the following code out of a Python forum.  This will pre-append a
		line to the begining of a file.'''

		fobj = fileinput.FileInput(file_name, inplace=1)
		first_line = fobj.readline()
		sys.stdout.write("%s\n%s" % (line, first_line))
		for line in fobj:
			sys.stdout.write("%s" % line)

		fobj.close()
