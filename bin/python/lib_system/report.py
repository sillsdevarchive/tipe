#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110721
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle system and process reporting tasks.

# History:
# 20110721 - djd - Initial draft


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, sys, fileinput
from datetime import *
from configobj import ConfigObj, Section


# Load the local classes



###############################################################################
################################## Begin Class ################################
###############################################################################


class Report (object) :

	# Intitate the whole class
	def __init__(self, projLogFile = None, projErrFile = None,
					debug = False, projectName = None) :

		self._debugging         = False
		self._projLogFile       = projLogFile
		self._projErrorLogFile  = projErrFile
		self._debugging         = debug
		self._projectName       = projectName


	def terminal (self, msg) :
		'''Send a message to the terminal with a little formating to make it
		look nicer.'''

		# Output the message and wrap it if it is over 60 chars long.
		print self.wordWrap(msg, 60)


	def terminalCentered (self, msg) :
		'''This will try to center text on a 60 char-long line.  If it is more
		than that it will wrap the text.'''

		if len(msg) < 60 :
			print self.centerText(msg, 60)
		else :
			print self.wordWrap(msg, 60)


	def error (self, msg, dest='t') :
		'''Report error to log and/or terminal.'''

		# Output to terminal if indicated
		if dest == "t" :
			self.terminal(msg)


	def wordWrap (self, text, width) :
		'''A word-wrap function that preserves existing line breaks
			and most spaces in the text. Expects that existing line
			breaks are linux style newlines (\n).'''

		def func(line, word) :
			nextword = word.split("\n", 1)[0]
			n = len(line) - line.rfind('\n') - 1 + len(nextword)
			if n >= width:
				sep = "\n"
			else:
				sep = " "
			return '%s%s%s' % (line, sep, word)
		text = text.split(" ")
		while len(text) > 1:
			text[0] = func(text.pop(0), text[0])
		return text[0]

	#FIXME: This doesn't work yet
	def centerText (self, text, width) :
		'''As long as the length of the text does not exceed the width of the line.
		This will center the text in the line and leave white space before and
		after.'''

	#    return '{:^' + str(width) + '}'.format(text)
		return '{:*^60}'.format('text')


###############################################################################
################################# Logging routines ############################
###############################################################################

# These have to do with keeping a running log file.  Everything done is recorded
# in the log file and that file is trimmed to a length that is specified in the
# system settings.  Everything is channeled to the log file but depending on
# what has happened, they are classed in three levels:
#   1) Common event going to log and terminal
#   2) Warning event going to log and terminal if debugging is turned on
#   3) Error event going to the log and terminal

	def writeToLog (self, code, msg, mod = None) :
		'''Send an event to the log file. and the terminal if specified.
		Everything gets written to the log.  Whether a message gets written to
		the terminal or not depends on what type (code) it is.  There are four
		codes:
			MSG = General messages go to both the terminal and log file
			LOG = Messages that go only to the log file
			WRN = Warnings that go to the terminal and log file
			ERR = Errors that go to both the terminal and log file.'''

		# Build the mod line
		if mod :
			mod = mod + ': '
		else :
			mod = ''

		# Write out everything but LOG messages to the terminal
		if code != 'LOG' :
			self.terminal(code + ' - ' + msg)

		# Test to see if this is a live project by seeing if the project name is
		# set.  If it is, we can write out log files.  Otherwise, why bother?
		if self._projectName != 'None' :
			# When are we doing this?
			date_time, secs = str(datetime.now()).split(".")

			# Build the event line
			if code == 'ERR' :
				eventLine = '\"' + date_time + '\", \"' + code + '\", \"' + mod + msg + '\"'
			else :
				eventLine = '\"' + date_time + '\", \"' + code + '\", \"' + msg + '\"'

			# Do we need a log file made?
			if not os.path.isfile(self._projLogFile) or os.path.getsize(self._projLogFile) == 0 :
				writeObject = codecs.open(self._projLogFile, "w", encoding='utf_8')
				writeObject.write('TIPE event log file created: ' + date_time + '\n')
				writeObject.close()

			# Now log the event to the top of the log file using preAppend().
			self.preAppend(eventLine, self._projLogFile)

			# Write errors and warnings to the error log file
			if code == 'WRN' and self._debugging :
				self.writeToErrorLog(eventLine)

			if code == 'ERR' :
				self.writeToErrorLog(eventLine)

		return


	def writeToErrorLog (self, eventLine) :
		'''In a perfect world there would be no errors, but alas there are and
		we need to put them in a special file that can be accessed after the
		process is run.  The error file from the previous session is deleted at
		the begining of each new run.'''

		# Because we want to read errors from top to bottom, we don't pre append
		# them to the error log file.
		if not os.path.isfile(self._projErrorLogFile) :
			writeObject = codecs.open(self._projErrorLogFile, "w", encoding='utf_8')
		else :
			writeObject = codecs.open(self._projErrorLogFile, "a", encoding='utf_8')

		# Write and close
		writeObject.write(eventLine + '\n')
		writeObject.close()

		return


	def trimLog (self, projLogLineLimit = 1000) :
		'''Trim the system log file.  This will take an existing log file and
		trim it to the amount specified in the system file.'''

		# Of course this isn't needed if there isn't even a log file
		if os.path.isfile(self._projLogFile) :

			# Change this to an int()
			projLogLineLimit = int(projLogLineLimit)

			# Read in the existing log file
			readObject = codecs.open(self._projLogFile, "r", encoding='utf_8')
			lines = readObject.readlines()
			readObject.close()

			# Process only if we have enough lines
			if len(lines) > projLogLineLimit :

				writeObject = codecs.open(self._projLogFile, "w", encoding='utf_8')
				lineCount = 0
				for line in lines :
					if projLogLineLimit > lineCount :
						writeObject.write(line)
						lineCount +=1

				writeObject.close()

		return


	def preAppend (self, line, file_name) :
		'''Got the following code out of a Python forum.  This will pre-append a
		line to the begining of a file.'''

		fobj = fileinput.FileInput(file_name, inplace=1)
		first_line = fobj.readline()
		sys.stdout.write("%s\n%s" % (line, first_line))
		for line in fobj:
			sys.stdout.write("%s" % line)

		fobj.close()




