#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging, logging.config

class NoDeltaError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class Automat(object):
	def test():
		"""
		doctest (unit testing)
		"""
		import doctest
		failed, total = doctest.testmod()
		print "doctest: %d/%d tests failed." % (failed, total)

	def __init__(self, S=list(), s0=None, F=list(), Sigma=list(), delta=dict(), name="EinAutomat"):
		self.log = logging.getLogger()
		lhandler = logging.StreamHandler()
		lformatter = logging.Formatter('%(asctime)s %(levelname)s:  %(message)s')
		lhandler.setFormatter(lformatter)
		self.log.addHandler(lhandler)
		self.log.setLevel(logging.INFO)

		if len(S) == 0:
			raise ValueError('Die "endliche Menge der möglichen Zustände" S des Automaten ist leer')
		if len(F) == 0:
			raise ValueError('Die "Menge der Endzustände" F ist leer')
		if len(Sigma) == 0:
			raise ValueError('Die "endliche Menge der Eingabezeichen, Alphabet" Σ (Sigma) ist leer')
		if len(delta) == 0:
			raise ValueError('Die "(determinierte) Zustands-Überführungsfunktion" δ (delta) ist leer')
		if s0 == None:
			s0 = S[0]
			self.log.debug('setze "Anfangszustand" s0 auf \'%s\'' % s0)
		
		self.S = S
		self.s0 = s0
		self.F = F
		self.Sigma = Sigma
		self.delta = delta
		self.deltaVollstaendig = None
		self.name = name
		self.reset()

	def reset(self):
		"""
		Setzt den Automaten zurueck
		"""
		self.Lesekopf = 0
		self.Zustand = self.s0

	def check(self, Wort):
		"""
		Prüft, ob das gegebene Wort zur akzeptierten Sprache des Automaten gehoert
		"""
		self.reset()
		for Zeichen in Wort:
			if Zeichen not in self.Sigma:
				self.log.error("Zeichen '%s' nicht teil des Alphabets." %  Zeichen)
				return False
			neuZustand = self._delta(self.Zustand, Zeichen)
			if neuZustand == None:
				self.log.error("Kein Ziel-Zustand für Zeichen '%s' von Zustand '%s' definiert" % (Zeichen, self.Zustand))
				return False
			else:
				self.Zustand = neuZustand
		if self.Zustand not in self.F:
			self.log.error("Kein Endzustand erreicht")
			return False
		return True

	def _delta(self, Zustand, Zeichen):
		Zeichen = str(Zeichen)
		if not self.delta.has_key(Zustand):
			self.log.warning("Kein Zustand '%s' ?" % Zustand)
		else:
			for keyObject in self.delta[zustand].keys():
				if isinstance(keyObject, string):
					print "key: %s (string)" % keyObject
				elif isinstance(keyObject, list):
					print "key: %s (list)" % keyObject
			if not self.delta[Zustand].has_key(Zeichen):
				self.log.warning("Kein Zustand/Zeichen '%s/%s' ?" % (Zustand, Zeichen))
				self.log.warning(self.delta[Zustand])
			else:
				return self.delta[Zustand][Zeichen]
		return None

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

	def _getDeltaTable(self):
		maxLength = 1
		
		for zeichen in self.Sigma:
			zLength = len(str(zeichen)) 
			if  zLength > maxLength:
				maxLength = zLength
				
		for zustand in self.S:
			zLength = len(str(zustand))
			if  zLength > maxLength:
				maxLength = zLength

		fmtString = '%' + str(maxLength) + 's'
		s = ' ' + (fmtString % str(' δ'))
		pfxLength = len(s)

		for zeichen in self.Sigma:
			s += ' | ' + (fmtString % zeichen)
		s += "\n"
		s += "-" * ((maxLength+2) * len(self.Sigma) + (len(self.Sigma)) + pfxLength)
		s += "\n"
		for zustand in self.S:
			s += ' ' + (fmtString % zustand)
			for zeichen in self.Sigma:
				zZustand = self._delta(zustand, zeichen) or '-'
				s += ' | %s' % (fmtString % zZustand)
			s += "\n"
		return s

	def __str__(self):
		s = "Deterministischer Automat '%s'\n%s\n" % (self.name, "=" * 80)
		s += "Anfangszustand :\n %s\n" % self.s0
		s += "Endliche Menge der möglichen Zustände S :\n {%s}\n" % ', '.join(self.S)
		s += "Menge der Endzustände F :\n {%s}\n" % ', '.join(self.F)
		s += "Endliche Menge der Eingabezeichen Σ :\n {%s}\n" % ', '.join(self.Sigma)
		s += "Überführungsfunktion:\n"
		s += self._getDeltaTable()
		s += "%80s\n" % ('(' + (self.isDeltaVollstaendig() and 'vollständig' or 'partiell') + ')' )
		s += "%s\n\n" % ("=" * 80)
		return s
		
