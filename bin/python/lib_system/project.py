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



# REFACTOR
# Not sure yet what all is needed in the following commented code
###############################################################################

#def override(sysConfig, fname) :
#    '''Subprocess of override_components().  The purpose is to override default
#    settings taken from the TIPE system (sysConfig) file with those found in the
#    project.conf file (projConfig).'''

#    # Read in the project.conf file and create an object
#    projConfig = ConfigObj(fname)
#    res = ConfigObj(sysConfig.dict())

#    # Recall this function to override the default settings
#    res.override(projConfig)
#    return res


#def override_components(aConfig, fname) :
#    '''Overrides component settings that we got from the default XML system
#    settings file.'''
#    res = ConfigObj()
#    projConfig = ConfigObj(fname)
#    for s, v in projConfig.items() :
#        newtype = v['Type']
#        old = Section(projConfig, 1, projConfig, indict = aConfig['Defaults'].dict())
#        old.override(v)
#        oldtype = Section(v, 2, projConfig, indict = aConfig[v['compType']].dict())
#        oldtype.override(newtype)
#        res[s] = old
#        res[s]['Type'] = oldtype
#    return res


#def override_section(self, aSection) :
#    '''Overrides an entire setting section.'''

#    for k, v in self.items() :
#        if k in aSection :
#            if isinstance(v, dict) and isinstance(aSection[k], dict) :
#                v.override(aSection[k])
#            elif not isinstance(v, dict) and not isinstance(aSection[k], dict) :
#                self[k] = aSection[k]


## This will reasign the standard ConfigObj function that works much like ours
## but not quite what we need for working with XML as one of the inputs.
#Section.override = override_section


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

###############################################################################

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


def loadProjectSettings (projHome, userHome, tipeHome) :
	'''Load up the project.conf settings.  This will first look in the current
	folder for the .project.conf file.  One exsits then we will first load the
	system defaults, then override with the user settings (if any) then finally
	override with the project settings.'''

	# Set path to project config file
	projProjConf    = os.path.join(projHome, '.project.conf')

	# Do a quick load to get the project type, then we'll reload in order
	tipeProj = ''
	if os.path.isfile(projProjConf) :
		temp = ConfigObj(projProjConf)
		tipeProj = temp['ProjectInfo']['projectType']
	else :
		raise IOError, "Can't open " + projProjConf

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

	# Now get the settings from the .project.conf file if there is one.
	if os.path.exists(projProjConf) :
		# Merge default settings with global settings
		res.merge(ConfigObj(projProjConf))


	# Return the final results of the conf settings
	return res


def makeProjectSettings (projHome, userHome, tipeHome, tipeProj) :

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



#####################################################################################


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
		# Config files (These are hardwired, should they be?)
		self.tipeUserConf               = os.path.join(self.userHome, 'tipe.conf')
		self.tipeProjConf               = os.path.join(self.projHome, '.tipe.conf')
		self.projectConfFile            = os.path.join(self.projHome, '.project.conf')

		# Load the TIPE config settings and do a safe start
		self._sysConfig                     = safeStart(projHome, userHome, tipeHome)

		# Set all the system settings
		if self._sysConfig :
			self.initLogging(self.projHome)
			self.version                    = self._sysConfig['System']['systemVersion']
			self.userName                   = self._sysConfig['System']['userName']
			self.tipeEditDate               = self._sysConfig['System']['tipeEditDate']
			self.orgTipeEditDate            = self.tipeEditDate
			# File paths
			self.projErrorLogFile           = os.path.join(self.projHome, self._sysConfig['FileNames']['projErrorLogFile'])
			self.projLogLineLimit           = self._sysConfig['System']['projLogLineLimit']

		# Look for a project in the current location and load the settings
		if os.path.isfile(self.projectConfFile) :
			self._projConfig = loadProjectSettings(self.projHome, self.userHome, self.tipeHome)
			if self._projConfig :
				self.projectType                = self._projConfig['ProjectInfo']['projectType']
				self.projectName                = self._projConfig['ProjectInfo']['projectName']
				self.projectEditDate            = self._projConfig['ProjectInfo']['projectEditDate']
				self.orgProjectEditDate         = self.projectEditDate
				self.projectCreateDate          = self._projConfig['ProjectInfo']['projCreateDate']
				self.projectIDCode              = self._projConfig['ProjectInfo']['projectIDCode']
		else :
			# Set this in case there is no project present
			self.projectName                    = 'None'


