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
# 20110721 - djd - Removed reporting class


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


def safeStart (projHome, userHome, tipeHome) :
	'''TIPE will first load all the tipe.xml default values from the system and
	override with the settings it finds in the user's tipe.conf file.  Next it
	will look in the current folder for a tipe.conf file to further override if
	necessary. Once this is done the program can start'''

	# Check to see if the file is there, then read it in and break it into
	# sections. If it fails, scream really loud!
	tipeXML = os.path.join(tipeHome, 'bin', 'tipe.xml')
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
	tipeProj = os.path.join(projHome, '.tipe.conf')
	if os.path.exists(tipeProj) :
		tp = ConfigObj(tipeProj)
		# Merge with project settings
		res.merge(tp)

	# Return the final results of the conf settings
	return res


def loadProjectSettings (tipeProj, projHome, userHome, tipeHome) :
	'''Load up the project.conf settings.  This will first look in the current
	folder for the .project.conf file.  One exsits then we will first load the
	system defaults, then override with the user settings (if any) then finally
	override with the project settings.  When all that is done we'll look to see
	if the project exists in the user's config file.  If not, we'll add it in
	the projects section.'''

	# Set paths
	projProjConf        = os.path.join(projHome, '.project.conf')
	tipeUserConfFile    = os.path.join(userHome, 'tipe.conf')

	# Get the default settings.  Check the system, then override with the users
	# if needed
	res = getDefaultProjSettings(projHome, userHome, tipeHome, tipeProj)

	# Now get the settings from the .project.conf file if there is one.
	if os.path.exists(projProjConf) :
		# Merge default settings with global settings
		res.merge(ConfigObj(projProjConf))

		# Check the user's config for this project, silently add if needed
		pname = res['ProjectInfo']['projectName']
		ptype = res['ProjectInfo']['projectType']
		pid = res['ProjectInfo']['projectIDCode']
		date = res['ProjectInfo']['projCreateDate']
		if not isRecordedProject(tipeUserConfFile, pid) == True :
			recordProject(tipeUserConfFile, projHome, pname, ptype, pid, date)

	# Return the final results of the conf settings
	return res


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


def isRecordedProject (tipeUserConfFile, pid) :
	'''Check to see if this project is recorded in the user's config'''

	if os.path.isfile(tipeUserConfFile) :
		cf = ConfigObj(tipeUserConfFile)
		try :
			isConfPID = cf['Projects'][pid]
			return True
		except :
			return False


def getDefaultProjSettings (projHome, userHome, tipeHome, tipeProj) :

	tipeProjXML     = os.path.join(tipeHome, 'resources', 'lib_projTypes', tipeProj, tipeProj + '.xml')
	userProjXML     = os.path.join(userHome, 'resources', 'lib_projTypes', tipeProj, tipeProj + '.xml')

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


###############################################################################
################################## Begin Class ################################
###############################################################################

class Project (object) :

	def __init__(self, projHome, userHome, tipeHome) :

		# Set all the initial paths and locations
		# System level paths
		self.tipeHome           = tipeHome
		self.userHome           = userHome
		self.projHome           = projHome
		self.tipeFonts          = os.path.join(tipeHome, 'resources', 'lib_fonts')
		self.tipeIllustrations  = os.path.join(tipeHome, 'resources', 'lib_illustratons')
		self.tipeAdmin          = os.path.join(tipeHome, 'resources', 'lib_admin')
		self.tipeCompTypes      = os.path.join(tipeHome, 'resources', 'lib_compTypes')
		self.tipeProjTypes      = os.path.join(tipeHome, 'resources', 'lib_projTypes')
		# User/Global level paths
		self.userScripts        = os.path.join(userHome, 'resources', 'lib_scripts')
		self.userFonts          = os.path.join(userHome, 'resources', 'lib_fonts')
		self.userIllustrations  = os.path.join(userHome, 'resources', 'lib_illustratons')
		self.userAdmin          = os.path.join(userHome, 'resources', 'lib_admin')
		self.userCompTypes      = os.path.join(userHome, 'resources', 'lib_compTypes')
		self.userProjTypes      = os.path.join(userHome, 'resources', 'lib_projTypes')

		# Load the TIPE config settings and do a safe start
		self._sysConfig         = safeStart(projHome, userHome, tipeHome)

		# Set all the system settings
		if self._sysConfig :
			self.tipeProjConfFile   = os.path.join(self.projHome, self._sysConfig['Files']['tipeProjConfFile']['name'])
			self.projectConfFile    = os.path.join(self.projHome, self._sysConfig['Files']['projectConfFile']['name'])
			self.tipeUserConfFile   = os.path.join(self.userHome, self._sysConfig['Files']['tipeUserConfFile']['name'])
			for k in ('systemVersion',      'userName',
					  'debugging',          'tipeEditDate',
					  'projLogLineLimit',   'lockExt',
					  'thisProjectType') :
				setattr(self, k, self._sysConfig['System'][k] if self._sysConfig else None)

			self.orgTipeEditDate    = self.tipeEditDate

		# Look for a project in the current location and load the settings
		if os.path.isfile(self.projectConfFile) :
			self._projConfig = loadProjectSettings(self.thisProjectType, self.projHome, self.userHome, self.tipeHome)
			for k in ('projectType',        'projectName',
					  'projectEditDate',    'projCreateDate',
					  'projectIDCode') :
				setattr(self, k, self._projConfig['ProjectInfo'][k] if self._projConfig else None)
			if self._projConfig :
				self.projLogFile        = os.path.join(self.projHome, self._projConfig['Files']['projLogFile']['name'])
				self.projErrorLogFile   = os.path.join(self.projHome, self._projConfig['Files']['projErrorLogFile']['name'])
				self.orgProjectEditDate = self.projectEditDate


