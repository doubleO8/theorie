#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging, logging.config
import os,sys
from automatenausgabe import *

class NotInSigmaException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class NoSuchStateException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class NoAcceptingStateException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

def test():
	"""
	doctest (unit testing)
	"""
	import doctest
	failed, total = doctest.testmod()
	print("doctest: %d/%d tests failed." % (failed, total))

class Automat(OAsciiAutomat, OLaTeXAutomat, ODotAutomat):
	def _initLogging(self):
		self.log = logging.getLogger("x")
		if len(self.log.handlers) == 0:
			lhandler = logging.StreamHandler()
			lformatter = logging.Formatter('%(asctime)s %(levelname)s:  %(message)s')
			lhandler.setFormatter(lformatter)
			self.log.addHandler(lhandler)
			self.log.setLevel(logging.DEBUG)
	
	def _toList(self, what):
		if isinstance(what, basestring):
			return what.split()
		elif isinstance(what, list):
			return what
		else:
			raise ValueError("Cannot convert '%s' to list()" % str(what))

	def __init__(self, S, s0, F, Sigma, delta, name="EinAutomat", beschreibung='', testWords=None):
		"""
		>>> mini = Automat('z0 z1', 'z0', 'z1', 'a', {'z0' : {'a' : 'z1'}})
		>>> mini._delta('z0', 'a') == 'z1'
		True
		>>> mini._delta('z0', 'b')
		Traceback (most recent call last):
		...
		NotInSigmaException: 'b'
		>>> mini._delta('zX', 'a')
		Traceback (most recent call last):
		...
		NoSuchStateException: 'zX'

		@param S: Endliche Menge der moeglichen Zustaende
		@param s0: Anfangszustand
		@param F: Menge der Endzustaende
		@param Sigma: Endliche Menge der Eingabezeichen
		@param delta: Zustands-Ueberfuehrungstabelle/dict()
		@param name: Bezeichner fuer den Automaten
		@param beschreibung: Beschreibung fuer den Automaten
		"""
		self._initLogging()
		
		S = self._toList(S)
		F = self._toList(F)
		Sigma = self._toList(Sigma)
		
		if len(S) == 0:
			raise ValueError('Die "endliche Menge der möglichen Zustände" S des Automaten ist leer')
		if len(F) == 0:
			raise ValueError('Die "Menge der Endzustände" F ist leer')
		if len(Sigma) == 0:
			raise ValueError('Die "endliche Menge der Eingabezeichen, Alphabet" Σ (Sigma) ist leer')
		if len(delta) == 0:
			raise ValueError('Die "(determinierte) Zustands-Überführungsfunktion" δ (delta) ist leer')
		
		self.S = S
		self.s0 = s0
		self.F = F
		self.Sigma = Sigma
		self.delta = delta
		self.deltaVollstaendig = None
		self.name = name
		self.ZustandIndex = dict()
		self.Zustand = self.s0
		self.testWords = testWords
		self.beschreibung = beschreibung
		self.reset()

	def reset(self):
		"""
		Setzt den Automaten zurueck
		"""
		self.Zustand = self.s0

	def _delta(self, Zustand, Zeichen):
		"""
		Zustands-Ueberfuehrungsfunktion

		@param Zustand: Quell-Zustand
		@param Zeichen: einzulesendes Zeichen
		@return: Erreichter Zustand oder None
		"""
		Zeichen = str(Zeichen)

		if not Zeichen in self.Sigma:
			self.log.debug("'%s' nicht Teil des Alphabets" % Zeichen)
			raise NotInSigmaException(Zeichen)

		if not self.delta.has_key(Zustand):
			self.log.debug("Kein Zustand '%s' ?" % Zustand)
			raise NoSuchStateException(Zustand)

		for keyObject in self.delta[Zustand].keys():
			if isinstance(keyObject, tuple):
				if Zeichen in keyObject:
					return self.delta[Zustand][keyObject]
			elif Zeichen == keyObject:
				return self.delta[Zustand][keyObject]
			
		self.log.debug("Kein Folgezustand fuer '%s' von '%s' ?" % (Zeichen, Zustand))
		return None

	def check(self, Wort, doRaise=False):
		"""
		Prüft, ob das gegebene Wort zur akzeptierten Sprache des Automaten gehoert
		>>> mini = Automat('z0 z1', 'z0', 'z1', 'a', {'z0' : {'a' : 'z1'}, 'z1' : {'a' : 'z1'}})
		>>> mini.check("a")
		True
		>>> mini.check("b")
		False
		>>> mini.check("aaaa")
		True
		>>> mini.check("aba")
		False
		>>> mini.check("aba", True)
		Traceback (most recent call last):
		...
		NotInSigmaException: 'b'

		>>> mini2 = Automat('s0 s1 s2 s3', 's0', 's3', ['0', '1'], { 's0' : { "0" : 's1', "1" : 's0'}, 's1' : { '0' : 's2', '1' : 's0'}, 's2' : { '0' : 's2', '1' : 's3'}, 's3' : { '0' : 's3', '1' : 's3'} })
		>>> mini2.check("10011")
		True
		>>> mini2.check("a")
		False
		>>> mini2.check("111111111111")
		False
		>>> mini2.check("001")
		True
		>>> mini2.check("111111111111", True)
		Traceback (most recent call last):
		...
		NoAcceptingStateException: 'Kein Endzustand erreicht'
		>>> mini2.check("a", True)
		Traceback (most recent call last):
		...
		NotInSigmaException: 'a'

		>>> mini3 = Automat('z0 z1', 'z0', 'z1', ['a', 'b'], {'z0' : {'a' : 'z1'}, 'z1' : {'a' : 'z1'}})
		>>> print mini3.Sigma
		['a', 'b']
		>>> mini3.check("ab", True)
		Traceback (most recent call last):
		...
		NoAcceptingStateException: 'Kein Endzustand erreicht'

		@param Wort: Das zu pruefende Wort
		@return: True oder False
		"""
		self.reset()
		self.log.debug("Teste Wort '%s'" % Wort)
		Wort = str(Wort)
		for Zeichen in Wort:
			try:
				altZustand = self.Zustand
				self.Zustand = self._delta(self.Zustand, Zeichen)
				if self.Zustand == None:
					self.log.debug("Kein Ziel-Zustand fuer Zeichen '%s' von Zustand '%s' definiert" % (Zeichen, altZustand))
					if doRaise:
						raise NoAcceptingStateException("Kein Endzustand erreicht")
					return False
			except NotInSigmaException, e:
				self.log.debug("Zeichen '%s' nicht Teil des Alphabets." %  Zeichen)
				if doRaise:
					raise
				return False

		if self.Zustand not in self.F:
			self.log.debug("Kein Endzustand erreicht.")
			if doRaise:
				raise NoAcceptingStateException("Kein Endzustand erreicht")
			return False
		return True

	def checkWords(self, words, silence=False):
		resultset = list()
		words = self._toList(words)
		for word in words:
			result = 'OUCH'
			successful = False
			try:
				self.check(word, True)
				result = 'Akzeptiert.'
				successful = True
			except NotInSigmaException, e:
				result = "'%s' ist nicht im Alphabet." % e.value
			except NoSuchStateException, e:
				result = "Zustand '%s' ist nicht in Sigma." % e.value
			except NoAcceptingStateException, e:
				result = "Kein finaler Zustand erreicht."
			resultset.append((word, successful, result))
			if not silence:
				self.log.info("[%6s] %s : %s" % ((successful and "SUCCESS" or "FAILED"), word, result))
		return resultset

	def addFehlerzustand(self, sF = 'sF'):
		if not self.delta.has_key(sF):
			self.delta[sF] = dict()
			for zeichen in self.Sigma:
				self.delta[sF][zeichen] = sF
			return sF
		else:
			raise ValueError("Fehlerzustand '%s' gibt es bereits ?! " % sF)

	def _deltaVollstaendig(self):
		for zustand in self.S:
			for zeichen in self.Sigma:
				if self._delta(zustand, zeichen) == None:
					self.deltaVollstaendig = False
					return False
		self.deltaVollstaendig = True
		return self.deltaVollstaendig
	
	def isDeltaVollstaendig(self):
		if self.deltaVollstaendig == None:
			self._deltaVollstaendig()
		return self.deltaVollstaendig

	def machDeltaVollstaendig(self):
		if self.isDeltaVollstaendig():
			return
		sF = self.addFehlerzustand()
		for zustand in self.S:
			for zeichen in self.Sigma:
				if self._delta(zustand, zeichen) == None:
					self.delta[zustand][zeichen] = sF
		self.deltaVollstaendig = True

	def __str__(self):
		s = "Deterministischer Automat '%s'\n%s\n" % (self.name, "=" * 80)
		s += "Anfangszustand :\n %s\n" % self.s0
		s += "Endliche Menge der möglichen Zustände S :\n {%s}\n" % ', '.join(self.S)
		s += "Menge der Endzustände F :\n {%s}\n" % ', '.join(self.F)
		s += "Endliche Menge der Eingabezeichen Σ :\n {%s}\n" % ', '.join(self.Sigma)
		s += "Überführungsfunktion:\n"
		s += self._getAsciiArtDeltaTable()
		s += "%80s\n" % ('(' + (self.isDeltaVollstaendig() and 'vollständig' or 'partiell') + ')' )
		s += "%s\n\n" % ("=" * 80)
		return s

