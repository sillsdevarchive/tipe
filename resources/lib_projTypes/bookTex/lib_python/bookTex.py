#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110728
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project infrastructure tasks.

# History:
# 20110728 - djd - Initial draft

print "bookTex.py loading"

###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, sys, fileinput
from datetime import *
from configobj import ConfigObj, Section

# Load the local classes
from project import Project
from bookTex_command import Command
from book import Book
from xml.etree import ElementTree

###############################################################################
############################ Define Global Functions ##########################
###############################################################################

# These root level functions work at a fundamental level of the system


###############################################################################
################################## Begin Class ################################
###############################################################################

class bookTex (Project) :

	def __init__(self) :

		# Set all the initial paths and locations

		self.aProject = aProject

###############################################################################
############################# Begin Main Functions ############################
###############################################################################


	def changeProjectSetting (self, aProject) :
		'''This will do something.'''

		print "It is working!"


