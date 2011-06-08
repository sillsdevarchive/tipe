#!/usr/bin/python2
# -*- coding: utf_8 -*-
# version: 20080423
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This script will auto-generate the system makefile based on settings found in
# the .conf file.  It is supposed to be generic and build for the type of
# publishing project it is.  It does this every time the typeset file is used
# with valid commands.

# History:
# 20100823 - djd - Initial draft (Started with make_scripture.py)


###############################################################################
################################## Load Modules ###############################
###############################################################################
# Firstly, import all the modules we need for this process

import sys, os, codecs, operator, csv

# Import supporting local classes
import tools


class MakeMakefile (object) :


# FIXME: There are no doubt much leftover code from the make_scripture.py that
# will make this module less then generic.  As we find code like this it needs
# to be replaced so this module will work with any recognized type in the
# system.

	def main (self, log_manager) :
		'''This is the main process function for generating the makefile.'''

		self._log_manager = log_manager
		basePath = os.environ.get('TIPE_BASE')
		sourcePath = os.path.abspath(self._log_manager._settings['System']['Paths'].get('PATH_SOURCE', '../Source'))

		# Get the type of project this is
		self._projectType = tools.getProjectType()

		# The folder name for peripheral material is auto created here
		peripheralFolderName = os.getcwd().split('/')[-1]

		# Create the new makefile object (overwrite the old file)
		# Note here about encoding. If you use utf_8_sig rather than
		# just utf_8 it will put a BOM in the file. This seems to make
		# Make choke. Keeping with just utf_8 seems to fix it.
		makefileObject = codecs.open('.makefile', 'w', encoding='utf_8')

		# Create the file elements
		makefileHeader = "# Makefile\n\n# This is an auto-generated file, do not edit. Any necessary changes\n" + \
				"# should be made to the .scripture.conf file.\n\n"

		# Pull in settings stored in the Process section of the .scripture.conf object
		# As there are sub-sections we will add them to the settings object one
		# at after another. There's probably a better way to do this but not today ;-)
		makefileSettings = ""

		# Output the helper commands
		for key, value, in self._log_manager._settings['System']['HelperCommands'].iteritems() :
			makefileSettings += key + "=" + value + '\n'

		# Get our switches from their respective sections
		useIllustrations = self._log_manager._settings['Format']['Illustrations']['USE_ILLUSTRATIONS']
		makefileSettings += 'USE_ILLUSTRATIONS=' + useIllustrations + '\n'

		usePlaceholders = self._log_manager._settings['Format']['Illustrations']['USE_PLACEHOLDERS']
		makefileSettings += 'USE_PLACEHOLDERS=' + usePlaceholders + '\n'

		useWatermark = self._log_manager._settings['Format']['PageLayout']['USE_WATERMARK']
		makefileSettings += 'USE_WATERMARK=' + useWatermark + '\n'

		useCropmarks = self._log_manager._settings['Format']['PageLayout']['USE_CROPMARKS']
		makefileSettings += 'USE_CROPMARKS=' + useCropmarks + '\n'

		usePageborder = self._log_manager._settings['Format']['PageLayout']['USE_PAGE_BORDER']
		makefileSettings += 'USE_PAGE_BORDER=' + usePageborder + '\n'

		useAdjustments = self._log_manager._settings['ProjectText']['WorkingText']['Features']['USE_ADJUSTMENTS']
		makefileSettings += 'USE_ADJUSTMENTS=' + useAdjustments + '\n'

		useHyphenation = self._log_manager._settings['Format']['Hyphenation']['useHyphenation']
		makefileSettings += 'USE_HYPHENATION=' + useHyphenation + '\n'

		# Pickup some other misc settings needed by makefile
		sourceLock = self._log_manager._settings['ProjectText']['SourceText']['LOCKED']
		makefileSettings += 'LOCKED=' + sourceLock + '\n'

		sourceName = self._log_manager._settings['ProjectText']['SourceText']['NAME_SOURCE_ORIGINAL']
		makefileSettings += 'NAME_SOURCE_ORIGINAL=' + sourceName + '\n'

		graphicsList = self._log_manager._settings['Format']['Illustrations']['LIST_GRAPHICS']
		c = 0
		makefileSettings += 'LIST_GRAPHICS='
		for fileName in graphicsList :
			if c == 0 :
				makefileSettings += fileName
				c+=1
			else :
				makefileSettings += ' ' + fileName

		makefileSettings += '\n'

		# Modules used by the makefile, note the use of extra
		# quoting. This is to preserve the strings.
		for key, value, in tools.pubInfoObject['Modules'].iteritems() :
			makefileSettings += key + "=" + value + '\n'

		# Pull in the one extention and module that is not in the proj conf
		makefileSettings += 'MOD_PARA_ADJUST=' + self._log_manager._settings['System']['Processes']['MOD_PARA_ADJUST'] + '\n'
		makefileSettings += 'EXT_SOURCE=' + self._log_manager._settings['ProjectText']['SourceText']['EXT_SOURCE'] + '\n'

		for key, value, in tools.pubInfoObject['Extensions'].iteritems() :
			makefileSettings += key + "=" + value + '\n'

		# Get our path information from our project .conf file and output absolute paths
		for key, value, in self._log_manager._settings['System']['Paths'].iteritems() :
			makefileSettings += key + '=' + os.path.abspath(value) + '\n'

		# Path info from the pub settings file
		for key, value, in tools.pubInfoObject['Paths'].iteritems() :
			if value.split('/')[0] == '__TIPE__' :
				makefileSettings += key + '=' + value.replace('__TIPE__', basePath) + '\n'
			else :
				makefileSettings += key + '=' + os.path.abspath(value) + '\n'

		# Insert the peripheral folder name here. This is a
		# hard-coded insert because it should always be the
		# name given here. The user cannot change this.
		makefileSettings += 'PATH_SOURCE_PERIPH=' + sourcePath + '/' + peripheralFolderName + '\n'

		# The map processing folder is put in the Process folder
		# like the peripheral folder.
		makefileSettings += 'PATH_MAP=' + os.path.abspath(tools.pubInfoObject['Paths']['PATH_PROCESS']) + '/Maps\n'

		# We will use a function to tell us what the project
		# config name is.
		makefileSettings += 'FILE_PROJECT_CONF=' + tools.getProjectConfigFileName() + '\n'

		for key, value, in tools.pubInfoObject['Files'].iteritems() :
			# The book file only happens once
			if key == 'FILE_BOOK' :
				date = tools.getYMD()
				projectID = self._log_manager._settings['Project']['ProjectInformation']['projectID']
				makefileSettings += key + "=" + projectID + '-' + date + '-' + value + '\n'
			else :
				makefileSettings += key + "=" + value + '\n'

		# Get file names from project .scripture.conf file that are scattered around
		makefileSettings += 'FILE_ILLUSTRATION_DATA=' + self._log_manager._settings['Format']['Illustrations']['FILE_ILLUSTRATION_DATA'] + '\n'
		makefileSettings += 'FILE_PAGE_BORDER=' + self._log_manager._settings['Format']['PageLayout']['FILE_PAGE_BORDER'] + '\n'
		makefileSettings += 'FILE_WATERMARK=' + self._log_manager._settings['Format']['PageLayout']['FILE_WATERMARK'] + '\n'

		for key, value, in tools.pubInfoObject['TeX'].iteritems() :
			makefileSettings += key + "=" + value + '\n'

		# Build up all the component groupings

		# Build component groups (This worked until some of the list items had multiple items)
		# makefileSettings += '\n'.join(key + '=' + ' '.join(value) for key, value in self._log_manager._settings['Format']['BindingGroups'].iteritems()) + '\n'
		# Now we do this...
		for key, value in self._log_manager._settings['Format']['BindingGroups'].iteritems() :
			vList = []
			for item in value :
				# Take out any extra stuff
				vList.append(item.split()[0])

			makefileSettings += key + '=' + ' '.join(vList) + '\n'

		# Get the book meta group (made up of component groups)
		makefileSettings += '\n'.join(key + '=' + ' '.join(value) for key, value in self._log_manager._settings['Format']['MetaGroups'].iteritems()) + '\n'

		# Add component mapping info here
		editor = self._log_manager._settings['ProjectText']['SourceText']['Features'].get('projectEditor')

		# Build filter list of all possible components in this project
		# The following would work to build the initial list:
		# filterList = []
		# for list in self._log_manager._settings['Format']['Binding'].itervalues() :
		#     filterList.extend(list)
		# However, using reduce is a much faster way. Note the '[]' a the end of the
		# line. This initializes the filterList.
		# components = reduce(operator.add, self._log_manager._settings['Format']['BindingGroups'].itervalues(), [])
		# However, the problem with this is that it doesn't preserve order.
		# To preserve order you need something like this:
		filterList = set()
		components = []
		for group in self._log_manager._settings['Format']['BindingGroups'].iterkeys() :
			for item in self._log_manager._settings['Format']['BindingGroups'].get(group) :
				# Some components may carry bagage, we separate that out here
				ic = item.split()[0]
				if ic and not item in filterList :
					filterList.add(ic)
					components.append(ic)

		# Output all the components for makefile
		makefileSettings += 'COMPONENTS_ALL=' + ' '.join(components) + '\n'

		# Output a list of all the components that have illustrations
		captionsFileName = tools.pubInfoObject['Files']['FILE_ILLUSTRATION_CAPTIONS']
		projectPeripheralFolderName = os.getcwd().split('/')[-1]
		projectPeripheralFolderPath = sourcePath + '/' + projectPeripheralFolderName
		projectIllustrationsCaptions = projectPeripheralFolderPath + "/" + captionsFileName

		# Make a list of bookIDs that will use illustrations in them
		# One problem is that at the begining of the project there may
		# not be a file there yet. This has to be optional.
		bkids = set()
		inFileData = ''
		try :
			inFileData = csv.reader(open(projectIllustrationsCaptions), dialect=csv.excel)
			for line in inFileData :
				if line[1].upper() != 'BOOKID' :
					bkids.add(line[1].lower())

			makefileSettings += 'HAS_ILLUSTRATIONS=' + ' '.join(bkids) + '\n'
		except :
			self._log_manager.log('INFO', 'Not illustrations found for this publication.')
			makefileSettings += 'HAS_ILLUSTRATIONS=\n'

		# MAP COMPONENT PROCESSES
		# Maps may or may not be used in any given publication. If they are
		# this next bit will produce some process commands for each map according
		# to settings in the system. A couple special map processes are created
		# here and injected into the main make file to make map processing easier.
		# The commands are then accessed by the makefile part of the process in
		# the maps rules set. First we begin with some common params
		processFolder       = os.getcwd() + "/" + tools.pubInfoObject['Paths']['PATH_PROCESS']
		mapFolder           =  os.getcwd() + "/" + tools.pubInfoObject['Paths']['PATH_MAPS']
		fontFolder          =  os.getcwd() + "/" + tools.pubInfoObject['Paths']['PATH_FONTS']
		extPNG              = tools.pubInfoObject['Extensions']['EXT_PNG']
		extPDF              = tools.pubInfoObject['Extensions']['EXT_PDF']
		extSVG              = tools.pubInfoObject['Extensions']['EXT_SVG']

		# INTERMEDIATE PNG PROCESS
		# Before final effects are applied to the map image we create an intermediate
		# version from the finalized SVG version which was edited in Inkscape. This
		# will be created by the Inkscape command-line utility using the command we
		# create here.
		# First we point Inkscape to the right fonts
		fontConfig          = 'FONTCONFIG_PATH=' + fontFolder
		inkscape            = self._log_manager._settings['Format']['MapProcesses']['inkscape']
		inkscapeCommands    = self._log_manager._settings['Format']['MapProcesses']['inkscapeCommands']
		for item in self._log_manager._settings['Format']['BindingGroups']['GROUP_MAPS'] :
			source          = ''
			target          = ''
			if item != '' :
				source      = '--file=' + mapFolder + '/' + item.split()[0] + '.' + extSVG
				target      = '--export-png=' + mapFolder + '/' + item.split()[0] + '.' + extPNG
				# Put it all together in a single command and output
				command     = fontConfig + ' ' + inkscape + ' ' + inkscapeCommands + ' ' + source + ' ' + target
				makefileSettings += 'PROCESS_MAP_PNG-' + item.split()[0] + '=' + command + '\n'

		# FINAL COMPONENT PDF PROCESS
		# This creates the final component PDF version which will be brought
		# into the final map group file. Because some maps may need to be rotated
		# this code will produce a custom command for each map that is being
		# processed.
		imageMagick         = self._log_manager._settings['Format']['MapProcesses']['imageMagick']
		colorSpace          = self._log_manager._settings['Format']['MapProcesses']['colorSpace']
		imageMagickCommands = self._log_manager._settings['Format']['MapProcesses']['imageMagickCommands']
		# Add a map color mode for reference for map processes outside
		# ImageMagick
		makefileSettings += 'MAP_COLOR_MODE=' + colorSpace.split()[1].lower() + '\n'

		# The use of bw is not valid for a colorspace but we need to do this to
		# select the right background in aother operation.  This will change it
		# to gray so ImageMagick doesn't choke.
		if colorSpace == '-colorspace bw' :
			colorSpace = '-colorspace gray'

		for item in self._log_manager._settings['Format']['BindingGroups']['GROUP_MAPS'] :
			source          = ''
			target          = ''
			rotate          = ''
			if item != '' :
				# If the component has a rotation parameter, it is in the
				# second half of the component string.
				try :
					rotate  = '-rotate ' + item.split()[1]
				except :
					pass

				source      = 'png:' + mapFolder + '/' + item.split()[0] + '.' + extPNG
				target      = 'pdf:' + processFolder + '/' + item.split()[0] + '.' + extPDF
				# Put it all together in a single command and output
				command     = imageMagick + ' ' + source + ' ' + imageMagickCommands + ' ' + rotate + ' ' + colorSpace + ' ' + target
				makefileSettings += 'PROCESS_MAP_PDF-' + item.split()[0] + '=' + command + '\n'


		#######################################################################
		# At this point it would be good to add a couple more 'HAS_' lists which
		# could be used by makefile to use more generic rules so that components
		# can all be processed by the same rules.  More code will need to be
		# written like above.
		#######################################################################

		# Output a list of all component key names and names
		for cID in components :

			try:
				makefileSettings += tools.getComponentKeyName(cID) + '=' + tools.getComponentTargetName(cID) + '\n'
			except:
				self._log_manager.log('ERRR', 'Component: [' + cID + '] is not known to the system', 'true')


		# Create the final key/values for the file
		makefileFinal = ""

		# Add in system level include files first, then the component types
		makefileFinal += "include " + basePath + "/bin/make/lib_" + self._projectType + "/system.mk\n"

		for value in tools.pubInfoObject['Components']['componentTypeList'] :
			makefileFinal += "include " + basePath + "/bin/make/lib_" + self._projectType + "/" + value + ".mk\n"

		# Output to the new makefile file
		makefileObject.write(makefileHeader + makefileSettings + makefileFinal)

	def expandMetaGroups (self, groups) :
		'''This will expand meta groups in the binding list.'''

		components = ""
		for thisGroup in groups :
			components += " ".join(self._log_manager._settings['Format']['Binding'][thisGroup])

		return components



# This starts the whole process going
def doIt(log_manager):
	thisModule = MakeMakefile()
	return thisModule.main(log_manager)
