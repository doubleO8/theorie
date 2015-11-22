#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (C) 2010  WB

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
                
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
                                
You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
import sys
import traceback
from automaten import *
from automatenausgabe import *
from automatenleser import *
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

parser.add_option('-f', "--filter",
                  default=False,
                  help="Consider only TYPE automata (separated by ',')\
                    Possible values: %s" % ', '.join(sorted(FILTER_TYPES)),
                  dest="filter")

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

parser.add_option('-r', "--regexp",
                  action="store_true", default=False,
                  help="Verification By Regular Expression",
                  dest="regexpVerify")

parser.add_option('-t', "--test-words",
                  default=False,
                  help="Test words (seperated by whitespace)",
                  dest="testWords")

parser.add_option("--test-words-append",
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
                  action="store_const",
                  const=logging.DEBUG,
                  default=logging.INFO,
                  help="set loglevel to DEBUG",
                  dest="loglevel")

parser.add_option("--log-warning",
                  action="store_const",
                  const=logging.WARNING,
                  default=logging.INFO,
                  help="set loglevel to WARNING",
                  dest="loglevel")

(options, files) = parser.parse_args()

# Logging init
logger = AutomatLogger(options.loglevel).log
autoFilter = FILTER_TYPES

# Filter ggf. setzen
if options.filter:
    try:
        autoFilter = set(options.filter.split(',')).intersection(FILTER_TYPES)
    except Exception, e:
        pass

#: Liste der Automaten, die in den Report geschrieben werden sollen
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
                # if options.epsilon:
                #	logger.warn("Epsilonfrei machen")
                #	A = A.EpsilonFrei()

                epsilon = isinstance(A, EpsilonAutomat) and True or False
                deterministisch = A.istDEA()
                automatenTyp = '%s%s' % ((epsilon and 'e' or ''), (deterministisch and 'DEA' or 'NEA'))

                logger.debug(
                    "[%s] class:%s epsilon:%s deterministisch: %s" % (automatenTyp, repr(A), epsilon, deterministisch))
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

                if options.regexpVerify:
                    try:
                        logger.debug("testing %s via RegExp" % ', '.join(localTestWords))
                        A.verifyByRegExp(localTestWords)
                    except Exception, e:
                        if options.loglevel == logging.DEBUG:
                            logger.debug(e)

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

# Automaten-Report erstellen
if options.pdf and len(automaten) > 0:
    filebase = options.pdf
    if options.pdf.lower().endswith('.pdf'):
        filebase = options.pdf[:-4]
    automatenReport(automaten, finalFileBase=filebase)
