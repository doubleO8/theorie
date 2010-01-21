#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging, logging.config, os, sys, re
import automaten
import automatenausgabe, automatenleser

def test():
	"""
	doctest (unit testing)
	"""
	import doctest, automaten, logging
	automaten.AutomatLogger(logging.DEBUG).log
	failed, total = doctest.testmod()
	print("doctest: %d/%d tests failed." % (failed, total))

class InfiniteBand(object):
	BLANK = '*'

	def __init__(self, content=None):
		"""
		>>> b = InfiniteBand()
		>>> b.read()
		'*'
		>>> b.read()
		'*'
		>>> b.left()
		Traceback (most recent call last):
		...
		ValueError: No Tape's Land. Versuchte, ueber den Bandanfang hinaus zu lesen!
		"""
		self.pos = 0
		self._band = list(InfiniteBand.BLANK)
		self.log = automaten.AutomatLogger().log
		
		if content != None:
			if isinstance(content, basestring):
				self._band += list(content)
			elif isinstance(content, list):
				self._band += content
			else:
				raise ValueError("Nicht unterstuetzter Datentyp fuer initialen Bandinhalt")

		if self._band[-1] != InfiniteBand.BLANK:
			self._band.append(InfiniteBand.BLANK)
	
	def read(self):
		if self.pos < 0:
			raise ValueError("No Tape's Land. Versuchte, ueber den Bandanfang hinaus zu lesen!")
		elif self.pos == len(self._band) + 1:
			self._band.append(InfiniteBand.BLANK)
		return self._band[self.pos]

	def write(self, char):
		if self.pos >= len(self._band)-1:
			self._band.append(InfiniteBand.BLANK)
		self._band[self.pos] = char
		return self.read()

	def left(self):
		self.pos -= 1
		return self.read()

	def right(self):
		self.pos += 1
		return self.read()

	def __str__(self):
		return ''.join(self._band)

