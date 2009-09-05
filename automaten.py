#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging, logging.config
import os,sys
from automatenausgabe import *

class AutomatException(Exception):
	"""
	>>> x = AutomatException('ohje', frozenset(['achNein']), 'xXx')
	>>> x
	AutomatException()
	>>> print x
	'ohje' xXx [achNein]
	"""
	def __init__(self, value, validSet=frozenset(), explanation=''):
		self.value = value
		self.validSet = validSet
		self.explanation = explanation
	def __str__(self):
		# Alte Exception gab nur value zurueck, deswegen: HACK.
		if len(self.value) > 10:
			return repr(self.value)
		validSetText = ''
		if len(self.validSet):
			validSetText = '[%s]' % ','.join(sorted(self.validSet))
		return "%s %s %s" % (repr(self.value), self.explanation, validSetText)

class NotInSigmaException(AutomatException):
	def __init__(self, value, validSet=frozenset()):
		AutomatException.__init__(self, value, validSet, 'ist nicht Teil der Menge der Eingabezeichen')

class NoSuchStateException(AutomatException):
	def __init__(self, value, validSet=frozenset()):
		AutomatException.__init__(self, value, validSet, 'ist nicht Teil der Menge der moeglichen Zustaende')

class NoAcceptingStateException(AutomatException):
	def __init__(self, value, validSet=frozenset()):
		AutomatException.__init__(self, value, validSet, 'ist nicht Teil der Menge der moeglichen Endzustaende')

