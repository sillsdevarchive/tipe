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
from report import Report
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


def loadProjectSettings (tipeUserConf, projHome, userHome, tipeHome) :
	'''Load up the project.conf settings.  This will first look in the current
	folder for the .project.conf file.  One exsits then we will first load the
	system defaults, then override with the user settings (if any) then finally
	override with the project settings.  When all that is done we'll look to see
	if the project exists in the user's config file.  If not, we'll add it in
	the projects section.'''

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

	# Check the user's config for this project, silently add if needed
	pname = res['ProjectInfo']['projectName']
	ptype = res['ProjectInfo']['projectType']
	pid = res['ProjectInfo']['projectIDCode']
	date = res['ProjectInfo']['projCreateDate']
	if not isRecordedProject(tipeUserConf, pid) == True :
		recordProject(tipeUserConf, projHome, pname, ptype, pid, date)

	# Return the final results of the conf settings
	return res


def recordProject (tipeUserConf, projHome, pname, ptype, pid, date) :
	'''Add information about this project to the user's tipe.conf located in
	the home config folder.'''

	mod = 'project.recordProject()'
	if os.path.isfile(tipeUserConf) :
		cf = ConfigObj(tipeUserConf)

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


def isRecordedProject (tipeUserConf, pid) :
	'''Check to see if this project is recorded in the user's config'''

	if os.path.isfile(tipeUserConf) :
		cf = ConfigObj(tipeUserConf)
		try :
			isConfPID = cf['Projects'][pid]
			return True
		except :
			return False


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
		self.tipeUserConf       = os.path.join(self.userHome, 'tipe.conf')
		self.tipeProjConf       = os.path.join(self.projHome, '.tipe.conf')
		self.projectConfFile    = os.path.join(self.projHome, '.project.conf')
		self.lockExt            = '.locked'

		# Load the TIPE config settings and do a safe start
		self._sysConfig         = safeStart(projHome, userHome, tipeHome)

		# Set all the system settings
		if self._sysConfig :
			self.version            = self._sysConfig['System']['systemVersion']
			self.userName           = self._sysConfig['System']['userName']
			self.tipeEditDate       = self._sysConfig['System']['tipeEditDate']
			self.orgTipeEditDate    = self.tipeEditDate
			# File paths
			self.projErrorLogFile   = os.path.join(self.projHome, self._sysConfig['FileNames']['projErrorLogFile'])
			self.projLogLineLimit   = self._sysConfig['System']['projLogLineLimit']

		# Look for a project in the current location and load the settings
		if os.path.isfile(self.projectConfFile) :
			self._projConfig = loadProjectSettings(self.tipeUserConf, self.projHome, self.userHome, self.tipeHome)
			if self._projConfig :
				self.projectType        = self._projConfig['ProjectInfo']['projectType']
				self.projectName        = self._projConfig['ProjectInfo']['projectName']
				self.projectEditDate    = self._projConfig['ProjectInfo']['projectEditDate']
				self.orgProjectEditDate = self.projectEditDate
				self.projectCreateDate  = self._projConfig['ProjectInfo']['projCreateDate']
				self.projectIDCode      = self._projConfig['ProjectInfo']['projectIDCode']
		else :
			# Set this in case there is no project present
			self.projectName            = 'None'
			self.projectIDCode          = ''

		# Initialize any needed services
		self.initLogging(self.projHome)

