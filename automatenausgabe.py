#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, tempfile, shutil, random, atexit
from subprocess import *
import automaten

WORKINGDIR = os.path.abspath('.')
PDFLATEX_BIN = 'pdflatex'

OUTPUTDIR = os.path.join(WORKINGDIR, 'texOutput')
EPSILON = 'EPSILON'

def test():
	"""
	doctest (unit testing)
	"""
	import doctest, automaten, logging
	automaten.AutomatLogger(logging.DEBUG).log
	failed, total = doctest.testmod()
	print("doctest: %d/%d tests failed." % (failed, total))

class SelfRemovingTempdir(object):
	def __init__(self, workDir=None, removeAtExit=True, log = None):
		self.workDir = workDir
		self.removeAtExit = removeAtExit
		if log == None:
			import automaten
			log = automaten.AutomatLogger().log
		self.log = log
		self.tmp = tempfile.mkdtemp(dir=workDir)
		if self.removeAtExit:
			atexit.register(self._atExitHooker)
		self.log.debug("tmp: %s, removed at exit : %s" % (self.tmp, self.removeAtExit))
	
	def _getRandomFilename(self, seq=list("a7ksLo2ksk38AOIDHJKgbenmguziwoamna35678923ohdskljjhwriu"), length=18):
		random.shuffle(seq)
		filename = ''.join(seq)
		return filename[:length]
	
	def getRandomFilename(self):
		return os.path.join(self.tmp, self._getRandomFilename())

	def _atExitHooker(self):
		if self.removeAtExit:
			self.log.debug("Removing tmp '%s'" % self.tmp)
			shutil.rmtree(self.tmp)

def runCommand(command, parameter=None, logger=None, workDir=os.getcwd(), validReturnCodes = [0]):
	if logger == None:
		import automaten
		logger = automaten.AutomatLogger().log

	cwd = os.getcwd()
	cmd = command 
	if parameter:
		cmd += ' ' + parameter
	buffer=1024
	retcode = -1
	stdout = ''
	stderr = ''

	logger.debug("Ausfuehren : '%s'" % cmd)
	try:
		os.chdir(workDir)
		p = Popen(cmd, shell=True, bufsize=buffer, stdout=PIPE, stderr=PIPE, close_fds=True)
		p.wait()
		retcode = p.returncode
		stdout = p.stdout.read()
		stderr = p.stderr.read()
		if not retcode in validReturnCodes:
			if retcode < 0:
				logger.error("Ausfuehrung schlug fehl : %d" % -retcode)
			elif retcode > 0:
				logger.warning("Ausfuehrung return code : %d" % retcode)
			logger.error("%s" % cmd)
			logger.error("STDERR Output:")
			logger.error(stderr)
			logger.debug("STDOUT Output:")
			logger.debug(stdout)
	except OSError, e:
		logger.critical("Ausfuehrung schlug fehl: %s" %  e)
	logger.debug("return code : '%s'" % retcode)
	os.chdir(cwd)
	return (retcode, stdout, stderr)

def kuerzMenge(items, max=5):
	if len(items) < max:
		zeichen = ','.join(items)
	else:
		zeichen = "%s,..,%s" % (items[0], items[-1])
	return zeichen

class AusgebenderAutomat(object):
	def __init__(self):
		self.log = automaten.AutomatLogger().log
		#self.log.debug("I live ... again")

	def kuerzMenge(self, items, max=5):
		self.log.debug("kuerzmenge(%s, %s)" % (items, max))
		if len(items) < max:
			zeichen = ','.join(items)
		else:
			zeichen = "%s,..,%s" % (items[0], items[-1])
		return zeichen

	def _fzAscii(self, what):
		"""
		String-Representation einer Menge (frozenset).
			*	Falls Menge aus nur einem Element besteht, wird dieses als String zurueckgegeben,
			*	falls Menge leer, wird '-' zurueckgegeben, 
			*	andernfalls ein String der Form {a,b,c,d,e,f}
		"""
		if len(what) == 1:
			return list(what)[0]
		if len(what) == 0:
			return '-'
		return '{%s}' % ','.join(sorted(what))

	def _readTemplate(self, template):
		if not os.path.isfile(template):
			raise IOError("Template '%s' nicht gefunden." % (template))
		return open(template).read()

	def writeContent(self, target, content):
		if isinstance(content, list):
			content = "\n".join(content)
		try:
			out = open(target, "w")
			out.write(content)
			out.close()
			return True
		except Exception, e:
			self.log.error(e)
		return False

	def writePlaintext(self, targetDir='.', targetFile=None, prefix='', suffix='.automat'):
		if not targetFile:
			targetFile = self.name.lower()
			if targetFile == '':
				print "OUCH, targetFile=''"
				return False
			target = os.path.join(os.path.abspath(targetDir), prefix + targetFile + suffix)
		else:
			target = targetFile
		return self.writeContent(target, self._plaintext())

