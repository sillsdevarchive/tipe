#!/usr/bin/python2
# -*- coding: utf_8 -*-
# version: 20110608
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This module will handle basic system functions that are
# common to many scripts.

# History:
# 20110608 - djd - Initial refactor from ptxplus to tipe


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the modules we need for this process

import re, os, shutil, codecs, csv, sys, unicodedata
from configobj import ConfigObj
from datetime import *
from functools import partial
from itertools import imap


def taskRunner (log_manager, component_manager, thisTask) :
	'''This is the final function used for running all system tasks.
		All calls from the system to run a task or process should
		end up here.'''

	# Tell the log what we're doing.
	log_manager.log("DBUG", "INFO: Starting process: " + thisTask)

	if log_manager._settings['System']['ErrorHandling'].get('debugMode', 'true').lower() == 'true' :
		# Import the module
		module = __import__(thisTask, globals(), locals(), [])
		log_manager.log("DBUG", "Imported module: " + thisTask)
		# Run the module
		module.doIt(log_manager, component_manager)
		log_manager.log("DBUG", "Completed: " + thisTask)

	else :
		# If we are in debug mode then do it like this to suppress debugging code

		# Import/load the module
		try :
			module = __import__(thisTask, globals(), locals(), [])
			log_manager.log("DBUG", "Imported module: " + thisTask)
		except :
			userMessage("ERRR: Hmmm, cannot seem to import the \"" + thisTask + "\" module. This will not bode well for the rest of the process.")
			log_manager.log("ERRR", "Could not import module: " + thisTask)

		# Run the module
		try :
			module.doIt(log_manager)
			log_manager.log("DBUG", "Process completed: " + thisTask)
		except :
			userMessage("ERRR: Cannot run the \"" + thisTask + "\" module.")
			log_manager.log("ERRR", "Cannot run the \"" + thisTask + "\" module.")


def getModuleArguments () :
	'''Return a list of arguments for the current module.
		This function will querry the sys.argv[1] parameter
		to figure out what they are. This allows flexibility
		to add new modules without having to define parms in
		the .conf file. They can just be passed with the
		module name.'''

	# Strip out the module name from the standard sys.argv[1]
	# It has to be the first part of the param.
	cmd = sys.argv[1]
	modName = cmd.split()[0]

	# Now strip the module name out and gather up the args
	modArgs = cmd.replace(modName, '').split()

	return modArgs


def getSystemName () :
	'''Return the current system ID.'''

	return getSystemSettingsObject()['System']['systemName']


def getSystemVersion () :
	'''Return the current system ID.'''

	return getSystemSettingsObject()['System']['systemVersion']


def getSystemUser () :
	'''Return the current system user name.'''

	try :
		return getSystemSettingsOverrideObject()['System']['userName']

	except :
		return getSystemSettingsObject()['System']['userName']


def getSystemSourceHomePath () :
	'''Return the current system source path.'''

	try :
		return getSystemSettingsOverrideObject()['Process']['Paths']['PATH_SOURCE_HOME']

	except :
		return getSystemSettingsObject()['Process']['Paths']['PATH_SOURCE_HOME']


def getSettingsObject () :
	'''Return a single settings object for use in normal processes.
		This will pull in the project system and global override
		configuration files and turn them into a combined object
		which will be used on project processes.'''

	projectDefault = getProjectDefaultSettingsObject()
	project = getProjectSettingsObject()
	sysObj = getSystemSettingsObject()

	try :
		override = getSystemSettingsOverrideObject()
	except :
		override = ""

	# Now we will merge all the object together to make one master
	# object that will be used for all operations.

	# It is logical, when merging the objects, to think that if
	# there are duplicate keys, the last one in will win. However
	# for whatever reason ConfigObj takes a different approch.
	# In the ConfigObj module it is the first in that wins. In
	# our system we want the object that have the overrides in
	# in it to go in first. That is why the order is the way it
	# is here.

	if project != None :
		try :
			override.merge(sysObj)
			project.merge(override)
		except :
			project.merge(sysObj)

		return project
	else :
		# If no project settings file exists just use the
		# system and override objects
		try :
			override.merge(sysObj)
			projectDefault.merge(override)
		except :
			projectDefault.merge(sysObj)

		return projectDefault