###############################################################################
############################# Begin Main Functions ############################
###############################################################################

	def writeProjConfFiles (self) :
		'''Write out all relevent project conf files if there is at least
		project in memory.'''

		# We'll test for a project by looking for a name
		if self.projectName != 'None' :
			date_time, secs = str(datetime.now()).split(".")
			# Write out config files only if the edit date has changed
			if self.orgTipeEditDate != self.tipeEditDate :
				self._sysConfig.filename = self.tipeProjConf
				self._sysConfig.write()

			if self.orgProjectEditDate != self.projectEditDate :
				self._projConfig.filename = self.projectConfFile
				self._projConfig.write()



	def initLogging (self, dir) :
		'''Initialize the log file system.'''

		self.report = Report(
			projLogFile         = os.path.join(dir, self._sysConfig['FileNames']['projLogFile']) if self._sysConfig else None,
			projErrFile         = os.path.join(dir, self._sysConfig['FileNames']['projErrorLogFile']) if self._sysConfig else None,
			debug               = self._sysConfig and self._sysConfig['System']['debugging'],
			projectConfFile     = self.projectConfFile)


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
		for key, value in self._projConfig['Folders'].iteritems() :
			thisFolder = os.path.join(home, value)
			if not os.path.isdir(thisFolder) :
				os.mkdir(thisFolder)
				self.writeToLog('LOG', 'Created folder: ' + value, mod)


	def makeProject (self, settings="") :
		'''Create a new publishing project based on a specific predefined
		project type. This command will take the following parameters:
			-ptype "text"   The project type (required)
			-pname "text"   The human readable name of the project
			-pid "text"     The project ID code
			-ctype "text"   Component type to add to this project
			-comp file      File name of a component to add '''

		mod = 'project.makeProject()'

		# Collect our parameters
		c = 0; ptype = ''; pname = ''; pid = ''; ctype = ''; comp = ''
		commands = ['-ptype', '-pname', '-pid', '-ctype', '-comp']
		for s in settings :
			if s in commands :
				if s == '-ptype' :
					ptype = settings[c+1]
				elif s == '-pname' :
					pname = settings[c+1]
				elif s == '-pid' :
					pid = settings[c+1]
				elif s == '-ctype' :
					ctype = settings[c+1]
				elif s == '-comp' :
					comp = settings[c+1]
			else :
				if s[0] == '-' :
					self.writeToLog('ERR', 'Command (' + s + ') not found, process failed!', mod)
					return

			c+=1

		# It is required that there be at least a project type defined we will
		# look for that here and fail if we don't find it
		if ptype == '' :
			self.writeToLog('ERR', 'Project type required (-ptype), process failed!', mod)
			return

		# See if a project is already here by looking for a .project.conf file
		if os.path.isfile(self.projectConfFile) :
			self.writeToLog('ERR', 'Hault! A project is already defined in this location.', mod)
			return

		# A new project will need to be based on a predefined type.  First check
		# to see if that type exists.  Project type definition files can exist
		# in two places, they users settings area and the system.  We will use
		# the first instance we find and we will look in the user's settings
		# area first.
		if os.path.isdir(os.path.join(self.userProjTypes, ptype)) :
			projTypeToUse = os.path.join(self.userProjTypes, ptype)
		elif os.path.isdir(os.path.join(self.tipeProjTypes, ptype)) :
			projTypeToUse = os.path.join(self.tipeProjTypes, ptype)
		else :
			self.writeToLog('ERR', 'Project type does not exist: ' + ptype, mod)
			return

		# Initialize new project now
		self._projConfig = makeProjectSettings(self.projHome, self.userHome, self.tipeHome, ptype)
		if self._projConfig :
			date_time, secs = str(datetime.now()).split(".")
			self.projectType = ptype
			self.projectConfFile = os.path.join(self.projHome, '.project.conf')
			self._projConfig['ProjectInfo']['projectName'] = pname
			self.projectName = pname
			self._projConfig['ProjectInfo']['projectIDCode'] = pid
			self.projectIDCode = pid
			self._projConfig['ProjectInfo']['projCreateDate'] = date_time
			self.projectCreateDate = date_time
			self._projConfig['ProjectInfo']['projectEditDate'] = date_time
			self.projectEditDate = date_time
			self.orgProjectEditDate = ''
			self.orgTipeEditDate = ''
			self.initLogging(self.projHome)
			self.initProject(self.projHome)
			return True
		else :
			self.writeToLog('ERR', 'Failed to initialize project.', mod)
			return


	def removeProject (self, settings="") :
		'''Remove the project from the current working folder.'''

		# 1) Check if the project actually exists and report and pass if it does
		# 2) If the project does exists, give a warning and ask for input. (add a force override)
		# 3) Remove references from project tipe.conf
		# 4) Clean out all project and component residue (this is where work could be lost)
		# 5) Report the process is done

		pass


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
	def trimLog(self, projLogLineLimit) : self.report.trimLog(projLogLineLimit)


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

	def _command_changeUser (self, argv) :
		'''Change the user name of this specific installation of TIPE.'''

		mod = 'project.changeUser'
		date_time, secs = str(datetime.now()).split(".")
		self._sysConfig['System']['userName'] = argv[0]
		self._sysConfig['System']['userEditDate'] = date_time
		userConfig = ConfigObj(self.tipeUserConf)
		if userConfig['System']['userName'] == self._sysConfig['System']['userName'] :
			self.writeToLog('MSG', 'Name already in use: ' + self._sysConfig['System']['userName'], mod)
		else :
			userConfig.filename = self.tipeUserConf
			userConfig['System']['userEditDate'] = self._sysConfig['System']['userEditDate']
			userConfig['System']['userName'] = self._sysConfig['System']['userName']
			userConfig.write()
			self.writeToLog('MSG', 'User name changed to: ' + self._sysConfig['System']['userName'], mod)


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
		'''Usage: newProject ProjectType [ProjectName] | Setup a new project in the
		current directory.'''

		if self.makeProject(argv) :
				self.writeToLog('MSG', 'Created new project at: ' + os.getcwd(), 'project.newProject()')


	def _command_removeProject (self, argv) :
		'''Usage: removeProject ProjectType | Remove an existing project in
		the current directory.'''

		if self.removeProject(argv) :
				self.writeToLog('MSG', 'Removed project at: ' + os.getcwd(), 'project.newProject()')


