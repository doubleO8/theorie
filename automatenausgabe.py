# -*- coding: utf-8 -*-
import os, sys, tempfile, shutil, random, atexit
from subprocess import *

WORKINGDIR = os.path.abspath('.')
PDFLATEX_BIN = 'pdflatex'

OUTPUTDIR = os.path.join(WORKINGDIR, 'texOutput')
EPSILON = 'EPSILON'

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
		return out

	def _addSigma(self):
		return ['# Alphabet definieren. Muss mit "Sigma:" beginnen, durch Whitespace getrennt.', "Sigma:\t" + ' '.join(sorted(list(self.Sigma))) ]

	def _addS0(self):
		return ['# Startzustand definieren. Muss mit "s0:" beginnen, durch Whitespaces getrennt.', "s0:\t" + ' '.join(sorted(list(self.s0))) ]

	def _addF(self):
		return ['# Finale Zustaende definieren. Muss mit "F:" beginnen, durch Whitespace getrennt.', "F:\t" + ' '.join(sorted(list(self.F))) ]

	def _addS(self):
		return ['# Optional: Zustaende definieren.', 
			'# Falls nicht definiert, werden Zustaende aus den Uebergaengen zusammengestellt.',
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
	def _mangleName(self, name):
		return name.replace("_", ' ')
	
	def _TeXSpecification(self):
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

	def _TeXIncludeFigure(self, file, caption=None, label=None):
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
	
	def _TeXResults(self):
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
		return r'\section{Automat %s}' % self._mangleName(self.name)
		
	def _toTeX(self, template=None, dot_template=None):
		s = self._readTemplate(template)

		s = s.replace("%%__AUTOMAT__", self._TeXAutomatStart())
		s = s.replace("%%__SPEC__", self._TeXSpecification())
		s = s.replace("%%__DELTA__", self._TeXDeltaTable())
		s = s.replace('%%__RESULTS__', self._TeXResults())
		s = s.replace('%%__VERIFY__', self._TeXVerify())

		if 'createDotDocument' in dir(self):
			dotgraph = self.createDotDocument(dot_template)
			if dotgraph:
				aName = self._mangleName(self.name)
				label = 'dot%s' % aName 
				caption = 'Automat %s' % aName
				s = s.replace('%%__DOT_GRAPH__', r'\subsection{Graph}' + self._TeXIncludeFigure(dotgraph, caption, label))
			else:
				self.log.error("Kein dotgraph")

		return s

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

	def appendContent(self, content):
		self.content += content

	def write(self, finalFile=None):
		if finalFile:
			self.finalFile = finalFile
		needSecondRun = False
		
		binder = self._readTemplate(self.template)
		if (-1 != binder.find("listoftables") ) or (-1 != binder.find("listoffigures") ):
			needSecondRun = True
		binder = binder.replace("%%__CONTENT__", "\n".join(self.content))

		if not self.writeContent(self.texTarget, binder):
			return

		validReturnCodes = [0, 1]
		(rc, out, err) = runCommand(PDFLATEX_BIN, ('-interaction batchmode "%s"' % self.texTarget), workDir=self.t.tmp, validReturnCodes=validReturnCodes)
		if not (rc in validReturnCodes):
			print err
			print "----------------------"
			print out
			self.t.removeAtExit = False

		if needSecondRun:
			(rc, out, err) = runCommand(PDFLATEX_BIN, ('-interaction batchmode "%s"' % self.texTarget), workDir=self.t.tmp, validReturnCodes=validReturnCodes)
			if not (rc in validReturnCodes):
				print err
				print "----------------------"
				print out
				self.t.removeAtExit = False

		if rc in validReturnCodes:
			(rc, out, err) = runCommand(PDFLATEX_BIN, ('-interaction batchmode "%s"' % self.texTarget), workDir=self.t.tmp, validReturnCodes=validReturnCodes)
			if rc != 0:
				print err
				print "----------------------"
				print out
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
