#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging, logging.config, os, sys, re
import automaten
import automatenausgabe, automatenleser

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
	DELIMITER = '#'

	def __init__(self, S, s0, F, Sigma, K, k0='k0', delta=None, 
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
		self.verifyWords = verifyWords
		
		#: Bandinhalt
		self.band = list()
		
		#: Ableitungspfad
		self.ableitung = list()
		
		self.rulesCounter = 1
		#: Dict mit den Ableitungsregeln, so dass 
		# Ableitungsregeln wie folgt aufgelistet werden koennen ..
		# (Zustand, Bandinhalt, Kellerinhalt) |- #<NUMMER> (Zustand', Bandinhalt', Kellerinhalt')
		self.rulesDict = dict()

	def reset(self):
		automaten.Automat.reset(self)
		self.keller = [self.k0]
		self.zustand = self.s0
		self.band = list()
		self.ableitung = list()

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
			raise automaten.NotInKException(kellerzeichen, self.K)

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
		
		self.rulesDict[(zustand, bandzeichen, kellerzeichen, zustandStrich, ''.join(kellerzeichenStrich))] = self.rulesCounter
		self.rulesCounter += 1

		return True
	
	def flushRules(self):
		"""
		Ableitungsregeln loeschen
		"""
		self.delta = dict()
		return len(self.delta)
	
	def push(self, items):
		"""
		Zeichen auf den Keller schmeissen
		"""
		if len(items) == 1:
			items = list(items)
		items = list(reversed(items))
		if items != [DeterministischerKellerautomat.EPSILON]:
			#self.log.debug("Pushing: %s" % repr(items))
			self.keller += items
	
	def pop(self):
		"""
		Oberstes Kellerzeichen lesen und loeschen
		"""
		return self.keller.pop()
	
	def _stackEmpty(self):
		"""
		Ist der Keller leer ?
		"""
		return self.keller == [self.k0]

	def _bandEmpty(self):
		"""
		Ist das Band leer ?
		ACHTUNG: EPSILON auf Band wird auch als 'leer' interpretiert.
		"""
		if len(self.band) == 0:
			return True
		elif self.band == [DeterministischerKellerautomat.EPSILON]:
			return True
		return False

	def step(self, zustandStrich, kellerzeichenStrich=None):
		"""
		Zustand aendern:
			* Oberstes Kellerzeichen loeschen
			* Zustand wechseln
			* Neue kellerzeichen auf den Keller schmeissen
		"""
		if isinstance(zustandStrich, tuple):
			(zustandStrich, kellerzeichenStrich) = zustandStrich
		self.pop()
		self.push(kellerzeichenStrich)
		self.zustand = zustandStrich

	def __str__(self):
		return "Deterministischer Kellerautomat"

	def _getStateVerbose(self, read):
		"""
		Generiert einen String, der den aktuellen Zustand in der Form
			(Zustand, Gelesene Zeichen, Kellerinhalt)
		repraesentiert.
		"""
		return "(%s, %s, %s)" % (self.zustand, read, ''.join(reversed(self.keller)))

	def _logStateInfo(self, Zeichen, prefix=''):
		"""
		Logging des aktuellen Zustandes mit aktuell gelesenem Zeichen
		"""
		self.log.debug("%s[%-2s] %-7s Keller: %s" % (prefix, self.zustand, Zeichen, ','.join(self.keller)))
		

	def _fixWord(self, Wort):
		"""
		Fuegt ggf einen Wortdelimiter hinzu
		*HEREBEDRAGONS*
		"""
		if Wort[-1] != DeterministischerKellerautomat.DELIMITER:
			#self.log.warn("Adding Delimiter '%s'" % DeterministischerKellerautomat.DELIMITER)
			Wort += DeterministischerKellerautomat.DELIMITER
		return Wort

	def _fixZeichen(self, Zeichen):
		"""
		Veraendert ggf. Bandende-Zeichen in Epsilon-Zeichen
		*HEREBEDRAGONS*
		"""
		if Zeichen == DeterministischerKellerautomat.DELIMITER:
			Zeichen = DeterministischerKellerautomat.EPSILON
		return Zeichen

	def checkVerbose(self, Wort):
		"""
		Ruft die check()-Funktion mit 'Geschwaetzig'-Parameter auf.
		"""
		return self.check(Wort, doItVerbose=True)

	def check(self, Wort, doRaise=False, doItVerbose=False):
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
		>>> PDA.check("aaabb", True)
		Traceback (most recent call last):
		...
		NoRuleForStateException: 's2' hat keine definierten Regeln fuer (EPSILON, a) 
		>>> PDA.check("a")
		False
		>>> PDA.check("aaaaaab")
		False
		>>> PDA.checkVerbose("aaabbb")
		True
		"""
		self.reset()
		accepted = False
		Wort = self._fixWord(Wort)

		self.ableitung.append(self._getStateVerbose(Wort))

		for i in range(len(Wort)):
			(zustandStrich, kellerzeichenStrich) = (None, None)
			Zeichen = self._fixZeichen(Wort[i])
			read = Wort[i:]
			self.band.append(Zeichen)
			
			self._logStateInfo(Zeichen, prefix='> ')

			# Oberstes Kellerzeichen herausfinden (ohne pop() !)
			try:
				head = self.keller[-1]
			except Exception, e:
				if doRaise:
					raise
				return False

			self.log.debug("Kellerzeichen     : %s" % head)
			#self.log.debug(">" * 80)

#			# Ueberfuehrung ohne Zeichen (siehe Barth, Kap. 5.2., Seite 58)
#			try:
#				(zustandStrich, kellerzeichenStrich) = self._delta(self.zustand, DeterministischerKellerautomat.EPSILON, head)
#				self.log.debug("Ueberfuehrung ohne Zeichen !")
#			except Exception, e:
#				#self.log.debug("Ueberfuehrung ohne Zeichen: %s" % e)
#				pass
#			if (zustandStrich, kellerzeichenStrich) != (None, None):
#				self.log.warning("===%-50s===" % 'HARRRRRR')
#				self.log.warning("===%-50s===" % ("%s,%s" % (zustandStrich, kellerzeichenStrich)))

			if (zustandStrich, kellerzeichenStrich) == (None, None):
				# Ueberfuehrung mit Zeichen
				try:
					(zustandStrich, kellerzeichenStrich) = self._delta(self.zustand, Zeichen, head)
				except Exception, e:
					self.log.debug("Ueberfuehrung MIT Zeichen schlug fehl: %s" % e)

			if ((zustandStrich, kellerzeichenStrich) == (None, None)) and not self._bandEmpty():
				if doRaise:
					raise automaten.NoRuleForStateException(self.zustand, explanation='hat keine definierten Regeln fuer (%s, %s)' % (Zeichen, head))
				#self.log.debug("Don't go breaking my heart ..")
				break
			else:
				self.step((zustandStrich, kellerzeichenStrich))
				self.band.pop()
				self.ableitung.append(self._getStateVerbose(read))

			self._logStateInfo(Zeichen, prefix='< ')

		self.log.debug(" = Zustand      : %-40s (Final: %s)" % (self.zustand, (self.zustand in self.F)))
		self.log.debug(" = Band         : %-40s (Leer : %s)" % (','.join(self.band), self._bandEmpty()))
		self.log.debug(" = Kellerinhalt : %-40s (Leer : %s)" % (','.join(self.keller), self._stackEmpty()))
		self.log.debug("-" * 80)
		self.log.debug("")

		if (self.zustand in self.F) and self._stackEmpty() and self._bandEmpty():
			accepted = True
		elif doRaise:
			raise NoAcceptingStateException(self.zustand, self.S)

		if doItVerbose:
			self.log.info("%-10s: %s => %sKZEPTIERT." % ( ("'%s'" % Wort), ' |- '.join(self.ableitung), (accepted and 'A' or 'NICHT A')))
		else:
			self.log.info("Wort '%s' : %skzeptiert." % ( Wort[:-1], (accepted and "A" or "Nicht a") ))

		return accepted

	def _delta(self, Zustand, Zeichen, Kellerzeichen):
		"""
		Ueberfuehrungsfunktion
		"""
		logmessage = "(%s, %s, %s) = " % (Zustand, Zeichen, Kellerzeichen)

		if self.delta[Zustand].has_key( (Zeichen, Kellerzeichen) ):
			(zustandStrich, kellerzeichenStrich) = self.delta[Zustand][(Zeichen, Kellerzeichen)]
			logmessage += "(%s, %s)" % (zustandStrich, ''.join(kellerzeichenStrich))
			rNum = self.rulesDict[(Zustand, Zeichen, Kellerzeichen, zustandStrich, ''.join(kellerzeichenStrich))]
			logmessage = '#%-2d %s' % (rNum, logmessage) 
			self.log.debug(logmessage)
			return self.delta[Zustand][(Zeichen, Kellerzeichen)]
		else:
			logmessage += "(?, ?!)"

		self.log.debug(logmessage)
		raise automaten.NoRuleForStateException(Zustand, explanation='hat keine definierten Regeln fuer (%s, %s)' % (Zeichen, Kellerzeichen))

	def verifyByRegExp(self, testWords=None, regexp=None):
		raise NotImplementedError("Verify By Regular Expression: not applicable.")

if __name__ == '__main__':
	test()