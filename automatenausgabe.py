# -*- coding: utf-8 -*-
import os, sys, tempfile
from subprocess import *

WORKINGDIR = '/Users/wolf/Documents/programming/theorie'
OUTPUTDIR = WORKINGDIR + os.path.sep + 'texOutput'

def kuerzMenge(items, max=5):
	if len(items) < max:
		zeichen = ','.join(items)
	else:
		zeichen = "%s,..,%s" % (items[0], items[-1])
	return zeichen

class AusgebenderAutomat(object):
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

	def _genFilename(self, tdir=None):
		return tempfile.mkstemp(dir=OUTPUTDIR)[1]

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
				zielLength = len(self._fzString(self._delta(zustand, zeichen)))
				if  zielLength > maxLength:
					maxLength = zielLength
			except Exception,e:
				pass

		fmtString = '%' + str(maxLength) + 's'
		deltaString = ' ' * (maxLength-1) + 'δ'
		
		headParts = [deltaString]
		for zeichen in self.Sigma:
			headParts.append(fmtString % zeichen)

		rows.append(prefix + ' | '.join(headParts))
		strich = '-' * maxLength
		strichParts = list([(fmtString % strich)] * len(headParts))
		rows.append(prefix + "-+-".join(strichParts) + '-')

		for zustand in sorted(self.S):
			rowParts = [(fmtString % zustand)]
			for zeichen in sorted(self.Sigma):
				sZustand = '!'
				try:
					zielZustand = self._delta(zustand, zeichen)
					sZustand = self._fzAscii(zielZustand)
				except Exception, e:
					print e
					sZustand = '/'
				rowParts.append(fmtString % sZustand)
			rows.append(prefix + ' | '.join(rowParts))

		return "\n".join(rows) + "\n"

class ODotAutomat(AusgebenderAutomat):
	def _DotPath(self, quelle, ziel, zeichenString):
		return '%s -> %s [ label = "%s" ];' % (quelle, ziel, zeichenString)
		
	def _toDot(self, template='template.dot'):
		self._genZustandIndex(True)
		if not os.path.isfile(template):
			raise IOError("Template '%s' nicht gefunden." % (template))
		content = open(template).read()
		s = content
		s = s.replace('//__FINAL_STATES__', ' '.join(self.F) + ";\n")
		s = s.replace('//__ORIGIN__', "null -> %s;\n" % self.s0)
		nodes = []
		
		for zustand in self.delta:
			for zeichen in self.delta[zustand].keys():
				ziel = self.delta[zustand][zeichen]
				if isinstance(zeichen, tuple):
					self.log.warning(zeichen)
					zeichen = kuerzMenge(zeichen)
				nodes.append(self._DotPath(zustand, ziel, zeichen))
		s = s.replace('//__PATH__', "\n".join(nodes))
		return s

	def createDotDocument(self, filename = None):
		basename = self._genFilename()
		
		dot_filename = os.path.basename(basename + '.gv')
		pdf_filename = os.path.basename(basename + '.pdf')

		basedir = os.path.dirname(basename)
		cwd = os.getcwd()
		try:
			os.chdir(basedir)
			out = open(dot_filename, "w")
			rawLines = self._toDot().split("\n")
			content = list()
			for line in rawLines:
				if not line.strip().startswith("//"):
					content.append(line)
			out.write("\n".join(content))
			out.close()
			command = 'dot -Tpdf -o "%s" "%s"' % (pdf_filename, dot_filename)
			#print command
			call(command, shell=True)
		except Exception, e:
			self.log.error(e)
			pdf_filename = False
		os.chdir(cwd)
		return pdf_filename

