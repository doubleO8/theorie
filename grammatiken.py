#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging, logging.config, os, sys, re
import automaten

class RechtslineareGrammatik(automaten.Automat):
	def __init__(self, N, T, P, S, F=''):
		# Nicht-Terminalzeichen A,B,C [Automatenzustaende]
		# frozenset
		self.N = self._toFrozenSet(N)
		
		# Terminalzeichen a,b,c [AutomatenSigma]
		# frozenset
		self.T = self._toFrozenSet(T)
		
		# Produktionen
		# dict( NT : {NT -> T} )
		self.P = P
		
		# Startsymbol
		# [Automaten s0]
		self.S = S

		self.F = self._toFrozenSet(F)
	
	def __str__(self):
		pfeil = '→'
		s = list()
		s.append('Endliche Menge der Nicht-Terminalsymbole : {%s}' % ', '.join(sorted(self.N)))
		s.append('Endliche Menge der Terminalsymbole       : {%s}' % ', '.join(sorted(self.T)))
		s.append('P = {')
		for finalZustand in self.F:
			s.append("     %-4s %s %s" % (finalZustand, pfeil, 'ε'))
		for (NT, T, zNT) in self.P:
			if NT == self.S:
				NT = 'S'
			s.append("     %-4s %s %s %s" % (NT, pfeil, T, zNT))
		s.append('    }')
		return "\n".join(s)