###############################################################################
############################# Begin Main Functions ############################
###############################################################################


	def writeProjConfFiles (self) :
		'''Write out all relevent project conf files if there is at least
		project in memory.'''

		ts = self.tStamp()

		# Check the "thisProjectType" for existence of a project
		if self.thisProjectType :
			# Write out config files only if the edit date has changed
			if self.orgTipeEditDate != self.tipeEditDate :
				self._sysConfig.filename = self.tipeProjConfFile
				self.tipeEditDate = ts
				self.orgTipeEditDate = ts
				self._sysConfig.write()
				if self.debugging == 'True' :
					self.writeToLog('LOG', 'Updated .tipe.conf file.', 'project.writeProjConfFiles')

			if self.orgProjectEditDate != self.projectEditDate :
				self._projConfig.filename = self.projectConfFile
				self.projectEditDate = ts
				self.orgProjectEditDate = ts
				self._projConfig.write()
				if self.debugging == 'True' :
					self.writeToLog('LOG', 'Updated .project.conf file.', 'project.writeProjConfFiles')


	def initProject (self, home) :
		'''Initialize a new project by creating all necessary global items like
		folders, etc.'''

		mod = 'project.initProject()'

		# Create all necessary folders
		fldrs = self._projConfig['Folders'].__iter__()
		for f in fldrs :
			folderName = ''; parentFolder = ''
			fGroup = self._projConfig['Folders'][f]
			for key, value in fGroup.iteritems() :
				if key == 'name' :
					folderName = value
				elif key == 'location' :
					if value :
						parentFolder = value
				else :
					pass

			if parentFolder :
				thisFolder = os.path.join(home, parentFolder, folderName)
			else :
				thisFolder = os.path.join(home, folderName)

			if not os.path.isdir(thisFolder) :
				os.mkdir(thisFolder)
				if self.debugging == 'True' :
					self.terminal('Created folder: ' + folderName)

		# Create some necessary files
		fls = self._projConfig['Files'].__iter__()
		for fs in fls :
			fileName = ''; parentFolder = ''
			fGroup = self._projConfig['Files'][fs]
			for key, value in fGroup.iteritems() :
				if key == 'name' :
					fileName = value
					if fs == 'projLogFile' :
						self.projLogFile = os.path.join(home, value)
					elif fs == 'projErrorLogFile' :
						self.projErrorLogFile = os.path.join(home, value)
				elif key == 'location' :
					if value :
						parentFolder = value
				else :
					pass

			if parentFolder :
				thisFile = os.path.join(home, parentFolder, fileName)
			else :
				thisFile = os.path.join(home, fileName)

		self._projConfig = loadProjectSettings(self.thisProjectType, home, self.userHome, self.tipeHome)

		self.writeProjConfFiles()


	def makeProject (self, pType='', pName='', pID='', pDir='') :
		'''Create a new publishing project.  If parms are blank defaults will be
		substituted'''

		mod = 'project.makeProject()'
		ts = self.tStamp()

		# It is required that there be at least a project type defined we will
		# look for that here and fail if we don't find it
		if pType == '' :
			pType = 'bookTex'
			self.thisProjectType = pType
			self._sysConfig['System']['thisProjectType'] = pType
			self.terminal('Type parameter missing, using default of bookTex')

		if pName == '' :
			pName = 'Missing Name'
			self.projectName = pName
			self.terminal('Name parameter missing, setting to \"Missing Name\"')

		if pID == '' :
			# create a simple short guid
			import time
			pID = hex(int(time.time()))
			self.terminal('ID parameter missing, setting to [' + pID + ']')

		self.projectIDCode = pID

		# This can create a project in directory other than the current one.
		if pDir == '' :
			pDir = os.path.join(self.projHome, pID)
			# FIXME: Does this need to be hardwired
			self.tipeProjConfFile = os.path.join(pDir, '.tipe.conf')
			self.terminal('Directory parameter missing, set to: ' + pDir)


		# See if a project is already in the target dir by looking for a
		# .project.conf file
		# FIXME: Does this need to be hardwired
		pConf = os.path.join(pDir, '.project.conf')
		if os.path.isfile(pConf) or os.path.isfile(pConf + self.lockExt)  :
			self.terminal('Hault! A project is already defined in this folder.')
			return

		# See if a project is in the parent dir by looking for a .project.conf file
		(head, tail) = os.path.split(pDir)
		# FIXME: Does this need to be hardwired
		if os.path.isfile(os.path.join(head, '.project.conf')) :
			self.terminal('Hault! A project is already defined in the parent folder')
			return

		# Test if this project already exists in the user's config file.
		if isRecordedProject(self.tipeUserConfFile, pID) :
			self.terminal('Hault! ID [' + pID + '] already defined for another project')
			return

		# A new project will need to be based on a predefined type.  First check
		# to see if that type exists.  Project type definition files can exist
		# in two places, they users settings area and the system.  We will use
		# the first instance we find and we will look in the user's settings
		# area first.
		if os.path.isdir(os.path.join(self.userProjTypes, pType)) :
			projTypeToUse = os.path.join(self.userProjTypes, pType)
		elif os.path.isdir(os.path.join(self.tipeProjTypes, pType)) :
			projTypeToUse = os.path.join(self.tipeProjTypes, pType)
		else :
			self.terminal('Error: Project type does not exist: ')
			return

		# Initialize new project now
		if not os.path.isdir(pDir) :
			os.mkdir(pDir)

		# Pull in default settings and update project settings
		self._projConfig = getDefaultProjSettings(pDir, self.userHome, self.tipeHome, pType)
		if self._projConfig :
			self.projectConfFile = os.path.join(pDir, '.project.conf')
			self._projConfig['ProjectInfo']['projectType'] = pType
			self.projectType = pType
			self._projConfig['ProjectInfo']['projectName'] = pName
			self.projectName = pName
			self._projConfig['ProjectInfo']['projectIDCode'] = pID
			self.projectIDCode = pID
			self._projConfig['ProjectInfo']['projCreateDate'] = ts
			self.projectCreateDate = ts
			self._projConfig['ProjectInfo']['projectEditDate'] = ts
			self.projectEditDate = ts
			self.orgProjectEditDate = ''
			self.tipeEditDate = ts
			self.orgTipeEditDate = ''
			self.writeProjConfFiles()
			self.initProject(pDir)
			# Record the project with the system
			recordProject(self.tipeUserConfFile, pDir, pName, pType, pID, ts)
			return True
		else :
			self.terminal('ERR', 'Failed to initialize project.', mod)
			return


	def removeProject (self, pID) :
		'''Remove the project from the TIPE system.  This will not remove the
		project data but will 'disable' the project.'''

		# 1) Check the user's conf file to see if the project actually exists
		if not isRecordedProject(self.tipeUserConfFile, pID) :
			self.terminal('Project ID [' + pID + '] not found in system configuration.')
			return
		else :
			# 2) If the project does exist in the user config, disable the project
			cf = ConfigObj(self.tipeUserConfFile)
			projPath = cf['Projects'][pID]['projectPath']
			projTipeConf = os.path.join(projPath, '.tipe.conf')
			projProjConf = os.path.join(projPath, '.project.conf')
			if os.path.isfile(projTipeConf) :
				os.rename(projTipeConf, projTipeConf + self.lockExt)
			if os.path.isfile(projProjConf) :
				os.rename(projProjConf, projProjConf + self.lockExt)

			# 3) Remove references from user tipe.conf
			del cf['Projects'][pID]
			cf.write()

			# 4) Report the process is done
			self.terminal('Project [' + pID + '] removed from system configuration.')
			return


	def restoreProject (self, pDir) :
		'''Restore a project in the current folder'''

		projTipeConf = os.path.join(pDir, '.tipe.conf')
		projProjConf = os.path.join(pDir, '.project.conf')
		if os.path.isfile(projTipeConf + self.lockExt) and os.path.isfile(projProjConf + self.lockExt) :
			os.rename(projTipeConf + self.lockExt, projTipeConf)
			os.rename(projProjConf + self.lockExt, projProjConf)
			return True


	def addNewComponent(self, idCode, compType) :
		'''Add a new component id to the binding order and create a new
		component config section for it'''

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


	def changeSystemSetting (self, key, value) :
		'''Change global default setting (key, value) in the System section'''

		mod = 'project.changeSystemDefault()'

		# Load user config object
		if os.path.isfile(self.tipeUserConfFile) :
			cf = ConfigObj(self.tipeUserConfFile)

		# Change the setting here
		cf['System'][key] = value
		self._sysConfig['System'][key] = value
		self.writeToLog('MSG', 'Changed ' + key + ' to: ' + value, mod)
		ts = self.tStamp()
		self._sysConfig['System']['tipeEditDate'] = ts
		self.tipeEditDate = ts
		cf['System']['userEditDate'] = ts
		cf.write()

		# Write the change out right a way
		self.writeProjConfFiles()


	# These are Report mod functions that are exposed to the project class