def getSystemSettingsObject () :
	'''Return an object from the ptx-plus.conf which
		contains the system settings.'''

	# There should always be a conf file here
	return ConfigObj(os.environ.get('TIPE_BASE') + "/bin/tipe.conf", encoding='utf_8')


def getProjectType (path=os.getcwd()) :
	'''Return the type of publication project this is.
		We will do this by checkging to see what kind of
		.conf object we have in the root of the project
		which we assume to be the cwd unless something
		else is specified.'''

	for t in getSystemSettingsObject()['System']['pubTypeList'] :
		if os.access(path + '/.' + t + '.conf', os.R_OK) :
			return t


def getProjectSettingsObject () :
	'''Return an object which contains the project settings.'''

	if os.path.isfile(os.getcwd() + "/" + getProjectConfigFileName()) != None :
		# Load in the settings from our project
		return ConfigObj(os.getcwd() + "/" + getProjectConfigFileName(), encoding='utf_8')


def getProjectDefaultSettingsObject () :
	'''Return a default project object from the system.'''

	# FIXME: This may cause an error because the .conf file
	# may not be found.

	defaultFile = os.environ.get('TIPE_BASE') + "/resources/lib_sysFiles/" + getProjectConfigFileName()

	if os.path.isfile(defaultFile) :
		# Load in the settings from our default .conf file
		return ConfigObj(defaultFile, encoding='utf_8')


def getSystemSettingsOverrideObject () :
	'''If it exists, return an object which contains the system override
		settings found in ~/.config/xetex-tipe.'''

	home = os.environ.get('HOME')
	overrideFile = home + "/.config/tipe/override.conf"

	if os.path.isfile(overrideFile) == True :
		return ConfigObj(overrideFile, encoding='utf_8')


def getComponentSourceFileName (compID) :
	'''Return the file name of a source file as determined by by the Scripture
	editor.  If the ID is not recognized it will return nothing'''

	settingsProject = getProjectSettingsObject()
	settingsSystem = getSystemSettingsObject()
	suffix = settingsProject['ProjectText']['SourceText'].get('NAME_SOURCE_ORIGINAL')
	extention = settingsProject['ProjectText']['SourceText'].get('EXT_SOURCE')
	value = getComponentTargetName(compID)
	key = getComponentKeyName(compID)

	# The suffix is only a Paratext naming convention. It is not
	# needed for peripheral files and will not be present for other
	# kinds of files. We will just strip it out for peripheral files
	# FIXME: This is dependent on there being a 'content' component
	# type but if this is another kind of publication type, that may
	# not be the case. This needs to be more generic.
	if key.find('_content') > -1 :
		return value + suffix + "." + extention
	else :
		return value + "." + extention


def getComponentKeyName (compID) :
	'''Return the key for a given component ID.  If the component ID has a
	number suffix it will pass that through.'''

	instance = ''
	rawID = compID

	# Check to see if this is a component that has mulitple instances
	# and adjust ID if it does.  The first three letters are what we
	# need for look-up info.
	if len(compID) == 4 :
		instance = compID[-1]
		rawID = compID[0:3]

	# Check all types of components.  The template list has all the components
	# in it so we draw from that list.
	for key, value in pubInfoObject['Components']['Template'].iteritems() :
		for compType in pubInfoObject['Components']['componentTypeList'] :
			if rawID + '_' + compType == key :
				return rawID + instance + '_' + compType


