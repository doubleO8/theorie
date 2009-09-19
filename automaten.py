#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging, logging.config, os, sys, re
import automatenausgabe

if 'USED_LOGLEVEL' not in dir():
	USED_LOGLEVEL = logging.INFO

class AutomatLogger(object):
	__instance = None
	
	class __implementation:
		def __init__(self, loglevel=None):
			if not loglevel:
				global USED_LOGLEVEL
				loglevel = USED_LOGLEVEL
			self._initLogging(loglevel)

		def getId(self):
			return id(self)

		def _initLogging(self, loglevel):
			self.log = logging.getLogger("automatenlogger")
			if len(self.log.handlers) == 0:
				lhandler = logging.StreamHandler()
				lformatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
				lhandler.setFormatter(lformatter)
				self.log.addHandler(lhandler)
				self.log.setLevel(loglevel)
				self.log.debug(loglevel)

	def __init__(self, loglevel=None):
		if AutomatLogger.__instance is None:
			AutomatLogger.__instance = AutomatLogger.__implementation(loglevel)
		self.__dict__['_AutomatLogger__instance'] = AutomatLogger.__instance

	def __getattr__(self, attr):
		return getattr(self.__instance, attr)

	def __setattr__(self, attr, value):
		return setattr(self.__instance, attr, value)

class AutomatException(Exception):
	"""
	>>> x = AutomatException('ohje', frozenset(['achNein']), 'xXx')
	>>> x
	AutomatException()
	>>> print x
	'ohje' xXx [achNein]
	"""
	def __init__(self, value, validSet=frozenset(), explanation='', hint=None, ableitungspfad=list()):
		self.value = value
		self.validSet = validSet
		self.explanation = explanation
		self.hint = hint
		self.ableitungspfad = ableitungspfad

	def _ableitungsPfad__str__(self, what):
		if len(what) == 0:
			return ''
		items = list()
		for item in what:
			items.append('{%s}' % ','.join(sorted(item)))
		return " Ableitung:\n %s" % '->'.join(items)

	def __str__(self):
		## Alte Exception gab nur value zurueck, deswegen: HACK.
		##if len(self.value) > 10:
		##	return repr(self.value)
		validSetText = ''
		hint = ''
		ableitungspfadText = self._ableitungsPfad__str__(self.ableitungspfad) 
		if len(self.validSet):
			validSetText = '[%s]' % ','.join(sorted(self.validSet))
		if self.hint:
			hint = '*%s* ' % self.hint.upper()
		return "%s%s %s %s%s" % (hint, repr(self.value), self.explanation, validSetText, ableitungspfadText)

class NotInSigmaException(AutomatException):
	def __init__(self, value, validSet=frozenset(), hint=None, ableitungspfad=list()):
		AutomatException.__init__(self, value, validSet, 'ist nicht Teil der Menge der Eingabezeichen', hint, ableitungspfad)

class NoSuchStateException(AutomatException):
	def __init__(self, value, validSet=frozenset(), hint=None, ableitungspfad=list()):
		AutomatException.__init__(self, value, validSet, 'ist nicht Teil der Menge der moeglichen Zustaende', hint, ableitungspfad)

class NoAcceptingStateException(AutomatException):
	def __init__(self, value, validSet=frozenset(), ableitungspfad=list()):
		AutomatException.__init__(self, value, validSet, 'ist nicht Teil der Menge der moeglichen Endzustaende', ableitungspfad)

class NoRuleForStateException(AutomatException):
	def __init__(self, value, statesWithRules=list(), ableitungspfad=list()):
		AutomatException.__init__(self, value, frozenset(statesWithRules), 'hat keine definierten Regeln.', ableitungspfad)

def test():
	"""
	doctest (unit testing)
	"""
	import doctest
	AutomatLogger(logging.DEBUG).log
	failed, total = doctest.testmod()
	print("doctest: %d/%d tests failed." % (failed, total))

