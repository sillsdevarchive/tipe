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

import codecs, os, sys, fileinput, shutil, imp
#from configobj import ConfigObj, Section


# Load the local classes
from tools import *

#from component import Component
#from book import Book
#from xml.etree import ElementTree


###############################################################################
############################ Define Global Functions ##########################
###############################################################################






###############################################################################
################################## Begin Class ################################
###############################################################################

class Project (object) :

	def __init__(self, projConfig, userConfig, projHome, userHome, tipeHome) :

		self.projHome           = projHome
		self.userHome           = userHome
		self.tipeHome           = tipeHome

		# Load project config files
		self._projConfig        = projConfig
		self._userConfig         = userConfig

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

		# Set all the system settings
		if self._userConfig :
			self.projConfFile    = os.path.join(self.projHome, self._userConfig['Files']['projConfFile']['name'])
			self.userConfFile   = os.path.join(self.userHome, self._userConfig['Files']['userConfFile']['name'])
			for k in ('systemVersion',      'userName',
					  'debugging',          'lastEditDate',
					  'projLogLineLimit',   'lockExt') :
				setattr(self, k, self._userConfig['System'][k] if self._userConfig else None)

			self.orgLastEditDate    = self.lastEditDate

		# Load project settings
		for k in ('projectType',            'projectName',
				  'projectLastEditDate',    'projectCreateDate',
				  'projectIDCode',          'projectComponentTypes') :
			setattr(self, k, self._projConfig['ProjectInfo'][k] if self._projConfig else None)

		# In case we are in a situation where we had to make an aProject object
		# with an empty projConfig we will test before doing this.
		if len(self._projConfig) > 0 :
			self.projLogFile        = os.path.join(self.projHome, self._projConfig['Files']['projLogFile']['name'])
			self.projErrorLogFile   = os.path.join(self.projHome, self._projConfig['Files']['projErrorLogFile']['name'])
			self.orgProjectEditDate = self.projectLastEditDate


		# Load project type commands
		try :
			print "Loading: " + os.path.join(self.thisTipeProjTypeLib, self.projectType)
			imp.load_source(self.projectType, os.path.join(self.thisTipeProjTypeLib, self.projectType))
			__import__(self.projectType)
		except Exception, e:
			print sys.path
			print e
			terminal('Failed to load ' + self.projectType + ' project commands')


	def initProject (self, pdir) :
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
					if value != 'None' :
						parentFolder = value
				else :
					pass

			if parentFolder :
				thisFolder = os.path.join(pdir, parentFolder, folderName)
			else :
				thisFolder = os.path.join(pdir, folderName)

			# Create a source folder name in case there is one
			sourceFolder = os.path.join(self.tipeHome, 'resources', 'lib_projTypes', self._projConfig['ProjectInfo']['projectType'], 'lib_folders', folderName)

			if not os.path.isdir(thisFolder) :
				if os.path.isdir(sourceFolder) :
					shutil.copytree(sourceFolder, thisFolder)
				else :
					os.mkdir(thisFolder)
					if self.debugging == 'True' :
						terminal('Created folder: ' + folderName)

		# Create some necessary files
		fls = self._projConfig['Files'].__iter__()
		for fs in fls :
			fileName = ''; parentFolder = ''
			fGroup = self._projConfig['Files'][fs]
			for key, value in fGroup.iteritems() :
				if key == 'name' :
					fileName = value
					if fs == 'projLogFile' :
						self.projLogFile = os.path.join(pdir, value)
					elif fs == 'projErrorLogFile' :
						self.projErrorLogFile = os.path.join(pdir, value)
				elif key == 'location' :
					if value :
						parentFolder = value
				else :
					pass

			if parentFolder :
				thisFile = os.path.join(pdir, parentFolder, fileName)
			else :
				thisFile = os.path.join(pdir, fileName)

			# Create source file name
			sourceFile = os.path.join(self.tipeHome, 'resources', 'lib_projTypes', self._projConfig['ProjectInfo']['projectType'], 'lib_files', fileName)
			# Make the file if it is not already there
			if not os.path.isfile(thisFile) :
				if os.path.isfile(sourceFile) :
					shutil.copy(sourceFile, thisFile)
				else :
					open(thisFile, 'w').close()
					if self.debugging == 'True' :
						terminal('Created file: ' + thisFile)


		# Create a new version of the project config file
		newProjConfig = getDefaultProjSettings(pdir, self.userHome, self.tipeHome, self._projConfig['ProjectInfo']['projectType'])
		newProjConfig['ProjectInfo']['writeOutProjConfFile'] = True
		self._projConfig = mergeProjConfig(newProjConfig, pdir, self.userHome, self.tipeHome)
		self = Project(self._projConfig, self._userConfig, pdir, self.userHome, self.tipeHome)


	def initComponentType (self, ctype) :
		'''Initialize a component type in this project.  This will copy all the
		necessary files and folders into the project to support the processing
		of this component type.'''

		pass


	def makeProject (self, ptype, pname, pid, pdir='') :
		'''Create a new publishing project.'''

		# A new project only needs to have the necessary configuration files.
		# The rest is made with the check project file the first time a
		# component is processed.
		if not pdir :
			pdir = os.getcwd()
		elif pdir == '.' :
			pdir = os.getcwd()
		else :
			pdir = os.path.abspath(pdir)

		# Do some further testing to be sure we are not starting a project
		# inside another project.
		(head, tail) = os.path.split(pdir)
		live = os.path.isfile(os.path.join(head, '.project.conf'))
		dead = os.path.isfile(os.path.join(head, '.project.conf' + self.lockExt))
		if live :
			terminal('Hault! Live project already defined in parent folder')
			return
		elif dead :
			terminal('Hault! Locked project already defined in parent folder')
			return

		# Test if this project already exists in the user's config file.
		if isRecordedProject(self.userConfFile, pid) :
			terminal('Hault! ID [' + pid + '] already defined for another project')
			return

		# If we made it this far lets see if the pdir is there
		if not os.path.isdir(pdir) :
			os.mkdir(pdir)

		date = tStamp()
		self._userConfig['System']['isProject'] = True
		self._userConfig['System']['projCreateDate'] = date
		self.initProject(pdir)

		recordProject(self.userConfFile, pdir, pname, ptype, pid, date)
		self._projConfig['ProjectInfo']['projectType']            = ptype
		self._projConfig['ProjectInfo']['projectName']            = pname
		self._projConfig['ProjectInfo']['projectLastEditDate']    = ''
		self._projConfig['ProjectInfo']['projectCreateDate']      = date
		self._projConfig['ProjectInfo']['projectIDCode']          = pid
		terminal('Created [' + pid + '] project at: ' + pdir)

		# Finally write out the project config file
		writeConfFiles(self._userConfig, self._projConfig, self.userHome, pdir)
		self.writeToLog('LOG', 'Created [' + pid + '] project at: ' + date, 'project.makeProject()')


	def removeProject (self, pid) :
		'''Remove the project from the TIPE system.  This will not remove the
		project data but will 'disable' the project.'''

		# 1) Check the user's conf file to see if the project actually exists
		try :
			if self._userConfig['Projects'][pid] :
				# 2) If the project does exist in the user config, disable the project
				projPath = self._userConfig['Projects'][pid]['projectPath']
				projConfFile = os.path.join(projPath, '.project.conf')
				if os.path.isfile(projConfFile) :
					os.rename(projConfFile, projConfFile + self.lockExt)

				# 3) Remove references from user tipe.conf
				del self._userConfig['Projects'][pid]
				reportSysConfUpdate(self)

				# 4) Report the process is done
				terminal('Project [' + pid + '] removed from system configuration.')
				return

		except :
			terminal('Project ID [' + pid + '] not found in system configuration.')
			return


	def restoreProject (self, pdir) :
		'''Restore a project in the current folder'''

		projConfFile = os.path.join(pdir, '.project.conf')
		if os.path.isfile(projConfFile + self.lockExt) :
			os.rename(projConfFile + self.lockExt, projConfFile)
			self._projConfig = mergeProjConfig(ConfigObj(projConfFile), pdir, self.userHome, self.tipeHome)
			self = Project(self._projConfig, self._userConfig, pdir, self.userHome, self.tipeHome)
			pname = self._projConfig['ProjectInfo']['projectName']
			ptype = self._projConfig['ProjectInfo']['projectType']
			pid = self._projConfig['ProjectInfo']['projectIDCode']
			date = self._projConfig['ProjectInfo']['projectCreateDate']
			recordProject(self.userConfFile, pdir, pname, ptype, pid, date)
			return True


	def addComponentType (self, ctype) :
		'''Add a component type to the current project.  Before doing so, it
		must varify that the requested component type is valid to add to this
		type of project.'''

		self.initComponentType(ctype)
		pass


	def changeSystemSetting (self, key, value) :
		'''Change global default setting (key, value) in the System section of
		the TIPE user settings file.  This will write out changes
		immediately.'''

		if not self._userConfig['System'][key] == value :
			self._userConfig['System'][key] = value
			reportSysConfUpdate(self)
			terminal('Changed ' + key + ' to: ' + value)
			setattr(self, key, self._userConfig['System'][key] if self._userConfig else None)
		else :
			terminal(key + ' already set to ' + value)


