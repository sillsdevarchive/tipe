#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110721
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle system process commands.  This relys a lot on the
# optparse lib.  Documentation can be found here:
# http://docs.python.org/library/optparse.html

# History:
# 20110721 - djd - Begin initial draft


###############################################################################
################################# Command Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os
from optparse import OptionParser
from report import Report

# Load the local classes


commands = {}

class MetaCommand(type) :

	def __init__(c, namestring, t, d) :
		global commands
		super(MetaCommand, c).__init__(namestring, t, d)
		if c.type :
			commands[c.type] = c.__call__()


class Command (object) :
	'''The main command object class.'''

	__metaclass__ = MetaCommand
	type = None

	# Intitate the whole class
	def __init__(self) :
		self.parser = OptionParser(self.__doc__)
		self.setupOptions(self.parser)

	def run(self, aProject, args) :
		(self.options, self.args) = self.parser.parse_args(args = args)

	def setupOptions(self, parser) :
		pass

	def help(self) :
		self.parser.print_help()


###############################################################################
########################### Command Classes Go Here ###########################
###############################################################################
# Insert the commands you want visable to the system here in the order you want
# them to appear when listed.


# FIXME: To enable more flexibility, we need to move the command parameters out
# to the XML files.  How do we do that?

class About (Command) :
	'''Display the system's About text'''

	type = "about"

	def run(self, aProject, args) :
		mod = 'command.About()'
		super(About, self).run(aProject, args)
		aProject.terminal(aProject._sysConfig['System']['aboutText'])


class ChangeSettings (Command) :
	'''Change a system setting.'''

	type = "change"

	def run(self, aProject, args) :
		mod = 'command.ChangeSettings()'
		super(ChangeSettings, self).run(aProject, args)
		aProject.changeSystemSetting(args[0][2:], args[1])

	def setupOptions(self, parser) :
		self.parser.add_option("--userName", action="store", help="Change the system user name.")
		self.parser.add_option("--language", action="store", help="Change the interface language.")
		self.parser.add_option("--loglimit", action="store", help="Set the number of lines the log file is allowed to have.")


class Debugging (Command) :
	'''Turn on debugging (verbose output) in the logging.'''

	type = "debug"

	def run(self, aProject, args) :
		mod = 'command.Debugging()'
		super(Debugging, self).run(aProject, args)
		if args[0][2:] == 'on' :
			aProject.changeSystemSetting("debugging", "True")

		if args[0][2:] == 'off' :
			aProject.changeSystemSetting("debugging", "False")

	def setupOptions(self, parser) :
		self.parser.add_option("--on", action="store_true", help="Turn on debugging for the log file output.")
		self.parser.add_option("--off", action="store_false", help="Turn off debugging for the log file output.")


class Help (Command) :
	'''Provide user with information on a specific command.'''

	type = "help"

	def run(self, aProject, args) :
		global commands
		if len(args) :
			cmd = commands[args[0]]
			cmd.help()
		else :
			for c in commands.keys() :
				aProject.terminal(c)

			if len(commands) <= 2 :
				aProject.terminal("\nType [help command] for more general command information.")


class GUIManager (Command) :
	'''Start a TIPE GUI manager program'''

	type = "manager"

	def run(self, aProject, args) :
		super(GUIManager, self).run(aProject, args)
		if args[1].lower() == 'standard' :
			aProject.terminal("Sorry, this GUI Manager has not been implemented yet.")
		elif args[1].lower() == 'web' :
			aProject.terminal("Sorry, the web client has not been implemented yet.")
		else :
			aProject.terminal("Not a recognized GUI Manager.")

	def setupOptions(self, parser) :
		self.parser.add_option("-c", "--client", action="store", type="string", help="Start up the TIPE client.")


