#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110610
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle processes at the component level.

# History:
# 20110610 - djd - Begin initial draft


###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os
from document import Document

# Load the local classes


class Component (Document) :

	# Intitate the whole class
	def __init__(self, name, aProject, compConfig) :
		super(Component, self).__init__(aProject, compConfig)

		self.name = name




###############################################################################


	def initComponentFiles (self, aProject) :
		'''Initialize all the necessary files for a given component.'''
		pass
		# Discover the type of component it is

		print self._config['file_output']

################################################################################







	def createMakefile(self, fh) :
		'''Create a makefile rule for a specific component and append it to the
		project makefile.'''

#        compUSFM = self._textFolder + '/' + compID + '.usfm'
#        compTEX = self._processFolder + '/' + compID + '.tex'

#        # Build the makefile commands
#        makefileCommand = compUSFM + ' : ' + compTEX + '\n' + \
#            '\t@echo INFO: Creating: ' + compUSFM + '\n' + \
#            '\ttouch ' + compUSFM + '\n\n'

#        makefileCommand += compTEX + ' :' + '\n' + \
#            '\ttouch ' + compTEX + '\n\n'


#        writeObject = codecs.open(self._makefileFile, "w", encoding='utf_8')
#        writeObject.write(makefileCommand)
#        aProject.writeToLog('LOG', 'createMakefile(): Created ' + process + ' makefile for ' + compID)
#        writeObject.close()

#$(PATH_PROCESS)/$(1).$(EXT_TEX) : $(PATH_PROCESS)/$(FILE_TEX_SETTINGS)
#	@echo INFO: Creating: $(1).$(EXT_TEX)
#	@$(MOD_RUN_PROCESS) "$(MOD_MAKE_TEX)" "$(1)" "$(1).$(EXT_WORK)" "$$@" ""

		return True