class OPlaintextAutomat(AusgebenderAutomat):
	def _addHeader(self):
		out = list(['# Automatendefinition'])
		out.append("Name: %s" % self.name)
		if self.beschreibung:
			out.append("Beschreibung: %s" % self.beschreibung)
		try:
			if self.type:
				out.append("Type: %s" % self.type)
		except Exception, e:
			pass
		return out

	def _addSigma(self):
		return ['# Alphabet definieren. Muss mit "Sigma:" beginnen, durch Whitespace getrennt.', "Sigma:\t" + ' '.join(sorted(list(self.Sigma))) ]

	def _addS0(self):
		return ['# Startzustand definieren. Muss mit "s0:" beginnen, durch Whitespaces getrennt.', "s0:\t" + ' '.join(sorted(list(self.s0))) ]

	def _addF(self):
		return ['# Finale Zustaende definieren. Muss mit "F:" beginnen, durch Whitespace getrennt.', "F:\t" + ' '.join(sorted(list(self.F))) ]

	def _addS(self):
		return ['# (NEA, DEA: Optional) Zustaende definieren.', 
			'# (NEA,DEA: Falls nicht definiert, werden Zustaende aus den Uebergaengen zusammengestellt.)',
			'# Muss mit "S:" beginnen, durch Whitespace getrennt.',
			"S:\t" + ' '.join(sorted(list(self.S))) ]

	def _addTestWords(self):
		if self.testWords:
			if len(self.testWords) > 0:
				return ['# Testworte. Muss mit "TestWords:" beginnen, durch Whitespace getrennt.', "TestWords:\t" + ' '.join(sorted(list(self.testWords))) ]
		return list()

	def _addVerifyRegExp(self):
		if self.verifyRegExp:
			return ['# Regular Expression, die das Ergebnis fuer die Testworte definiert.',
					'# Muss mit "RegularExpression:" beginnen, durch Whitespace getrennt.', 
					"RegularExpression:\t " + self.verifyRegExp ]
		return list()

	def _addDelta(self):
		out = list(['# Uebergaenge, Format :', '# Zustand, Zeichen, Zielzustand (durch whitespace getrennt)', 
		'# Zeichen kann ein einzelnes Zeichen oder durch Kommas separierte Zeichenmenge sein (OHNE whitespace!)'])
		
		for zustand in sorted(self.delta.keys()):
			for fzKeyset in self.delta[zustand]:
				ziele = self.delta[zustand][fzKeyset]
				
				for zeichen in reversed(sorted(fzKeyset)):
					for zielZustand in sorted(ziele):
						self.log.debug("%s %s %s" % (zustand, zeichen, zielZustand))
						out.append("%s\t%s\t%s" % (zustand, zeichen, zielZustand))
		return out

	def _addVerifyWords(self):
		if not self.verifyWords:
			return list()
		out = list()
		failingWords = list()
		acceptedWords = list()
		
		for word in self.verifyWords:
			result = self.verifyWords[word]
			if result == True:
				acceptedWords.append(word)
			else:
				failingWords.append(word)

		if len(failingWords) > 0:
			out += ['# Optional: Worte, die _nicht akzeptiert werden duerfen', '# Muss mit "FailingVerifyWords:" beginnen, durch Whitespace getrennt' ]
			out.append("%s:\t%s" % ('FailingVerifyWords', ' '.join(failingWords)))
		if len(acceptedWords) > 0:
			out += ['# Optional: Worte, die akzeptiert werden muessen', '# Muss mit "AcceptedVerifyWords:" beginnen, durch Whitespace getrennt' ]
			out.append("%s:\t%s" % ('AcceptedVerifyWords', ' '.join(acceptedWords)))
		return out

	def _plaintext(self, joiner="\n", pretty=True):
		LINE = ['#' * 80]
		SPACER = ['']
		
		out = list()
		if pretty:
			out += LINE
		out += self._addHeader()
		if pretty:
			out += LINE + SPACER + SPACER
		out += self._addSigma()
		if pretty:
			out += SPACER
		out += self._addS0()
		if pretty:
			out += SPACER
		out += self._addS()
		if pretty:
			out += SPACER
		out += self._addF()
		if pretty:
			out += SPACER
		out += self._addDelta()
		if pretty:
			out += SPACER
		out += self._addVerifyWords()
		if pretty:
			out += SPACER
		out += self._addTestWords()
		if pretty:
			out += SPACER
		out += self._addVerifyRegExp()
		if pretty:
			out += SPACER
		return joiner.join(out)

class OAsciiAutomat(AusgebenderAutomat):
	def _getAsciiArtDeltaTable(self, prefix=' '):
		pfxLen = len(prefix)
		rows = list([prefix + "Überführungsfunktion:"])
		maxLength = 1

		for zeichen in self.Sigma:
			zLength = len(self._fzString(zeichen)) 
			if  zLength > maxLength:
				maxLength = zLength

		for zustand in self.S:
			zLength = len(str(zustand))
			if  zLength > maxLength:
				maxLength = zLength
			try:
				zielLength = len(self._fzString(self._delta__str__(zustand, zeichen)))
				if  zielLength > maxLength:
					maxLength = zielLength
			except Exception,e:
				pass

		fmtString = '%' + str(maxLength) + 's'
		deltaString = ' ' * (maxLength-1) + 'δ'
		
		headParts = [deltaString]
		for zeichen in sorted(self.Sigma):
			headParts.append(fmtString % zeichen)

		rows.append(prefix + ' | '.join(headParts))
		strich = '-' * maxLength
		strichParts = list([(fmtString % strich)] * len(headParts))
		rows.append(prefix + "-+-".join(strichParts) + '-')

		for zustand in sorted(self.S):
			rowParts = [(fmtString % zustand)]
			rowPrefix = (zustand in self.F and '*' * len(prefix) or prefix)
			for zeichen in sorted(self.Sigma):
				sZustand = '!'
				try:
					zielZustand = self._delta__str__(zustand, zeichen)
					sZustand = self._fzAscii(zielZustand)
				except Exception, e:
					print e
					sZustand = '/'
				rowParts.append(fmtString % sZustand)
			rows.append(rowPrefix + ' | '.join(rowParts))

		return "\n".join(rows) + "\n"