def getComponentTargetName (compID) :
	'''Return the value for a given component ID key.  The value equates to the
	template name that is used for this component.  If there is more than one
	instance of this type of component it will add that to the value (template)
	name.'''

	instance = ''
	rawID = compID

	# Check to see if this is a component that has mulitple instances and adjust
	# ID if it does.  The first three letters are what we need for look-up info.
	if len(compID) == 4 :
		instance = compID[-1]
		rawID = compID[0:3]

	# Check all types of components.  The template list has all the components
	# in it so we draw from that list.
	for key, value in pubInfoObject['Components']['Template'].iteritems() :
		for compType in pubInfoObject['Components']['componentTypeList'] :
			# When dealing with content objects the source file name can be
			# different depending on the editor used to create it.  This will
			# sort that out as long as it is a known editor.
			if compType == 'content' :
				editor = getProjectSettingsObject()['ProjectText']['SourceText']['Features'].get('projectEditor')
				for k, v in pubInfoObject['Components']['NameMap_' + editor.upper()].iteritems() :
					if k == rawID + '_' + compType :
						return v + instance

			else :
				if rawID + '_' + compType == key :
					return value + instance


def getProjectConfigFileName () :
	'''Return the configuration file name for this project.'''

	return '.' + getProjectType() + '.conf'


def makeUserOverrideFile () :
	'''Create a user override file but only if it doesn't already exist.'''

	home = os.environ.get('HOME')
	overrideFile = home + "/.config/tipe/override.conf"
	if not os.path.isfile(overrideFile) :
		if not os.path.isdir(home + '/.config/tipe') :
			os.mkdir(home + '/.config/tipe')

		# Make a new empty file if none exists
		object = codecs.open(overrideFile, "w", encoding='utf_8')
		object.close()


def setSystemUser (userName) :
	'''Set the users name in the user config override file.'''

	home = os.environ.get('HOME')
	overrideFile = home + "/.config/tipe/override.conf"

	try :
		override = getSystemSettingsOverrideObject()
		override['System']['userName'] = userName
		override.write()
	except :
		# If we can't get the object then it probably isn't there, we'll
		# go a head and make one, then write in the information we want.
		if not os.path.isfile(overrideFile) :
			makeUserOverrideFile()
			object = codecs.open(overrideFile, "a", encoding='utf_8')
			object.write('# System settings\n')
			object.write('[System]' + '\n\n')
			object.write('# The name of the person using this system.\n')
			object.write('userName = \'' + userName + '\'\n\n')
			object.close()

	# Report what happened
	userMessage('INFO: System user name set to: ' + getSystemUser())


def setSystemSourceHome (sourceHomePath) :
	'''Set the path to project source files that the system will copy into
		its text folder. This information is stored in the config override file'''

	home = os.environ.get('HOME')
	overrideFile = home + "/.config/tipe/override.conf"

	try :
		override = getSystemSettingsOverrideObject()
		override['Process']['Paths']['PATH_SOURCE_HOME'] = sourceHomePath
		override.write()
	except :
		# If we can't get the object then it probably isn't there, we'll
		# go a head and make one, set the user name to default then write
		# in the source path information we want.
		if not os.path.isfile(overrideFile) :
			makeUserOverrideFile()
			object = codecs.open(overrideFile, "a", encoding='utf_8')
			object.write('# System settings\n')
			object.write('[System]' + '\n\n')
			object.write('# The name of the person using this system.\n')
			object.write('userName = \'Default User\'\n\n')
			object.write('# Process information\n')
			object.write('[Process]' + '\n\n')
			object.write('# System Paths\n')
			object.write('[[Paths]]' + '\n')
			object.write('PATH_SOURCE_HOME = \'' + sourceHomePath + '\'\n\n')
			object.close()
			userMessage('INFO: System user name set to: Default User, you may want to change it to the right name with the command: tipe set-user\n')
		else :
			object = codecs.open(overrideFile, "a", encoding='utf_8')
			object.write('\n# Process information\n')
			object.write('[Process]' + '\n\n')
			object.write('# System Paths\n')
			object.write('[[Paths]]' + '\n')
			object.write('PATH_SOURCE_HOME = \'' + sourceHomePath + '\'\n\n')
			object.close()

	# Report what happened
	userMessage('INFO: System source path set to: ' + getSystemSourceHomePath())


