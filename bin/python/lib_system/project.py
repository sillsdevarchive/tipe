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
from component import Component


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
		self._userConfig        = userConfig

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
			self.projConfFile   = os.path.join(self.projHome, self._userConfig['Files']['projConfFile']['name'])
			self.userConfFile   = os.path.join(self.userHome, self._userConfig['Files']['userConfFile']['name'])
			for k in ('systemVersion',      'userName',
					  'debugging',          'lastEditDate',
					  'projLogLineLimit',   'lockExt') :
				setattr(self, k, self._userConfig['System'][k] if self._userConfig else None)

			self.orgLastEditDate    = self.lastEditDate

		# If there is no project yet we want to just skip this next part
		try :
			self.loadConfig()
			self.loadComponents()
		except :
			pass


	def addNewComponent (self, cid, ctype, csource) :
		'''Add component to the current project by adding them to the component
		binding list and inserting component info into the project conf file.
		All supplied arguments need to be valid.  This function will fail if the
		type, source or ID are not valid or if the component already exsists in
		the binding order list.'''

		typeList = self._projConfig['ProjectInfo']['validCompTypes']
		validCompList = self._projConfig['Components'][ctype]['validIdCodes']
		if cid not in self._projConfig['ProjectInfo']['projectComponentBindingOrder'] :
			if ctype in typeList and cid in validCompList and os.path.isfile(csource) :
				# Add component code to binding order list
				listOrder = []
				listOrder = self._projConfig['ProjectInfo']['projectComponentBindingOrder']
				listOrder.append(cid)
				# If one doesn't already exsist, create a section under the
				# component type section
				try :
					isHere = self._projConfig['Components'][ctype][cid]
				except :
					compItem = ConfigObj()
					compItem['Components'] = {}
					compItem['Components'][ctype] = {}
					compItem['Components'][ctype][cid] = {}
					compItem['Components'][ctype][cid]['source'] = csource
					self._projConfig.merge(compItem)

				self._projConfig['ProjectInfo']['projectComponentBindingOrder'] = listOrder
				self._projConfig['ProjectInfo']['writeOutProjConfFile'] = True
				self.writeToLog('MSG', 'Component added: ' + str(cid), 'bookTex.addNewComponents()')
		else :
				self.writeToLog('WRN', 'Component exsits: ' + str(cid) + ' No action taken.', 'bookTex.addNewComponents()')


	def removeComponent (self, comp) :
		'''Remove a component from the current project by removing them from the
		component binding list and from their type information section.'''

		orderList = []
		orderList = self._projConfig['ProjectInfo']['projectComponentBindingOrder']
		if comp in orderList :
			orderList.remove(comp)
		else :
			self.writeToLog('WRN', 'Component [' + comp + '] not found in binding order list', 'bookTex.removeComponents()')

		self._projConfig['ProjectInfo']['projectComponentBindingOrder'] = orderList
		# Remove references in the Components section.  To do this we will need
		# to look up the ctype first.
		compTypeList = self._projConfig['ProjectInfo']['projectComponentTypes']
		for ctype in compTypeList :
			try :
				del self._projConfig['Components'][ctype][comp]
				self._projConfig['ProjectInfo']['writeOutProjConfFile'] = True
				self.writeToLog('MSG', 'Removed component: [' + comp + '] from project.', 'bookTex.removeComponents()')
			except :
				pass



	def addNewComponentType (self, ctype) :
		'''Add a component type to the current project.  Before doing so, it
		must varify that the requested component type is valid to add to this
		type of project.  The component type is only added to the
		projectComponentTypes list in the project conf file.  The next time TIPE
		is run the component type will be initialized.'''

		compTypeList = []
		compTypeList = self._projConfig['ProjectInfo']['projectComponentTypes']

		if ctype in self.validCompTypes :
			if not ctype in compTypeList :
				compTypeList.append(ctype)
				self._projConfig['ProjectInfo']['projectComponentTypes'] = compTypeList
				self._projConfig.merge(getDefaultCompTypeSettings(self.userHome, self.tipeHome, ctype))
				self._projConfig['ProjectInfo']['writeOutProjConfFile'] = True
				self.writeToLog('MSG', 'Component type: [' + ctype + '] added to the project.', 'bookTex.addNewComponentType()')
			else :
				self.writeToLog('WRN', 'Component type: [' + ctype + '] already exsits.', 'bookTex.addNewComponentType()')

		else :
			self.writeToLog('ERR', 'Invalid component type: [' + ctype + ']', 'bookTex_command.AddCompType')


	def removeComponentType (self, ctype) :
		'''Remove a component type to the current project.  Before doing so, it
		must varify that the requested component type is valid.'''

		compTypeList = []
		compTypeList = self._projConfig['ProjectInfo']['projectComponentTypes']

		if ctype in compTypeList :
			# Remove it from the components list
			compTypeList.remove(ctype)
			self._projConfig['ProjectInfo']['projectComponentTypes'] = compTypeList
			# Remove references in the Components section
			del self._projConfig['Components'][ctype]
			self._projConfig['ProjectInfo']['writeOutProjConfFile'] = True
			# FIXME: More should be done at this point to remove files, etc of the comp type.
			self.writeToLog('MSG', 'Component type: [' + ctype + '] removed from project.', 'bookTex.removeComponentType()')
		else :
			self.writeToLog('WRN', 'Component type: [' + ctype + '] does not exsits.', 'bookTex.removeComponentType()')


