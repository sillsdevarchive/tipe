#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110610
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project configuration managment tasks.

# History:
# 20110610 - djd - Initial draft


###############################################################################
################################### Shell Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os
from configobj import ConfigObj


class Configure (object) :

	def __init__(self) : pass

#        self._placeholder = ""
#        self._processLogObject = []


	def getObject (self, configFile) :
		'''Return a configuration object from a ini file.'''

		return ConfigObj(configFile, encoding='utf_8')


	def getSystem (self) :
		'''Return the system settings object'''

		return self.getObject(os.environ.get('TIPE_BASE') + "/bin/tipe.conf")
