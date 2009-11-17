#!/usr/bin/env python
# -*- coding: utf-8 -*-
from automaten import *
from automatenausgabe import *
from automatenleser import *
import traceback
from optparse import OptionParser

FILTER_TYPES = set(['NEA', 'DEA', 'eNDA', 'eDEA'])
# parse options et al
parser = OptionParser()

parser.add_option('-p', "--print",
					action="store_true", default=False,
					help="Print ASCII representation of the automaton",
					dest="ascii")

parser.add_option('-d', "--dump",
					action="store_true", default=False,
					help="Print raw data",
					dest="dump")

parser.add_option('-f', "--filter",
					default=False,
					help="Consider only TYPE automata (separated by ',')\
					Possible values:\
					%s" % ', '.join(sorted(FILTER_TYPES)),
					dest="filter")

parser.add_option('-g', "--grammar",
					action="store_true", default=False,
					help="Try to create a Grammar for Automata",
					dest="grammar")

parser.add_option('-v', "--verify",
					action="store_true", default=False,
					help="Verify automaton",
					dest="verify")

parser.add_option('-t', "--test-words",
					default=False,
					help="Test words (seperated by whitespace)",
					dest="testWords")

parser.add_option("--dot-dump",
					action="store_true", default=False,
					help="Dump DOT source",
					dest="dotdump")

parser.add_option('-w', "--write-pdf",
					default=False,
					help="Write report to PDF",
					dest="pdf")

parser.add_option("--log-debug",
					action="store_const", const=logging.DEBUG,
					default=logging.INFO,
					help="set loglevel to DEBUG",
					dest="loglevel")

parser.add_option("--log-info",
					action="store_const", const=logging.INFO,
					help="set loglevel to INFO",
					dest="loglevel")

parser.add_option("--log-warning",
					action="store_const", 
					const=logging.WARNING,
					help="set loglevel to WARNING",
					dest="loglevel")

(options, files) = parser.parse_args()

# Logging init
logger = AutomatLogger(options.loglevel).log
autoFilter = FILTER_TYPES
if options.filter:
	try:
		autoFilter = set(options.filter.split(',')).intersection(FILTER_TYPES)
	except Exception, e:
		pass

automaten = list()
for file in files:
	if not file.endswith("~"):
		try:
			A = AutomatenLeser(filename=file, log=logger).automat()
			epsilon = isinstance(A, EpsilonAutomat) and True or False
			deterministisch = A.istDEA()
			automatenTyp = '%s%s' % ((epsilon and 'e' or ''), (deterministisch and 'DEA' or 'NEA'))
			
			logger.debug("[%s] class:%s epsilon:%s deterministisch: %s" % (automatenTyp, repr(A), epsilon, deterministisch))

			if not automatenTyp in autoFilter:
				logger.debug("Ignoriere %s. %s nicht in %s" % (A.name, automatenTyp, ', '.join(autoFilter)))
			else:
				automaten.append(A)
	
				if options.dump:
					print A.dump()
	
				if options.ascii:
					print A
	
				if options.dotdump:
					print A.createDotDocument(dumpOnly=True)
	
				if options.verify:
					A.verify()
					A.verifyByRegExp()
	
				if options.grammar:
					try:
						print A.Grammatik()
					except Exception, e:
						print "Grammaaaatik"
						pass
	
				if options.testWords:
					words = options.testWords.split()
					A.checkWords(words)
					A.verifyByRegExp(words)
		except Exception, e:
			logger.error("[EXCEPTION] '%s' %s" % (file, e))
			traceback.print_exc(file=sys.stdout)

if options.pdf and len(automaten) > 0:
	filebase = options.pdf
	if options.pdf.lower().endswith('.pdf'):
		filebase = options.pdf[:-4]
	automatenReport(automaten, finalFileBase=filebase)
