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

import codecs, os, inspect

# Load the local classes


class Component (Document) :

	# Intitate the whole class
	def __init__(self, aProject, compconfig) :
		super(Component, self).init(sysconfig)

		self._sourceConfig      = compconfig
		self._sourceFile        = os.path.join(self._home, self._sourceConfig['sourceFile'])


	def checkComponent (self, thisComponent) :
		'''Check the intetrity of a project component.'''

		# Fist see if it exists in the project .source file.  All components
		# should be found there.
		if not os.path.isfile(self._sourceFile) :
			aProject.writeToLog('ERR', 'checkComponent(): No source configuration file found for this project.')
			aProject.writeToLog('ERR', 'checkComponent(): This component does not exist: ' + thisComponent)
			return False
		else :
			if not self.doesExist(thisComponent) :
				aProject.writeToLog('ERR', 'checkComponent(): This component not in source list: ' + thisComponent)
				return False

		return True


	def addComponent (self, thisComponent) :
		'''Add a component to a project.  The component needs to be "registered"
		in several places and several dependent objects need to be created as
		well.'''

		# First check to see if the source file is there.
		if not os.path.isfile(self._sourceFile) :
			self.makeSourceList()

		# Try adding to the source link list
		if self.addComponentSourceLink(thisComponent) :
			# If that worked we'll add it to the binding list
			self.addComponentToBindingOrder(thisComponent)

		return


	def addComponentSourceLink (self, thisComponent) :
		'''Called on from addComponent() this will add component ID to the
		source link list.'''

		# Do a silent check to see if it actually exsits or not in the source
		# link list.  If it does, we don't touch it because we could loose the
		# link data.
		privateObject = configure.getSource()
		try :
			if privateObject['ComponentSourceLink'][thisComponent] :
				aProject.writeToLog('WRN', 'addComponentSourceLink(): Component already exists: ' + thisComponent)
				return False
		except :
			# Write out the component code to source file
			privateObject['ComponentSourceLink'][thisComponent] = thisComponent
			privateObject.write()
			aProject.writeToLog('LOG', 'addComponent(): Added source link list: ' + thisComponent)
			return True


	def addComponentToBindingOrder (self, thisComponent) :
		'''Called on from addComponent() this will add a component to the
		binding order.  The binding order can contain multiple instances of a
		single ID. Because of this, this function can be called on by more
		than just addComponent().'''

		privateObject = configure.getSource()
		oldOrder = []
		try :
			oldOrder = privateObject['BindingOrder']['order']
		except : pass

		# Need to output as a proper list.
		oldOrder.append(thisComponent)
		privateObject['BindingOrder']['order'] = oldOrder
		privateObject.write()
		aProject.writeToLog('LOG', 'addComponent(): Added to binding order: ' + thisComponent)

		return


	def doesExist (self, thisComponent) :
		'''Simple T or F to see if a component is listed in the source file.'''

		keyList = configure.getSource()['ComponentSourceLink'].keys()
		for key in keyList :
			if key == thisComponent :
				return True

		return False


	def makeSourceList (self) :
		'''Create an empty source list file.'''

		# Do we need a source file made?
		if not os.path.isfile(self._sourceFile) :
			writeObject = codecs.open(self._sourceFile, "w", encoding='utf_8')
			writeObject.write('[ComponentSourceLink]\n\n[BindingOrder]\n\n')
			writeObject.close()

		return