class ODotAutomat(AusgebenderAutomat):
	def _DotPath(self, quelle, ziel, zeichenString):
		# ziel muss frozenset sein .. strings werden zerhackt
		label = self._fzAscii(zeichenString)
		if label == EPSILON:
			label = 'ε'
		p = '%s -> %s [ label = "%s" ];' % (quelle, self._fzAscii(ziel), label)
		#self.log.debug(p)
		return p
		
	def _toDot(self, template):
		s = self._readTemplate(template)
		s = s.replace('//__FINAL_STATES__', ' '.join(self.F) + ";\n")
		s = s.replace('//__ORIGIN__', "null -> %s;\n" % self._fzAscii(self.s0))
		nodes = []
		
		for zustand in self.delta:
			for zeichen in self.delta[zustand].keys():
				ziel = self.delta[zustand][zeichen]
				if isinstance(zeichen, tuple):
					self.log.warning(zeichen)
					zeichen = kuerzMenge(zeichen)
				if isinstance(ziel, frozenset) and len(ziel) > 1:
					for item in ziel:
						nodes.append(self._DotPath(zustand, frozenset([item]), zeichen))
				else:
					nodes.append(self._DotPath(zustand, ziel, zeichen))
		s = s.replace('//__PATH__', "\n".join(nodes))
		return s

	def createDotDocument(self, template = None, dumpOnly=False):
		if not template:
			template = os.path.join(os.path.abspath('output_templates'), 'automat.dot')

		tdir = SelfRemovingTempdir()
		basename = tdir.getRandomFilename()

		dot_filename = basename + '.gv'
		pdf_filename = basename + '.pdf'

		returnValue = pdf_filename

		rawLines = self._toDot(template).split("\n")
		content = list()
		for line in rawLines:
			if not line.strip().startswith("//"):
				content.append(line)
		
		if dumpOnly:
			return "\n".join(content)

		if not self.writeContent(dot_filename, content):
			returnValue = False
		
		if returnValue:
			param = '-Tpdf -o "%s" "%s"' % (pdf_filename, dot_filename)
			(rc, out, err) = runCommand('dot', param, logger=self.log, workDir=tdir.tmp)
			if rc != 0:
				print err
				print "----------------------"
				print out
				returnValue = False
		
		return returnValue

