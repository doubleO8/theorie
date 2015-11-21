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
import automaten
import kellerautomaten
import crappy_logger
from crappy_logger import AutomatLogger


def test():
    """
    doctest (unit testing)
    """
    import doctest
    import logging
    crappy_logger.AutomatLogger(logging.DEBUG).log
    failed, total = doctest.testmod()
    print("doctest: %d/%d tests failed." % (failed, total))


class ChomskyGrammatik(automaten.Automat):
    EPSILON = 'EPSILON'

    def addProduction(self, left, right):
        right = tuple(self._toList(right))
        if not set(left).intersection(self.N):
            self.log.error("%s not in N: %s" % (left, self.N))
            return False
        if not set(left).intersection(set(list(self.N) + list(self.T))):
            self.log.error("%s not in N (%s) or T (%s)" % (left, self.N, self.T))
            return False

        if not left in self.P.keys():
            self.P[left] = set()

        if self.P[left].intersection(set(right)):
            self.log.warning("overring rule .. %s -> %s" % (left, right))

        self.P[left].add(right)

        self.rulesDict[tuple(left) + right] = self.rulesCounter
        self.rulesCounter += 1
        return True

    def isCNF(self):
        for nonterminal in self.P.keys():
            for production in self.P[nonterminal]:
                # production ist ein Tupel mit der rechten Seite
                # Bedingung fuer CNF: Regel muss folgende Form haben
                #	* <Terminal> -> <Nonterminal>
                #	* <Terminal> -> <Terminal><Terminal>
                if len(production) > 2:
                    self.log.debug("Regel hat mehr als 2 Elemente")
                    return False
                elif len(production) == 2:
                    if not (self.N.intersection(set(production)) == set(production)):
                        self.log.debug(
                            "Nicht alle Teile der Produktion sind Terminals. N:%s production:%s; intersection: %s" % (
                            self.N, production, self.N.intersection(set(production))))
                        return False
                elif not self.T.intersection(set(production)):
                    self.log.debug("Produktion ist kein Terminalsymbol")
                    return False
        return True

    def isGNF(self):
        for terminal in self.P.keys():
            for production in self.P[terminal]:
                # production ist ein Tupel mit der rechten Seite
                # Bedingung fuer CNF: Regel muss folgende Form haben
                #	* <Terminal> -> <Nonterminal>
                #	* <Terminal> -> <Terminal><Terminal>
                if len(production) > 2:
                    self.log.debug("Regel hat mehr als 2 Elemente")
                    return False
                elif len(production) == 2:
                    a = production[0]
                    alpha = production[1]
                    if not (self.T.intersection(set(a)) == set(a)):
                        self.log.debug(
                            "'a-Teil' der Produktion ist kein Terminalsymbol. T:%s a:%s; intersection: %s" % (
                            self.T, alpha, self.T.intersection(set(a))))
                        return False
                    if not (self.T.union(self.N).intersection(set(alpha)) == set(alpha)):
                        self.log.debug(
                            "'alpha-Teil' der Produktion ist kein Terminal- oder Nonterminalsymbol. T+N:%s a:%s; intersection: %s" % (
                            self.T.union(self.N), alpha, self.T.union(self.N).intersection(set(alpha))))
                        return False
        return True

    def CNF(self):
        pass

    def machKellerautomat(self):
        # DeterministischerKellerautomat
        # __init__(self, S, s0, F, Sigma, K, k0='k0', delta=None,
        #		name="EinDPDA", beschreibung='',
        #		testWords=None, verifyWords=None, verifyRegExp=None, accept=0):
        k_S = self.s0 + ' s1 sf'
        k_s0 = self.s0
        k_F = 'sf'
        k_K = list(['k0']) + list(self.T) + list(self.N)
        k_Sigma = self.T
        print k_S
        print k_s0
        print k_F
        print k_K
        print k_Sigma
        automat = kellerautomaten.DeterministischerKellerautomat(k_S, k_s0, k_F, k_Sigma, k_K)
        # def addRule(self, zustand, bandzeichen, kellerzeichen, zustandStrich, kellerzeichenStrich):
        # Regel fuer S Startsymbol von G
        automat.addRule(self.s0, kellerautomaten.DeterministischerKellerautomat.EPSILON, 'k0', 's1', ['S', 'k0'])

        # fuer jede Regel A -> gamma von G (oberstes Kellerzeichen ist erstes Zeichen von gamma)
        for nonterminal in self.P.keys():
            for production in self.P[nonterminal]:
                automat.addRule('s1', kellerautomaten.DeterministischerKellerautomat.EPSILON, nonterminal, 's1',
                                '+'.join(production))

        # fue alle Eingabezeichen bzw. Terminalzeichen a
        for zeichen in self.T:
            automat.addRule('s1', zeichen, zeichen, 's1', kellerautomaten.DeterministischerKellerautomat.EPSILON)

        # Regel fuer "wenn Keller wieder initial ist wird akzeptiert"
        automat.addRule('s1', kellerautomaten.DeterministischerKellerautomat.EPSILON, 'k0', 'sf', 'k0')

        print automat
        # print automat.check('(()(()))', doRaise=False, doItVerbose=True, stepByStep=True)
        return automat

    def __init__(self, N, T, P=dict(), S='S', F=''):
        """
        >>> N = "S"
        >>> T = "a b"
        >>> g = ChomskyGrammatik(N, T)
        >>> g.addProduction('S', "a S b")
        True
        >>> g.addProduction('S', ChomskyGrammatik.EPSILON)
        True
        >>> g.isCNF()
        False
        >>> g2 = ChomskyGrammatik(N, T)
        >>> g2.addProduction('S', 'a')
        True
        >>> g2.isCNF()
        True
        >>> g2.addProduction('S', 'S S')
        True
        >>> g2.isCNF()
        True
        """
        self._initLogging()
        # Nicht-Terminalzeichen A,B,C
        # frozenset
        self.N = self._toFrozenSet(N)

        # Terminalzeichen a,b,c
        # frozenset
        self.T = self._toFrozenSet(T)

        # Produktionen
        # dict( NT : {NT -> T} )
        if P:
            self.log.warning("addProduction() benutzen ..")
        self.P = dict()
        self.rulesDict = dict()
        self.rulesCounter = 0

        # Startsymbol
        # [Automaten s0]
        self.s0 = S

        self.F = self._toFrozenSet(F)
        self.reset()

    def __str__(self):
        pfeil = '→'
        s = list()
        s.append('Endliche Menge der Nicht-Terminalsymbole : {%s}' % ', '.join(sorted(self.N)))
        s.append('Endliche Menge der Terminalsymbole       : {%s}' % ', '.join(sorted(self.T)))
        s.append('P = {')
        # self.P[left].add(right)
        for left in self.P.keys():
            ableitungen = list()
            for right in self.P[left]:
                ableitungen.append(''.join(right))
            s.append("%s -> %s" % (left, ' | '.join(ableitungen)))
        s.append('    }')
        return "\n".join(s)


if __name__ == '__main__':
    test()
    N = "S"
    T = "( )"
    g = ChomskyGrammatik(N, T)
    # g.addProduction('S', "a S b")
    g.addProduction('S', "S S")
    g.addProduction('S', "A H")
    g.addProduction('H', "S Z")
    g.addProduction('S', "A Z")
    g.addProduction('A', ")")
    g.addProduction('Z', "(")


    # g.addProduction('S', ChomskyGrammatik.EPSILON)
    print g
    g.isCNF()
    # g.isGNF()
    k = g.machKellerautomat()