def getScriptureFileID (pathPlusFileName, settings_project) :
	'''Return the file ID name from a standard PTX-like file
		name. This assmes a full path in front of the
		file name.'''

	path, file = pathPlusFileName.rsplit("/", 1)
	nameSourceOriginal = settings_project['ProjectText']['SourceText']['NAME_SOURCE_ORIGINAL']
	nameSourceExtention = settings_project['ProjectText']['SourceText']['EXT_SOURCE']
	file = file.replace(nameSourceOriginal + "." + nameSourceExtention, "")
	return file


def getProjectID () :
	'''Get the project ID from the .conf file.'''

	return getProjectSettingsObject()['Project']['ProjectInformation']['projectID']


def inProject () :
	'''Simple test to see if a .conf file exists.'''

	if os.path.isfile(getProjectConfigFileName()) == True :
		return True
	else :
		return False


def isBackedUp () :
	'''Confirm if a backup file exists for a given project.
		This will look in the specified backup dir for
		the backup file related to projectID.'''

	settings = getSettingsObject()
	# For the location we use whatever the makefile.conf file has
	# whether it is abs or relative. Note, we use abs in archive_project.py
	backupFilePath = settings['System']['Backup']['backupPath']
	backupFile = backupFilePath + "/Backup.tar.gz"

	if os.path.isfile(backupFile) == True :
		return True
	else :
		return False


def makeDateStamp () :
	# Make a simple date stamp
	n = str(datetime.now())
	nObject = n.split(".")
	rightNow = str(nObject[0])
	rightNow = rightNow.replace("-", "")
	rightNow = rightNow.replace(" ", "")
	rightNow = rightNow.replace(":", "")
	return rightNow + nObject[1]


def getYMD () :
	'''Return a simple YearMonthDay string.'''

	date = str(datetime.today()).split(' ')
	return date[0].replace('-', '')


def makeUnicodeNumberRange (zero) :
	'''Given a standard Unicode codepoint (assumed to be for
		the number "0") in a string this will return the
		range of 0-9. This is useful for regex searches
		in non-Roman texts.'''

	# This will return the actuall human readable numbers in
	# the given language rather than the Unicode hex codes
	return '%s-%s' % (unichr(int(zero, 16)), unichr(int(zero, 16) + 9))


def makeUID () :
	'''Make a simple UID based on time stamp for log entries.
		most processes happen in less than a second, therefore
		we will only use seconds and milliseconds to construct
		the UID.'''

	now = str(datetime.now())
	time = now.split(' ')[1]
	hms, ms = time.split('.')
	s = hms.split(':')[2]
	return s + ms


def isProjectFolder () :
	'''Check to see if the project folder and the .conf file
		exists in the current directory.'''

	path = os.getcwd()
	ok = False
	if os.path.isfile(path + "/" + getProjectConfigFileName()) :
		ok = True

	return ok


def userConfirm (msg) :
	'''Ask the user to confirm something.'''

	confirm = False
	answer = raw_input("\nConfirm Action:\n\n" + wordWrap(msg, 60) + " (y/n): ")
	if answer.lower() == "y" :

		confirm = True

	elif answer.lower() == "n" :
		userMessage("INFO: No is okay too. We can do this another time.")
	else :
		userMessage("INFO: I am not sure what you mean by \"" + answer + "\" I am only " \
			"programed for \"y\" or \"n\" I am confused by anything else.")

	return confirm


def userInput (msg) :
	'''Ask the user a question that requires other than y/n input.'''

	return raw_input("\n" + wordWrap(msg, 60))


def userMessage (event) :
	'''Output a simple message to the user in the terminal.'''

	# We can make this prettier later.
	print wordWrap(event, 60)


def userMessageDialog (event, dialogType) :
	'''Output a windowed message to get the user's attention.'''

	if dialogType == 'ERRR' :
		dialogType = "--error --title='Process Error'"

	dialog_command = "zenity " + dialogType + " --window-icon=" + basePath + "/resources/icons/tipe.png --width=400 --text='" + event + "'"
	os.system(dialog_command)


