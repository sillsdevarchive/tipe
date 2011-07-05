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
# 20110704 - djd - Refactor for mulitple component and project type processing


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

# These root level functions work at a fundamental level of the system


def xml_to_section(fname) :
	'''Read in our default settings from the XML system settings file'''

	doc = ElementTree.parse(fname)
	data = {}
	xml_add_section(data, doc)
	return ConfigObj(data)


def xml_add_section(data, doc) :
	'''Subprocess of xml_to_section().  Adds sections in the XML to conf
	object.'''

	# Find all the key and value in a setting
	sets = doc.findall('setting')
	for s in sets :
		val = s.find('value').text
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


def override(sysConfig, fname) :
	'''Subprocess of override_components().  The purpose is to override default
	settings taken from the TIPE system (sysConfig) file with those found in the
	project.conf file (projConfig).'''

	# Read in the project.conf file and create an object
	projConfig = ConfigObj(fname)
	res = ConfigObj(sysConfig.dict())

	# Recall this function to override the default settings
	res.override(projConfig)
	return res


def override_components(aConfig, fname) :
	'''Overrides component settings that we got from the default XML system
	settings file.'''
	res = ConfigObj()
	projConfig = ConfigObj(fname)
	for s, v in projConfig.items() :
		newtype = v['Type']
		old = Section(projConfig, 1, projConfig, indict = aConfig['Defaults'].dict())
		old.override(v)
		oldtype = Section(v, 2, projConfig, indict = aConfig[v['compType']].dict())
		oldtype.override(newtype)
		res[s] = old
		res[s]['Type'] = oldtype
	return res


def override_section(self, aSection) :
	'''Overrides an entire setting section.'''

	for k, v in self.items() :
		if k in aSection :
			if isinstance(v, dict) and isinstance(aSection[k], dict) :
				v.override(aSection[k])
			elif not isinstance(v, dict) and not isinstance(aSection[k], dict) :
				self[k] = aSection[k]


# This will reasign the standard ConfigObj function that works much like ours
# but not quite what we need for working with XML as one of the inputs.
Section.override = override_section




def safeConfig(dir, fname, tipedir, setting, projconf = None) :
	'''This is the main function for reading in the XML data and overriding
	default settings with the current project settings.  This works with both
	the project.conf file and the components.conf files.'''

	# Check to see if the file is there, then read it in and break it into
	# sections. If it fails, scream really loud!
	f = os.path.join(tipedir, fname)
	if os.path.exists(f) :
		res = xml_to_section(f)
	else :
		raise IOError, "Can't open " + f

	# If this is a live project it should have been passed a valid project.conf
	# object.  Otherwise, the default settings from the XML will be good enough
	# to get going.
	if not projconf : projconf = res
	f = projconf['System']['FileNames'][setting]

	# If dealing with a components we'll use the same process but just create an
	# empty object if no components have been defined for the project or a
	# project doesn't exist.
	if fname == 'components.xml' :
		if os.path.exists(f) :
			conf = override_components(res, f)
		else :
			conf = ConfigObj()
	else :
		if os.path.exists(f) :
			conf = override(res, f)
		else :
			conf = res

	return (conf, res)


def safeStart (projHome, userHome, tipeHome) :
	'''TIPE will first load all the tipe.xml default values from the system and
	override with the settings it finds in the user's tipe.conf file.  Next it
	will look in the current folder for a tipe.conf file to further override if
	necessary.'''

	# Check to see if the file is there, then read it in and break it into
	# sections. If it fails, scream really loud!
	tipeXML = os.path.join(tipeHome, 'tipe.xml')
	if os.path.exists(tipeXML) :
		res = xml_to_section(tipeXML)
	else :
		raise IOError, "Can't open " + tipeXML

	# Now get the settings from the users global tipe.conf file
	tipeUser = os.path.join(userHome, 'tipe.conf')
	if os.path.exists(tipeUser) :
		tu = ConfigObj(tipeUser)

	# Merge default settings with global settings
	res.merge(tu)

	# Finally get the project tipe.conf override settings
	tipeProj = os.path.join(projHome, 'tipe.conf')
	if os.path.exists(tipeProj) :
		tp = ConfigObj(tipeProj)

		# Merge with project settings
		res.merge(tp)

	# Return the final results of the conf settings
	return res





###############################################################################
################################## Begin Class ################################
###############################################################################

class Project (object) :

	def __init__(self, projHome, userHome, tipeHome) :

		self.projHome                       = projHome
		self.userHome                       = userHome
		self.tipeHome                       = tipeHome

		# Load the TIPE config settings and do a safe start
		self._sysConfig                     = safeStart(projHome, userHome, tipeHome)

		# Check to see if there are project and component settings to load
		self._projConfig                    = {}
		self._compConfig                    = {}