if __name__ == '__main__':
	S = 's0 s1 s2 s3'.split(' ')
	s0 = 's0'
	F = 's3'.split(' ')
	Sigma = '0 1'.split(' ')
	delta = {
				's0' : {
							"0" : 's1',
							"1" : 's0',
						},
				's1' : {
							'0' : 's2',
							'1' : 's0',
						},
				's2' : {
							'0' : 's2',
							'1' : 's3',
						},
				's3' : {
							'0' : 's3',
							'1' : 's3',
						},
			}
	A = Automat(S, s0, F, Sigma, delta)

	bS = 's0 s1 s2 s3 s4 s5 s6 s7'.split(' ')
	bs0 = 's0'
	bF = 's2 s4 s7'.split(' ')
	bSigma = '0 1 2 3 4 5 6 7 8 9 + - . e'.split(' ')
	bdelta = {
				's0' : {
							"0" : 's2',
							"1" : 's2',
							"2" : 's2',
							"3" : 's2',
							"4" : 's2',
							"5" : 's2',
							"6" : 's2',
							"7" : 's2',
							"8" : 's2',
							"9" : 's2',
							"+" : 's1',
							"-" : 's1',
						},
				's1' : {
							"0" : 's2',
							"1" : 's2',
							"2" : 's2',
							"3" : 's2',
							"4" : 's2',
							"5" : 's2',
							"6" : 's2',
							"7" : 's2',
							"8" : 's2',
							"9" : 's2',
						},
				's2' : {
							"0" : 's2',
							"1" : 's2',
							"2" : 's2',
							"3" : 's2',
							"4" : 's2',
							"5" : 's2',
							"6" : 's2',
							"7" : 's2',
							"8" : 's2',
							"9" : 's2',
							"." : "s3",
							"e" : "s5"
						},
				's3' : {
							"0" : 's4',
							"1" : 's4',
							"2" : 's4',
							"3" : 's4',
							"4" : 's4',
							"5" : 's4',
							"6" : 's4',
							"7" : 's4',
							"8" : 's4',
							"9" : 's4',
						},
				's4' : {
							"0" : 's4',
							"1" : 's4',
							"2" : 's4',
							"3" : 's4',
							"4" : 's4',
							"5" : 's4',
							"6" : 's4',
							"7" : 's4',
							"8" : 's4',
							"9" : 's4',
							"e" : 's5',
						},
				's5' : {
							"0" : 's7',
							"1" : 's7',
							"2" : 's7',
							"3" : 's7',
							"4" : 's7',
							"5" : 's7',
							"6" : 's7',
							"7" : 's7',
							"8" : 's7',
							"9" : 's7',
							"+" : "s6",
							"-" : "s6",
						},
				's6' : {
							"0" : 's7',
							"1" : 's7',
							"2" : 's7',
							"3" : 's7',
							"4" : 's7',
							"5" : 's7',
							"6" : 's7',
							"7" : 's7',
							"8" : 's7',
							"9" : 's7',
						},
				's7' : {
							"0" : 's7',
							"1" : 's7',
							"2" : 's7',
							"3" : 's7',
							"4" : 's7',
							"5" : 's7',
							"6" : 's7',
							"7" : 's7',
							"8" : 's7',
							"9" : 's7',
						},
				'sX' : {
							('eins', 'zwei', 'drei') : 'sXX',
						},
			}
	B = Automat(bS, bs0, bF, bSigma, bdelta)
	print A
	print B
	A.check("1001")
	print B.check("-1.02")