class TuringMachine(automatenausgabe.OAsciiTuringmachine, automaten.Automat):
	HALT = 0
	RIGHT = 1
	LEFT = -1
	AKTION_ALLOWED = frozenset([HALT, RIGHT, LEFT])
	
	AKTION_DESCRIPTION = ['h', 'r', 'l']
	
	def __init__(self, S, s0, F, Sigma, B, delta=None, 
				name="EineTuringMaschine", beschreibung='', 
				testWords=None, verifyWords=None, verifyRegExp=None):
		"""
		>>> S = 's0 s1 sn sn1 se se1 sr sf'
		>>> F = 'sf'
		>>> Sigma = '0 1'
		>>> B = '0 1 *'
		>>> s0 = 's0'
		>>> tm = TuringMachine(S, s0, F, Sigma, B)
		>>> tm.addRule('s0', '*', 's1', '*', TuringMachine.RIGHT)
		True
		>>> tm.addRule('s1', '*', 'sf', '*', TuringMachine.HALT)
		True
		>>> tm.validDelta('s1', '*')
		True
		>>> tm.validDelta('X', '*')
		False
		>>> tm._delta('X', '*')
		Traceback (most recent call last):
		...
		NoSuchStateException: 'X' ist nicht Teil der Menge der moeglichen Zustaende [s0,s1,se,se1,sf,sn,sn1,sr]
		>>> tm._delta('s1', 'X')
		Traceback (most recent call last):
		...
		NoRuleForStateException: 's1' hat keine definierten Regeln fuer "X" 
		"""
		self._initLogging()
		
		# Umwandeln von Listen und Stringinhalte (whitespace-getrennt) in frozenset-Mengen
		self.S = self._toFrozenSet(S)
		self.s0 = s0
		self.F = self._toFrozenSet(F)
		self.B = self._toFrozenSet(B)
		self.Sigma = self._toFrozenSet(Sigma)
		if delta == None:
			delta = dict()
		self.delta = delta

		self.zustand = self.s0
		self.name = name
		self.beschreibung = beschreibung
		self.verifyWords = verifyWords
		self.testWords = testWords
		
		self.halted = False
		#: Automatentyp
		self.type = 'turing'

		self.rulesCounter = 1
		#: Dict mit den Ableitungsregeln, so dass 
		# Ableitungsregeln aufgelistet werden koennen ..
		self.rulesDict = dict()
		
		self.reset()

	def __str__(self):
		s = "Turingmaschine '%s'" % (self.name)
		s += "\n"
		if self.beschreibung:
			s += " %s\n" % self.beschreibung
		s += " Anfangszustand                          : %s\n" % self.s0
		s += " Endliche Menge der möglichen Zustände S : %s\n" % self._fzString(self.S)
		s += " Menge der Endzustände F                 : %s\n" % self._fzString(self.F)
		s += " Endliche Menge der Eingabezeichen Σ     : %s\n" % self._fzString(self.Sigma)
		s += " Endliche Menge der Bandzeichen B        : %s\n" % self._fzString(self.B)

		if '_getAsciiArtDeltaTable' in dir(self):
			s += self._getAsciiArtDeltaTable()

		return s

	def reset(self):
		automaten.Automat.reset(self)
		self.zustand = self.s0
		self.band = InfiniteBand()
		self.halted = False

	def addRule(self, zustand, bandzeichen, zustandStrich, bandzeichenStrich, aktion):
		"""
		"""
		if zustand not in self.S:
			raise automaten.NoSuchStateException(zustand, self.S)
		if isinstance(aktion, basestring):
			aktion = aktion.lower()
			if aktion == 'h':
				aktion = TuringMachine.HALT
			elif aktion == 'r':
				aktion = TuringMachine.RIGHT
			elif aktion == 'l':
				aktion = TuringMachine.LEFT

		if aktion not in TuringMachine.AKTION_ALLOWED:
			raise ValueError("aktion=%d ist nicht in %s" % (aktion, ','.join(TuringMachine.AKTION_ALLOWED)))

		if not self.delta.has_key(zustand):
			self.delta[zustand] = dict()

		self.delta[zustand][bandzeichen] = (zustandStrich, bandzeichenStrich, aktion)
		
		self.rulesDict[(zustand, bandzeichen, zustandStrich, bandzeichenStrich, aktion)] = self.rulesCounter
		self.rulesCounter += 1

		return True

	def check(self, Wort, doRaise=False, doItVerbose=False, stepByStep=False):
		"""
		>>> w = '01'
		>>> S = 's0 s1 sn sn1 se se1 sr sf'
		>>> F = 'sf'
		>>> Sigma = '0 1'
		>>> B = '0 1 *'
		>>> s0 = 's0'
		>>> tm = TuringMachine(S, s0, F, Sigma, B)
		>>> tm.addRule('s0', '*', 's1', '*', TuringMachine.RIGHT)
		True
		
		>>> tm.addRule('s1', '*', 'sf', '*', TuringMachine.HALT)
		True
		>>> tm.addRule('s1', '0', 'sn', '*', TuringMachine.RIGHT)
		True
		
		>>> tm.addRule('sn', '*', 'sn1', '*', TuringMachine.LEFT)
		True
		>>> tm.addRule('sn', '0', 'sn', '0', TuringMachine.RIGHT)
		True
		>>> tm.addRule('sn', '1', 'sn', '1', TuringMachine.RIGHT)
		True
		>>> tm.addRule('sn1', '1', 'sr', '*', TuringMachine.LEFT)
		True

		>>> tm.addRule('se', '*', 'se1', '*', TuringMachine.LEFT)
		True
		>>> tm.addRule('se', '0', 'se', '0', TuringMachine.RIGHT)
		True
		>>> tm.addRule('se', '1', 'se', '1', TuringMachine.RIGHT)
		True
		>>> tm.addRule('se1', '0', 'sr', '*', TuringMachine.LEFT)
		True

		>>> tm.addRule('sr', '*', 's1', '*', TuringMachine.RIGHT)
		True
		>>> tm.addRule('sr', '0', 'sr', '0', TuringMachine.LEFT)
		True
		>>> tm.addRule('sr', '1', 'sr', '1', TuringMachine.LEFT)
		True
		>>> tm.delta.keys()
		['se1', 'sr', 's1', 's0', 'sn', 'sn1', 'se']
		
		>>> tm.check("01", doRaise=True)
		True
		>>> tm.check("0101", doRaise=False)
		False
		"""
		self.reset()
		self.band = InfiniteBand(Wort)

		# "Step" Meta-Werte
		self.stepCount = 0
		self.stepByStepOutput = list()
		self.stepByStepImmediateOutput = False

		# Initialen Zustand merken
		self.stepper()

		while not self.halted:
			bandzeichen = self.band.read()

			try:
				self.step(self.zustand, bandzeichen)
			except Exception, e:
				if doRaise:
					raise
				self.log.error(e)
				self.halted = True
			self.log.debug("")

		# Print Step By Step Table
		if stepByStep and (self.stepByStepImmediateOutput == False):
			print "\n".join(self.stepByStepOutput)

		if self.halted and self.zustand in self.F:
			self.log.info("'%s' akzeptiert." % Wort)
			return True

		return False

	def checkVerbose(self, Wort):
		"""
		Ruft die check()-Funktion mit 'Geschwaetzig'-Parameter auf.
		"""
		return self.check(Wort, doItVerbose=True)

	def checkStepByStep(self,  Wort, doRaise=False):
		return self.check(Wort, stepByStep=True)

	def stepper(self, immediateOutput=None):
		if immediateOutput == None:
			immediateOutput = self.stepByStepImmediateOutput

		lines = list()
		spacer = ' | '
		self.stepCount += 1

		band = spacer.join(self.band._band)
		desc = ' ' * (self.band.pos + len(spacer) * self.band.pos)
		desc += '^%s' % self.zustand
		lines.append(band)
		lines.append(desc)
		lines.append("")
		
		self.stepByStepOutput += lines

		if immediateOutput:
			print "\n".join(lines)

	def step(self, zustand, bandzeichen):
		(zustandStrich, bandzeichenStrich, aktion) = self._delta(self.zustand, bandzeichen)
		self.band.write(bandzeichenStrich)
		if aktion == TuringMachine.HALT:
			self.halted = True
		elif aktion == TuringMachine.LEFT:
			self.band.left()
		elif aktion == TuringMachine.RIGHT:
			self.band.right()
		else:
			raise ValueError("aktion=%s !" % aktion)
		self.zustand = zustandStrich
		self.stepper()

	def validDelta(self, zustand, bandzeichen):
		if self.delta.has_key(zustand):
			return self.delta[zustand].has_key(bandzeichen)
		return False

	def _delta(self, zustand, bandzeichen):
		"""
		Ueberfuehrungsfunktion
		"""
		logmessage = "(%s, %s) = " % (zustand, bandzeichen)

		if self.validDelta(zustand, bandzeichen):
			(zustandStrich, bandzeichenStrich, aktion) = self.delta[zustand][bandzeichen]
			logmessage += "(%s, %s, %s)" % (zustandStrich, bandzeichenStrich, TuringMachine.AKTION_DESCRIPTION[aktion])
			# Regel-Nummer herausfinden:
			rNum = self.rulesDict[(zustand, bandzeichen, zustandStrich, bandzeichenStrich, aktion)]
			self.CHK_Rule = rNum
			logmessage = '#%-2d %s' % (rNum, logmessage) 
			self.log.debug(logmessage)
			return self.delta[zustand][bandzeichen]
		else:
			logmessage += "(?!, ?!, ?!)"
			if not self.delta.has_key(zustand):
				raise automaten.NoSuchStateException(zustand, self.S)

		self.log.debug(logmessage)
		raise automaten.NoRuleForStateException(zustand, explanation='hat keine definierten Regeln fuer "%s"' % bandzeichen)

	def flushRules(self):
		"""
		Ableitungsregeln loeschen
		"""
		self.delta = dict()
		return len(self.delta)

	def verifyByRegExp(self, testWords=None, regexp=None):
		raise NotImplementedError("Verify By Regular Expression: not applicable.")

if __name__ == '__main__':
	test()
