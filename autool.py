#!/usr/bin/env python
# -*- coding: utf-8 -*-
from automaten import *
from automatenausgabe import *
from automatenleser import *
import traceback
from optparse import OptionParser

FILTER_TYPES = set(['NEA', 'DEA', 'eNDA', 'eDEA', 'eNEA', 'finite', 'pushdown', 'turing'])

# parse options et al
parser = OptionParser()

parser.add_option('-a', "--ascii",
					action="store_true", default=False,
					help="Output ASCII representation of automaton\
					(as used in automata definition files)",
					dest="ascii")

parser.add_option('-d', "--dump",
					action="store_true", default=False,
					help="Print raw data",
					dest="dump")

#parser.add_option('-e', "--epsilonfree",
#					action="store_true", default=False,
#					help="remove epsilon transitions",
#					dest="epsilon")

parser.add_option('-f', "--filter",
					default=False,
					help="Consider only TYPE automata (separated by ',')\
					Possible values:\
					%s" % ', '.join(sorted(FILTER_TYPES)),
					dest="filter")

#parser.add_option('-g', "--grammar",
#					action="store_true", default=False,
#					help="Try to create a Grammar for Automata",
#					dest="grammar")

parser.add_option('-p', "--print",
					action="store_true", default=False,
					help="Print ASCII representation of the automaton",
					dest="printIt")

parser.add_option('-v', "--verify",
					action="store_true", default=False,
					help="Verify automaton",
					dest="verify")

parser.add_option('-z', "--verbose",
					action="store_true", default=False,
					help="Be verbose",
					dest="verbose")

parser.add_option('-s', "--step-by-step",
					action="store_true", default=False,
					help="Step By Step Verification",
					dest="step")

parser.add_option('-t', "--test-words",
					default=False,
					help="Test words (seperated by whitespace)",
					dest="testWords")

parser.add_option( "--test-words-append",
					action="store_true", default=False,
					help="Append given testwords to already defined list of testwords",
					dest="testWordsAppend")

parser.add_option("--dot-dump",
					action="store_true", default=False,
					help="Dump DOT source",
					dest="dotdump")

parser.add_option('-w', '-o', "--write-pdf",
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
		ignore = True
		
		try:
			L = AutomatenLeser(filename=file, log=logger)
			automatenTyp = L.type
			A = L.automat()
			
			# NEA/DEA et al
			if L.type == 'finite':
				
				## Epsilon frei machen
				#if options.epsilon:
				#	logger.warn("Epsilonfrei machen")
				#	A = A.EpsilonFrei()
	
				epsilon = isinstance(A, EpsilonAutomat) and True or False
				deterministisch = A.istDEA()
				automatenTyp = '%s%s' % ((epsilon and 'e' or ''), (deterministisch and 'DEA' or 'NEA'))
				
				logger.debug("[%s] class:%s epsilon:%s deterministisch: %s" % (automatenTyp, repr(A), epsilon, deterministisch))
			# Kellerautomaten
			elif L.type == 'pushdown':
				pass
			# Turingmaschinen ..
			elif L.type == 'turing':
				pass
			
			# Sonstiges ..
			else:
				raise NotImplementedError("Type '%s' not implemented .. YET" % L.type)

			if automatenTyp in autoFilter:
				ignore = False
			else:
				logger.info("Ignoriere %s. '%s' nicht in {%s}" % (A.name, automatenTyp, ', '.join(autoFilter)))

			if not ignore:
				automaten.append(A)

				localTestWords = list()
				if A.testWords:
					localTestWords += A.testWords
				if A.verifyWords:
					localTestWords += A.verifyWords.keys()
				if options.testWords and not options.testWordsAppend:
					localTestWords = options.testWords.split()
				elif options.testWords and options.testWordsAppend:
					localTestWords += options.testWords.split()
				localTestWords = sorted(set(localTestWords))
	
				if options.dump:
					print A.dump()
	
				if options.ascii:
					print A._plaintext()

				if options.printIt:
					print A

				if options.dotdump:
					print A.createDotDocument(dumpOnly=True)

				if options.verify:
					if not options.verbose:
						A.verify()
					else:
						try:
							A.verifyVerbose()
						except Exception, e:
							if options.loglevel == logging.DEBUG:
								logger.debug(e)

					try:
						A.verifyByRegExp()
					except Exception, e:
						if options.loglevel == logging.DEBUG:
							logger.debug(e)

				if options.step:
					if not options.printIt:
						print str(A) + "\n" * 2
					try:
						for word in localTestWords:
							A.checkStepByStep(word, doItVerbose=options.verbose)
							print
					except Exception, e:
						if options.loglevel == logging.DEBUG:
							logger.debug(e)

				#if options.grammar:
				#	try:
				#		print A.Grammatik()
				#	except Exception, e:
				#		print "Grammatik."

				if options.testWords and not options.step:
					A.checkWords(localTestWords)
					try:
						A.verifyByRegExp(localTestWords)
					except Exception, e:
						if options.loglevel == logging.DEBUG:
							logger.debug(e)

		except Exception, e:
			logger.error("[EXCEPTION] '%s' %s" % (file, e))
			traceback.print_exc(file=sys.stdout)

if options.pdf and len(automaten) > 0:
	filebase = options.pdf
	if options.pdf.lower().endswith('.pdf'):
		filebase = options.pdf[:-4]
	automatenReport(automaten, finalFileBase=filebase)