class NichtDeterministischerAutomat(Automat):
	def _toList(self, what):
		if isinstance(what, basestring):
			return what.split()
		elif isinstance(what, list):
			return what
		else:
			raise ValueError("Cannot convert '%s' to list()" % str(what))

	def _toTuple(self, what):
		"""
		>>> mini = NichtDeterministischerAutomat('s0', 's0', 's0', '0 1', { 's0' : {'0' : 's0'}})
		>>> mini._toTuple('a c b')
		('a', 'b', 'c')
		>>> mini._toTuple('z1')
		('z1',)
		"""
		return tuple(sorted(self._toList(what)))

	def _toSet(self, what):
		"""
		>>> mini = NichtDeterministischerAutomat('s0', 's0', 's0', '0 1', { 's0' : {'0' : 's0'}})
		>>> mini._toSet('a c b')
		set(['a', 'c', 'b'])
		>>> mini._toSet('z1')
		set(['z1'])
		"""
		return set(self._toList(what))

	def _fixDeltaMapping(self, delta):
		"""
		Sorgt dafuer, dass das delta dictionary die folgende Struktur hat:
			{
				<Zustand-Set> : {
									<Zeichen-Set> : <Zustand-Set>
									}
			}
		
		>>> delta = { 's0' : {'0' : 's0'} }
		>>> delta
		{'s0': {'0': 's0'}}
		>>> mini = NichtDeterministischerAutomat('s0', 's0', 's0', '0 1', delta)
		>>> deltaNeu = mini._fixDeltaMapping(delta)
		>>> deltaNeu
		{('s0',): {('0',): set(['s0'])}}
		"""
		deltaNeu = dict()
		for zustand in delta:
			tZustand = self._toTuple(zustand)
			deltaNeu[tZustand] = dict()
			for zeichen in delta[zustand]:
				ziel = delta[zustand][zeichen]
				tZeichen = self._toTuple(str(zeichen))
				#print("tZustand : >%s< tZeichen : >%s< ziel : >%s<" % (tZustand, tZeichen, ziel))
				deltaNeu[tZustand][tZeichen] = self._toSet(ziel)
		return deltaNeu
		
	def __init__(self, S, s0, F, Sigma, delta, name="EinAutomat", beschreibung='', testWords=None):
		"""
		>>> mini = NichtDeterministischerAutomat('s0 s1 s2 s3', 's0', 's3', '0 1', {'s0' : {'0' : ['s0', 's1'], '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}})
		>>> mini._delta('s0', '0') == ['s0', 's1']
		True
		>>> mini._delta('s0', 'b')
		Traceback (most recent call last):
		...
		NotInSigmaException: 'b'
		>>> mini._delta('zX', '0')
		Traceback (most recent call last):
		...
		NoSuchStateException: ('zX',)
		>>> mini._delta(['s0', 's1'], 1) == ['s0', 's1']
		True
		>>> mini._delta(['s0', 's1'], 1) == ['s0', 's1', 's3']
		True
		>>> mini._delta(['s0', 's1', 's3'], 1) == ['s0', 's2']
		True

		@param S: Endliche Menge der moeglichen Zustaende
		@param s0: Anfangszustaende
		@param F: Menge der Endzustaende
		@param Sigma: Endliche Menge der Eingabezeichen
		@param delta: Zustands-Ueberfuehrungstabelle/dict()
		@param name: Bezeichner fuer den Automaten
		@param beschreibung: Beschreibung fuer den Automaten
		"""
		self._initLogging()
		
		S = self._toSet(S)
		F = self._toSet(F)
		Sigma = self._toSet(Sigma)
		s0 = self._toList(s0)
		
		if len(S) == 0:
			raise ValueError('Die "endliche Menge der möglichen Zustände" S des Automaten ist leer')
		if len(s0) == 0:
			raise ValueError('Die "Menge der Anfangszustände" des Automaten ist leer')
		if len(F) == 0:
			raise ValueError('Die "Menge der Endzustände" F ist leer')
		if len(Sigma) == 0:
			raise ValueError('Die "endliche Menge der Eingabezeichen, Alphabet" Σ (Sigma) ist leer')
		if len(delta) == 0:
			raise ValueError('Die "(determinierte) Zustands-Überführungsfunktion" δ (delta) ist leer')
		
		self.S = S
		self.s0 = s0
		self.F = F
		self.Sigma = Sigma
		self.delta = delta
		self.deltaVollstaendig = None
		self.name = name
		self.ZustandIndex = dict()
		self.Zustand = self.s0
		self.testWords = testWords
		self.beschreibung = beschreibung
		self.reset()

	def _delta(self, Zustand, Zeichen):
		"""
		Zustands-Ueberfuehrungsfunktion

		@param Zustand: Quell-Zustand
		@param Zeichen: einzulesendes Zeichen
		@return: Erreichter Zustand oder None
		"""
		tZustand = self._toTuple(Zustand)
		Zeichen = str(Zeichen)

		if not Zeichen in self.Sigma:
			self.log.debug("'%s' nicht Teil des Alphabets" % Zeichen)
			raise NotInSigmaException(Zeichen)

		if len(tZustand) == 1 and not self.delta.has_key(Zustand):
			self.log.debug("Kein Zustand '%s' ?" % str(Zustand))
			raise NoSuchStateException(Zustand)

		for keyObject in self.delta[Zustand].keys():
			if Zeichen in keyObject:
				return self.delta[Zustand][keyObject]
			
		self.log.debug("Kein Folgezustand fuer '%s' von '%s' ?" % (Zeichen, Zustand))
		return None

if __name__ == '__main__':
	test()