class OLaTeXAutomat(AusgebenderAutomat):
	def _genZustandIndex(self, force=False):
		if self.ZustandIndex and not force:
			return self.ZustandIndex

		self.ZustandIndex = dict()
		i = 0
		for zustand in self.S:
			self.ZustandIndex[zustand] = i
			i += 1
		#self.log.debug(self.ZustandIndex)

	def _TeXNode(self, Zustand, orientation=''):
		styles = ['state']
		description = Zustand
		name = Zustand
		#	\node[initial,state]	(A)						{$q_a$};
		if Zustand in self.s0:
			styles.append('initial')
		if Zustand in self.F:
			styles.append('accepting')
		node = r'\node[%s]\t(%s)\t%s\t{%s};' % (','.join(styles), name, orientation, description)
		#self.log.debug(node)
		return node
		#return "\\node[%s]\t(%s)\t%s\t{%s};" % (','.join(styles), name, orientation, description)

	def _TeXEdge(self, Zustand):
		#(A) edge              node {0,1,L} (B)
		#    edge              node {1,1,R} (C)
		quelle = Zustand
		s = r'\t(%s)' % Zustand
		
		erreichbareZiele = dict()
		for zeichen in self.Sigma:
			ziel = self._delta(Zustand, zeichen)
			if ziel:
				if not erreichbareZiele.has_key(ziel):
					erreichbareZiele[ziel] = list()
				erreichbareZiele[ziel].append(zeichen)
		self.log.warning(erreichbareZiele)

		oMoeglichkeiten = ('', '[bend left]', '[bend right]')
		omLen = len(oMoeglichkeiten)
		zustandIndex = self._genZustandIndex()
		self.log.warning(zustandIndex)
		
		# Quell Index-Nummer
		qIndex = zustandIndex[Zustand]
		zielZaehler = 0
		
		for ziel in erreichbareZiele:
			orientation = ''
			eZieleLen = len(erreichbareZiele[ziel])

			ziel = list(ziel)[0]
			self.log.debug(repr(ziel))
			
			# Ziel Index-Nummer
			zIndex = zustandIndex[ziel]
			self.log.warning('zIndex> ' + str(zIndex))
			
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

			zeichen = kuerzMenge(erreichbareZiele[ziel])
			#if eZieleLen < 5:
			#	zeichen = ','.join(erreichbareZiele[ziel])
			#else:
			#	zeichen = "%s,..,%s" % (erreichbareZiele[ziel][0], erreichbareZiele[ziel][-1])

			s += "\tedge\t%s\tnode\t{%s}\t(%s)\n\t" % (orientation, zeichen, ziel)
		return s

	def _TeXSpecification(self):
		s = "\\textbf{Automat '%s'}" % self.name
		if self.beschreibung :
			s += "\\newline \\emph{%s}" % self.beschreibung
		s += "\\begin{itemize}\n"
		#s = "Deterministischer Automat '%s'\n%s\n" % (self.name, "=" * 80)
		s += "\\item[] Endliche Menge der möglichen Zustände $S = \\{%s\\}$\n" % ', '.join(self.S)
		s += "\\item[] %s ist Anfangszustand\n" % self.s0
		s += "\\item[] Menge der Endzustände $F = \\{%s\\}$\n" % ', '.join(self.F)
		s += "\\item[] Endliche Menge der Eingabezeichen $\\Sigma = \\{%s\\}$\n" % ', '.join(self.Sigma)
		return s + "\n\\end{itemize}"

	def _TeXDeltaTable(self):
		headerLine = ['$\delta$']
		for zeichen in self.Sigma:
			headerLine.append(zeichen)
		s = "\\begin{tabular}{r|%s}\n" % ('c' * (len(headerLine)-1))
		s += "\t&\t".join(headerLine) + "\\\\\n\\hline\n"

		for zustand in self.S:
			line = [zustand]
			for zeichen in self.Sigma:
				zielZustand = self._delta(zustand, zeichen)
				line.append(zielZustand != None and zielZustand or '-')
			s += "\t&\t".join(line) + "\t\\\\\n"
		return s + "\end{tabular}"

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
			testResults = [ r'\begin{tabular}{lll}' ]
			testResults.append(r'Erfolg & Wort & Ergebnis\\')
			testResults.append(r'\hline')
			for (word, successful, result) in self.checkWords(self.testWords):
				t = list()
				t.append(r'{\small %s}' % (successful and "OK" or r'\textbf{KO}'))
				t.append(r'{\small %s}' % word)
				t.append(r'{\small \emph{%s}}' % result)
				testResults.append(' & '.join(t) + r'\\')
			testResults.append(r'\end{tabular}')
			s = "\n".join(testResults)
		return s

	def _toTeX(self, template='template.tex'):
		self._genZustandIndex(True)
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
		s = s.replace("%%__DELTA__", self._TeXDeltaTable())
		s = s.replace('%%__RESULTS__', self._TeXResults())

		if 'createDotDocument' in dir(self):
			dotgraph = self.createDotDocument()
			if dotgraph:
				s = s.replace('%%__DOT_GRAPH__', r'\subsection{Gemalt mit dot}' + self._TeXIncludeFigure(dotgraph))
			else:
				self.log.error("Kein dotgraph")

		return s

	def createTeXDocument(self, filename = None):
		basename = self._genFilename()
		tex_filename = os.path.basename(basename + '.tex')
		pdf_filename = os.path.basename(basename + '.pdf')
		basedir = os.path.dirname(basename)

		cwd = os.getcwd()
		returnValue = os.path.abspath(basedir + os.path.sep + pdf_filename)
		
		try:
			os.chdir(basedir)
			out = open(tex_filename, "w")
			rawLines = self._toTeX().split("\n")
			content = list()
			for line in rawLines:
				if not line.strip().startswith("%"):
					content.append(line)
			out.write("\n".join(content))
			out.close()
			command = 'pdflatex "%s"' % tex_filename
			call(command, shell=True)
		except Exception, e:
			self.log.error(e)
			returnValue = False
		os.chdir(cwd)
		return returnValue