#    def addNewComponent(self, idCode, compType) :
#        '''Add a new component id to the binding order and create a new component config section for it'''

#        # We don't want to do this is the component already exists
#        if not idCode in self._compConf :
#            self._compConf[idCode] = Section(self._compConf, 1, self._compConf, indict = self._compMaster['Defaults'].dict())
#            for k, v in self._compConf[idCode].items() :
#                self._compConf[idCode][k] = v.replace('[compID]', idCode)
#            self._compConf[idCode]['Type'] = Section(self._compConf[idCode], 2, self._compConf, indict = self._compMaster[compType].dict())
#            self._book.addToBinding(idCode)
#
#            # Make the Component object and add to book and us
#            aComp = self.addComponent(idCode)

#            # Init the comp files if necessary
#            aComp.initComponentFiles(self)
#
#            # Set the flag for writing out the components config file
#            self._userConfig['System']['writeOutCompConf'] = True
#            return True

#        else :
#            return False

#    def addComponent(self, name) :
#        '''Create a component object for an existing component id and add it to
#        everything that needs to know about it.'''

#        aComp = Component(name, self, self._compConf[name])
#        self._components[aComp.name] = aComp
#        return self._book.addComponent(aComp)


#    def removeComponent (self, idCode) :
#        '''Remove a component from the project.'''
#
#        # We want to do this only if the component already exists
#        if idCode in self._compConf :
#            del(self._compConf[idCode])
#            self._book.removeFromBinding(idCode)
#            # Set the flag for writing out the components config file
#            self._userConfig['System']['writeOutCompConf'] = True
#            return True
#        else :
#            return False


