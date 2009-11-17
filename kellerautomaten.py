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

class DeterministischerKellerautomat(automaten.Automat):
	EPSILON = 'EPSILON'
	def __init__(self, S, s0, F, Sigma, K, k0, delta, 
				name="EinDPDA", beschreibung='', 
				testWords=None, verifyWords=None, verifyRegExp=None):
		"""
		>>> k0 = 'k0'
		>>> delta = dict()
		>>> delta['s0'] = { ('a', k0) : ('s1', 'a') }
		>>> delta['s1'] = { ('a', 'a') : ('s1', 'a'), \
							('b', 'a') : ('s2', DeterministischerKellerautomat.EPSILON) \
						}
		>>> delta['s2'] = { ('b', 'a') : ('s2', DeterministischerKellerautomat.EPSILON), \
							(DeterministischerKellerautomat.EPSILON, k0) : ('s3', k0), \
						}
		>>> DPDA = DeterministischerKellerautomat('s0 s1 s2 s3', 's0', 's0 s3', 'a b', 'k0 a', k0, delta)
		>>> DPDA._delta('s0', 'a', k0)
		('s1', 'a')
		>>> print DPDA.keller
		['a']
		>>> DPDA.reset()
		>>> DPDA.check('aaabbb#')
		True
		"""
		self._initLogging()
		
		# Umwandeln von Listen und Stringinhalte (whitespace-getrennt) in frozenset-Mengen
		self.S = self._toFrozenSet(S)
		self.s0 = s0
		self.F = self._toFrozenSet(F)
		self.Sigma = self._toFrozenSet(Sigma)
		self.K = self._toFrozenSet(K)
		self.k0 = k0
		self.delta = delta
		self.keller = [k0]
		
		self.name = name
		self.beschreibung = beschreibung
	
	def check(self, Wort, doRaise=False):
		self.reset()
		kellerZeichen = self.k0
		for zeichen in Wort:
			(zustandNeu, kellerZeichenNeu) = self._delta(self.Zustand, zeichen, kellerZeichen)
			#self.log.info("(%s, %s, %s) => (%s, %s) %s" % (self.Zustand, zeichen, kellerZeichen, zustandNeu, kellerZeichenNeu, list(reversed(self.keller))))
			self.Zustand = zustandNeu
			kellerZeichen = kellerZeichenNeu

	def _delta(self, Zustand, Zeichen, Kellerzeichen):
		logmessage = "(%s, %s, %s) => " % (Zustand, Zeichen, Kellerzeichen)
		if Zeichen == '#':
			self.log.warning("#")
			Zeichen = DeterministischerKellerautomat.EPSILON

		if self.delta[Zustand].has_key( (Zeichen, Kellerzeichen) ):
			(zielZustand, pushZeichen) = self.delta[Zustand][(Zeichen, Kellerzeichen)]
			if Zeichen == DeterministischerKellerautomat.EPSILON:
				self.log.warning("eps")
				zielZustand = Zustand
				pushZeichen = Kellerzeichen
				self.keller.pop()
			else:
				self.keller.append(pushZeichen)
			
			logmessage += "(%s, %s) %s" % (zielZustand, pushZeichen, list(reversed(self.keller)))
			self.log.info(logmessage)
			return (zielZustand, pushZeichen)
		raise ValueError("! %s: z:%s/k:%s" % (Zustand, Zeichen, Kellerzeichen))
	
	def reset(self):
		automaten.Automat.reset(self)
		self.keller = [self.k0]

if __name__ == '__main__':
	test()