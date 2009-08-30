#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging, logging.config
import os

class NoDeltaError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class Automat(object):
	log = None
	
	def test():
		"""
		doctest (unit testing)
		"""
		import doctest
		failed, total = doctest.testmod()
		print "doctest: %d/%d tests failed." % (failed, total)

	def __init__(self, S=list(), s0=None, F=list(), Sigma=list(), delta=dict(), name="EinAutomat"):
		self.log = logging.getLogger("x")
		if len(self.log.handlers) == 0:
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
		self.Eingabeband = '#'

	def lies(self):
		self.Zustand = self._delta(self.Zustand, self.Eingabeband[0])
		self.Eingabeband = self.Eingabeband[1:]

	def pruefWort(self, Wort):
		self.reset()
		self.Eingabeband = Wort + (not Wort.endswith('#') and '#' or '')
		while self.Zustand:
			altZustand = self.Zustand
			zeichen = self.Eingabeband[0]
			self.lies()
			if self.Zustand:
				self.log.info("[%2s] Lese %2d. Zeichen '%s' => %2s" % (altZustand, self.Lesekopf+1, zeichen, self.Zustand))
				self.Lesekopf += 1

		self.log.info("Das Wort '%s' gehoert%s zur Sprache des Automaten." % (Wort, (self.Zustand in self.F and '' or ' nicht')))
		return self.Zustand in self.F

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
			if Zeichen == '#':
				self.log.debug("Bandzeichen # !")
				return self.Zustand
			for keyObject in self.delta[Zustand].keys():
				if isinstance(keyObject, tuple):
					if Zeichen in keyObject:
						return self.delta[Zustand][keyObject]
				elif Zeichen == keyObject:
					return self.delta[Zustand][keyObject]
			
			self.log.debug("Kein Zustand/Zeichen '%s/%s' ?" % (Zustand, Zeichen))
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

	def _getAsciiArtDeltaTable(self):
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
		s += self._getAsciiArtDeltaTable()
		s += "%80s\n" % ('(' + (self.isDeltaVollstaendig() and 'vollständig' or 'partiell') + ')' )
		s += "%s\n\n" % ("=" * 80)
		return s

	def _TeXNode(self, Zustand, orientation=''):
		styles = ['state']
		description = Zustand
		name = Zustand
		#	\node[initial,state]	(A)						{$q_a$};
		if Zustand == self.s0:
			styles.append('initial')
		if Zustand in self.F:
			styles.append("accepting")
		return "\\node[%s]\t(%s)\t%s\t{%s};" % (','.join(styles), name, orientation, description)

	def _TeXEdge(self, Zustand):
		#(A) edge              node {0,1,L} (B)
		#    edge              node {1,1,R} (C)
		quelle = Zustand
		s = "\t(%s)" % Zustand
		
		erreichbareZiele = dict()
		for zeichen in self.Sigma:
			ziel = self._delta(Zustand, zeichen)
			if ziel:
				if not erreichbareZiele.has_key(ziel):
					erreichbareZiele[ziel] = list()
				erreichbareZiele[ziel].append(zeichen)

		oMoeglichkeiten = ('', '[bend left]', '[bend right]')
		omLen = len(oMoeglichkeiten)
		
		zielZaehler = 0
		for ziel in erreichbareZiele:
			orientation = ''
			if ziel == Zustand:
				orientation = '[loop above]'
			else:
				oNum = zielZaehler % omLen
				orientation = oMoeglichkeiten[oNum]
				zielZaehler +=1

			if len(erreichbareZiele[ziel]) < 5:
				zeichen = ','.join(erreichbareZiele[ziel])
			else:
				zeichen = "%s,..,%s" % (erreichbareZiele[ziel][0], erreichbareZiele[ziel][-1])
			s += "\tedge\t%s\tnode\t{%s}\t(%s)\n\t" % (orientation, zeichen, ziel)
		return s

	def _TeXSpecification(self):
		s = "\\begin{itemize}\n"
		#s = "Deterministischer Automat '%s'\n%s\n" % (self.name, "=" * 80)
		s += "\\item[] Endliche Menge der möglichen Zustände $S = {%s}$\n" % ', '.join(self.S)
		s += "\\item[] %s ist Anfangszustand\n" % self.s0
		s += "\\item[] Menge der Endzustände $F = {%s}$\n" % ', '.join(self.F)
		s += "\\item[] Endliche Menge der Eingabezeichen $\\Sigma = {%s}$\n" % ', '.join(self.Sigma)
		return s + "\n\\end{itemize}"
		
	def _toTeX(self):
		template = 'texOutput/template.tex'
		if not os.path.isfile(template):
			raise IOError("Template '%s' nicht gefunden." % (template))
		content = open(template).read()
		s = content
		tNodes = []
		tEdges = []
		orientation = ''
		for zustand in self.S:
			tNodes.append(self._TeXNode(zustand, orientation))
			tEdges.append(self._TeXEdge(zustand))
			orientation = '[right of=%s]' % zustand
		s = s.replace("%%__NODES__", "\n".join(tNodes))
		s = s.replace("%%__PATH__", "\path\n" + "\n".join(tEdges) + ";\n")
		s = s.replace("%%__SPEC__", self._TeXSpecification())
		
		return s

	def createTeXDocument(self, filename = "texOutput/OUT.tex"):
		out = open(filename, "w")
		rawLines = self._toTeX().split("\n")
		content = list()
		for line in rawLines:
			if not line.strip().startswith("%"):
				content.append(line)
		out.write("\n".join(content))
		out.close()

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
	A.createTeXDocument("texOutput/A.tex")
	
	cS = 's0 s1 s2 s3 s4 s5 s6 s7'.split(' ')
	cs0 = 's0'
	cF = 's2 s4 s7'.split(' ')
	cSigma = '0 1 2 3 4 5 6 7 8 9 + - . e'.split(' ')
	cdelta = {
				's0' : {
							('0', '1', '2', '3', '4', '5', '6', '7', '8', '9') : 's2',
							("+", '-') : 's1',
						},
				's1' : {
							('0', '1', '2', '3', '4', '5', '6', '7', '8', '9') : 's2',
						},
				's2' : {
							('0', '1', '2', '3', '4', '5', '6', '7', '8', '9') : 's2',
							"." : "s3",
							"e" : "s5"
						},
				's3' : {
							('0', '1', '2', '3', '4', '5', '6', '7', '8', '9') : 's4',
						},
				's4' : {
							('0', '1', '2', '3', '4', '5', '6', '7', '8', '9') : 's4',
							"e" : 's5',
						},
				's5' : {
							('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'): 's7',
							("+", '-') : "s6",
						},
				's6' : {
							('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'): 's7',
						},
				's7' : {
							('0', '1', '2', '3', '4', '5', '6', '7', '8', '9') : 's7',
						},
			}
	C = Automat(cS, cs0, cF, cSigma, cdelta, name="C Automat")

	#C.pruefWort("-17.0839292738-")
	C.createTeXDocument("texOutput/C.tex")