#    def loadComponents (self) :
#        '''Load all the component modules and information that have been defined
#        for this project.  This is taken from the projectComponentTypes list in
#        the conf file.  It then intializes each component type.'''

#        self.componentClasses = {}
#        if len(self.projectComponentTypes) > 0 :
#            for compType in self.projectComponentTypes :
#                if compType in self.validCompTypes :
#                    thisCompLib = os.path.join(self.tipeCompTypes, compType, 'lib_python')
#                    sys.path.insert(0, thisCompLib)
#                    try :
#                        compModule = __import__(compType)
#                        compClass = getattr(compModule, compType[0].upper() + compType[1:], Component)
#                    except :
#                        compClass = Component
#                        terminal('Error: Component module not found for: ' + compType)

#                    self.componentClasses[compType] = compClass
#                    compClass.initType(self)
#                else :
#                    terminal('Error: Invalid component type found: ' + compType)


	def loadConfig(self) :
		# Load project settings
		for k in ('projectType',            'projectName',
				  'projectLastEditDate',    'projectCreateDate',
				  'projectIDCode',          'projectComponentTypes',
				  'validCompTypes',         'writeOutProjConfFile') :

			setattr(self, k, self._projConfig['ProjectInfo'][k] if 'ProjectInfo' in self._projConfig else None)

		# In case we are in a situation where we had to make an aProject object
		# with an empty projConfig we will test before doing this.
		if len(self._projConfig) > 0 :
			self.projLogFile        = os.path.join(self.projHome, self._projConfig['Files']['projLogFile']['name'])
			self.projErrorLogFile   = os.path.join(self.projHome, self._projConfig['Files']['projErrorLogFile']['name'])
			self.orgProjectEditDate = self.projectLastEditDate


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


	def makeProject (self, ptype, pname, pid, pdir='') :
		'''Create a new publishing project.'''

		# Run some basic tests to see if this project can be created
		# Test if this project already exists in the user's config file.
		if isRecordedProject(self.userConfFile, pid) :
			terminal('Halt! ID [' + pid + '] already defined for another project')
			return False

		# Grab the cwd if pdir is empty for the default
		if not pdir or pdir == '.' :
			pdir = os.getcwd()
		else :
			# So a pdir has been passed now it needs testing
			pdir = os.path.abspath(pdir)
			# Test for parent project.
			if os.path.isfile(os.path.join(pdir, '.project.conf')) :
				terminal('Halt! Live project already defined in this location')
				return False
			elif os.path.isfile(os.path.join(os.path.dirname(pdir), '.project.conf')) :
				terminal('Halt! Live project already defined in parent folder')
				return False
			elif os.path.isfile(os.path.join(os.path.dirname(pdir), '.project.conf' + self.lockExt)) :
				terminal('Halt! Locked project already defined in parent folder')
				return False
			elif not os.path.isdir(os.path.dirname(pdir)) :
				terminal('Halt! Not a valid (parent) path: ' + pdir)
				return False

		# If we made it to this point we need to check to see if the project
		# folder exists, if it doesn't make.  We can create only one level deep
		# though.'
		if not os.path.isdir(pdir) :
			os.mkdir(pdir)

		# Create a new version of the project config file
		newProjConfig = getDefaultProjSettings(self.userHome, self.tipeHome, ptype)
		newProjConfig['ProjectInfo']['writeOutProjConfFile'] = True
		self._projConfig = newProjConfig
		self.loadConfig()

		date = tStamp()
		self._userConfig['System']['isProject'] = True
		self._userConfig['System']['projCreateDate'] = date
		self.initProject(pdir)

		self._projConfig['ProjectInfo']['projectType']            = ptype
		self._projConfig['ProjectInfo']['projectName']            = pname
		self._projConfig['ProjectInfo']['projectLastEditDate']    = ''
		self._projConfig['ProjectInfo']['projectCreateDate']      = date
		self._projConfig['ProjectInfo']['projectIDCode']          = pid
		recordProject(self.userConfFile, self._projConfig, pdir)

		# Finally write out the project config file
		writeConfFiles(self._userConfig, self._projConfig, self.userHome, pdir)
		self.writeToLog('LOG', 'Created [' + pid + '] project at: ' + date, 'project.makeProject()')


	def removeProject (self, pid='') :
		'''Remove the project from the TIPE system.  This will not remove the
		project data but will 'disable' the project.'''

		# If no pid was given we'll try to get the current on if there is one
		if pid == '' :
			if self.projectIDCode :
				pid = self.projectIDCode
			else :
				terminal('Project ID code not given or found. Remove project failed.')
				return False

		# If we made it this far we should be able to remove it
		try :
			# Check to see if the project does exist in the user config
			if self._userConfig['Projects'][pid] :
				projPath = self._userConfig['Projects'][pid]['projectPath']
				projConfFile = os.path.join(projPath, '.project.conf')
				# Disable the project
				if os.path.isfile(projConfFile) :
					os.rename(projConfFile, projConfFile + self.lockExt)

				# Remove references from user tipe.conf
				del self._userConfig['Projects'][pid]
				reportSysConfUpdate(self)

				# Report the process is done
				terminal('Project [' + pid + '] removed from system configuration.')
				return True

		except :
			terminal('Project ID [' + pid + '] not found in system configuration.')
			return False


	def restoreProject (self, pdir='') :
		'''Restore a project in the current folder'''

		# Normalize the path to the project we want to restore
		if pdir == '' or pdir == '.' :
			pdir = os.getcwd()
		else :
			pdir = os.path.abspath(pdir)

		# Restore the project
		projConfFile = os.path.join(pdir, '.project.conf')
		if os.path.isfile(projConfFile + self.lockExt) :
			os.rename(projConfFile + self.lockExt, projConfFile)

			# We could put a lot of code here to get this project recorded and
			# check the integrity, or, we could just let that happen the next
			# time TIPE is run on the project.  For now we'll do that.
			terminal('Restored project at: ' + pdir)
			return True

		else :
			terminal('Could not find project at: ' + pdir)
			return False


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


###############################################################################
################################# Logging routines ############################
###############################################################################

# These have to do with keeping a running project log file.  Everything done is
# recorded in the log file and that file is trimmed to a length that is
# specified in the system settings.  Everything is channeled to the log file but
# depending on what has happened, they are classed in three levels:
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
			terminal('\n' + code + ' - ' + msg)

		# Test to see if this is a live project by seeing if the project conf is
		# there.  If it is, we can write out log files.  Otherwise, why bother?
		if os.path.isfile(self.projConfFile) :

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
			terminal(eventLine)

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


