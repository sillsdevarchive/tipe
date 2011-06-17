#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110615
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle default template configuration.

# History:
# 20110615 - djd - Initial draft


###############################################################################
################################### Shell Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os
from xml.etree.ElementTree import XMLID, ElementTree
tree = ElementTree()

# Load the local classes


class ConfigTemplate (object) :

	# Intitate the whole class
	def __init__(self) :

		#self.home              = dir
		self.base               = os.environ.get('TIPE_BASE')


	def readTemplate (self, target) :
		'''Read in default settings from TIPE system'''

		template       = os.path.join(self.base, 'bin', target)

		try:
			tree = ET.parse(template)
		except Exception, inst:
			# FIXME: How do we write to the log file when this mod is dependent on the project mod?
			# aProject.writeToLog('ERR', mod, "Unexpected error opening %s: %s" % (xml_file_in, inst))
			return

		tree = ET.parse(template)



#        # Open and read XML file
#        fhXML = file(template)
#        txtXML = ''.join(fhXML)
#        fhXML.close
#        (eXML, dXML) = XMLID(txtXML)

#        print dXML.has_key('system')
#        print dXML.keys()
#        for key in dXML.keys() :
#            print dXML.get(key)

		return True


	def mergeInDefaults (self, home, default, current) :
		'''This will merge project and default configuration files.It assumes
		that both files exists and will fail miserably if one doesn't.  It will
		insert into the new version of the project configuration any new params
		appear in the system defaults.  This is to better facilitate any
		upgrades/bug fixes, ect. that might have occurred to the system since the
		project was last run.  Conversely, any parameters that exist in the
		project configuration but are not found in the system defaults will be
		removed and reported on in the system log file.  As these parameters are
		no longer valid to the system there is no need for them to be kept when
		upgrading.  Any existing parameters in the project that differ from the
		system default will be preserved.'''

		pass


	def writeNewConfig (self, home, default, new) :
		'''This will write out a new project configuration file based on its
		parent system default settings file.'''

		pass