#    def terminal(self, msg) : self.report.terminal(msg)
#    def terminalCentered(self, msg) : self.report.terminalCentered(msg)
#    def writeToLog(self, code, msg, mod) : self.report.writeToLog(code, msg, mod)
#    def trimLog(self, projLogLineLimit) : self.report.trimLog(projLogLineLimit)



###############################################################################
############################# Report/Log Functions ############################
###############################################################################


	def terminal (self, msg) :
		'''Send a message to the terminal with a little formating to make it
		look nicer.'''

		# Output the message and wrap it if it is over 60 chars long.
		print self.wordWrap(msg, 60)


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


	def tStamp (self) :
		'''Create a simple time stamp for logging and timing purposes.'''

		date_time, secs = str(datetime.now()).split(".")

		return date_time


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

		# Test to see if this is a live project by seeing if the project type is
		# set.  If it is, we can write out log files.  Otherwise, why bother?
		if self.thisProjectType :

			# When are we doing this?
			ts = self.tStamp()

			# Build the event line
			if code == 'ERR' :
				eventLine = '\"' + ts + '\", \"' + code + '\", \"' + mod + msg + '\"'
			else :
				eventLine = '\"' + ts + '\", \"' + code + '\", \"' + msg + '\"'

			# Do we need a log file made?
			try :
				if not os.path.isfile(self.projLogFile) or os.path.getsize(self.projLogFile) == 0 :
					writeObject = codecs.open(self.projLogFile, "w", encoding='utf_8')
					writeObject.write('TIPE event log file created: ' + ts + '\n')
					writeObject.close()

				# Now log the event to the top of the log file using preAppend().
				self.preAppend(eventLine, self.projLogFile)

				# Write errors and warnings to the error log file
				if code == 'WRN' and self.debugging == 'True':
					self.writeToErrorLog(eventLine)

				if code == 'ERR' :
					self.writeToErrorLog(eventLine)

			except :
				self.terminal(msg)

		return


	def writeToErrorLog (self, eventLine) :
		'''In a perfect world there would be no errors, but alas there are and
		we need to put them in a special file that can be accessed after the
		process is run.  The error file from the previous session is deleted at
		the begining of each new run.'''

		try :
			# Because we want to read errors from top to bottom, we don't pre append
			# them to the error log file.
			if not os.path.isfile(self.projErrorLogFile) :
				writeObject = codecs.open(self.projErrorLogFile, "w", encoding='utf_8')
			else :
				writeObject = codecs.open(self.projErrorLogFile, "a", encoding='utf_8')

			# Write and close
			writeObject.write(eventLine + '\n')
			writeObject.close()
		except :
			self.terminal('eventLine')

		return


	def trimLog (self, projLogLineLimit = 1000) :
		'''Trim the system log file.  This will take an existing log file and
		trim it to the amount specified in the system file.'''

		# Of course this isn't needed if there isn't even a log file
		if os.path.isfile(self.projLogFile) :

			# Change this to an int()
			projLogLineLimit = int(projLogLineLimit)

			# Read in the existing log file
			readObject = codecs.open(self.projLogFile, "r", encoding='utf_8')
			lines = readObject.readlines()
			readObject.close()

			# Process only if we have enough lines
			if len(lines) > projLogLineLimit :

				writeObject = codecs.open(self.projLogFile, "w", encoding='utf_8')
				lineCount = 0
				for line in lines :
					if projLogLineLimit > lineCount :
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