class OLaTeXAutomat(AusgebenderAutomat):
	"""
	>>> o = OLaTeXAutomat()
	>>> o._mangleState("hihi")
	'hihi'
	>>> o._mangleState("s0")
	'{s_0}'
	>>> o._mangleState("s_0")
	'{s_0}'
	"""
	import re
	statePattern = r'([a-zA-Z]+)(_?)(\d+)'
	stateRegexp = re.compile(statePattern)

	def _fzTex(self, what):
		"""
		String-Representation einer Menge (frozenset).
			*	Falls Menge aus nur einem Element besteht, wird dieses als String zurueckgegeben,
			*	falls Menge leer, wird '' zurueckgegeben, 
			*	andernfalls ein String der Form a, b, c, d, e, f
		"""
		if len(what) == 1:
			return list(what)[0]
		if len(what) == 0:
			return '-'
		return ', '.join(sorted(what))

	def _fzTexM(self, what):
		"""
		String-Representation einer Menge (frozenset).
			*	Falls Menge aus nur einem Element besteht, wird dieses als String zurueckgegeben,
			*	falls Menge leer, wird '' zurueckgegeben, 
			*	andernfalls ein String der Form a, b, c, d, e, f
		Diese Methode sorgt zusaetzlich noch fuer eine "mathematische" Repraesentation von 
		Zustaenden, also wird aus s0 "ein s mit einer tiefgestellten 0".
		"""
		if len(what) == 1:
			return self._mangleState(list(what)[0])
			#return list(what)[0]
		if len(what) == 0:
			return '-'
		mangled = list()
		for item in sorted(what):
			mangled.append(self._mangleState(item))
		return ', '.join(mangled)
		#return ', '.join(sorted(what))

	def _listTexM(self, what):
		"""
		String-Representation einer Menge (frozenset).
			*	Falls Menge aus nur einem Element besteht, wird dieses als String zurueckgegeben,
			*	falls Menge leer, wird '' zurueckgegeben, 
			*	andernfalls ein String der Form a, b, c, d, e, f
		Diese Methode sorgt zusaetzlich noch fuer eine "mathematische" Repraesentation von 
		Zustaenden, also wird aus s0 "ein s mit einer tiefgestellten 0".
		"""
		if len(what) == 1:
			return self._mangleState(list(what)[0])
		if len(what) == 0:
			return '-'
		mangled = list()
		for item in what:
			mangled.append(self._mangleState(item))
		return ''.join(mangled)

	def _mangleName(self, name):
		"""
		Einen Namen fuer LaTeX aufbereiten ('_' durch Leerzeichen ersetzen)
		"""
		return name.replace("_", ' ')

	def _mangleState(self, state):
		"""
		Zustandbezeichner verschoenern
		"""
		m = OLaTeXAutomat.stateRegexp.match(state)
		if m:
			state = '{%s_%s}' % (m.group(1), m.group(3))
		return state

	def _TeXIncludeFigure(self, file, caption=None, label=None):
		"""
		Ein Bild einfuegen, ggf mit caption und label ..
		"""
		label = label and (r'\label{%s}' % label) or ''
		caption = caption and (r'\caption{%s}' % caption) or ''
		return """
		\\begin{figure}[ht!]
		\\centering
		\\includegraphics[width=1.0\linewidth]{%s}
		%s
		%s
		\\end{figure}
		""" % (file, caption, label)

	def _TeXSpecification(self):
		"""
		Auotmaten-Spezifikation hinzufuegen
		"""
		s = list()
		aTyp = "(%seterministischer) Automat" % ((self.istDEA() and 'D' or 'Nichtd'))

		name = self._mangleName(self.name)
		
		s.append(r'\textbf{%s \emph{%s}}' % (aTyp, name))
		sigmaKopie = self.Sigma
		if EPSILON in sigmaKopie:
			s.append(r" ($\epsilon$-Übergänge möglich)")
			sigmaKopie = self.Sigma.difference(frozenset([EPSILON])).union(frozenset(['$\epsilon$']))

		if self.beschreibung :
			s.append(r"\newline \emph{%s}" % self.beschreibung)
		s.append(r"\begin{itemize}")
		s.append(r'\item[] Endliche Menge der möglichen Zustände $S = \{%s\}$' % self._fzTex(self.S))
		s.append(r"\item[] \{%s\} ist Anfangszustand" % self._fzTex(self.s0))
		s.append(r"\item[] Menge der Endzustände $F = \{%s\}$" % self._fzTex(self.F))
		s.append(r"\item[] Endliche Menge der Eingabezeichen $\Sigma = \{%s\}$" % self._fzTex(sigmaKopie))
		if self.verifyRegExp:
			s.append(r"\item[] Regulärer Ausdruck zur Verifikation $%s$" % self.verifyRegExp)
		
		s.append(r'\end{itemize}')
		return "\n".join(s)

	def _TeXDeltaTable(self):
		"""
		Ueberfuehrungsfunktions-Tabelle hinzufuegen
		"""
		s = list()
		headerLine = [r'$\delta$']
		sortedSigma = sorted(self.Sigma)
		
		for zeichen in sortedSigma:
			if zeichen == EPSILON:
				zeichen = '$\epsilon$'
			headerLine.append(zeichen)
		
		s.append(r'\begin{table}[ht]')
		s.append(r'\begin{tabular}{r|%s}' % ('c' * (len(headerLine)-1)))
		s.append(r' & '.join(headerLine) + r' \\')
		s.append(r'\hline')

		for zustand in sorted(self.S):
			line = [ (zustand in self.F and '{*}' or '') + zustand ]
			for zeichen in sortedSigma:
				zielZustand = self._delta__str__(zustand, zeichen)
				line.append(self._fzTex(zielZustand))
			s.append(r' & '.join(line))
			s.append(r' \\')
		
		s.append(r'\end{tabular}')
		s.append(r'\caption{Überführungstabelle für %s}' % self._mangleName(self.name))
		s.append(r'\end{table}')

		return "\n".join(s)

	def _TeXResults(self):
		"""
		Testergebnisse hinzufuegen
		"""
		s = ''
		if self.testWords:
			testResults = [ r'\subsection{Test}', r'\begin{longtable}{lll}' ]
			testResults.append(r'Erfolg & Wort & Ergebnis\\')
			testResults.append(r'\hline')
			for (word, successful, result) in self.checkWords(self.testWords):
				t = list()
				t.append(r'{\small %s}' % (successful and "OK" or r'\textbf{KO}'))
				t.append(r'{\small %s}' % word)
				t.append(r'{\small \emph{%s}}' % result)
				testResults.append(' & '.join(t) + r'\\')
			testResults.append(r'\end{longtable}')
			s = "\n".join(testResults)
		return s

	def _TeXVerify(self):
		"""
		Verifikationsergebnisse hinzufuegen
		"""
		s = ''
		if self.verifyWords:
			testResults = [ r'\subsection{Verifikationstests}', r'\begin{longtable}{llll}' ]
			testResults.append(r'Wort & Erwartungswert & Ergebnis & Verifiziert\\')
			testResults.append(r'\hline')
			for word in self.verifyWords:
				expected = self.verifyWords[word]
				
			for (word, successful, result) in self.checkWords(self.verifyWords.keys()):
				t = list()
				t.append(r'{\small %s}' % word)
				t.append(r'{\small %s}' % self.verifyWords[word])
				t.append(r'{\small \emph{%s, %s}}' % (successful, result))
				t.append(r'{\small %s}' % ((self.verifyWords[word] == successful) and "ja" or r'\textbf{NEIN}'))
				testResults.append(' & '.join(t) + r'\\')
			testResults.append(r'\end{longtable}')
			s = "\n".join(testResults)
		return s

	def _TeXAutomatStart(self):
		"""
		Automatenbeschreibung und -definition beginnen
		"""
		return r'\section{Automat %s}' % self._mangleName(self.name)

	def _toTeX(self, template=None, dot_template=None):
		"""
		Automat definieren und beschreiben.
		Falls eine der Komponenten (Spezifikation, Test, Ueberfuehrungstabelle ..) 
		nicht hinzugefuegt werden konnte (also eine Exception geworfen wurde), 
		wird dieser Fehler geloggt, aber ignoriert.
		"""
		s = self._readTemplate(template)

		try:
			s = s.replace("%%__AUTOMAT__", self._TeXAutomatStart())
		except Exception, e:
			self.log.warning("calling _TeXAutomatStart() failed.")
			self.log.warning(e)

		try:
			s = s.replace("%%__SPEC__", self._TeXSpecification())
		except Exception, e:
			self.log.warning("calling _TeXSpecification() failed.")
			self.log.warning(e)

		try:
			s = s.replace("%%__DELTA__", self._TeXDeltaTable())
		except Exception, e:
			self.log.warning("calling _TeXDeltaTable() failed.")
			self.log.warning(e)

		try:
			s = s.replace('%%__RESULTS__', self._TeXResults())
		except Exception, e:
			self.log.warning("calling _TeXResults() failed.")
			self.log.warning(e)

		try:
			s = s.replace('%%__VERIFY__', self._TeXVerify())
		except Exception, e:
			self.log.warning("calling _TeXVerify() failed.")
			self.log.warning(e)

		try:
			if 'createDotDocument' in dir(self):
				dotgraph = self.createDotDocument(dot_template)
				if dotgraph:
					aName = self._mangleName(self.name)
					label = 'dot%s' % aName 
					caption = 'Automat %s' % aName
					s = s.replace('%%__DOT_GRAPH__', r'\subsection{Graph}' + self._TeXIncludeFigure(dotgraph, caption, label))
				else:
					self.log.debug("Es wurde kein DOT Graph hinzugefuegt.")
		except Exception, e:
			self.log.warning("calling createDotDocument() failed.")
			self.log.warning(e)

		return s

