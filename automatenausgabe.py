# -*- coding: utf-8 -*-
import os, sys, tempfile, shutil, random, atexit
from subprocess import *
import logging

WORKINGDIR = '/Users/wolf/Documents/programming/theorie'
PDFLATEX_BIN = 'pdflatex'

OUTPUTDIR = os.path.join(WORKINGDIR, 'texOutput')
EPSILON = 'EPSILON'
TIKZ = False

class SelfRemovingTempdir(object):
	def __init__(self, workDir=None, removeAtExit=True, log = None):
		self.workDir = workDir
		self.removeAtExit = removeAtExit
		if log == None:
			logging.basicConfig(level=logging.INFO)
			log = logging.getLogger('runCommand')
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
		logging.basicConfig(level=logging.DEBUG)
		logger = logging.getLogger('runCommand')

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

	def _genZustandIndex(self, force=False):
		if self.ZustandIndex and not force:
			return self.ZustandIndex

		self.ZustandIndex = dict()
		i = 0
		for zustand in sorted(self.S):
			self.ZustandIndex[zustand] = i
			i += 1
		#self.log.debug(self.ZustandIndex)

	def _readTemplate(self, template):
		if not os.path.isfile(template):
			raise IOError("Template '%s' nicht gefunden." % (template))
		return open(template).read()

	def _genFilename(self, tdir=None):
		return tempfile.mkstemp(dir=OUTPUTDIR)[1]

class OPlaintextAutomat(AusgebenderAutomat):
	def _addHeader(self):
		out = list(['# Automatendefinition'])
		out.append("Name: %s" % self.name)
		if self.beschreibung:
			out.append("Beschreibung: %s" % self.beschreibung)
		return out

	def _addSigma(self):
		return ['# Alphabet definieren. Muss mit "Sigma:" beginnen, durch Whitespace getrennt.', "Sigma:\t" + ' '.join(list(self.Sigma)) ]

	def _addS0(self):
		return ['# Startzustand definieren. Muss mit "s0:" beginnen, durch Whitespaces getrennt.', "s0:\t" + ' '.join(list(self.s0)) ]

	def _addF(self):
		return ['# Finale Zustaende definieren. Muss mit "F:" beginnen, durch Whitespace getrennt.', "F:\t" + ' '.join(list(self.F)) ]

	def _addDelta(self):
		out = list(['# Uebergaenge, Format :', '# Zustand, Zeichen, Zielzustand (durch whitespace getrennt)'])
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
		out += self._addF()
		if pretty:
			out += SPACER
		out += self._addDelta()
		if pretty:
			out += SPACER
		out += self._addVerifyWords()
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
		p = '%s -> %s [ label = "%s" ];' % (quelle, self._fzAscii(ziel), self._fzAscii(zeichenString))
		#self.log.debug(p)
		return p
		
	def _toDot(self, template):
		self._genZustandIndex(True)
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

	def createDotDocument(self, filename = None):
		basename = self._genFilename()
		basedir = os.path.dirname(basename)
		dot_filename = os.path.join(basedir, os.path.basename(basename + '.gv'))
		pdf_filename = os.path.basename(basename + '.pdf')
		template = os.path.join(basedir, 'template.dot')
		returnValue = os.path.join(basedir, pdf_filename)

		try:
			out = open(dot_filename, "w")
			rawLines = self._toDot(template).split("\n")
			content = list()
			for line in rawLines:
				if not line.strip().startswith("//"):
					content.append(line)
			out.write("\n".join(content))
			out.close()
		except Exception, e:
			self.log.error(e)
			returnValue = False
		
		param = '-Tpdf -o "%s" "%s"' % (pdf_filename, dot_filename)
		(rc, out, err) = runCommand('dot', param, logger=self.log, workDir=basedir)
		if rc != 0:
			print err
			print "----------------------"
			print out
			returnValue = False
		
		return returnValue

