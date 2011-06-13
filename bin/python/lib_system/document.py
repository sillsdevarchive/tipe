#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110610
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle processes at the document level.

# History:
# 20110610 - djd - Initial draft


###############################################################################
################################### Shell Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os

# Load the local classes
from configure import *
configure = Configure()
from report import *
report = Report()
from component import *
component = Component()


class Document (object) :

	# Intitate the whole class
	def __init__(self) :

		self._home          = os.getcwd()
		self._sysConfig     = configure.getSystem()
		self._makefileFile  = self._home + '/' + self._sysConfig['System']['makefileFile']
		self._textFolder    = self._home + '/' + self._sysConfig['System']['textFolder']
		self._processFolder = self._home + '/' + self._sysConfig['System']['processFolder']


	def createMakefile (self, compID, process) :
		'''Create a makefile with instructions for processing this component.'''


		compUSFM = self._textFolder + '/' + compID + '.usfm'
		compTEX = self._processFolder + '/' + compID + '.tex'

		# Build the makefile commands
		makefileCommand = compUSFM + ' : ' + compTEX + '\n' + \
			'\t@echo INFO: Creating: ' + compUSFM

		writeObject = codecs.open(self._makefileFile, "w", encoding='utf_8')
		writeObject.write(makefileCommand)
		report.writeToLog('LOG', 'document.createMakefile: Created ' + process + ' makefile for ' + compID)
		writeObject.close()

		return True


#$(PATH_PROCESS)/$(1).$(EXT_TEX) : $(PATH_PROCESS)/$(FILE_TEX_SETTINGS)
#	@echo INFO: Creating: $(1).$(EXT_TEX)
#	@$(MOD_RUN_PROCESS) "$(MOD_MAKE_TEX)" "$(1)" "$(1).$(EXT_WORK)" "$$@" ""






