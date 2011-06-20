#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110610
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle processes at the book level.

# History:
# 20110610 - djd - Initial draft


###############################################################################
################################# Book Class ##################################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

# import codecs, os
from document import Document


class Book (Document) :

	# Intitate the whole class
	def __init__(self, aProject, bookConfig) :
		super(Book, self).__init__(aProject, bookConfig)

		self._components = []
		if bookConfig['bindingOrder'] :
			for c in bookConfig['bindingOrder'] :
				aProject.addComponent(c)


	def createMakefile(self, fh) :
		'''Create a makefile that contains rules for all the components listed
		in the project.  This could be a very large makefile.'''
		for c in self._components :
			c.createMakefile(fh)


	def addComponent(self, aComp) :
		'''Add a component to the book component order list.'''
		self._components.append(aComp)
		return aComp