#    def _command_reInitComponentFiles (self, argv) :
#        '''Usage: reInitComponentFiles [CompID] [CompType] | This is a way to
#        call initComponentFiles to replace any missing component files.'''
#
#        self.initComponentFiles(argv[0], argv[1])


#    def _command_runMake () :
#        '''Usage: runMake | All component processes are expected to be run via
#        makefile.  This is a generic makefile running function.'''

#        # Send off the command return error code
#        error = os.system(sysConfig['System']['makeStartParams'] + os.getcwd() + '/' + sysConfig['System']['makefileFile'])
#
#        if error == 0 :
#            return True
#        else :
#            report.terminal('ERROR: tipe.runMake: ' + str(error))
#            return



###############################################################################
############################### Reporting Class ###############################
###############################################################################


class Report (object) :

	# Intitate the whole class
	def __init__(self, projLogFile = None, projErrFile = None, debug = False, projectConfFile = None) :

		self._debugging         = False
		self._projLogFile       = projLogFile
		self._projErrorLogFile  = projErrFile
		self._debugging         = debug
		self._projectConfFile   = projectConfFile


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

		# If the project type is set then this is a live project and we can
		# write out log files.  Otherwise, why bother?
		if self._projectConfFile :
			# When are we doing this?
			date_time, secs = str(datetime.now()).split(".")

			# Build the event line
			if code == 'ERR' :
				eventLine = '\"' + date_time + '\", \"' + code + '\", \"' + mod + msg + '\"'
			else :
				eventLine = '\"' + date_time + '\", \"' + code + '\", \"' + msg + '\"'

			# Do we need a log file made?
			if not os.path.isfile(self._projLogFile) or os.path.getsize(self._projLogFile) == 0 :
				writeObject = codecs.open(self._projLogFile, "w", encoding='utf_8')
				writeObject.write('TIPE event log file created: ' + date_time + '\n')
				writeObject.close()

			# Now log the event to the top of the log file using preAppend().
			self.preAppend(eventLine, self._projLogFile)

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
		if not os.path.isfile(self._projErrorLogFile) :
			writeObject = codecs.open(self._projErrorLogFile, "w", encoding='utf_8')
		else :
			writeObject = codecs.open(self._projErrorLogFile, "a", encoding='utf_8')

		# Write and close
		writeObject.write(eventLine + '\n')
		writeObject.close()

		return


	def trimLog (self, projLogLineLimit = 1000) :
		'''Trim the system log file.  This will take an existing log file and
		trim it to the amount specified in the system file.'''

		# Of course this isn't needed if there isn't even a log file
		if os.path.isfile(self._projLogFile) :

			# Change this to an int()
			projLogLineLimit = int(projLogLineLimit)

			# Read in the existing log file
			readObject = codecs.open(self._projLogFile, "r", encoding='utf_8')
			lines = readObject.readlines()
			readObject.close()

			# Process only if we have enough lines
			if len(lines) > projLogLineLimit :

				writeObject = codecs.open(self._projLogFile, "w", encoding='utf_8')
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




