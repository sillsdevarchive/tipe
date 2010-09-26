#!/usr/bin/python2
# -*- coding: utf_8 -*-
# version: 20080529
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This class contains functions for working with fonts in
# the context of a publishing project.

# History:
# 20080819 - djd - Initial draft
# 20081023 - djd - Refactored due to changes in project.conf
# 20081111 - djd - Changed locations of font files, also fixed
#        problem with font files not copying.


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, sys, shutil

# Import supporting local classes
import tools

class FontManager (object) :

	# Intitate the whole class
	def __init__(self) :

		# Pull in the project settings object that
		# will be passed along with this object.
		self._settings_project = tools.getProjectSettingsObject()

		if self._settings_project['System']['General'].get('debugMode', 'false').lower() == 'true' :

			self.projectFontFamily = self._settings_project['Format']['Fonts'].get('projectFontFamily', 'GenBkBas')
			self.projectFontsFolder = os.getcwd() + "/" + self._settings_project['System']['Paths'].get('PATH_FONTS', 'Fonts')
			self.pathToFontLibrary = self._settings_project['System']['Paths']['PATH_FONT_LIB']
			if os.path.isdir(self.pathToFontLibrary) :
				self.fontFamilySourceFolder = self.pathToFontLibrary + "/" + self.projectFontFamily
			else :
				self.pathToFontLibrary = os.environ.get('PTXPLUS_BASE') + "/resources/lib_fonts"
				self.fontFamilySourceFolder = self.pathToFontLibrary + "/" + self.projectFontFamily


		else :
			try :
				self.projectFontFamily = self._settings_project['Format']['Fonts'].get('projectFontFamily', 'GenBkBas')
				self.projectFontsFolder = os.getcwd() + "/" + self._settings_project['System']['Paths'].get('PATH_FONTS', 'Fonts')
				self.pathToFontLibrary = self._settings_project['System']['Paths']['PATH_FONT_LIB']
				if os.path.isdir(self.pathToFontLibrary) :
					self.fontFamilySourceFolder = self.pathToFontLibrary + "/" + self.projectFontFamily
				else :
					self.pathToFontLibrary = os.environ.get('PTXPLUS_BASE') + "/resources/lib_fonts"
					self.fontFamilySourceFolder = self.pathToFontLibrary + "/" + self.projectFontFamily

			except :
				# Idealy, we don't want to hard-code anything but in some cases it is just
				# necessary to do it.
				self.projectFontFamily = "GenBkBas"
				self.projectFontsFolder = os.getcwd() + "/Fonts"
				self.fontFamilySourceFolder = os.environ.get('PTXPLUS_BASE') + "/resources/lib_fonts/GenBkBas"

		self.projectFontFamilyFolder = self.projectFontsFolder + "/" + self.projectFontFamily


	def haveFonts (self) :
		'''Check to see if the font family listed in the project.conf
			file is in the project.'''

		ok = False
		# Realistically we can only look for the family font folder
		# We can't always be sure of what fonts are in the family or
		# how many of them there are. For that reason we need to keep
		# this simple (for now)
		if os.path.isdir(self.projectFontFamilyFolder) :
			if len(os.listdir(self.projectFontFamilyFolder)) > 0 :
				ok = True

		return ok


	def installFonts (self) :
		'''Install the fonts that are listed in the project.conf file
			and return True, otherwise return False.'''

		ok = False
		# If we can see a destination folder then there probably isn't anything to do.
		if not os.path.isdir(self.projectFontFamilyFolder) :
			os.mkdir(self.projectFontFamilyFolder)
			tools.userMessage('Created folder: ' + self.projectFontFamilyFolder)
		if os.path.isdir(self.fontFamilySourceFolder) == True :
			tools.copyFiles(self.fontFamilySourceFolder, self.projectFontFamilyFolder)
			ok = True

		return ok


	def localiseFontsConf(self) :
		'''Sets the <dir> and <cachdir> to be the directory in which
			   the fonts.conf file exists. This helps to provide better
			   seperation of our fonts from the system.'''

		fileName = self.projectFontsFolder + "/fonts.conf"
		# First lets check to see if the fonts.conf file exists
		if os.path.isfile(fileName) == False :
			srcname = os.environ.get('PTXPLUS_BASE') + "/resources/Fonts/fonts.conf"
			# See if there is even a fonts folder to work with
			if os.path.isdir(self.projectFontsFolder) == False :
				os.mkdir(self.projectFontsFolder)

			shutil.copy(srcname, fileName)

		# Import this module for this process only (May need to move it if other processes ever need it)
		from xml.etree.cElementTree import ElementTree

		et = ElementTree(file = fileName)
		path = os.path.dirname(os.path.abspath(fileName))
		for p in ('dir', 'cachedir') :
			et.find(p).text = path

		# Write out the new font.conf file
		et.write(fileName, encoding = 'utf-8')
