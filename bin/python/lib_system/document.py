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

class Document (object) :

	# Intitate the whole class
	def __init__(self, aProject, compConfig) :
		pass

	def render(self) :
		fh = file("Makefile", "w")
		self.createMakefile(fh)
		fh.close()
		# run make

	def createMakefile (self, fh) :
		''' This is a dummy function that is here to cover for functions of the
		same name in the component and book modules.'''

		pass

		'''Create a makefile with instructions for processing this component.'''


