#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging, logging.config, os, sys, re
import automatenausgabe, automatenleser
import automaten

def test():
	"""
	doctest (unit testing)
	"""
	import doctest
	automaten.AutomatLogger(logging.DEBUG).log
	failed, total = doctest.testmod()
	print("doctest: %d/%d tests failed." % (failed, total))

class NotInKException(automaten.AutomatException):
	def __init__(self, value, validSet=frozenset(), hint=None, ableitungspfad=list()):
		automaten.AutomatException.__init__(self, value, validSet, 'ist nicht Teil der Menge der Kellerzeichen', hint, ableitungspfad)

class DeterministischerKellerautomat(automaten.Automat):
	EPSILON = 'EPSILON'
	DELIMITER = '#'

	def __init__(self, S, s0, F, Sigma, K, k0, delta=None, 
				name="EinDPDA", beschreibung='', 
				testWords=None, verifyWords=None, verifyRegExp=None):
		self._initLogging()
		
		# Umwandeln von Listen und Stringinhalte (whitespace-getrennt) in frozenset-Mengen
		self.S = self._toFrozenSet(S)
		self.s0 = s0
		self.F = self._toFrozenSet(F)
		self.Sigma = self._toFrozenSet(Sigma)
		self.K = self._toFrozenSet(K)
		self.k0 = k0
		if delta == None:
			delta = dict()
		self.delta = delta
		self.keller = [k0]
		self.zustand = self.s0
		self.name = name
		self.beschreibung = beschreibung

	def addRule(self, zustand, bandzeichen, kellerzeichen, zustandStrich, kellerzeichenStrich):
		"""
		>>> S = ['s0', 's1', 's2', 's3']
		>>> Sigma = ['a', 'b']
		>>> F = ['s0', 's3']
		>>> k0 = 'k0'
		>>> K = [k0, 'a']
		>>> s0 = 's0'
		>>> PDA = DeterministischerKellerautomat(S, s0, F, Sigma, K, k0)
		>>> PDA.addRule('s44', 'a', 'k0', 's1', 'a+k0')
		Traceback (most recent call last):
		...
		NoSuchStateException: 's44' ist nicht Teil der Menge der moeglichen Zustaende [s0,s1,s2,s3]
		>>> PDA.addRule('s0', 'X', 'k0', 's1', 'a+k0')
		Traceback (most recent call last):
		...
		NotInSigmaException: 'X' ist nicht Teil der Menge der Eingabezeichen [a,b]
		>>> PDA.addRule('s0', 'a', 'b', 's1', 'a+k0')
		Traceback (most recent call last):
		...
		NotInKException: 'b' ist nicht Teil der Menge der Kellerzeichen [a,k0]
		>>> PDA.addRule('s0', 'a', 'k0', 's2', 'a')
		True
		>>> PDA.addRule('s0', 'a', 'k0', 's1', 'a+k0')
		True
		>>> PDA.delta['s0'][('a', 'k0')] == ('s1', ['a', 'k0'])
		True
		>>> PDA.flushRules()
		0
		>>> PDA.addRule('s0', 'a', 'k0', 's1', 'a+k0')
		True
		>>> PDA.addRule('s0', 'a', 'k0', 's1', ['a', k0])
		True
		>>> PDA.addRule('s1', 'a', 'a', 's1', 'a+a')
		True
		>>> PDA.addRule('s1', 'b', 'a', 's2', 'EPSILON')
		True
		>>> PDA.addRule('s2', 'b', 'a', 's2', 'EPSILON')
		True
		>>> PDA.addRule('s2', 'EPSILON', 'k0', 's3', 'k0')
		True
		"""
		if zustand not in self.S:
			raise automaten.NoSuchStateException(zustand, self.S)
		if bandzeichen not in self.Sigma and (bandzeichen != self.EPSILON):
			raise automaten.NotInSigmaException(bandzeichen, self.Sigma)
		if kellerzeichen not in self.K:
			raise NotInKException(kellerzeichen, self.K)

		if self.delta.has_key(zustand):
			if self.delta[zustand].has_key((bandzeichen, kellerzeichen)):
				(altZustandStrich, altKellerzeichenStrich) = self.delta[zustand][(bandzeichen, kellerzeichen)]
				self.log.warning("Overriding rule: delta(%s, %s, %s) = (%s, %s)" % (zustand, bandzeichen, kellerzeichen, altZustandStrich, altKellerzeichenStrich))
				self.log.warning("           with: delta(%s, %s, %s) = (%s, %s)" % (zustand, bandzeichen, kellerzeichen, zustandStrich, kellerzeichenStrich))
		else:
			self.delta[zustand] = dict()

		if not isinstance(kellerzeichenStrich, list):
			if len(kellerzeichenStrich) == 1:
				kellerzeichenStrich = list(kellerzeichenStrich)
			else:
				kellerzeichenStrich = kellerzeichenStrich.split('+')

		self.delta[zustand][(bandzeichen, kellerzeichen)] = (zustandStrich, kellerzeichenStrich)
		return True
	
	def flushRules(self):
		self.delta = dict()
		return len(self.delta)
	
	def push(self, items):
		items = list(reversed(items))
		if items == [DeterministischerKellerautomat.EPSILON]:
			self.log.debug("Not adding epsilon")
		else:
			self.log.debug("Pushing: %s" % repr(items))
			self.keller += items
	
	def pop(self):
		return self.keller.pop()

	def __str__(self):
		return "Deterministischer Kellerautomat"

	
	def check(self, Wort, doRaise=False):
		"""
		>>> S = ['s0', 's1', 's2', 's3']
		>>> Sigma = ['a', 'b']
		>>> F = ['s0', 's3']
		>>> k0 = 'k0'
		>>> K = [k0, 'a']
		>>> s0 = 's0'
		>>> PDA = DeterministischerKellerautomat(S, s0, F, Sigma, K, k0)
		>>> PDA.addRule('s0', 'a', 'k0', 's1', 'a+k0')
		True
		>>> PDA.addRule('s1', 'a', 'a', 's1', 'a+a')
		True
		>>> PDA.addRule('s1', 'b', 'a', 's2', 'EPSILON')
		True
		>>> PDA.addRule('s2', 'b', 'a', 's2', 'EPSILON')
		True
		>>> PDA.addRule('s2', 'EPSILON', 'k0', 's3', 'k0')
		True
		>>> PDA.check("aaabbb")
		True
		"""
		self.reset()
		if Wort[-1] != DeterministischerKellerautomat.DELIMITER:
			self.log.warn("Adding Delimiter '%s'" % DeterministischerKellerautomat.DELIMITER)
			Wort += DeterministischerKellerautomat.DELIMITER
			
		for Zeichen in Wort:
			if Zeichen == DeterministischerKellerautomat.DELIMITER:
				Zeichen = DeterministischerKellerautomat.EPSILON
			self.log.debug("Zeichen       : %s" % Zeichen)
			self.log.debug("Keller        : %s" % ','.join(self.keller))
			head = self.keller[-1]
			self.log.debug("Kellerzeichen : %s" % head)
			
			(zustandStrich, kellerzeichenStrich) = self._delta(self.zustand, Zeichen, head)

			self.zustand = zustandStrich
			self.pop()
			self.push(kellerzeichenStrich)
			self.log.debug("Zustand: %s Keller  : %s" % (self.zustand, ','.join(self.keller)))
			self.log.debug("")

		if self.zustand in self.F and self.keller == [self.k0]:
			self.log.info("Akzeptiert.")
			return True
		return False

	def _delta(self, Zustand, Zeichen, Kellerzeichen):
		logmessage = "(%s, %s, %s) => " % (Zustand, Zeichen, Kellerzeichen)
		
		if Zeichen == DeterministischerKellerautomat.DELIMITER:
			self.log.warning("Delimiter '%s'!" % DeterministischerKellerautomat.DELIMITER)

		if self.delta[Zustand].has_key( (Zeichen, Kellerzeichen) ):
			(zustandStrich, kellerzeichenStrich) = self.delta[Zustand][(Zeichen, Kellerzeichen)]
			logmessage += "(%s, %s)" % (zustandStrich, ''.join(kellerzeichenStrich))
			self.log.debug(logmessage)
			return self.delta[Zustand][(Zeichen, Kellerzeichen)]
		else:
			logmessage += "?!"
		self.log.debug(logmessage)

		raise ValueError("! %s: z:%s/k:%s" % (Zustand, Zeichen, Kellerzeichen))
	
	def reset(self):
		automaten.Automat.reset(self)
		self.keller = [self.k0]

if __name__ == '__main__':
	test()