def makefileCommand (command) :
	'''Send off a makefile command.'''


	if getSettingsObject()['System']['General'].get('debugMode', 'false').lower() == 'true' :
		params = getSettingsObject()['System']['MakefileSettings']['makeFileParams']

		# Build the command
		sysCommand = "make " + params + " " + command

		# Send off the command return error code
		return os.system(sysCommand)

	else :

		# Get any special makefile params for debugging
		try :
			params = getSettingsObject()['System']['MakefileSettings']['makeFileParams']

			# Build the command
			sysCommand = "make " + params + " " + command

			# Send off the command return error code
			return os.system(sysCommand)

		except :
			userMessage('ERRR: Could not run makefile command. The ' + getProjectConfigFileName() + ' file may be corrupt.')


def doCustomProcess (processCommand) :
	'''Run a custom command line process on a file. The process string is
		the complete command line with valid paths for all files used.
		Return True if successful.'''

	# Send off the command to the system
	error = os.system(processCommand)

	# Report if the copy actually took place.
	if not error :
		return True
	else :
		return False


def copyFiles (srcDir, dstDir) :
	'''Copy all the files in a dir to another. It assumes the
		destination dir exists and it will not copy
		recursively.'''

	names = os.listdir(srcDir)
	for name in names:
		srcname = os.path.join(srcDir, name)
		dstname = os.path.join(dstDir, name)
		if not os.path.isdir(srcname) :
			shutil.copy(srcname, dstname)


def chmodFiles (srcDir, mode) :
	'''Change the permission on all the files in a dir to something else.
		It assumes the destination dir exists and it will not work
		recursively. For mode it depends on stat() to give it the
		permission code. The calling function delivers this.'''

	names = os.listdir(srcDir)
	for name in names:
		srcname = os.path.join(srcDir, name)
		if os.path.isfile(srcname) :
			os.chmod(srcname, mode)


def unlinkFiles (srcDir) :
	'''Remove all the files in a dir. It assumes the destination dir
		exists and it will not work recursively.'''

	names = os.listdir(srcDir)
	for name in names:
		srcname = os.path.join(srcDir, name)
		if os.path.isfile(srcname) :
			os.unlink(srcname)


def copyAll (src, dst) :
	'''Just like copyFiles but will do folders too it will copy
		them into the destination folder which must exist.'''

	names = os.listdir(src)
	for name in names:
		srcname = os.path.join(src, name)
		dstname = os.path.join(dst, name)
		if not os.path.isdir(srcname) :
			shutil.copy(srcname, dstname)
		else :
			shutil.copytree(srcname, dstname)


def removeFolder (targetDir) :
	'''Hopefully this is a safe way to recursively remove a folder
		and everything in it.'''


	for root, dirs, files in os.walk(targetDir, topdown=False) :
		for name in files :
			os.remove(os.path.join(root, name))
		for name in dirs :
			os.rmdir(os.path.join(root, name))

	os.rmdir(targetDir)


def cleanUpProject (targetDir) :
	'''Clean out all the unecessary project files. Not sure
		if this is in use anywhere. It was made for project
		archiving but the cleanup is now done by excluding
		files we don't want in the archive. This, and the
		functions below may be removed at some point.'''

	cleanOutLogFiles(targetDir)
	cleanOutBakFiles(targetDir)
	cleanOutTexFiles(targetDir)
	cleanOutSvnDirs(targetDir)


def cleanOutLogFiles (targetDir) :
	'''Clean out all the .log files in a project.'''

	for root, dirs, files in os.walk(targetDir) :
		for name in files :
			if name.find('.log') > -1 :
				os.remove(os.path.join(root, name))


def cleanOutBakFiles (targetDir) :
	'''Clean out all the .bak and '~' files in a project.'''

	for root, dirs, files in os.walk(targetDir) :
		for name in files :
			if name[-1:] == "~" :
				os.remove(os.path.join(root, name))