#        self._sysConfig                     = safeConfig(dir, "project.xml", tipedir, 'projConfFile')[0]
#        self._compConf, self._compMaster    = safeConfig(dir, "components.xml", tipedir, 'compConfFile', projconf = self._sysConfig)
#        self._components                    = {}

		# Initialize our book module
#        self._book                          = Book(self, self._sysConfig['Book'])
#        self._book.loadBooks(self)

		if self._sysConfig :
			self.initLogging(self.projHome)
			self.version                    = self._sysConfig['System']['systemVersion']
			self.userName                   = self._sysConfig['System']['userName']
			self.projectName                = self._sysConfig['System']['projectName']
#            self.isProject                  = self._sysConfig['System']['isProject']
#            self.projConfFile               = os.path.join(self.home, self._sysConfig['System']['FileNames']['projConfFile'])
			self.errorLogFile               = os.path.join(self.projHome, self._sysConfig['FileNames']['errorLogFile'])
#            self.logLineLimit               = self._sysConfig['System']['logLineLimit']
#            self.textFolder                 = os.path.join(self.home, self._sysConfig['System']['FolderNames']['textFolder'])
#            self.processFolder              = os.path.join(self.home, self._sysConfig['System']['FolderNames']['processFolder'])
#            self.reportFolder               = os.path.join(self.home, self._sysConfig['System']['FolderNames']['reportFolder'])


	def writeConfFiles(self) :
		if self._sysConfig['System']['isProject'] :
			date_time, secs = str(datetime.now()).split(".")
			self._sysConfig['System']['projEditDate'] = date_time   # bad for VCS
			# Write out component config file now only if the save flag has been
			# set.  Set the flag back to False before we write.
			if self._sysConfig['System']['writeOutCompConf'] == True :
				self._sysConfig['System']['writeOutCompConf'] = False
				self._compConf.filename = self._sysConfig['System']['FileNames']['compConfFile']
				self._compConf.write()
			self._sysConfig.filename = self._sysConfig['System']['FileNames']['projConfFile']
			self._sysConfig.write()


	def initLogging (self, dir) :
		'''Initialize the log file system.'''

		self.report = Report(
			logFile         = os.path.join(dir, self._sysConfig['FileNames']['logFile']) if self._sysConfig else None,
			errFile         = os.path.join(dir, self._sysConfig['FileNames']['errorLogFile']) if self._sysConfig else None,
			debug           = self._sysConfig and self._sysConfig['System']['debugging'])
#            isProject       = self._sysConfig and self._sysConfig['System']['isProject'])


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
		'''Initialize a new project by creating all necessary global items like
		folders, etc.'''

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
			self.writeToLog('ERR', 'Project already exists here!', mod)
			return False

	def addNewComponent(self, idCode, compType) :
		'''Add a new component id to the binding order and create a new component config section for it'''

		# We don't want to do this is the component already exists
		if not idCode in self._compConf :
			self._compConf[idCode] = Section(self._compConf, 1, self._compConf, indict = self._compMaster['Defaults'].dict())
			for k, v in self._compConf[idCode].items() :
				self._compConf[idCode][k] = v.replace('[compID]', idCode)
			self._compConf[idCode]['Type'] = Section(self._compConf[idCode], 2, self._compConf, indict = self._compMaster[compType].dict())
			self._book.addToBinding(idCode)

			# Make the Component object and add to book and us
			aComp = self.addComponent(idCode)

			# Init the comp files if necessary
			aComp.initComponentFiles(self)

			# Set the flag for writing out the components config file
			self._sysConfig['System']['writeOutCompConf'] = True
			return True

		else :
			return False

	def addComponent(self, name) :
		'''Create a component object for an existing component id and add it to
		everything that needs to know about it.'''

		aComp = Component(name, self, self._compConf[name])
		self._components[aComp.name] = aComp
		return self._book.addComponent(aComp)


	def removeComponent (self, idCode) :
		'''Remove a component from the project.'''

		# We want to do this only if the component already exists
		if idCode in self._compConf :
			del(self._compConf[idCode])
			self._book.removeFromBinding(idCode)
			# Set the flag for writing out the components config file
			self._sysConfig['System']['writeOutCompConf'] = True
			return True
		else :
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


	# These are Report mod functions that are exposed to the project class
	def terminal(self, msg) : self.report.terminal(msg)
	def terminalCentered(self, msg) : self.report.terminalCentered(msg)
	def writeToLog(self, code, msg, mod) : self.report.writeToLog(code, msg, mod)
	def trimLog(self, logLineLimit) : self.report.trimLog(logLineLimit)


