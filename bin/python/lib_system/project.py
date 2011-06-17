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
from config_template import ConfigTemplate
confTemp = ConfigTemplate()
from component import Component
from book import Book
from xml.etree import ElementTree


def xml_to_section(fname) :
	doc = ElementTree.parse(fname)
	data = {}
	xml_add_section(data, doc)
	return ConfigObj(data)

def xml_add_section(data, doc) :
	sets = doc.findall('setting')
	for s in sets :
		data[s.attrib['id']] = s.find('default').text
	sects = doc.findall('section')
	for s in sects :
		nd = {}
		data[s.attrib['id']] = nd
		xml_add_section(nd, s)

def override(aConfig, fname) :
	oConfig = ConfigObj(fname)
	aConfig.override(oConfig)

def override_components(aConfig, fname) :
	oConfig = ConfigObj(fname)
	for s, v in oConfig.items() :
		old = ConfigObj(aConfig['defaults'].dict())
		old.override(v)
		aConfig[s] = ConfigObj(old)

def override_section(self, aSection) :
	for k, v in self.items() :
		if k in aSection :
			if isinstance(v, dict) and isinstance(aSection[k], dict) :
				v.override(aSection[k])
			elif not isinstance(v, dict) and not isinstance(aSection[k], dict) :
				self[k] = v

Section.override = override_section

def safeConfig(dir, fname, tipedir, setting, projconf = None) :
	f = os.path.join(tipedir, fname + '.xml')
	if os.path.exists(f) :
		res = xml_to_section(f)
	else :
		return None
	if not projconf : projconf = res
	f = projconf['System']['FileNames'][setting]
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

		self.home = dir

		# Load project config files
		self._sysConfig = safeConfig(dir, "tipe", tipedir, 'projectConf')
		self._bookConfig = safeConfig(dir, "book", tipedir, 'bookConf', projconf = self._sysConfig)
		self._compsConfig = safeConfig(dir, "component", tipedir, 'compConf', projconf = self._sysConfig)
		self._book = Book(self, self._bookConfig)
		self._components = {}

		if self._sysConfig :
			self.report = Report(
					logfile = os.path.join(dir, self._sysConfig['System']['FileNames']['logFile']) if self._sysConfig else None,
					errfile = os.path.join(dir, self._sysConfig['System']['FileNames']['errorLogFile']) if self._sysConfig else None,
					debug = self._sysConfig and self._sysConfig['System']['debugging'])

#        if self._sysConfig :
			self.version            = self._sysConfig['System']['systemVersion']
			self.projConfFile       = os.path.join(self.home, self._sysConfig['System']['FileNames']['projectConf'])
			self.bookConfFile       = os.path.join(self.home, self._sysConfig['System']['FileNames']['bookConf'])
			self.compConfFile       = os.path.join(self.home, self._sysConfig['System']['FileNames']['compConf'])
			self.errorLogFile       = os.path.join(self.home, self._sysConfig['System']['FileNames']['errorLogFile'])
			self.logLineLimit       = self._sysConfig['System']['logLineLimit']
			self.textFolder         = os.path.join(self.home, self._sysConfig['System']['FolderNames']['textFolder'])
			self.processFolder      = os.path.join(self.home, self._sysConfig['System']['FolderNames']['processFolder'])
			self.reportFolder       = os.path.join(self.home, self._sysConfig['System']['FolderNames']['reportFolder'])

		# Create book params
		if self._bookConfig :
			self.bindingOrder       = self._bookConfig['Binding']['order']

		# Create component params
		# FIXME: This needs to be thought out a little more
#        if self._compsConfig :
#            self.extSty              = self._compsConfig['ScriptureBook']['extStyle']


	def checkProject (self, home) :
		'''Check to see if all the project assets are present wherever "home"
		is.  At a bare minimum we must have a project.conf file.  This will
		return Null if that is not found.'''

		if not self._sysConfig : return False
		if not self._bookConfig : return False