class NichtDeterministischerAutomat(automatenausgabe.OAsciiAutomat, automatenausgabe.OLaTeXAutomat, automatenausgabe.ODotAutomat, automatenausgabe.OPlaintextAutomat):
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
		elif isinstance(what, tuple):
			return list(what)
		else:
			raise ValueError("Cannot convert '%s' to list()" % str(what))

	def _toFrozenSet(self, what):
		"""
		>>> mini = NichtDeterministischerAutomat('s0', 's0', 's0', '0 1', { 's0' : {'0' : 's0'}})
		>>> mini._toFrozenSet('a c b')
		frozenset(['a', 'c', 'b'])
		>>> mini._toFrozenSet('z1')
		frozenset(['z1'])
		>>> mini._toFrozenSet(set(['a', 'c', 'b']))
		frozenset(['a', 'c', 'b'])
		"""
		if isinstance(what, set):
			return frozenset(what)
		return frozenset(self._toList(what))

	def _fzString(self, what):
		"""
		String-Representation einer Menge (frozenset).
		
		>>> mini = NichtDeterministischerAutomat('s0', 's0', 's0', '0 1', { 's0' : {'0' : 's0'}})
		>>> mini._fzString(frozenset([]))
		'{}'
		>>> mini._fzString(frozenset(['a', 'c', 'b']))
		'{a,b,c}'
		
		"""
		return '{%s}' % ','.join(sorted(what))

	def _int2bin(self, value, fill=0):
		"""
		>>> A = NichtDeterministischerAutomat('z0 z1', 'z0', 'z0', '0 1', {'z0' : {'0' : 'z0', '1' : 'z1'}, 'z1' : {'0' : 'z0', '1' : 'z1'}})
		>>> b2 = A._int2bin(2)
		>>> b2
		'10'
		>>> A.check(b2)
		True
		>>> b1 = A._int2bin(1)
		>>> b1
		'1'
		>>> A.check(b1)
		False
		"""
		result = list()
		while value:
			result.append(str(value & 1))
			value >>= 1
		result.reverse()
		return ''.join(result).zfill(fill) 

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

	def _initLogging(self):
		self.log = AutomatLogger().log

	def __init__(self, S, s0, F, Sigma, delta, name="EinNDA", beschreibung='', 
				testWords=None, verifyWords=None, verifyRegExp=None):
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
		>>> mini = NichtDeterministischerAutomat('s0 s1 s2 s3', 'zY', 's3', '0 1', {'s0' : {'0' : ['s0', 's1'], '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}})
		Traceback (most recent call last):
		...
		NoSuchStateException: *STARTZUSTAND* frozenset(['zY']) ist nicht Teil der Menge der moeglichen Zustaende [s0,s1,s2,s3]
		>>> mini = NichtDeterministischerAutomat('s0 s1 s2 s3', 's0', 'zZ', '0 1', {'s0' : {'0' : ['s0', 's1'], '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}})
		Traceback (most recent call last):
		...
		NoSuchStateException: *ENDZUSTAENDE* frozenset(['zZ']) ist nicht Teil der Menge der moeglichen Zustaende [s0,s1,s2,s3]
		>>> mini = NichtDeterministischerAutomat('s0 s1 s2 s3', 's0', 's3', '0 1', {'NotInAlphabet' : {'0' : ['s0', 's1'], '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}})
		Traceback (most recent call last):
		...
		NoSuchStateException: *UEBERFUEHRUNGSFUNKTION* frozenset(['NotInAlphabet']) ist nicht Teil der Menge der moeglichen Zustaende [s0,s1,s2,s3]
		
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
		
		# Ueberpruefen I - S, s0, F, Sigma sowie delta duerfen nicht leer sein.
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
		
		# Ueberpruefen II - s0 und F muessen Untermengen von S sein
		if not s0.issubset(S):
			raise NoSuchStateException(s0, S, hint="Startzustand")
		if not F.issubset(S):
			raise NoSuchStateException(F, S, hint="Endzustaende")

		self.S = S
		self.s0 = s0
		self.F = F
		self.Sigma = Sigma
		self.delta = self._fixDeltaMapping(delta)
		self.ableitungsPfad = list()

		# Ueberpruefen III - das delta Ueberfuehrungsregelwerk soll keine Uebergaenge fuer Zustaende
		#                    definieren, die nicht eine Untermenge von S sind
		fzDeltaKeys = frozenset(self.delta.keys()) 
		if not fzDeltaKeys.issubset(self.S):
			raise NoSuchStateException(fzDeltaKeys.difference(self.S), self.S, "Ueberfuehrungsfunktion")

		# Ueberpruefen IV - das delta Ueberfuehrungsregelwerk soll keine Uebergaenge fuer Zustaende
		#                    definieren, die Zeichen benutzen, die nicht in Sigma sind
		for zustand in fzDeltaKeys:
			zZeichen = self.delta[zustand].keys()
			zeichenSet = set()
			for item in zZeichen:
				addme = list(item)[0]
				zeichenSet.add(addme)
			self.log.debug('%s : %s, in Sigma: %s' % (zustand, zeichenSet, zeichenSet.issubset(self.Sigma)))
			
			if not zeichenSet.issubset(self.Sigma):
				raise NotInSigmaException(zeichenSet.difference(self.Sigma), self.Sigma)

		# Ein paar meta Daten ..
		self.name = name
		self.ZustandIndex = dict()
		self.testWords = testWords
		self.verifyWords = verifyWords
		self.verifyRegExp = verifyRegExp
		self.beschreibung = beschreibung
		self.ableitungsPfad = list()

		if self.testWords == None:
			self.log.debug("Adding Test Words")
			self.testWords = self.testWorteGenerator()
		# Automat zuruecksetzen (aktuellen Zustand auf s0 setzen)
		self.reset()

	def __str__(self):
		s = "%seterministischer Automat '%s'" % ((self.istDEA() and 'D' or 'Nichtd'), self.name)
		if EpsilonAutomat.EPSILON in self.Sigma:
			s += " (ε-Übergänge möglich)"
		s += "\n"
		if self.beschreibung:
			s += " %s\n" % self.beschreibung
		s += " Anfangszustand                          : %s\n" % self._fzString(self.s0)
		s += " Endliche Menge der möglichen Zustände S : %s\n" % self._fzString(self.S)
		s += " Menge der Endzustände F                 : %s\n" % self._fzString(self.F)
		s += " Endliche Menge der Eingabezeichen Σ     : %s\n" % self._fzString(self.Sigma)
		if '_getAsciiArtDeltaTable' in dir(self):
			s += self._getAsciiArtDeltaTable()
		s += " (%se Überführungsfunktion)\n" % (self.istDeltaVollstaendig() and 'vollständig' or 'partiell')
		return s

	def _ableitungsPfad__str__(self):
		if len(self.ableitungsPfad) == 0:
			return ''
		items = list()
		for item in self.ableitungsPfad:
			items.append('{%s}' % ','.join(sorted(item)))
		return " Ableitung:\n %s" % ' -> '.join(items)

	def reset(self):
		"""
		Setzt den Automaten zurueck
		"""
		self.Zustand = self.s0
		self.ableitungsPfad = list()

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

	def _delta__str__(self, Zustand, Zeichen):
		"""
		Delta Funktion, fuer Aufrufe innerhalb von __str__() Aufrufen verwendet werden kann.
		"""
		return self._delta(Zustand, Zeichen)

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
		>>> mini._delta(frozenset(['s0', 's1']), 1)
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
			self.log.debug(" '%s' nicht Teil des Alphabets (%s)" % (Zeichen, self._fzString(self.Sigma)))
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
			if len(Zustand) > 1:
				#self.log.warning("!! Zustand: schon frozenset: %s %d" % (repr(Zustand), len(Zustand)))
				ziele = frozenset()
				for item in Zustand:
					ziele = ziele.union(self._delta(item, Zeichen))
				return ziele
		else:
			self.log.warning("Zustand: nicht unterstuetzter Datentyp %s" % repr(Zustand))
			raise ValueError()

		# Da Namen der Zustaende Strings sind, brauchen wir den Zustand auch als String
		stringZustand = list(Zustand)[0]

		# Pruefen, ob der zu behandelnde Zustand ueberhaupt Teil der Zustandsmenge ist
		if not Zustand.issubset(self.S):
			#self.log.debug("Zustand '%s' nicht in der Zustandsmenge '%s' ?" % (Zustand, ','.join(sorted(self.S))))
			raise NoSuchStateException(stringZustand, self.S)

		# Keine Regeln fuer Zustand definiert
		if not Zustand.issubset(self.delta):
			raise NoRuleForStateException(stringZustand, self.delta.keys())

		for keyObject in self.delta[stringZustand].keys():
			if Zeichen in keyObject:
				return self.delta[stringZustand][keyObject]

		#self.log.debug("Kein Folgezustand fuer '%s' von '%s'." % (Zeichen, Zustand))
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
				self.ableitungsPfad.append(self.Zustand)
				if len(self.Zustand) == 0:
					msg = "Kein Ziel-Zustand fuer Zeichen '%s' (Alphabet: %s)" % (Zeichen, self._fzString(self.Sigma))
					msg += " von Zustand %s definiert." % (self._fzString(altZustand))
					self.log.debug(msg)
					if doRaise:
						raise NoAcceptingStateException(self.Zustand, self.S)
					return False
			except NotInSigmaException, e:
				self.log.debug("Zeichen '%s' nicht Teil des Alphabet %s." %  (Zeichen,  self._fzString(self.Sigma)))
				if doRaise:
					raise
				return False
			except NoRuleForStateException, e:
				self.log.debug("Zeichen '%s' nicht Teil des Alphabets." %  Zeichen)
				if doRaise:
					raise
				return False

		if len(self.Zustand.intersection(self.F)) == 0:
			self.log.debug("Kein Endzustand erreicht.")
			if doRaise:
				raise NoAcceptingStateException(self.Zustand, self.F)
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
			except NoRuleForStateException, e:
				result = "Kein finaler Zustand erreicht (Keine Regel definiert für '%s')." % e.value
			resultset.append((word, successful, result))
			if not silence:
				self.log.info("%-20s [%s] %-5s : %s" % (self.name, (successful and "SUCCESS" or "FAILURE"), word, result))
				self.log.debug(self._ableitungsPfad__str__())
		return resultset

	def _RegularExpressionTestWorte(self, worte, regexp=None):
		if not regexp:
			regexp = self.verifyRegExp
		if not regexp.startswith("^"):
			regexp = '^' + regexp
		if not regexp.endswith("$"):
			regexp += '$'
		pattern = re.compile(regexp)
	
		verifyWords = dict()
		for wort in worte:
			res = pattern.match(wort)
			verifyWords[wort] = pattern.match(wort) and True or False
		return verifyWords

	def verifyByRegExp(self, testWords=None, regexp=None):
		if not testWords:
			testWords = self.testWords
		if not regexp and not self.verifyRegExp:
			self.log.warning("Cannot verify by Regular Expression, returning True")
			return True
		vWords = self._RegularExpressionTestWorte(testWords, regexp)
		self.log.info("Verify by Regular Expression:")
		return self.verify(vWords)
		
	def verify(self, vWords=None):
		verified = True
		if vWords == None:
			if self.verifyWords != None:
				vWords = self.verifyWords
		
		if vWords == None or (isinstance(vWords, dict) and len(vWords) == 0):
			self.log.warning("%s: Will not be verified." % self.name)
			return

		for word in vWords:
			expectation = vWords[word]
			result = self.check(word)
			self.log.info("[VERIFY] %-10s expecting: %-5s, got: %-5s" % (word, expectation, result))
			if expectation != result:
				self.log.error("%s: '%s' failed!" % (self.name, word))
				self.log.debug(self.ableitungsPfad)
				verified = False
		self.log.info("Automat '%s' %sverifiziert" % (self.name, (not verified and 'NICHT ') or ''))
		return verified

class Automat(NichtDeterministischerAutomat):
	def __init__(self, S, s0, F, Sigma, delta, name="EinDEA", beschreibung='', testWords=None, verifyWords=None, verifyRegExp=None):
		"""
		>>> mini = Automat('s0 s1 s2 s3', 's0', 's3', '0 1', {'s0' : {'0' : 's0 s1', '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}})
		Traceback (most recent call last):
		...
		Exception: Ich fuehle mich so nichtdeterministisch.

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
		NotInSigmaException: 'b' ist nicht Teil der Menge der Eingabezeichen [a]

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
		NoAcceptingStateException: frozenset(['s0']) ist nicht Teil der Menge der moeglichen Endzustaende [s3]
		>>> mini2.check("a", True)
		Traceback (most recent call last):
		...
		NotInSigmaException: 'a' ist nicht Teil der Menge der Eingabezeichen [0,1]

		>>> mini3 = Automat('z0 z1', 'z0', 'z1', ['a', 'b'], {'z0' : {'a' : 'z1'}, 'z1' : {'a' : 'z1'}})
		>>> print mini3.Sigma
		frozenset(['a', 'b'])
		>>> mini3.check("ab", True)
		Traceback (most recent call last):
		...
		NoAcceptingStateException: frozenset([]) ist nicht Teil der Menge der moeglichen Endzustaende [z0,z1]

		"""
		NichtDeterministischerAutomat.__init__(self, S, s0, F, Sigma, delta, name, beschreibung, testWords, verifyWords, verifyRegExp)
		if not self.istDEA():
			raise Exception("Ich fuehle mich so nichtdeterministisch.")

class EpsilonAutomat(NichtDeterministischerAutomat):
	EPSILON='EPSILON'
	
	def __init__(self, S, s0, F, Sigma, delta, name="EinNDAe", beschreibung='', testWords=None, verifyWords=None, verifyRegExp=None):
		"""
		"""
		Sigma = self._toList(Sigma)
		Sigma.append(EpsilonAutomat.EPSILON)
		NichtDeterministischerAutomat.__init__(self, S, s0, F, Sigma, delta, name, beschreibung, testWords, verifyWords, verifyRegExp)

	def _delta(self, Zustand, Zeichen):
		"""
		"""
		leereMenge = frozenset([])
		zielMenge = NichtDeterministischerAutomat._delta(self, Zustand, Zeichen)
		self.log.debug("%s(%s) : zM: %s." % (Zustand, Zeichen, zielMenge))
		if zielMenge == leereMenge:
			epsilonMenge = NichtDeterministischerAutomat._delta(self, Zustand, EpsilonAutomat.EPSILON)
			self.log.debug("%s : zM: %s; eM: %s" % (Zeichen, zielMenge, epsilonMenge))
			
			gesehen = dict()
			while epsilonMenge != leereMenge:
				self.log.debug("Mit Epsilon gehts weiter .. -> %s" % epsilonMenge)
				zielMenge = NichtDeterministischerAutomat._delta(self, epsilonMenge, Zeichen)
				if not gesehen.has_key(zielMenge):
					gesehen[zielMenge] = 0
				gesehen[zielMenge] += 1
				
				if gesehen[zielMenge] > 2:
					self.log.warning("loop %s" % gesehen)
					return leereMenge
				if zielMenge != leereMenge:
					self.log.debug("==>> %s" % zielMenge)
					return zielMenge
				epsilonMenge = NichtDeterministischerAutomat._delta(self, epsilonMenge, EpsilonAutomat.EPSILON)
			self.log.debug("auch epsilon menge war nix")
		return zielMenge

	def _delta__str__(self, Zustand, Zeichen):
		"""
		Delta Funktion, fuer Aufrufe innerhalb von __str__() Aufrufen verwendet werden kann.
		In diesem Fall werden Epsilon-Uebergaenge _nicht aufgeloest.
		"""
		return NichtDeterministischerAutomat._delta(self, Zustand, Zeichen)

	def check(self, Wort, doRaise=False):
		try:
			result = NichtDeterministischerAutomat.check(self, Wort, doRaise=True)
			return result
		except NoAcceptingStateException, e:
			leereMenge = frozenset([])
			self.log.debug("Ende des Wortes, kein Endzustand erreicht, wir sind bei %s" % e.value)
			if e.value == leereMenge:
				self.log.debug("Wir sind bei leerer Menge, das wird also nichts mehr")
				if doRaise:
					raise
				return False

			epsilonMenge = NichtDeterministischerAutomat._delta(self, e.value, EpsilonAutomat.EPSILON)
			self.log.debug("Mit epsilon gehts hierhin %s" % epsilonMenge)
			gesehen = dict()
			
			while epsilonMenge != leereMenge:
				inter = epsilonMenge.intersection(self.F)
				if inter != leereMenge:
					self.log.debug("aber mit dem epsilon ..")
					self.log.debug(inter)
					return True
				if not gesehen.has_key(epsilonMenge):
					gesehen[epsilonMenge] = 0
				gesehen[epsilonMenge] += 1
				if gesehen[epsilonMenge] > 1:
					self.log.warning("loop %s" % gesehen)
					raise
				epsilonMenge = NichtDeterministischerAutomat._delta(self, epsilonMenge, EpsilonAutomat.EPSILON)
			if doRaise:
				raise
		except Exception, e:
			if doRaise:
				raise
		self.log.debug("check(%s, %s) ----> FALSE" % (Wort, doRaise))
		return False

	def testWorteGenerator(self, length=3, Sigma=None):
		return NichtDeterministischerAutomat.testWorteGenerator(self, length, self.Sigma - frozenset([EpsilonAutomat.EPSILON]))

if __name__ == '__main__':
	test()