class CreateProject (Command) :
	'''Create a new project based on a predefined project type.'''

	type = "create"

	def run(self, aProject, args) :
		mod = 'command.CreateProject()'
		super(CreateProject, self).run(aProject, args)
		c = 0; ptype = ''; pname = ''; pid = ''; pdir = ''
		for o in args :
			if o == '-t' or o == '--ptype' :
				ptype = args[c+1]
			elif o == '-n' or o == '--pname' :
				pname = args[c+1]
			elif o == '-i' or o == '--pid' :
				pid = args[c+1]
			elif o == '-d' or o == '--pdir' :
				pdir = args[c+1]

			c+=1

		print ptype, pname, pid, pdir
		if aProject.makeProject(ptype, pname, pid, pdir) :
				aProject.writeToLog('MSG', 'Created new project!', mod)

	def setupOptions(self, parser) :
		self.parser.add_option("-t", "--ptype", action="store", help="Set the type of project this will be, this is required.")
		self.parser.add_option("-n", "--pname", action="store", help="Set the name of project this will be, this is required.")
		self.parser.add_option("-i", "--pid", action="store", help="Set the type of project this will be, this is required.")
		self.parser.add_option("-d", "--pdir", action="store", help="Create project in this directory, default is current directory.")


# This is an example command class
#class Setup (Command) :
#    '''Setup creates a new object'''
#    type = "setup"
#    def run(self, aProject, args) :
#        super(Setup, self).run(aProject, args)
#        # do something here, options are in self.options
#
#    def setupOptions(self, parser) :
#        self.parser.add_option("-d", "--dir", type="string", action="store", help="Create project in this directory")


class RemoveProject (Command) :
	'''Remove an active project from the system and lock the working conf files.
	If no project ID is given the default is the project in the cwd.  If there
	is no project in the cwd it will fail.'''

	type = "remove"

	def run(self, aProject, args) :
		mod = 'command.RemoveProject()'
		super(RemoveProject, self).run(aProject, args)
		if len(args) :
			pID = args[1]
		else :
			if aProject.projectIDCode != '' :
				pID = aProject.projectIDCode
			else :
				aProject.writeToLog('ERR', 'Project ID code not given or found. Remove project failed.', mod)

		if aProject.removeProject(pID) :
			aProject.writeToLog('MSG', 'Removed project: [' + pID + ']', mod)

	def setupOptions(self, parser) :
		self.parser.add_option("-i", "--pid", type="string", action="store", help="The ID code of the project to be removed.")


class RestoreProject (Command) :
	'''Restores a project in the dir given. The default dir is cwd.'''

	type = "restore"

	def run(self, aProject, args) :
		mod = 'command.RestoreProject()'
		super(RestoreProject, self).run(aProject, args)
		if len(args) :
			print args[1], os.path.split(os.getcwd())[1]

			if os.path.split(os.getcwd())[1] == args[1] :
				pDir = os.getcwd()
			else :
				pDir = os.path.abspath(args[1])
		else :
			pDir = os.getcwd()

		if aProject.restoreProject(pDir) :
			aProject.writeToLog('MSG', 'Restored project at: ' + pDir, mod)
		else :
			aProject.writeToLog('ERR', 'Restoring project at: ' + pDir + ' failed.', mod)

	def setupOptions(self, parser) :
		self.parser.add_option("-d", "--dir", type="string", action="store", help="Restore a project in this directory")








###############################################################################
####################### TIPE System Command Classes ###########################
###############################################################################

# Here go all the command classes that TIPE knows how to use.  If it isn't
# defined here, it will not work.  The documentation for each command goes in
# the command so when the user types 'help' followed by the command they will
# get whatever documentation there is for that command.


class Render (Command) :
	'''Documentation goes here'''

	def render(self, argv) :
		'''Usage: render [compID] | Render the current component.'''

		mod = 'tipe.render()'

		# First check our project setup and try to auto correct any problems that
		# might be caused from missing project assets.  This can include files
		# like.sty, .tex, .usfm, and folders, etc.
		if not self.checkProject(aProject.self) :
			self.writeToLog('ERR', 'No project found!', mod)
			return

		aDoc = self.getDoc(argv[0])
		if not aDoc :
			self.writeToLog('ERR', 'Component [' + argv[0] + '] not found in project', mod)
			return

		#FIXME: What does this next line do?
		aDoc.render()

		# Create the makefile for processing this particular component.  This is
		# done every time TIPE is run.
		if aDoc.createMakefile(thisComponent, command) :
			if runMake() :
				self.writeToLog('MSG', 'Process completed successful!', mod)
			else :
				self.writeToLog('ERR', 'Process did not complete successfuly. Check logs for more information.', mod)

		# Collect the results and report them in the log

		return True