class OLaTeXAutomat(AusgebenderAutomat):
	def _TeXNode(self, Zustand, orientation=''):
		styles = ['state']
		description = Zustand
		name = Zustand
		#	\node[initial,state]	(A)						{$q_a$};
		if Zustand in self.s0:
			styles.append('initial')
		if Zustand in self.F:
			styles.append('accepting')
		node = r'\node[%s] (%s) %s {%s};' % (','.join(styles), name, orientation, description)
		self.log.debug(node)
		return node

	def _TeXEdge(self, Zustand):
		#(A) edge              node {0,1,L} (B)
		#    edge              node {1,1,R} (C)
		quelle = Zustand
		s = r'(%s)' % Zustand
		
		erreichbareZiele = dict()
		for zeichen in self.Sigma:
			ziel = self._delta(Zustand, zeichen)
			if ziel:
				if not erreichbareZiele.has_key(ziel):
					erreichbareZiele[ziel] = list()
				erreichbareZiele[ziel].append(zeichen)
		#self.log.debug("Erreichbare Ziele Index : %s" % erreichbareZiele)

		oMoeglichkeiten = ('', '[bend left]', '[bend right]')
		omLen = len(oMoeglichkeiten)
		zustandIndex = self._genZustandIndex()
		#self.log.debug("Zustand-Index : %s" % zustandIndex)
		
		# Quell Index-Nummer
		qIndex = zustandIndex[Zustand]
		zielZaehler = 0
		
		for ziel in erreichbareZiele:
			stringZiel = list(ziel)[0]
			orientation = ''
			eZieleLen = len(erreichbareZiele[ziel])

			self.log.debug("ZIEL: %s (%s)" % (stringZiel, repr(ziel)))
			
			# Ziel Index-Nummer
			zIndex = zustandIndex[stringZiel]
			self.log.debug('zIndex> ' + str(zIndex))
			
			indexDelta = qIndex - zIndex
			
			if indexDelta == 0:
				orientation = '[loop above]'
			if indexDelta > 1:
				orientation = '[bend right]'
			elif indexDelta < -1:
				orientation = '[bend left]'

			if eZieleLen > 0 and orientation == '':
				oNum = zielZaehler % omLen
				orientation = oMoeglichkeiten[oNum]
				zielZaehler +=1
			
			self.log.debug("kuerzmenge PRE")
			zeichen = self.kuerzMenge(erreichbareZiele[ziel])
			self.log.debug("kuerzmenge POST")

			s += " edge %s node {%s} (%s)\n " % (orientation, zeichen, stringZiel)
		return s

	def _TeXSpecification(self):
		s = list()
		aTyp = "%seterministischer Automat" % ((self.istDEA() and 'D' or 'Nichtd'))

		s.append(r'\textbf{%s \emph{%s}}' % (aTyp, self.name))
		if EPSILON in self.Sigma:
			s.append(r" ($\epsilon$-Übergänge möglich)")

		if self.beschreibung :
			s.append(r"\newline \emph{%s}" % self.beschreibung)
		s.append(r"\begin{itemize}")
		s.append(r'\item[] Endliche Menge der möglichen Zustände $S = \{%s\}$' % self._fzTex(self.S))
		s.append(r"\item[] \{%s\} ist Anfangszustand" % self._fzTex(self.s0))
		s.append(r"\item[] Menge der Endzustände $F = \{%s\}$" % self._fzTex(self.F))
		s.append(r"\item[] Endliche Menge der Eingabezeichen $\Sigma = \{%s\}$" % self._fzTex(self.Sigma))
		s.append(r'\end{itemize}')
		return "\n".join(s)

	def _TeXDeltaTable(self):
		s = list()
		headerLine = [r'$\delta$']
		for zeichen in self.Sigma:
			headerLine.append(zeichen)
		s.append(r'\begin{tabular}{r|%s}' % ('c' * (len(headerLine)-1)))
		s.append(r' & '.join(headerLine) + r' \\')
		s.append(r'\hline')

		for zustand in sorted(self.S):
			line = [ (zustand in self.F and '{*}' or '') + zustand ]
			for zeichen in self.Sigma:
				zielZustand = self._delta(zustand, zeichen)
				line.append(self._fzTex(zielZustand))
			s.append(r' & '.join(line))
			s.append(r' \\')
		
		s.append(r'\end{tabular}')

		return "\n".join(s)

	def _TeXIncludeFigure(self, file, caption=None, label=None):
		label = label and ("\\label{%s}" % label) or ''
		caption = caption and ("\\caption{%s}" % caption) or ''
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

	def _tikzGraph(self):
		self._genZustandIndex(True)
		tNodes = []
		tEdges = []
		orientation = ''
		for zustand in self.S:
			tNodes.append(self._TeXNode(zustand, orientation))
			tEdges.append(self._TeXEdge(zustand))
			orientation = '[right of=%s]' % zustand
		return (tNodes, tEdges)

	def _addTikz(self):
		if TIKZ:
			(tNodes, tEdges) = self._tikzGraph()
			s = s.replace("%%__TIKZ_BEGIN__", r"\begin{tikzpicture}[->,>=stealth',shorten >=1pt,auto,node distance=2.0cm, semithick]")
			s = s.replace("%%__TIKZ_STYLE__", r"\tikzstyle{every state}=[fill=none,draw=black,text=black]")
			s = s.replace("%%__TIKZ_END__", r"\end{tikzpicture}")
			s = s.replace("%%__NODES__", "\n".join(tNodes))
			s = s.replace("%%__PATH__", "\path\n" + "\n".join(tEdges) + ";\n")
	
	def _TeXAutomatStart(self):
		return r'\section{%s}' % self.name
		
	def _toTeX(self, template):
		s = self._readTemplate(template)

		s = s.replace("%%__AUTOMAT__", self._TeXAutomatStart())
		s = s.replace("%%__SPEC__", self._TeXSpecification())
		s = s.replace("%%__DELTA__", self._TeXDeltaTable())
		s = s.replace('%%__RESULTS__', self._TeXResults())
		s = s.replace('%%__VERIFY__', self._TeXVerify())

		if 'createDotDocument' in dir(self):
			dotgraph = self.createDotDocument()
			if dotgraph:
				s = s.replace('%%__DOT_GRAPH__', r'\subsection{Gemalt mit dot}' + self._TeXIncludeFigure(dotgraph))
			else:
				self.log.error("Kein dotgraph")

		return s

	def createLaTeXBinder(self, files=list(), output=None):
		if 'log' not in dir(self) :
			logging.basicConfig(level=logging.DEBUG)
			self.log = logging.getLogger('cLB')

		basename = self._genFilename()
		basedir = os.path.dirname(basename)
		tex_filename = os.path.basename(basename + '.tex')
		pdf_filename = os.path.basename(basename + '.pdf')
		template = os.path.join(basedir, 'binder.tex')
		returnValue = os.path.join(basedir, pdf_filename)

		s = self._readTemplate(template)
		includeFiles = list()
		for file in files:
			includeFiles.append(r'\include{%s}' % file)
		s = s.replace("%%__FILES__", "\n".join(includeFiles))
		try:
			out = open(os.path.join(basedir, tex_filename), "w")
			out.write(s)
			out.close()
		except Exception, e:
			try:
				self.log.error(e)
			except Exception, e:
				print e
			returnValue = False

		(rc, out, err) = runCommand(PDFLATEX_BIN, '"%s"' % tex_filename, logger=self.log, workDir=basedir)
		if rc != 0:
			print err
			print "----------------------"
			print out
			returnValue = False
		(rc, out, err) = runCommand(PDFLATEX_BIN, '"%s"' % tex_filename, logger=self.log, workDir=basedir)
		if rc != 0:
			print err
			print "----------------------"
			print out
			returnValue = False
		
		return returnValue

	def createTeXDocument(self, filename = None):
		basename = self._genFilename()
		basedir = os.path.dirname(basename)
		tex_filename = os.path.basename(basename + '.tex')
		pdf_filename = os.path.basename(basename + '.pdf')
		template = os.path.join(basedir, 'template.tex')
		returnValue = os.path.join(basedir, pdf_filename)
		
		try:
			out = open(os.path.join(basedir, tex_filename), "w")
			rawLines = self._toTeX(template).split("\n")
			content = list()
			for line in rawLines:
				if not line.strip().startswith("%"):
					content.append(line)
			out.write("\n".join(content))
			out.close()
		except Exception, e:
			self.log.error(e)
			returnValue = False
		
		(rc, out, err) = runCommand(PDFLATEX_BIN, '"%s"' % tex_filename, logger=self.log, workDir=basedir)
		if rc != 0:
			print err
			print "----------------------"
			print out
			returnValue = False
		
		return returnValue

if __name__ == '__main__':
	runCommand("true", "whatever")
	