###############################################################################
############################# Begin Main Functions ############################
###############################################################################

	def initLogging (self, pHome) :
		'''Initialize logging functions'''

		self.report = Report(
			projLogFile         = os.path.join(pHome, self._sysConfig['FileNames']['projLogFile']) if self._sysConfig else None,
			projErrFile         = os.path.join(pHome, self._sysConfig['FileNames']['projErrorLogFile']) if self._sysConfig else None,
			debug               = self._sysConfig and self._sysConfig['System']['debugging'],
			projectName         = self.projectName)


	def writeProjConfFiles (self) :
		'''Write out all relevent project conf files if there is at least
		project in memory.'''

		# We'll test for a project by looking for a name
		if self.projectName != 'None' :
			# Write out config files only if the edit date has changed
			if self.orgTipeEditDate != self.tipeEditDate :
				self._sysConfig.filename = self.tipeProjConf
				self._sysConfig.write()

			if self.orgProjectEditDate != self.projectEditDate :
				self._projConfig.filename = self.projectConfFile
				self._projConfig.write()


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
				self.report.writeToLog('LOG', 'Created folder: ' + value, mod)

		self.writeProjConfFiles()


	def makeProject (self, pType='', pName='', pID='', pDir='') :
		'''Create a new publishing project.  If parms are blank defaults will be
		substituted'''

		mod = 'project.makeProject()'
		date_time, secs = str(datetime.now()).split(".")

		# It is required that there be at least a project type defined we will
		# look for that here and fail if we don't find it
		if pType == '' :
			pType = 'bookTex'
			self.report.writeToLog('WRN', 'Type parameter missing, using default of bookTex', mod)

		if pName == '' :
			pName = 'Missing Name'
			self.report.writeToLog('WRN', 'Name parameter missing, setting to None', mod)

		if pID == '' :
			# create a simple short guid
			import time
			pID = hex(int(time.time()))
			self.report.writeToLog('WRN', 'ID parameter missing, setting to [' + pID + ']', mod)

		# This can create a project in directory other than the current one.
		if pDir == '' :
			pDir = os.path.join(self.projHome, pID)
			self.tipeProjConf = os.path.join(pDir, '.tipe.conf')
			self.report.writeToLog('WRN', 'Directory parameter missing, set to: ' + pDir , mod)


		# See if a project is already in the target dir by looking for a
		# .project.conf file
		pConf = os.path.join(pDir, '.project.conf')
		if os.path.isfile(pConf) or os.path.isfile(pConf + self.lockExt)  :
			self.report.writeToLog('ERR', 'Hault! A project is already defined in this folder.', mod)
			return

		# See if a project is in the parent dir by looking for a .project.conf file
		(head, tail) = os.path.split(pDir)
		if os.path.isfile(os.path.join(head, '.project.conf')) :
			self.report.writeToLog('ERR', 'Hault! A project is already defined in the parent folder', mod)
			return

		# Test if this project already exists in the user's config file.
		if isRecordedProject(self.tipeUserConf, pID) :
			self.report.writeToLog('ERR', 'Hault! ID [' + pID + '] already defined for another project', mod)
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
			self.report.writeToLog('ERR', 'Project type does not exist: ' + pType, mod)
			return

		# Initialize new project now
		if not os.path.isdir(pDir) :
			os.mkdir(pDir)

		self._projConfig = makeProjectSettings(pDir, self.userHome, self.tipeHome, pType)
		if self._projConfig :
			self.projectType = pType
			self.projectConfFile = os.path.join(pDir, '.project.conf')
			self._projConfig['ProjectInfo']['projectName'] = pName
			self.projectName = pName
			self._projConfig['ProjectInfo']['projectIDCode'] = pID
			self.projectIDCode = pID
			self._projConfig['ProjectInfo']['projCreateDate'] = date_time
			self.projectCreateDate = date_time
			self._projConfig['ProjectInfo']['projectEditDate'] = date_time
			self.projectEditDate = date_time
			self.orgProjectEditDate = ''
			self.tipeEditDate = date_time
			self.orgTipeEditDate = ''
			self.initLogging(pDir)
			self.initProject(pDir)
			# Record the project with the system
			recordProject(self.tipeUserConf, pDir, pName, pType, pID, date_time)
			return True
		else :
			self.report.writeToLog('ERR', 'Failed to initialize project.', mod)
			return


	def removeProject (self, settings="") :
		'''Remove the project from the TIPE system.  This will not remove the
		project data but will 'disable' the project.  This command takes the
		following parameters:
			-pid "text"     The project ID code (required)'''

		mod = 'project.removeProject()'

		# Collect our parameters
		c = 0; pid = ''
		commands = ['-pid']
		for s in settings :
			if s in commands :
				if s == '-pid' :
					pid = settings[c+1]
			else :
				if s[0] == '-' :
					self.report.writeToLog('ERR', 'Command (' + s + ') not found, process failed!', mod)
					return

		# 1) Check the user's conf file to see if the project actually exists
		if not isRecordedProject(self.tipeUserConf, pid) :
			self.report.writeToLog('ERR', 'Project ID [' + pid + '] not found in system configuration.', mod)
			return
		else :
			# 2) If the project does exist in the user config, disable the project
			cf = ConfigObj(self.tipeUserConf)
			projPath = cf['Projects'][pid]['projectPath']
			projTipeConf = os.path.join(projPath, '.tipe.conf')
			projProjConf = os.path.join(projPath, '.project.conf')
			if os.path.isfile(projTipeConf) :
				os.rename(projTipeConf, projTipeConf + self.lockExt)
			if os.path.isfile(projProjConf) :
				os.rename(projProjConf, projProjConf + self.lockExt)

			# 3) Remove references from user tipe.conf
			del cf['Projects'][pid]
			cf.write()

			# 4) Report the process is done
			self.report.writeToLog('MSG', 'Project [' + pid + '] removed from system configuration.', mod)
			return


	def restoreProject (self) :
		'''Restore a project in the current folder'''


		if os.path.isfile(self.projTipeConf) :
			os.rename(projTipeConf + self.lockExt, projTipeConf)

		if os.path.isfile(self.projProjConf) :
			os.rename(projProjConf + self.lockExt, projProjConf)


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
		if os.path.isfile(self.tipeUserConf) :
			cf = ConfigObj(self.tipeUserConf)

		# Change the setting here
		cf['System'][key] = value
		self._sysConfig['System'][key] = value
		self.report.writeToLog('MSG', 'Changed ' + key + ' to: ' + value, mod)
		date_time, secs = str(datetime.now()).split(".")
		self._sysConfig['System']['tipeEditDate'] = date_time
		self.tipeEditDate = date_time
		cf['System']['userEditDate'] = date_time
		cf.write()


	# These are Report mod functions that are exposed to the project class
	def terminal(self, msg) : self.report.terminal(msg)
	def terminalCentered(self, msg) : self.report.terminalCentered(msg)
	def writeToLog(self, code, msg, mod) : self.report.writeToLog(code, msg, mod)
	def trimLog(self, projLogLineLimit) : self.report.trimLog(projLogLineLimit)