###############################################################################
########################### TIPE System Commands ##############################
###############################################################################

# Here go all the commands that TIPE knows how to use.  If it isn't defined
# here, it will not work.  The documentation for each command goes in the
# command so when the user types 'help' followed by the command they will get
# whatever documentation there is for that command.  Each command funtion must
# be prefixed by '_command_'.  After that goes the actual command.


	def _command_addToBinding (self, argv) :

		self._book.addToBinding(argv[0])


	def _command_removeFromBinding (self, argv) :

		self._book.removeFromBinding(argv[0])



	def _command_changeSetting (self, argv) :
		'''Usage: changeSetting [section] [key] [value] | Change a system
		setting.  To use this you need to know exactly what the setting is and
		where it is located in the configuration object.  Use at your own
		risk.'''

		mod = 'project._command_changeSetting()'
		new = argv[2]
		old = self._sysConfig[argv[0]][argv[1]]
		if new != old :
			self._sysConfig[argv[0]][argv[1]] = argv[2]
			self.writeToLog('MSG', 'Changed ' + argv[1] + ' from [' + old + '] to ' + self._sysConfig[argv[0]][argv[1]], mod)
		else :
			self.writeToLog('WRN', 'New setting is the same, no need to change.', mod)


	def _command_render(self, argv) :
		'''Usage: render [compID] | Render the current component.'''

		mod = 'tipe.render()'

		# First check our project setup and try to auto correct any problems that
		# might be caused from missing project assets.  This can include files
		# like.sty, .tex, .usfm, and folders, etc.
		if not self.checkProject(aProject.self) :
			self.writeToLog('ERR', 'No project found!', mod)
			return

		aDoc = self.getDoc(argv[0])
		if not aDoc :
			self.writeToLog('ERR', 'Component [' + argv[0] + '] not found in project', mod)
			return

		#FIXME: What does this next line do?
		aDoc.render()

		# Create the makefile for processing this particular component.  This is
		# done every time TIPE is run.
		if aDoc.createMakefile(thisComponent, command) :
			if runMake() :
				self.writeToLog('MSG', 'Process completed successful!', mod)
			else :
				self.writeToLog('ERR', 'Process did not complete successfuly. Check logs for more information.', mod)

		# Collect the results and report them in the log

		return True


	def _command_addComponent (self, argv) :
		'''Usage: addComponent [CompID] [CompType] | Add a new component to the
		project.'''

		# FIXME: Should add some code to catch bad params

		if self.addNewComponent(argv[0], argv[1]) :
			self.writeToLog('MSG', 'Added component: ' + argv[0] + ' | Type = ' + argv[1], 'tipe.addComponent()')
		else :
			if self._compConf[argv[0]] :
				self.writeToLog('WRN', 'Component: [' + argv[0] + '] already exists, no changes made.', 'tipe.addComponent()')


	def _command_removeComponent (self, argv) :
		'''Usage: removeComponent [CompID] | Remove a component from the
		project.'''

		if argv[0] in self._compConf :
			if self.removeComponent(argv[0]) :
				self.writeToLog('MSG', 'Removed component: ' + argv[0], 'tipe.removeComponent()')
			else :
				self.writeToLog('WRN', 'Component: ' + argv[0] + ' cannot be removed.', 'tipe.removeComponent()')
		else :
			self.writeToLog('WRN', 'Component: ' + argv[0] + ' not found.', 'tipe.removeComponent()')


	def _command_tipeManager (self, argv) :
		'''Usage: tipeManager | Start the TIPE Manager GUI'''

		self.terminal('SORRY: Manager GUI has not been implemented yet.')


	def _command_newProject (self, argv) :
		'''Usage: newProject [CompID] [CompType] | Setup a new project in the
		current directory.'''

		if self.makeProject(os.getcwd()) :
			self.writeToLog('MSG', 'Created new project at: ' + os.getcwd(), 'tipe.newProject()')


	def _command_reInitComponentFiles (self, argv) :
		'''Usage: reInitComponentFiles [CompID] [CompType] | This is a way to
		call initComponentFiles to replace any missing component files.'''

		self.initComponentFiles(argv[0], argv[1])


	def _command_runMake () :
		'''Usage: runMake | All component processes are expected to be run via
		makefile.  This is a generic makefile running function.'''

		# Send off the command return error code
		error = os.system(sysConfig['System']['makeStartParams'] + os.getcwd() + '/' + sysConfig['System']['makefileFile'])

		if error == 0 :
			return True
		else :
			report.terminal('ERROR: tipe.runMake: ' + str(error))
			return



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

			# Change this to an int()
			logLineLimit = int(logLineLimit)

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