#    def getDoc (self, name) :
#        '''Create a document object.'''
##        # FIXME: I think this needs more work and thought.
#        if name == "Book" :
#            return self._book
#        try :
#            return self._components[name]
#        except KeyError :
#            return None

	# These are Report mod functions that are exposed to the project class via
	# the tools class
#    def terminal(self, msg) : self.terminal(msg)
#    def terminalCentered(self, msg) : self.terminalCentered(msg)
	def writeToLog(self, code, msg, mod) : self.writeToLog(code, msg, mod)
	def trimLog(self, logLineLimit) : self.trimLog(logLineLimit)
#    def mergeProjConfig(self, projConfig, projHome, userHome, tipeHome) : self.mergeProjConfig(projConfig, projHome, userHome, tipeHome)
#    def writeConfFiles(self, userConfig, newProjConfig, userHome, projHome) : self.writeConfFiles(userConfig, newProjConfig, userHome, projHome)
#    def isRecordedProject(self, userConfFile, pid) : self.isRecordedProject(userConfFile, pid)

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
			terminal(code + ' - ' + msg)

		# Test to see if this is a live project by seeing if the project type is
		# set.  If it is, we can write out log files.  Otherwise, why bother?
		if self.projectType :

			# When are we doing this?
			ts = tStamp()

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
				terminal(msg)

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
			terminal('eventLine')

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