class OPlaintextKellerAutomat(AusgebenderAutomat):
	def _addVerifyRegExp(self):
		return list()

	def _addS0(self):
		return ['# Startzustand definieren. Muss mit "s0:" beginnen, durch Whitespaces getrennt.', 
				"s0:\t%s" % self.s0 ]

	def _addK0(self):
		return ['# Initialer Kellerinhalt. Muss mit "k0:" beginnen, durch Whitespaces getrennt.', 
				"k0:\t%s" % self.k0 ]

	def _addK(self):
		return ['# Endliche Menge der Kellerzeichen k. Muss mit "K:" beginnen, durch Whitespace getrennt', "K:\t" + ' '.join(sorted(list(self.K))) ]

	def _plaintext(self, joiner="\n", pretty=True):
		LINE = ['#' * 80]
		SPACER = ['']

		specialK = list()

		specialK += self._addK0()
		if pretty:
			specialK += SPACER
		specialK += self._addK()

		return OPlaintextAutomat._plaintext(self) + joiner.join(specialK)

	def _addDelta(self):
		out = list(['# Uebergaenge, Format :', 
		'# Zustand, Zeichen, Kellerzeichen, Zielzustand, Kellerzeichen(push) (durch whitespace getrennt)',
		'# Mehrere (push) Kellerzeichen muessen durch + getrennt werden])'])
		
		#self.delta[zustand][(bandzeichen, kellerzeichen)] = (zustandStrich, kellerzeichenStrich)

		for zustand in sorted(self.delta.keys()):
			for (bandzeichen, kellerzeichen) in self.delta[zustand]:
			 	(zustandStrich, kellerzeichenStrich) = self.delta[zustand][(bandzeichen, kellerzeichen)]
			 	kellerzeichenStrich = '+'.join(kellerzeichenStrich)
				self.log.debug("(%s, %s, %s) = (%s, %s)" % (zustand, bandzeichen, kellerzeichen, zustandStrich, kellerzeichenStrich))
				out.append("%s\t%s\t%s\t%s\t%s" % (zustand, bandzeichen, kellerzeichen, zustandStrich, kellerzeichenStrich))
		return out


####################################################################################################
# KELLERAUTOMATEN: ANFANG
####################################################################################################
class AusgebenderKellerAutomat(AusgebenderAutomat):
	def _getRulesHash(self):
		rulesHash = dict()

		for zustand in sorted(self.delta.keys()):
			# geordnete Bandzeichen- und Kellerzeichenlisten
			bandzeichenListe = set()
			kellerzeichenListe = set()
			for (b, k) in self.delta[zustand].keys():
				bandzeichenListe.add(b)
				kellerzeichenListe.add(k)
			bandzeichenListe = sorted(list(bandzeichenListe))
			kellerzeichenListe = sorted(list(kellerzeichenListe))
			
			for bandzeichen in bandzeichenListe:
				for kellerzeichen in kellerzeichenListe:
					if self.delta[zustand].has_key((bandzeichen, kellerzeichen)):
						(zustandStrich, kellerzeichenStrich) = self.delta[zustand][(bandzeichen, kellerzeichen)]
						rNum = self.rulesDict[(zustand, bandzeichen, kellerzeichen, zustandStrich, ''.join(kellerzeichenStrich))]
						rulesHash[rNum] = (zustand, bandzeichen, kellerzeichen, zustandStrich, kellerzeichenStrich)

		return rulesHash

class OAsciiKellerAutomat(AusgebenderKellerAutomat):
	def _getAsciiArtDeltaTable(self, prefix=' '):
		lines = list()
		rulesHash = self._getRulesHash()
		for k in sorted(rulesHash.keys()):
			(zustand, bandzeichen, kellerzeichen, zustandStrich, kellerzeichenStrich) = rulesHash[k]
			lines.append("%s#%d %s(%s, %s, %-2s) = (%s, %s)" % (prefix + ' ' * 4, k, 'δ', zustand, bandzeichen, kellerzeichen, zustandStrich, ''.join(kellerzeichenStrich)))
		if len(lines) > 0:
			lines = [ prefix + 'Überführungsregeln                      :'] + lines
		else:
			lines = ['HMM .. KEINE Regeln definiert ??']
		return "\n".join(lines)
		
		for zustand in sorted(self.delta.keys()):
			# geordnete Bandzeichen- und Kellerzeichenlisten
			bandzeichenListe = set()
			kellerzeichenListe = set()
			for (b, k) in self.delta[zustand].keys():
				bandzeichenListe.add(b)
				kellerzeichenListe.add(k)
			bandzeichenListe = sorted(list(bandzeichenListe))
			kellerzeichenListe = sorted(list(kellerzeichenListe))
			
			rulesHash = dict()
			for bandzeichen in bandzeichenListe:
				for kellerzeichen in kellerzeichenListe:
					if self.delta[zustand].has_key((bandzeichen, kellerzeichen)):
						(zustandStrich, kellerzeichenStrich) = self.delta[zustand][(bandzeichen, kellerzeichen)]
						rNum = self.rulesDict[(zustand, bandzeichen, kellerzeichen, zustandStrich, ''.join(kellerzeichenStrich))]
						rulesHash[rNum] = "%s#%d %s(%s, %s, %-2s) = (%s, %s)" % (prefix + ' ' * 4, rNum, 'δ', zustand, bandzeichen, kellerzeichen, zustandStrich, ''.join(kellerzeichenStrich))
			for k in sorted(rulesHash.keys()):
				lines.append(rulesHash[k])
		if len(lines) > 0:
			lines = [ prefix + 'Überführungsregeln                      :'] + lines
		else:
			lines = ['HMM .. KEINE Regeln definiert ??']
		return "\n".join(lines)

