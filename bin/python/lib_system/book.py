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

		# This section of the configuration will contian only things pertaining
		# to a book object.  We'll asign it here.
		self._components = []

	def loadBooks(self, aProject) :
		if self._config['bindingOrder'] :
			for c in self._config['bindingOrder'] :
				aProject.addComponent(c)


	def createMakefile(self, fh) :
		'''Create a makefile that contains rules for all the components listed
		in the project.  This could be a very large makefile.'''
		for c in self._components :
			c.createMakefile(fh)

	def addComponent(self, aComp) :
		self._components.append(aComp)
		return aComp

	def addToBinding(self, name) :
		'''This will do a simple component append to the bindingOrder list and
		add it to the project.conf file.  This is often called by
		project.addNewComponent(). [Note: more complex functions will need to be
		written for binding order manipulation.]'''

		# Append the comp name to the end of the bindingOrder list.  Note, you
		# cannot use the .append() command.  You must manually merge two lists.
		# The "name" var becomes a list that is merged to the end of the
		# bindingOrder list.
		self._config['bindingOrder'] = self._config['bindingOrder'] + [name]






