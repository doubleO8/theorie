#!/usr/bin/env python
# -*- coding: utf-8 -*-
from automaten import *
from automatenausgabe import *
from automatenleser import *

from optparse import OptionParser

# parse options et al
parser = OptionParser()

parser.add_option('-p', "--print",
					action="store_true", default=False,
					help="Print ASCII representation of the automaton",
					dest="ascii")

parser.add_option('-v', "--verify",
					action="store_true", default=False,
					help="Verify automaton",
					dest="verify")

parser.add_option('-t', "--test-words",
					default=False,
					help="Test words (seperated by whitespace)",
					dest="testWords")

parser.add_option('-w', "--write-pdf",
					default=False,
					help="Test words (seperated by whitespace)",
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
					help="set loglevel to DEBUG",
					dest="loglevel")

(options, files) = parser.parse_args()

# Logging init
logger = AutomatLogger(options.loglevel).log

automaten = list()
for file in files:
	try:
		A = AutomatenLeser(filename=file).automat()
		automaten.append(A)
	
		if options.ascii:
			print A
	
		if options.verify:
			A.verify()
			A.verifyByRegExp()
	
		if options.testWords:
			words = options.testWords.split()
			A.checkWords(words)
			A.verifyByRegExp(words)
	except Exception, e:
		logger.error("[EXCEPTION] '%s' %s" % (file, e))

if options.pdf and len(automaten) > 0:
	filebase = options.pdf
	if options.pdf.lower().endswith('.pdf'):
		filebase = options.pdf[:-4]
	automatenReport(automaten, finalFileBase=filebase)
