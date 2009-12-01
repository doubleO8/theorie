#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, tempfile, shutil, random, atexit, re
from subprocess import *
import logging
import automaten

def test():
	"""
	doctest (unit testing)
	"""
	import doctest
	automaten.AutomatLogger(logging.DEBUG).log
	failed, total = doctest.testmod()
	print("doctest: %d/%d tests failed." % (failed, total))

class AutomatenLeser(object):
	def _getFileContent(self, filename):
		if not os.path.isfile(filename):
			raise IOError("Datei '%s' nicht gefunden." % (filename))
		return open(filename).readlines()

	def _strippedList(self, l):
		out = list()
		for item in l:
			item = item.strip()
			if item != '' and not item.startswith("#"):
				out.append(item)
		return out

	def _teileOderJaule(self, line, description='Etwas'):
		(field, sepp, data) = line.rpartition(':')
		if field != '' and sepp != '':
			return data.split()
		else:
			self.log.error("Konnte Definition von %s nicht aus '%s' lesen." % (description, data))
		return None

	def parsePlaintext(self, lines = None, description='<Lines>'):
		if lines == None:
			lines = self.lines
		if self.filename:
			description = '<File> %s' % self.filename

		Sigma = None
		F = None
		s0 = None
		S = set()
		Sread = None
		delta = dict()
		name = 'EinAutomat'
		beschreibung = ''
		verifyWords = None
		testWords = None
		verifyRegExp = None
		failingWords = list()
		acceptedWords = list()

		#: Regular Expression, die Doppelpunkte von Whitespace um sich herum befreit
		doppelPunkt = re.compile( r'\s+:\s+')

		for line in lines:
			line = doppelPunkt.sub(':', line.lstrip(), count=1)
			if line.startswith("Sigma:"):
				if Sigma != None:
					self.log.warning("Sigma bereits definiert (%s)" % Sigma)
				Sigma = self._teileOderJaule(line, 'Sigma')
			elif line.startswith("S:"):
				if Sread != None:
					self.log.warning("Sread bereits definiert (%s)" % F)
				Sread = self._teileOderJaule(line, 'S')
			elif line.startswith("F:"):
				if F != None:
					self.log.warning("F bereits definiert (%s)" % F)
				F = self._teileOderJaule(line, 'F')
			elif line.startswith("s0:"):
				if s0 != None:
					self.log.warning("s0 bereits definiert (%s)" % s0)
				s0 = self._teileOderJaule(line, 's0')
			elif line.startswith("Name:"):
				data = self._teileOderJaule(line, 'Name')
				if data:
					name = ' '.join(data).lstrip()
			elif line.startswith("Beschreibung:"):
				data = self._teileOderJaule(line, 'Beschreibung')
				if data:
					beschreibung = ' '.join(data).lstrip()
			elif line.startswith("FailingVerifyWords:"):
				failingWords = self._teileOderJaule(line, 'Nicht akzeptierte Worte')
			elif line.startswith("AcceptedVerifyWords:"):
				acceptedWords = self._teileOderJaule(line, 'Zu akzeptierende Worte')
			elif line.startswith("TestWords:"):
				testWords = self._teileOderJaule(line, 'Testworte')
			elif line.startswith("RegularExpression:"):
				verifyRegExp = self._teileOderJaule(line, 'Regular Expression')[0]
			else:
				splatter = line.split()
				if len(splatter) != 3:
					self.log.warning("%s: [%s] Konnte Ueberfuehrungsdefinition nicht aus '%s' lesen" % (description, name, line))
				else:
					(zustand, zeichen, ziel) = splatter
					S.add(zustand)
					S.add(ziel)
					if delta.has_key(zustand):
						#self.log.debug("Zustand '%s' ist bereits in delta" % zustand)
						pass
					else:
						delta[zustand] = dict()
					dd = delta[zustand]

					if zeichen.find(',') != -1:
						#self.log.debug("Zeichen LISTE")
						zListe = zeichen.split(',')
					else:
						zListe = list([zeichen])

					for zeichen in zListe:
						if dd.has_key(zeichen):
							self.log.debug("Zustand '%s', Zeichen '%s' ist bereits in delta" % (zustand, zeichen))
						else:
							dd[zeichen] = set()
						
						dd[zeichen].add(ziel)

		if len(failingWords) + len(acceptedWords) > 0:
			verifyWords = dict()
			for fail in failingWords:
				verifyWords[fail] = False
			for accept in acceptedWords:
				verifyWords[accept] = True

		if Sread:
			Sread = set(Sread)
			self.log.debug("S=%s wird erweitert um Sread=%s" % (S, Sread))
			S = S.union(Sread)
			for zustand in Sread:
				if not delta.has_key(zustand):
					delta[zustand] = dict()
		self.log.debug("Name: '%s'" % name)
		self.log.debug("Beschreibung: '%s'" % beschreibung)
		self.log.debug("Sigma: %s" % Sigma)
		self.log.debug("S: %s" % S)
		self.log.debug("Sread: %s" % Sread)
		self.log.debug("s0: %s" % s0)
		self.log.debug("F: %s" % F)
		self.log.debug("delta: %s" % delta)
		self.log.debug("verifyWords: %s" % verifyWords)
		self.log.debug("testWords: %s" % testWords)
		self.log.debug("Regular Expression: %s" % verifyRegExp)

		return (S, s0, F, Sigma, delta, name, beschreibung, verifyWords, testWords, verifyRegExp)

	def _initLogging(self, log=None):
		if not log:
			self.log = automaten.AutomatLogger().log
		else:
			self.log = log

	def automat(self):
		(S, s0, F, Sigma, delta, name, beschreibung, verifyWords, testWords, verifyRegExp) = self.parsePlaintext()
		if automaten.EpsilonAutomat.EPSILON in Sigma:
			return automaten.EpsilonAutomat(S, s0, F, Sigma, delta, name, beschreibung, verifyWords=verifyWords, testWords=testWords, verifyRegExp=verifyRegExp)
		return automaten.NichtDeterministischerAutomat(S, s0, F, Sigma, delta, name, beschreibung, verifyWords=verifyWords, testWords=testWords, verifyRegExp=verifyRegExp)

	def __init__(self, filename=None, contentList=None, data=None, dataDelimiter="\n", log=None):
		"""
		>>> AutomatenLeser()
		Traceback (most recent call last):
		...
		ValueError: Hmm .. ohne Daten wird's schwierig.
		>>> automatenString='Sigma			: 0 1; F             :  B              ;A                  1        B;A 0 A;s0:A;AcceptedVerifyWords: 01 1;FailingVerifyWords: 0 00 10;Beschreibung:DumbAutomat;Name:DumpDumb'
		>>> L = AutomatenLeser(data=automatenString, dataDelimiter=';').automat()
		>>> print L.Sigma
		frozenset(['1', '0'])
		>>> print L.S
		frozenset(['A', 'B'])
		>>> print L.F
		frozenset(['B'])
		>>> print L.delta
		{'A': {frozenset(['1']): frozenset(['B']), frozenset(['0']): frozenset(['A'])}}
		>>> L.verify()
		True
		>>> L.name
		'DumpDumb'
		>>> L.beschreibung
		'DumbAutomat'
		"""
		self._initLogging(log)
		self.lines = list()
		self.filename = None
		content = list()
		
		if filename != None:
			self.filename = filename
			content = self._strippedList(self._getFileContent(filename))
		elif contentList != None:
			content = contentList
		elif data != None:
			content = data.split(dataDelimiter)
		else:
			raise ValueError("Hmm .. ohne Daten wird's schwierig.")

		if len(content) == 0:
			raise ValueError("content ist leer")
		else:
			self.lines = content

if __name__ == '__main__':
	test()
