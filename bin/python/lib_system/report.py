#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110610
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle all things doing with reporting to the user.

# History:
# 20110610 - djd - Initial draft


###############################################################################
################################### Shell Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, sys, fileinput
from datetime import *


# Import local classes
from configure import *
configure = Configure()


class Report (object) :

	# Intitate the whole class
	def __init__(self) :

		self._basePath = os.environ.get('TIPE_BASE')
		if not self._basePath :
			self._basePath = "/usr/share/xetex-tipe"
			os.environ['TIPE_BASE'] = self._basePath

		self._debugging         = False
		self._sysConfig         = configure.getSystem()
		self._home              = os.getcwd()
		self._logFile           = self._home + '/' + self._sysConfig['System']['logFile']
		self._errorLogFile      = self._home + '/' + self._sysConfig['System']['errorLogFile']
		if self._sysConfig['System']['debugging'].lower() == 'true' :
			self._debugging     = True


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

		# Output to error log


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

	def writeToLog (self, code, msg) :
		'''Send an event to the log file. and the terminal if specified.'''

		# When are we doing this?
		date_time, secs = str(datetime.now()).split(".")

		# Build the event line
		eventLine = '\"' + date_time + '\", \"' + code + '\", \"' + msg

		# Do we need a log file made?
		if not os.path.isfile(self._logFile) or os.path.getsize(self._logFile) == 0 :
			writeObject = codecs.open(self._logFile, "w", encoding='utf_8')
			writeObject.write('TIPE event log file created: ' + date_time + '\n')
			writeObject.close()

		# Now log the event to the top of the file using preAppend()
		if code == 'MSG' :
			self.preAppend(eventLine, self._logFile)
			self.terminal(code + ' - ' + msg)
		elif code == 'LOG' :
			self.preAppend(eventLine, self._logFile)
			if self._debugging :
				self.terminal(code + ' - ' + msg)
		elif code == 'WRN' :
			self.preAppend(eventLine, self._logFile)
			self.terminal(code + ' - ' + msg)
			if self._debugging :
				self.writeToErrorLog(eventLine)
		elif code == 'ERR' :
			self.preAppend(eventLine, self._logFile)
			self.writeToErrorLog(eventLine)
			self.terminal(code + ' - ' + msg)
		else :
			self.preAppend(eventLine, self._logFile)
			self.terminal('report.writeToLog: WARNING! log code: ' + code + ' not recognized. BTW, the message is: (' + msg + ')')

		return


	def writeToErrorLog (self, eventLine) :
		'''In a perfect world there would be no errors, but alas there are and
		we need to put them in a special file that can be accessed after the
		process is run.  The error file from the previous session is deleted at
		the begining of each new run.'''

		# Because we want to read errors from top to bottom, we don't pre append
		# them to the error log file.
		if not os.path.isfile(self._errorLogFile) :
			writeObject = codecs.open(self._errorLogFile, "w", encoding='utf_8')
		else :
			writeObject = codecs.open(self._errorLogFile, "a", encoding='utf_8')

		# Write and close
		writeObject.write(eventLine)
		writeObject.close()

		return


	def trimLog (self) :
		'''Trim the system log file.  This will take an existing log file and
		trim it to the amount specified in the system file.'''

		# Of course this isn't needed if there isn't even a log file
		if os.path.isfile(self._logFile) :
			lineLimit = int(self._sysConfig['System']['logLines'])

			# Read in the existing log file
			readObject = codecs.open(self._logFile, "r", encoding='utf_8')
			lines = readObject.readlines()
			readObject.close()

			# Process only if we have enough lines
			if len(lines) > lineLimit :
				writeObject = codecs.open(self._logFile, "w", encoding='utf_8')
				lineCount = 0
				for line in lines :
					if lineLimit > lineCount :
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