#        if not self._compsConfig : return False

		if not self._sysConfig : print False
		if not self._bookConfig : print False
		if not self._compsConfig : print False

		# From this point we will check for and add all the necessary project
		# assets.  Anything that is missing will be replaced by a default
		# version of the asset.

		# Check for the base set of folders
		if not os.path.isdir(self.textFolder) :
			os.mkdir(self.textFolder)
			self.writeToLog('LOG', 'checkProject(): Created Text folder')
		if not os.path.isdir(self.processFolder) :
			os.mkdir(self.processFolder)
			self.writeToLog('LOG', 'checkProject(): Created Process folder')
		if not os.path.isdir(self.reportFolder) :
			os.mkdir(self.reportFolder)
			self.writeToLog('LOG', 'checkProject(): Created Reports folder')

		# Check for key settings files

		return True


	def makeProject (self, home, settings="") :
		'''Create a new publishing project.'''

		# A new project only needs to have the necessary configuration files.
		# The rest is made with the check project file the first time a
		# component is processed.  However, if these files already exists we
		# will abandon the process
		if not os.path.isfile(self.projConfFile) and \
			not os.path.isfile(self.bookConfFile) and \
			not os.path.isfile(self.compConfFile) :
			if self.makeProjectConfigFiles(home, settings) :
				return True
		else :
			self.writeToLog('ERR', 'Conf files already exists', 'project.makeProject()')
			return False


	def makeProjectConfigFiles (self, home, settings="") :
		'''Create a fresh, default project.  The project configuration files are
		made from default configuration files found in TIPE.'''

		# Copy in the files


		# Insert some initial settings

		date_time, secs = str(datetime.now()).split(".")
#        writeObject = codecs.open(self._projectFile, "w", encoding='utf_8')
#        writeObject.write('[TIPE]\n')
#        writeObject.write('version = ' + self._version + '\n')
#        writeObject.write('created = ' + date_time + '\n')
#        writeObject.close()

		return True

	def getDoc (self, name) :
		'''Create a document object.'''
#        # FIXME: This needs more work and thought.
		if name == "Book" :
			return self._book
		try :
			return self._components[name]
		except KeyError :
			return None

	def addNewComponent(self, name) :
		self._compsConfig[name].initialisedefaultcomponentvaluessomehow()
		aComp = self.addComponent(name)
		aComp.initFiles()

	def addComponent(self, name) :
		aComp = Component(self, self._compsConfig[name], name)
		self._components[aComp.name] = aComp
		return self._book.addComponent(aComp)

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
	def __init__(self, logfile = None, errfile = None, debug = False) :

		self._debugging         = False
		self._logFile           = logfile
		self._errorLogFile      = errfile
		self._debugging = debug


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
		'''Send an event to the log file. and the terminal if specified.'''

		# When are we doing this?
		date_time, secs = str(datetime.now()).split(".")

		# Build the mod line
		if mod :
			mod = mod + ': '
		else :
			mod = ''

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

		# Now log the event to the top of the file using preAppend().  We will
		# only report what module it came from when it is a warning or an error.
		if code == 'MSG' :
			self.preAppend(eventLine, self._logFile)
			self.terminal(code + ' - ' + msg)
		elif code == 'LOG' :
			self.preAppend(eventLine, self._logFile)
			if self._debugging :
				self.terminal(code + ' - ' + msg)
		elif code == 'WRN' :
			self.preAppend(eventLine, self._logFile)
			self.terminal(code + ' - ' + mod + msg)
			if self._debugging :
				self.writeToErrorLog(eventLine)
		elif code == 'ERR' :
			self.preAppend(eventLine, self._logFile)
			self.writeToErrorLog(eventLine)
			self.terminal(code + ' - ' + mod + msg)
		else :
			self.preAppend(eventLine, self._logFile)
			self.terminal('writeToLog: WARNING! log code: ' + code + ' not recognized. BTW, the message is: (' + msg + ')')

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