class NoRuleForStateException(AutomatException):
	def __init__(self, value, statesWithRules=list()):
		AutomatException.__init__(self, value, frozenset(statesWithRules), 'hat keine definierten Regeln.')

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
		NotInSigmaException: 'b' ist nicht Teil der Menge der Eingabezeichen 
		>>> mini._delta('zX', 'a')
		Traceback (most recent call last):
		...
		NoSuchStateException: 'zX' ist nicht Teil der Menge der moeglichen Zustaende 

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
		NotInSigmaException: 'b' ist nicht Teil der Menge der Eingabezeichen 

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
		NotInSigmaException: 'a' ist nicht Teil der Menge der Eingabezeichen 

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
		"""
		>>> mini = NichtDeterministischerAutomat('s0', 's0', 's0', '0 1', { 's0' : {'0' : 's0'}})
		>>> mini._toList('')
		['']
		>>> mini._toList('a b c d')
		['a', 'b', 'c', 'd']
		>>> mini._toList(['a', 'b', 'c', 'd'])
		['a', 'b', 'c', 'd']
		"""
		if isinstance(what, basestring):
			return what.split(' ')
		elif isinstance(what, list):
			return what
		else:
			raise ValueError("Cannot convert '%s' to list()" % str(what))

	def _toFrozenSet(self, what):
		"""
		>>> mini = NichtDeterministischerAutomat('s0', 's0', 's0', '0 1', { 's0' : {'0' : 's0'}})
		>>> mini._toFrozenSet('a c b')
		frozenset(['a', 'c', 'b'])
		>>> mini._toFrozenSet('z1')
		frozenset(['z1'])
		"""
		return frozenset(self._toList(what))

	def _fixDeltaMapping(self, delta):
		"""
		Sorgt dafuer, dass das zurueckgegebene dictionary die folgende Struktur hat:
			{
				Zustand : {
							<Zeichen-Set> : <Zustand-Set>
							}
			}
		
		>>> delta = { 's0' : {'0' : 's0'} }
		>>> delta
		{'s0': {'0': 's0'}}
		>>> mini = NichtDeterministischerAutomat('s0', 's0', 's0', '0 1', delta)
		>>> deltaNeu = mini._fixDeltaMapping(delta)
		>>> deltaNeu
		{'s0': {frozenset(['0']): frozenset(['s0'])}}
		>>> oDelta = { 'a' : {'a b c' : 'd e f'} }
		>>> nDelta = mini._fixDeltaMapping(oDelta)
		>>> nDelta
		{'a': {frozenset(['a', 'c', 'b']): frozenset(['e', 'd', 'f'])}}
		"""
		deltaNeu = dict()
		for zustand in delta.keys():
			deltaNeu[zustand] = dict()
			for zeichen in delta[zustand]:
				ziel = delta[zustand][zeichen]
				sZeichen = self._toFrozenSet(zeichen)
				sZiel = self._toFrozenSet(ziel)
				deltaNeu[zustand][sZeichen] = sZiel
		return deltaNeu
		
	def __init__(self, S, s0, F, Sigma, delta, name="EinAutomat", beschreibung='', testWords=None):
		"""
		>>> mini = NichtDeterministischerAutomat('s0 s1 s2 s3', 's0', 's3', '0 1', {'s0' : {'0' : ['s0', 's1'], '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}})
		>>> mini._delta('s0', '0')
		frozenset(['s1', 's0'])
		>>> mini._delta('s0', 'b')
		Traceback (most recent call last):
		...
		NotInSigmaException: 'b' ist nicht Teil der Menge der Eingabezeichen [0,1]
		>>> mini._delta('zX', '0')
		Traceback (most recent call last):
		...
		NoSuchStateException: 'zX' ist nicht Teil der Menge der moeglichen Zustaende [s0,s1,s2,s3]

		@param S: Endliche Menge der moeglichen Zustaende
		@param s0: Anfangszustaende
		@param F: Menge der Endzustaende
		@param Sigma: Endliche Menge der Eingabezeichen
		@param delta: Zustands-Ueberfuehrungstabelle/dict()
		@param name: Bezeichner fuer den Automaten
		@param beschreibung: Beschreibung fuer den Automaten
		"""
		self._initLogging()
		
		# Umwandeln von Listen und Stringinhalte (whitespace-getrennt) in frozenset-Mengen
		S = self._toFrozenSet(S)
		F = self._toFrozenSet(F)
		Sigma = self._toFrozenSet(Sigma)
		s0 = self._toFrozenSet(s0)
		
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
		self.delta = self._fixDeltaMapping(delta)

		self.name = name
		self.ZustandIndex = dict()
		self.Zustand = self.s0
		self.testWords = testWords
		self.beschreibung = beschreibung
		self.reset()

	def istDEA(self):
		"""
		Ein DEA zeichnet sich dadurch aus, dass
			* s0 ein einzelner Anfangszustand und
			* jedem Paar(s, a) aus [S kreuz Sigma] ein einzelner Funktionswert (Zustand) 
		zugeordnet ist.
		
		>>> mini = NichtDeterministischerAutomat('s0 s1 s2 s3', 's0', 's3', '0 1', {'s0' : {'0' : 's0 s1', '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}})
		>>> mini.istDEA()
		False
		>>> m2 = NichtDeterministischerAutomat('s0 s1 s2 s3', 's0', 's3', '0 1', {'s0' : {'0' : 's0', '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}})
		>>> m2.istDEA()
		True
		"""
		if (len(self.s0) != 1):
			return False
		for zustand in self.delta:
			for zeichen in self.delta[zustand]:
				if len(self.delta[zustand][zeichen]) != 1:
					return False
		return True
	
	def istDeltaVollstaendig(self):
		"""
		>>> mini = NichtDeterministischerAutomat('s0 s1 s2 s3', 's0', 's3', '0 1', {'s0' : {'0' : 's0 s1', '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}})
		>>> mini.istDeltaVollstaendig()
		False
		>>> m2 = NichtDeterministischerAutomat('s0 s1 s2 s3', 's0', 's3', '0 1', {'s0' : {'0' : 's0 s1', '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}, 's3' : {}})
		>>> m2.istDeltaVollstaendig()
		True
		"""
		return len(self.F.difference(self.delta.keys())) == 0

	def testWorteGenerator(self, length=3, Sigma=None):
		"""
		Generiert Testworte der gewuenschten Laenge bestehend aus dem Alphabet des Automaten.
		Optional kann Sigma angegeben werden
		
		>>> mini = NichtDeterministischerAutomat('s0 s1 s2 s3', 's0', 's3', '0 1', {'s0' : {'0' : 's0 s1', '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}})
		>>> mini.testWorteGenerator(length=1)
		['1', '0', '11', '01', '10', '00']
		>>> mini.testWorteGenerator(Sigma=['a', 'b'], length=1)
		['a', 'b', 'aa', 'ba', 'ab', 'bb']

		@param length: Maximal-Laenge der generierten Worte
		@param Sigma: (optional) Alternativ-Alphabet
		@return: Liste mit Testworten
		"""
		if Sigma == None:
			Sigma = self.Sigma
		worte = list(Sigma)
		SigmaTmp = Sigma
		for i in xrange(length):
			SigmaTmp = [ a + b for b in Sigma for a in SigmaTmp]
			worte += SigmaTmp
		return worte

	def _delta(self, Zustand, Zeichen):
		"""
		Zustands-Ueberfuehrungsfunktion

		>>> mini = NichtDeterministischerAutomat('s0 s1 s2 s3', 's0', 's3', '0 1', {'s0' : {'0' : 's0 s1', '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}})
		>>> mini.S
		frozenset(['s3', 's2', 's1', 's0'])
		>>> mini.F
		frozenset(['s3'])
		>>> mini.Sigma
		frozenset(['1', '0'])
		>>> mini._delta(['s0', 's1'], 1)
		frozenset(['s2', 's0'])
		>>> mini._delta(['s0', 's1'], 1)
		frozenset(['s2', 's0'])
		>>> mini._delta(['s0', 's1', 's3'], 1)
		Traceback (most recent call last):
		...
		NoRuleForStateException: 's3' hat keine definierten Regeln. [s0,s1,s2]
		>>> mini._delta('s0', '1')
		frozenset(['s0'])

		@param Zustand: Quell-Zustand (falls kein list()-Objekt: wird mittels str() umgewandelt)
		@param Zeichen: einzulesendes Zeichen (wird mittels str() umgewandelt)
		@return: Menge der erreichten Zustaende oder leere Menge
		"""
		# Sicherstellen, dass Zeichen ein String ist
		Zeichen = str(Zeichen)
		
		# Pruefen, ob das zu lesende Zeichen ueberhaupt Teil der Menge der Eingabezeichen ist
		if Zeichen not in self.Sigma:
			self.log.debug("'%s' nicht Teil des Alphabets (%s)" % (Zeichen, ','.join(sorted(self.Sigma))))
			raise NotInSigmaException(Zeichen, self.Sigma)

		# Sonderbehandlung: Zustand kann auch eine Liste von Zustaenden sein
		if isinstance(Zustand, list):
			ziele = frozenset()
			for item in Zustand:
				ziele = ziele.union(self._delta(item, Zeichen))
			return ziele
		elif isinstance(Zustand, basestring):
			# Ansonsten: Zustand in frozenset verwandeln
			Zustand = frozenset([str(Zustand)])
		elif isinstance(Zustand, frozenset):
			#self.log.warning("Zustand: schon frozenset %s" % repr(Zustand))
			pass
		else:
			self.log.warning("Zustand: nicht unterstuetzter Datentyp %s" % repr(Zustand))
			import sys
			sys.exit(99)

		# Da Namen der Zustaende Strings sind, brauchen wir den Zustand auch als String
		stringZustand = list(Zustand)[0]

		# Pruefen, ob der zu behandelnde Zustand ueberhaupt Teil der Zustandsmenge
		if not Zustand.issubset(self.S):
			#self.log.debug("Zustand '%s' nicht in der Zustandsmenge '%s' ?" % (Zustand, ','.join(sorted(self.S))))
			raise NoSuchStateException(stringZustand, self.S)

		# Keine Regeln fuer Zustand definiert
		if not Zustand.issubset(self.delta):
			raise NoRuleForStateException(stringZustand, self.delta.keys())

		for keyObject in self.delta[stringZustand].keys():
			if Zeichen in keyObject:
				return self.delta[stringZustand][keyObject]
			
		self.log.warning("Kein Folgezustand fuer '%s' von '%s'." % (Zeichen, Zustand))
		return frozenset([])

	def check(self, Wort, doRaise=False):
		"""
		Prüft, ob das gegebene Wort zur akzeptierten Sprache des Automaten gehoert
		>>> mini = NichtDeterministischerAutomat('z0 z1', 'z0', 'z1', 'a', {'z0' : {'a' : 'z1'}, 'z1' : {'a' : 'z1'}})
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
		NotInSigmaException: 'b' ist nicht Teil der Menge der Eingabezeichen [a]

		>>> mini2 = NichtDeterministischerAutomat('s0 s1 s2 s3', 's0', 's3', ['0', '1'], { 's0' : { "0" : 's1', "1" : 's0'}, 's1' : { '0' : 's2', '1' : 's0'}, 's2' : { '0' : 's2', '1' : 's3'}, 's3' : { '0' : 's3', '1' : 's3'} })
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
		NoAcceptingStateException: frozenset(['s0']) ist nicht Teil der Menge der moeglichen Endzustaende [s3]
		>>> mini2.check("a", True)
		Traceback (most recent call last):
		...
		NotInSigmaException: 'a' ist nicht Teil der Menge der Eingabezeichen [0,1]

		>>> mini3 = NichtDeterministischerAutomat('z0 z1', 'z0', 'z1', ['a', 'b'], {'z0' : {'a' : 'z1'}, 'z1' : {'a' : 'z1'}})
		>>> print mini3.Sigma
		frozenset(['a', 'b'])
		>>> mini3.check("ab", True)
		Traceback (most recent call last):
		...
		NoAcceptingStateException: frozenset([]) ist nicht Teil der Menge der moeglichen Endzustaende [z0,z1]

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
				if len(self.Zustand) == 0:
					self.log.debug("Kein Ziel-Zustand fuer Zeichen '%s' von Zustand '%s' definiert" % (Zeichen, altZustand))
					if doRaise:
						raise NoAcceptingStateException(self.Zustand, self.S)
					return False
			except NotInSigmaException, e:
				self.log.debug("Zeichen '%s' nicht Teil des Alphabets." %  Zeichen)
				if doRaise:
					raise
				return False
			except NoRuleForStateException, e:
				self.log.debug("Zeichen '%s' nicht Teil des Alphabets." %  Zeichen)
				if doRaise:
					raise
				return False

		if not self.Zustand.issubset(self.F):
			self.log.debug("Kein Endzustand erreicht.")
			if doRaise:
				raise NoAcceptingStateException(self.Zustand, self.F)
			return False
		return True

if __name__ == '__main__':
	test()