class OLaTeXKellerAutomat(AusgebenderKellerAutomat, OLaTeXAutomat):
	def createDotDocument(self, dot_template=None):
		"""
		Es gibt keine dot-Graphik fuer Kellerautomaten
		"""
		return False

	def _TeXSpecification(self):
		s = list()
		aTyp = "Deterministischer Kellerautomat"
		name = self._mangleName(self.name)

		s.append(r'\textbf{%s \emph{%s}}' % (aTyp, name))

		if self.beschreibung :
			s.append(r"\newline \emph{%s}" % self.beschreibung)
		s.append(r"\begin{itemize}")
		s.append(r'\item[] Endliche Menge der möglichen Zustände $S = \{%s\}$' % self._fzTexM(self.S))
		s.append(r"\item[] $%s$ ist Anfangszustand" % self._mangleState(self.s0))
		s.append(r"\item[] Menge der Endzustände $F = \{%s\}$" % self._fzTexM(self.F))
		s.append(r"\item[] Menge der Kellerzeichen $K = \{%s\}$" % self._fzTexM(self.K))
		s.append(r"\item[] $%s$ ist Kellerstartzeichen" % self._mangleState(self.k0))
		s.append(r"\item[] Endliche Menge der Eingabezeichen $\Sigma = \{%s\}$" % self._fzTex(self.Sigma))
		s.append(r"\item[] Akzeptieren durch: \emph{%s}" % self.ACCEPT_DESCRIPTION[self.accept])
		s.append(r'\end{itemize}')
		return "\n".join(s)

	def _TeXDeltaTable(self):
		s = list()
		s.append(r"\begin{itemize}")

		rulesHash = self._getRulesHash()
		for rNum in sorted(rulesHash.keys()):
			(zustand, bandzeichen, kellerzeichen, zustandStrich, kellerzeichenStrich) = rulesHash[rNum]
			kellerzeichenStrichString = ''
			zustand = self._mangleState(zustand)
			zustandStrich = self._mangleState(zustandStrich)
			if bandzeichen == EPSILON:
					bandzeichen = r'\varepsilon'
			for kellerzeichen in kellerzeichenStrich:
				if kellerzeichen == EPSILON:
					kellerzeichen = r'\varepsilon'
				else:
					kellerzeichen = self._mangleState(kellerzeichen)
				kellerzeichenStrichString += kellerzeichen
			s.append(r"\item[(%s)] $\delta(%s, %s, %s) = (%s, %s)$" % (rNum, zustand, bandzeichen, kellerzeichen, zustandStrich, kellerzeichenStrichString))

		s.append(r'\end{itemize}')
		return "\n".join(s)
	
	def X_TeXResults(self):
		s = ''
		return s
		if self.testWords:
			testResults = [ r'\subsection{Test}', r'\begin{longtable}{lll}' ]
			testResults.append(r'Erfolg & Wort & Ergebnis\\')
			testResults.append(r'\hline')
			testMitPfadListe = list()
			
			for (word, successful, result, pfad) in self.checkWordsX(self.testWords):
				t = list()
				t.append(r'{\small %s}' % (successful and "OK" or r'\textbf{KO}'))
				t.append(r'{\small %s}' % word)
				t.append(r'{\small \emph{%s}}' % result)
				testResults.append(' & '.join(t) + r'\\')
				testMitPfadListe.append((word, pfad))
			testResults.append(r'\end{longtable}')
			
			testResults.append(r'\subsubsection{Ableitungspfade}')
			testResults.append(r"\begin{itemize}")
			for (word, pfad) in testMitPfadListe:
				testResults.append(r'\item[%s] %s' % (word, r' \vdash '.join(pfad)))
			testResults.append(r'\end{itemize}')
			s = "\n".join(testResults)
		return s

	def _TeXVerify(self):
		s = ''
		if self.verifyWords:
			testResults = [ r'\subsection{Verifikationstests}', r'\begin{longtable}{llll}' ]
			testResults.append(r'Wort & Erwartung & Ergebnis & Verifiziert\\')
			testResults.append(r'\hline')
			for word in self.verifyWords:
				expected = self.verifyWords[word]

			wpList = list()
			
			for (word, successful, result, pfad) in self.checkWordsX(self.verifyWords.keys()):
				t = list()
				t.append(r'{\small %s}' % word)
				t.append(r'{\small %s}' % self.verifyWords[word])
				t.append(r'{\small \emph{%s, %s}}' % (successful, result))
				t.append(r'{\small %s}' % ((self.verifyWords[word] == successful) and "ja" or r'\textbf{NEIN}'))
				testResults.append(' & '.join(t) + r'\\')
				wpList.append((word, pfad, successful))
			testResults.append(r'\end{longtable}')

			testResults.append(r'\subsubsection{Ableitungspfade}')
			testResults.append(r"\begin{itemize}")

			for (word, pfad, successful) in wpList:
				parts = list()
				for item in pfad:
					(zustand, band, keller) = item
					band = band.replace("#", "\#")
					parts.append("(%s, %s, %s)" % (self._mangleState(zustand), band, self._listTexM(keller) ))
				cesar = r'%s $%s L(KA)$' % (word, successful and r'\in' or r'\notin')
				testResults.append(r'\item[%s] $%s$\newline %s' % (word, r' \vdash '.join(parts), cesar))
			testResults.append(r'\end{itemize}')

			s = "\n".join(testResults)
		return s
