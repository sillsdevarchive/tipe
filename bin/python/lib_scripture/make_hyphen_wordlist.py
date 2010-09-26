#!/usr/bin/python2
# -*- coding: utf_8 -*-
# version: 20090120
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# Generate a list of hyphenated words based on supplied
# suffixes and prefixes and a word list that are part of
# the source text. This script will look for these files
# in the specified location and process them. The results
# are a hyphenated word list in the Hyphenation folder which
# can be used by another process to create the actual file
# TeX will use for hyphenation on the text.


# History:
# 20090130 - djd - Initial draft
# 20090327 - djd - Draft is working but issues remain over
#        output discrepancies. This needs to be revisited
#        later after some other larger issues are settled.
# 20090520 - djd - Massive changes made by TimE to add
#        regexp rules for making breaks and he also restructured
#        the file too.
# 20090831 - djd - Fixed file pointer config setting that was wrong
# 20090831 - te - Fixed bug that prevented spurious hyphens from getting
#        through not allowing strings to be analyzed


#############################################################
######################### Shell Class #######################
#############################################################

import codecs, csv, sys, operator
from collections import defaultdict
from operator import itemgetter

# Import supporting local classes
from encoding_manager import *
from itertools import *
import tools
from tools import normalize


class MakeHyphenWordlist (object) :
	_hyphens_re = re.compile(u'\u002D|\u00AD|\u2010') # Don't include U+2011 so we don't break on it.

	def __init__(self, log_manager):
		self._log_manager = log_manager
		self._hyphenations={}
		self._hyphen = set()
		self._hyphenCounts = {}
		self._wordlistReport = set()

	def main (self) :
		pathHyphenation = os.getcwd() + "/" + tools.pubInfoObject['Paths']['PATH_HYPHENATION']
		sourceHyphenatedWordsFile = pathHyphenation + '/' + tools.pubInfoObject['Files']['FILE_HYCUSTOM']
		sourcePrefixListFile = pathHyphenation + '/' + tools.pubInfoObject['Files']['FILE_HYPREFIX']
		sourceSuffixListFile = pathHyphenation + '/' + tools.pubInfoObject['Files']['FILE_HYSUFFIX']
		reportNonHypenatedWords = pathHyphenation + '/' + tools.pubInfoObject['Files']['FILE_HYNOT']
		sourceMasterWordsFile = self._log_manager._currentInput
		newHyphenationFile = self._log_manager._currentOutput
		hyphenBreakRules = self._log_manager._settings['Format']['Hyphenation']['hyphenBreakRules'].decode('utf_8').decode('unicode_escape')
		if hyphenBreakRules == "" :
			self._log_manager.log("WARN", "There were no hyphenation break rules found in your project.conf file. This may be ok but keep in mind that if there were no other hyphenated words manually listed there will be no output to the file this script is creating. Sorry, I cannot read your mind.")

		# Load the master wordlist.
		try:
			self.loadWordlistReport(sourceMasterWordsFile)
		except IOError, e:
			self._log_manager.log("ERRR", "Hyphenation auto-generation failed. Word list not read, due to: " + str(e))
			return

		# load the source user custom hyphenation file is there is one.
		self.loadPreHyphenatedWordList(sourceHyphenatedWordsFile)

		# Pass 1: This part is all about auto-generating hyphenated words. This can
		# be done a number of ways.
		self.generatePrefixSuffixHyphenation(sourceMasterWordsFile, sourcePrefixListFile, sourceSuffixListFile)
		# Pass 2: Use the provided regexp to find automatic break points.
		self.generateRuleBrokenHyphenations(hyphenBreakRules)

		#write out the hyphenation list
		self.writeHyphenationList(newHyphenationFile)

		#Debuging, write out words that could not be hyphenated
		self.writeFailedWords(reportNonHypenatedWords)


	def loadPreHyphenatedWordList(self,filepath):
		# Load the exsiting hyphen words source list if one is in the source folder.
		# We will fill a dictionary here that was created above with the defaultdict
		# module. That will be used for the final output when we're done.

		# A problem can occur here where stray word-final punctuation or other
		# non-word-forming characters can get included in the word string.
		# It would be possible to remove them here but it would not be easy.
		# After much thought I have decided to rely on the translator to
		# provide clean data and any problems found will need to be edited
		# by hand to correct them.
		hyphens = self.wordListFromFile(filepath)
		words = map(self.cleanWord, hyphens)
		self._hyphenations.update(filter(lambda wh: wh[0] in self._wordlistReport or wh[1] in self._wordlistReport, zip(words, hyphens)))
		self._wordlistReport.difference_update(words)
		self._wordlistReport.difference_update(hyphens)
		self.logHyphenCount("load " + filepath)


	def loadWordlistReport(self,sourceMasterWordsFile):
		# Read the sourceMasterWordsFile - Using utf_8_sig because
		# the source might be coming from outside the system and we
		# may need to be able to handle a BOM. Also, in the process
		# of bringing in our wordlist we will normalize it to NFD.
		f = open(sourceMasterWordsFile)
		wordlist_csv = csv.reader(f, dialect=csv.excel)
		for w in normalize(w.decode('utf_8_sig') for w,c in wordlist_csv):
			# We are not always sure what to do with words that already
			# contain a hyphen character. However we cannot just let them
			# disapear so we will capture these specific words in the log
			# file where they can be dealt with.
			if self._hyphens_re.search(w):
				self._log_manager.log("INFO", "Input candidate word already hyphenated: " + w)
			self._wordlistReport.add(w)
		self._log_manager.log("INFO", sourceMasterWordsFile + " loaded, found " + str(len(self._wordlistReport)) + " words.")


	def generatePrefixSuffixHyphenation(self,sourceMasterWordsFile,sourcePrefixListFile,suffixListPath):
		'''Generate hyphenated words based on the prefix and suffix lists.'''

		# Now we will look for and load all the peripheral files and report
		# on what we found.
		# Are there prefixList or suffixList to process?
		prefixList = map(self.cleanWord, self.wordListFromFile(sourcePrefixListFile))
		suffixList = map(self.cleanWord, self.wordListFromFile(suffixListPath))

		# Test to see if we have enough of the above objects to auto-generate some hyphenated words.
		if not (prefixList or suffixList):
			self._log_manager.log("DBUG", "Could not auto-generate hyphenated words, based on prefix or suffix. One or both of those files were not found.")
			return

		# If we made it this far the actual process can begin

		# Apply prefixes and suffixes to word list and create
		# new hyphenated words, add them to hyphenCandidates{}

		# Build a regex for both prefixes and suffixes
		prefixList.sort(key=len,reverse=True)
		prefixList.sort(reverse=True)
		suffixList.sort(key=len,reverse=True)
		suffixList.sort(reverse=True)

		# Make the Regex
		prefixTest = re.compile("^(?ui)(" + ('|'.join(prefixList)) + ")(?=-?\w\W{0,6}\w)")
		suffixTest = re.compile("(?ui)(?<=..)(" + ('|'.join(suffixList)) + ")$")

		for word in frozenset(self._wordlistReport):
			m = suffixTest.sub(r"-\1", prefixTest.sub(r"\1-", word))
			if '-' in m and m[-1] != '-' and not self._hyphenations.has_key(word):
				self._hyphenations[word] = m
				self._wordlistReport.discard(word)
		self.logHyphenCount("prefix/suffix hyphenation")


	def generateRuleBrokenHyphenations(self, hyphenBreakRules):
		'''Generate hyphenated words based on a regexp rule supplied by
			the conf file.'''

		if hyphenBreakRules:
			try:
				hyphenBreaks = re.compile(hyphenBreakRules)
			except:
				self._log_manager.log("ERRR", "Hyphenation auto-generation failed. Could not compile hyphen break rule:" + str(sys.exc_info()[1]))
				raise
			for word in frozenset(self._wordlistReport):
				hyphenation = word
				for off,match in enumerate(hyphenBreaks.finditer(word)):
					hyphenation = hyphenation[:match.end()+off] + '-' + hyphenation[match.end()+off:]
				hyphenation = hyphenation.strip('-')
				if hyphenation != word and word not in self._hyphenations:
					self._hyphenations[word] = hyphenation
					self._wordlistReport.discard(word)
			self.logHyphenCount("Rules based hyphenation")


	def writeHyphenationList(self, newHyphenationFile):
		# Output the values sorted by key to the newHyphenationFile (simple word list)
		# Turn the hyphenList to a list and sort it on the key.
		double_hyphens = re.compile(u'-{2,}')
		hyphenkeys = list(set(self._hyphenations.itervalues()))
		hyphenkeys.sort()
		f = codecs.open(newHyphenationFile, "w", encoding='utf_8')
		f.writelines(double_hyphens.sub('-',v).strip('-') +'\n' for v in hyphenkeys)
		f.close()
		self._log_manager.log('DBUG', "Total hyphenations added = %d" % sum(self._hyphenCounts.itervalues()))
		self._log_manager.log("DBUG", "Hyphenated word list created, made " + str(len(hyphenkeys)) + " words.")

	def writeFailedWords(self,path):
		f = codecs.open(path, "w", encoding='utf_8')
		words = list(w+'\n' for w in self._wordlistReport)
		words.sort(key=len)
		f.writelines(words)
		f.close()


	def logHyphenCount(self, phase):
		last = sum(self._hyphenCounts.itervalues())
		n = sum(h.count('-') for h in self._hyphenations.itervalues()) - last
		self._hyphenCounts[phase] = n
		self._log_manager.log('INFO','phase %s found %d hyphenations.' % (phase,n))
		self._log_manager.log('INFO','phase %s left %d words un-hyphenated.' % (phase,len(self._wordlistReport)))

	@staticmethod
	def cleanWord(word):
		return MakeHyphenWordlist._hyphens_re.sub('', word)


	def wordListFromFile(self, file_path):
		word_list = []
		if os.path.isfile(file_path) :

			try :
				# We don't know exactly what the encoding of this file is. It is probably
				# Unicode, more than likely utf_8. As such, we'll bring in the text raw,
				# then decode to Unicode. That should keep things working. We may need to
				# adjust this at some point to utf_8_sig to be able to deal with BOMs.
				# We also normalize the wordlist to NFD as we bring it in.
				f = codecs.open(file_path, 'rb',encoding='utf_8_sig')
				sourceHyphenListObject = normalize(f)

				# Push it into a list w/o line endings
				word_list = filter(bool,imap(operator.methodcaller('strip'), sourceHyphenListObject))
				self._log_manager.log("INFO", file_path + " loaded, found " + str(len(word_list)) + " words.")

			except UnicodeDecodeError, e :
				self._log_manager.log("ERRR", file_path + ": " + str(e))
				return []

			finally :
				f.close()

		else :
			self._log_manager.log("DBUG", file_path + " not found")

		return word_list



# This starts the whole process going
def doIt (log_manager) :

	thisModule = MakeHyphenWordlist(log_manager)
	return thisModule.main()