def cleanOutTexFiles (targetDir) :
	'''Clean out all the standard TeX files in a project.'''

	#fileList = []
	fileList = '.pdf', '.tex', '.delayed', '.parlocs'
	for root, dirs, files in os.walk(targetDir) :
		for name in files :
			for ext in fileList :
				if name.find(ext) > -1 :
					os.remove(os.path.join(root, name))


def cleanOutSvnDirs (targetDir) :
	'''Clean out any stray .svn folders - just in case. This should be used
		with caution. If you blow away the .svn folders in a live project
		you will have to do alot of back-tracking'''

	for root, dirs, files in os.walk(targetDir) :
		for folder in dirs :
			if folder == ".svn" :
				removeFolder(os.path.join(root, folder))


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


def walk(top, topdown=True, onerror=None) :
	'''Directory tree generator. This was blatantly ripped off
		from os.py. However, the islink function was removed
		to enable walking a tree with links.'''

	from os.path import join, isdir

	try:
		# Note that listdir and error are globals in this module due
		# to earlier import-*.
		names = os.listdir(top)
	except os.error, os.err:
		if onerror is not None:
			onerror(err)
		return

	dirs, nondirs = [], []
	for name in names:
		if isdir(join(top, name)):
			dirs.append(name)
		else:
			nondirs.append(name)

	if topdown:
		yield top, dirs, nondirs
	for name in dirs:
		path = join(top, name)
		for x in walk(path, topdown, onerror):
			yield x
	if not topdown:
		yield top, dirs, nondirs


def prependText (text, file) :
	'''Prepend a text string to a file. Return True if successful.
		Log an error and return False if not.'''

	newLines = ""
	# Slurp in all the data in the file
	if os.path.isfile(file) == True :
		orgObject = codecs.open(file, "r", encoding='utf_8')
		for line in orgObject :
			newLines = newLines + line

		orgObject.close()
		newObject = codecs.open(file, "w", encoding='utf_8')
		# Write out the object and stick the additional text to
		# the front of the existing text.
		newObject.write(text + newLines)

		return True
	else:
		return False


def dedupList (seq) :
	'''Remove the duplicate items from a list but keep the
		sort order. Using set() insures the first item in will
		be kept. It will return a list.'''

	seen = set()
	return [seen.add(element) or element for element in seq if element not in seen]


def getSliceOfText (text, start, amount) :
	'''For reporting purposes we may want to grab a slice of text to
		send to put in a log event. This will attempt to return a
		a slice of text that equals the amont (number of characters)
		given divided by 2. If it can't do that it will try to get
		as much as it can. The goal is to give the user a resonable
		piece of text so they know what the context is.'''

	text = text.strip()
	if amount > len(text) :
		amount = len(text)

	left = start - (amount / 2)
	right = start + (amount / 2)

	if right > len(text) :
		right = len(text)
		left = right - amount

	if left < 0 :
		left = 0
		right = left + amount
		if right > len(text) :
			right = len(text)

	if text[left:right] == "" :
		return "NO CONTEXT"
	else :
		return text[left:right]


def normalize (iterable, form='NFD') :
	'''This will return an iterable object that will normalize a
		file to the default of NFD. But you override by changing
		'form' to NFC by the calling function.'''

	return imap(partial(unicodedata.normalize,form),iterable)


class CSVtoDict (dict):
	'''This class provides a service which will convert a proper CSV file
		that uses the excel dialect and has a header row, into a
		dictionary object. The default record is ID but it can be
		changed to whatever is needed by passing a different value
		for recordkey.'''

	def __init__ (self, csv_file_path, recordkey='ID') :
		csvs = csv.DictReader(open(csv_file_path), dialect=csv.excel)
		records = list((row.pop(recordkey),row) for row in csvs)
		return super(CSVtoDict, self).__init__(records)


#####################################################################################
#               Declare Gobal Vars and Objects here
#####################################################################################

# Get the tipe basePath, declair as global
basePath = os.environ.get('TIPE_BASE')

# This is the information object that contains all the settings for this type of pub
if getProjectType() != None :
	pubInfoObject = ConfigObj(basePath + "/bin/" + getProjectType() + '.inf', encoding='utf_8')