####################################################################################################
# KELLERAUTOMATEN: ENDE
####################################################################################################


####################################################################################################
# TURINGMASCHINEN: ANFANG
####################################################################################################
class OAsciiTuringmachine(AusgebenderAutomat):
	def _getAsciiArtDeltaTable(self, prefix=' '):
		pfxLen = len(prefix)
		rows = list([prefix + "Maschinentafel:"])
		
		#: Beschreibungsfeldinhalt
		descField = ' S \ B'
		
		#: Maximale Laenge der Zustandnamen
		zustandMaxLength = len(descField)

		#: Sortierte Bandzeichenmenge
		sortedB = sorted(self.B)
		
		for zustand in self.S:
			zLength = len(str(zustand))
			if  zLength > zustandMaxLength:
				zustandMaxLength = zLength

		#: Feldbreite
		fieldWidth = zustandMaxLength + 1 + 2 + 2 +2
		# Bandzeichenlaenge(1) + maximale Laenge der Zustandnamen(?) + Kommas(2) + Blanks(2) + Klammern(2)
		
		fmtStringZustand = '%-' + str(zustandMaxLength) + 's'
		fmtStringField = '%-' + str(fieldWidth) + 's'

		# Header generieren ..
		headParts = [fmtStringZustand % descField]
		for bandzeichen in sortedB:
			headParts.append(fmtStringField % bandzeichen)
		rows.append(prefix + ' | '.join(headParts))

		# Striche 
		strichZustand = '-' * zustandMaxLength
		strich = '-' * fieldWidth
		strichParts = list([fmtStringZustand % strichZustand]) + [(fmtStringField % strich)] * (len(headParts)-1)
		rows.append(prefix + "-+-".join(strichParts) + '-')

		for zustand in sorted(self.S):
			rowParts = [(fmtStringZustand % zustand)]
			rowPrefix = (zustand in self.F and '*' * len(prefix) or prefix)
			
			for zeichen in sortedB:
				sZustand = '-'
				if self.validDelta(zustand, zeichen):
					(zustandStrich, bandzeichenStrich, aktion) = self.delta[zustand][zeichen]
					sZustand = '(%s, %s, %s)' % ( zustandStrich, bandzeichenStrich, self.AKTION_DESCRIPTION[aktion])

				rowParts.append(fmtStringField % sZustand)
			rows.append(rowPrefix + ' | '.join(rowParts))

		return "\n".join(rows) + "\n"

class OLaTeXTuringmaschine(OLaTeXAutomat):
	def _mangleAktion(self, aktion):
		"""
		Bandbewegungsbeschreibung fuer Menschen aufbereiten
		"""
		from turingmachine import TuringMachine
		if aktion == TuringMachine.HALT:
			return 'h'
		elif aktion == TuringMachine.LEFT:
			return 'l'
		return 'r'

	def createDotDocument(self, dot_template=None):
		"""
		Es gibt keine dot-Graphik fuer Turingmaschinen
		"""
		return False

	def _TeXSpecification(self):
		s = list()
		aTyp = "Turingmaschine"
		name = self._mangleName(self.name)

		s.append(r'\textbf{%s \emph{%s}}' % (aTyp, name))

		if self.beschreibung :
			s.append(r"\newline \emph{%s}" % self.beschreibung)
		s.append(r"\begin{itemize}")
		s.append(r'\item[] Endliche Menge der möglichen Zustände $S = \{%s\}$' % self._fzTexM(self.S))
		s.append(r"\item[] $%s$ ist Anfangszustand" % self._mangleState(self.s0))
		s.append(r"\item[] Menge der Endzustände $F = \{%s\}$" % self._fzTexM(self.F))
		s.append(r"\item[] Menge der Bandzeichen $B = \{%s\}$" % self._fzTex(self.B))
		s.append(r"\item[] Endliche Menge der Eingabezeichen $\Sigma = \{%s\}$" % self._fzTex(self.Sigma))
		s.append(r'\end{itemize}')
		return "\n".join(s)

	def _TeXDeltaTable(self):
		"""
		Ueberfuehrungsfunktions-Tabelle hinzufuegen
		"""
		s = list()
		sortedSigma = sorted(self.Sigma)
		sortedB = sorted(self.B)
		
		headerLine = [''] + sortedB
		
		s.append(r'\begin{table}[ht]')
		s.append(r'\begin{tabular}{r|%s}' % ('c' * (len(headerLine)-1)))
		s.append(r' & '.join(headerLine) + r' \\')
		s.append(r'\hline')

		for zustand in sorted(self.S):
			line = [ (zustand in self.F and '{*}' or '') + '$%s$' % self._mangleState(zustand) ]
			for bandzeichen in sortedB:
				if self.validDelta(zustand, bandzeichen):
					(zustandStrich, bandzeichenStrich, aktion) = self._delta(zustand, bandzeichen)
					zielKonfiguration = '($%s$, %s, %s)' % (self._mangleState(zustandStrich), bandzeichenStrich, self._mangleAktion(aktion))
				else:
					zielKonfiguration = '-'
				line.append(zielKonfiguration)
			s.append(r' & '.join(line))
			s.append(r' \\')
		
		s.append(r'\end{tabular}')
		s.append(r'\caption{Maschinentafel für %s}' % self._mangleName(self.name))
		s.append(r'\end{table}')
		return "\n".join(s)

	def _TeXVerify(self):
		"""
		Verifikationsergebnisse hinzufuegen
		"""
		s = ''
		if self.verifyWords:
			testResults = [ r'\subsection{Verifikationstests}', r'\begin{longtable}{llp{4cm}lcc}' ]
			testResults.append(r'Wort & E-wert & Ergebnis & Bandinhalt & Chr,Idx & Verifiziert\\')
			testResults.append(r'\hline')
			for word in self.verifyWords:
				expected = self.verifyWords[word]
				
			for (word, successful, result, band) in self.checkWordsX(self.verifyWords.keys()):
				t = list()
				t.append(r'{\small %s}' % word)
				t.append(r'{\small %s}' % self.verifyWords[word])
				t.append(r'{\small \emph{%s} \newline {\tiny %s}' % (successful, result))
				b = str(band)
				t.append(r'{\small %s}' % b)
				t.append(r'{\small %s (%d)}' % (band.read(), band.pos))
				t.append(r'{\small %s}' % ((self.verifyWords[word] == successful) and "ja" or r'\textbf{NEIN}'))
				testResults.append(' & '.join(t) + r'\\')
			testResults.append(r'\end{longtable}')
			s = "\n".join(testResults)
		return s
####################################################################################################
# TURINGMASCHINEN: ENDE
####################################################################################################


class LaTeXBinder(AusgebenderAutomat):
	def __init__(self, template=None, finalFileBase='AutomatBinder', WORKINGDIR=None, TEMPLATESDIR=None):
		if not WORKINGDIR:
			WORKINGDIR = os.path.abspath('.')
		if not TEMPLATESDIR:
			TEMPLATESDIR = os.path.join(WORKINGDIR, 'output_templates')
		if not template:
			template = os.path.join(TEMPLATESDIR, 'binder.tex')

		self.content = list()
		self.template = template
		self.t = SelfRemovingTempdir()
		base = self.t.getRandomFilename()
		self.texTarget = base + '.tex'
		self.pdfTarget = base + '.pdf'
		self.finalFile = os.path.join(WORKINGDIR, finalFileBase + '.pdf')
		AusgebenderAutomat.__init__(self)

	def appendContent(self, content):
		self.content += content

	def _logOutput(self, out):
		if out.strip() != '':
			for line in out.split("\n"):
				if line.strip() != '':
					self.log.debug("%s %s" % ('<STDOUT>', line))

	def write(self, finalFile=None):
		if finalFile:
			self.finalFile = finalFile
		needSecondRun = False

		binder = self._readTemplate(self.template)
		if (-1 != binder.find("listoftables") ) or (-1 != binder.find("listoffigures") ):
			needSecondRun = True
		binder = binder.replace("%%__CONTENT__", "\n".join(self.content))

		if not self.writeContent(self.texTarget, binder):
			self.log.error("Could not write content to texTarget '%s'. Abort." % self.texTarget)
			return

		(rc, out, err) = runCommand(PDFLATEX_BIN, ('-version'))
		if rc != 0:
			self.log.error("PDFLATEX missing ? PDFLATEX_BIN is '%s'. (Fix path to your 'pdflatex' binary in automatenausgabe.py or install pdflatex). Abort." % PDFLATEX_BIN)
			return

		validReturnCodes = [0, 1]
		(rc, out, err) = runCommand(PDFLATEX_BIN, ('-interaction batchmode "%s"' % self.texTarget), workDir=self.t.tmp, validReturnCodes=validReturnCodes)
		if not (rc in validReturnCodes):
			self._logOutput(out)
			self.t.removeAtExit = False

		if needSecondRun:
			(rc, out, err) = runCommand(PDFLATEX_BIN, ('-interaction batchmode "%s"' % self.texTarget), workDir=self.t.tmp, validReturnCodes=validReturnCodes)
			if not (rc in validReturnCodes):
				self._logOutput(out)
				self.t.removeAtExit = False

		if rc in validReturnCodes:
			(rc, out, err) = runCommand(PDFLATEX_BIN, ('-interaction batchmode "%s"' % self.texTarget), workDir=self.t.tmp, validReturnCodes=validReturnCodes)
			if rc != 0:
				self._logOutput(out)
				self.t.removeAtExit = False
			if (rc in validReturnCodes) and os.path.isfile(self.pdfTarget):
				shutil.move(self.pdfTarget, self.finalFile)
				runCommand('open', '"%s"' % self.finalFile)

def automatenReport(automaten, finalFileBase='AutomatReport', 
					WORKINGDIR=None, TEMPLATESDIR=None, AUTOMAT_TEMPLATE=None, BINDER_TEMPLATE=None,
					DOT_TEMPLATE=None
					):
	if not isinstance(automaten, list):
		automaten = [automaten]
	if len(automaten) == 0:
		print "Automatenliste ist mir zu leer."
		return
		
	if not WORKINGDIR:
		WORKINGDIR = os.path.abspath('.')
	if not TEMPLATESDIR:
		TEMPLATESDIR = os.path.join(WORKINGDIR, 'output_templates')
	if not AUTOMAT_TEMPLATE:
		AUTOMAT_TEMPLATE = os.path.join(TEMPLATESDIR, 'automat.tex')
	if not BINDER_TEMPLATE:
		BINDER_TEMPLATE = os.path.join(TEMPLATESDIR, 'binder.tex')
	if not DOT_TEMPLATE:
		DOT_TEMPLATE = os.path.join(TEMPLATESDIR, 'automat.dot')

	b = LaTeXBinder(BINDER_TEMPLATE, finalFileBase=finalFileBase)
	
	contentS = ''
	for automat in automaten:
		try:
			contentS += automat._toTeX(AUTOMAT_TEMPLATE, DOT_TEMPLATE)
		except Exception, e:
			print e
	content = list()
	
	for line in contentS.split("\n"):
		line = line.strip()
		if not line.startswith("%") and line != '':
			content.append(line)

	b.appendContent(content)
	b.write()

if __name__ == '__main__':
	test()