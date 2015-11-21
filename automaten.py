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
import logging, logging.config, os, sys, re
import copy
import automatenausgabe, automatenleser

if 'USED_LOGLEVEL' not in dir():
    USED_LOGLEVEL = logging.INFO


class AutomatLogger(object):
    __instance = None

    class __implementation:
        def __init__(self, loglevel=None):
            if not loglevel:
                global USED_LOGLEVEL
                loglevel = USED_LOGLEVEL
            self._initLogging(loglevel)

        def getId(self):
            return id(self)

        def _initLogging(self, loglevel):
            self.log = logging.getLogger("automatenlogger")
            if len(self.log.handlers) == 0:
                lhandler = logging.StreamHandler()
                lformatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
                lhandler.setFormatter(lformatter)
                self.log.addHandler(lhandler)
                self.log.setLevel(loglevel)
                self.log.debug(loglevel)

    def __init__(self, loglevel=None):
        if AutomatLogger.__instance is None:
            AutomatLogger.__instance = AutomatLogger.__implementation(loglevel)
        self.__dict__['_AutomatLogger__instance'] = AutomatLogger.__instance

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)


class AutomatException(Exception):
    """
    >>> x = AutomatException('ohje', frozenset(['achNein']), 'xXx')
    >>> x
    AutomatException()
    >>> print x
    'ohje' xXx [achNein]
    """

    def __init__(self, value, validSet=frozenset(), explanation='', hint=None, ableitungspfad=list()):
        self.value = value
        self.validSet = validSet
        self.explanation = explanation
        self.hint = hint
        self.ableitungspfad = ableitungspfad

    def _ableitungsPfad__str__(self, what):
        if len(what) == 0:
            return ''
        items = list()
        for item in what:
            items.append('{%s}' % ','.join(sorted(item)))
        return " Ableitung:\n %s" % '->'.join(items)

    def __str__(self):
        ## Alte Exception gab nur value zurueck, deswegen: HACK.
        ##if len(self.value) > 10:
        ##	return repr(self.value)
        validSetText = ''
        hint = ''
        ableitungspfadText = self._ableitungsPfad__str__(self.ableitungspfad)
        if len(self.validSet):
            validSetText = '[%s]' % ','.join(sorted(self.validSet))
        if self.hint:
            hint = '*%s* ' % self.hint.upper()
        return "%s%s %s %s%s" % (hint, repr(self.value), self.explanation, validSetText, ableitungspfadText)


class NotInSigmaException(AutomatException):
    def __init__(self, value, validSet=frozenset(), hint=None, ableitungspfad=list()):
        AutomatException.__init__(self, value, validSet, 'ist nicht Teil der Menge der Eingabezeichen', hint,
                                  ableitungspfad)


class NoSuchStateException(AutomatException):
    def __init__(self, value, validSet=frozenset(), hint=None, ableitungspfad=list()):
        AutomatException.__init__(self, value, validSet, 'ist nicht Teil der Menge der moeglichen Zustaende', hint,
                                  ableitungspfad)


class NoAcceptingStateException(AutomatException):
    def __init__(self, value, validSet=frozenset(), ableitungspfad=list()):
        AutomatException.__init__(self, value, validSet, 'ist nicht Teil der Menge der moeglichen Endzustaende',
                                  ableitungspfad)


class NoRuleForStateException(AutomatException):
    def __init__(self, value, statesWithRules=list(), ableitungspfad=list(),
                 explanation='hat keine definierten Regeln.'):
        AutomatException.__init__(self, value, frozenset(statesWithRules), explanation, ableitungspfad)


class EmptyStateException(AutomatException):
    def __init__(self, value, statesWithRules=list(), ableitungspfad=list()):
        AutomatException.__init__(self, value, frozenset(statesWithRules), 'Leere Zustandsmenge', ableitungspfad)


class NotInKException(AutomatException):
    def __init__(self, value, validSet=frozenset(), hint=None, ableitungspfad=list()):
        AutomatException.__init__(self, value, validSet, 'ist nicht Teil der Menge der Kellerzeichen', hint,
                                  ableitungspfad)


class NoKellerautomatRule(Exception):
    def __init__(self, zustand, bandzeichen, kellerzeichen, hint="Keine Ueberfuehrungsregel"):
        self.zustand = zustand
        self.bandzeichen = bandzeichen
        self.kellerzeichen = kellerzeichen
        self.hint = hint

    def __str__(self):
        return "%s (%s, %s, %s)" % (self.hint, self.zustand, self.bandzeichen, self.kellerzeichen)


class NonDeterministicKellerautomatRule(NoKellerautomatRule):
    def __init__(self, zustand, bandzeichen, kellerzeichen, other):
        NoKellerautomatRule.__init__(self, zustand, '%s<>%s' % (bandzeichen, other), kellerzeichen,
                                     "Nicht deterministische Ueberfuehrungsregel")


class EndOfWordKellerautomatException(Exception):
    def __init__(self, index, word):
        self.index = index
        self.word = word

    def __str__(self):
        return "Wir sind nur bis  Zeichen # %d von '%s' gekommen (%s)." % (
        self.index, self.word, self.word[:self.index])


def test():
    """
    doctest (unit testing)
    """
    import doctest
    AutomatLogger(logging.DEBUG).log
    failed, total = doctest.testmod()
    print("doctest: %d/%d tests failed." % (failed, total))


class NichtDeterministischerAutomat(automatenausgabe.OAsciiAutomat, automatenausgabe.OLaTeXAutomat,
                                    automatenausgabe.ODotAutomat, automatenausgabe.OPlaintextAutomat):
    def _toList(self, what):
        """
        >>> mini = NichtDeterministischerAutomat('s0', 's0', 's0', '0 1', { 's0' : {'0' : 's0'}})
        >>> mini._toList('')
        ['']
        >>> mini._toList('a b c d')
        ['a', 'b', 'c', 'd']
        >>> mini._toList(['a', 'b', 'c', 'd'])
        ['a', 'b', 'c', 'd']
        """
        if isinstance(what, basestring):
            return what.split(' ')
        elif isinstance(what, list):
            return what
        elif isinstance(what, tuple):
            return list(what)
        elif isinstance(what, frozenset):
            return list(what)
        else:
            raise ValueError("Cannot convert '%s' to list()" % str(what))

    def _toFrozenSet(self, what):
        """
        >>> mini = NichtDeterministischerAutomat('s0', 's0', 's0', '0 1', { 's0' : {'0' : 's0'}})
        >>> mini._toFrozenSet('a c b')
        frozenset(['a', 'c', 'b'])
        >>> mini._toFrozenSet('z1')
        frozenset(['z1'])
        >>> mini._toFrozenSet(set(['a', 'c', 'b']))
        frozenset(['a', 'c', 'b'])
        """
        if isinstance(what, set):
            return frozenset(what)
        return frozenset(self._toList(what))

    def _fzString(self, what):
        """
        String-Representation einer Menge (frozenset).

        >>> mini = NichtDeterministischerAutomat('s0', 's0', 's0', '0 1', { 's0' : {'0' : 's0'}})
        >>> mini._fzString(frozenset([]))
        '{}'
        >>> mini._fzString(frozenset(['a', 'c', 'b']))
        '{a,b,c}'

        """
        return '{%s}' % ','.join(sorted(what))

    def _int2bin(self, value, fill=0):
        """
        >>> A = NichtDeterministischerAutomat('z0 z1', 'z0', 'z0', '0 1', {'z0' : {'0' : 'z0', '1' : 'z1'}, 'z1' : {'0' : 'z0', '1' : 'z1'}})
        >>> b2 = A._int2bin(2)
        >>> b2
        '10'
        >>> A.check(b2)
        True
        >>> b1 = A._int2bin(1)
        >>> b1
        '1'
        >>> A.check(b1)
        False
        """
        result = list()
        while value:
            result.append(str(value & 1))
            value >>= 1
        result.reverse()
        return ''.join(result).zfill(fill)

    def _fixDeltaMapping(self, delta):
        """
        Sorgt dafuer, dass das zurueckgegebene dictionary die folgende Struktur hat:
            {
                Zustand : {
                            <Zeichen-Set> : <Zustand-Set>
                            }
            }

        >>> delta = { 's0' : {'0' : 's0'} }
        >>> delta
        {'s0': {'0': 's0'}}
        >>> mini = NichtDeterministischerAutomat('s0', 's0', 's0', '0 1', delta)
        >>> deltaNeu = mini._fixDeltaMapping(delta)
        >>> deltaNeu
        {'s0': {frozenset(['0']): frozenset(['s0'])}}
        >>> oDelta = { 'a' : {'a b c' : 'd e f'} }
        >>> nDelta = mini._fixDeltaMapping(oDelta)
        >>> nDelta
        {'a': {frozenset(['a', 'c', 'b']): frozenset(['e', 'd', 'f'])}}
        """
        deltaNeu = dict()
        for zustand in delta.keys():
            deltaNeu[zustand] = dict()
            for zeichen in delta[zustand]:
                ziel = delta[zustand][zeichen]
                sZeichen = self._toFrozenSet(zeichen)
                sZiel = self._toFrozenSet(ziel)
                deltaNeu[zustand][sZeichen] = sZiel

            loeschBar = list()
            zielDict = dict()
            for zeichenMenge in deltaNeu[zustand]:
                zielMenge = deltaNeu[zustand][zeichenMenge]
                # self.log.debug("** Zustand '%s' : %s => %s" % (zustand, zeichenMenge, zielMenge))
                if zielMenge not in zielDict:
                    zielDict[zielMenge] = frozenset()

                # self.log.debug("== Old: %s, New: %s" % (zielDict[zielMenge], zeichenMenge))
                zielDict[zielMenge] = zielDict[zielMenge].union(zeichenMenge)
                # self.log.debug(">> Now: %s" % (zielDict[zielMenge]))
                loeschBar.append(zeichenMenge)

            # self.log.error("XX " + self.dump(deltaNeu))
            for zeichenMenge in loeschBar:
                # self.log.debug("-- loesche Uebergang fuer '%s': %s" % (zustand, zeichenMenge))
                del (deltaNeu[zustand][zeichenMenge])
            # self.log.error("YY " + self.dump(deltaNeu))

            zustandDict = dict()
            for ziel in zielDict:
                zeichen = zielDict[ziel]
                zustandDict[zeichen] = ziel

                self.log.debug(">> Zustand '%s' : %s => %s" % (zustand, zeichen, ziel))
                deltaNeu[zustand][zeichen] = ziel
            # self.log.error("ZZ " + self.dump(deltaNeu))

        # self.log.debug(deltaNeu)
        return deltaNeu

    def _initLogging(self):
        self.log = AutomatLogger().log

    def __init__(self, S, s0, F, Sigma, delta, name="EinNDA", beschreibung='',
                 testWords=None, verifyWords=None, verifyRegExp=None):
        """
        >>> mini = NichtDeterministischerAutomat('s0 s1 s2 s3', 's0', 's3', '0 1', {'s0' : {'0' : ['s0', 's1'], '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}})
        >>> mini._delta('s0', '0')
        frozenset(['s1', 's0'])
        >>> mini._delta('s0', 'b')
        Traceback (most recent call last):
        ...
        NotInSigmaException: 'b' ist nicht Teil der Menge der Eingabezeichen [0,1]
        >>> mini._delta('zX', '0')
        Traceback (most recent call last):
        ...
        NoSuchStateException: 'zX' ist nicht Teil der Menge der moeglichen Zustaende [s0,s1,s2,s3]
        >>> mini = NichtDeterministischerAutomat('s0 s1 s2 s3', 'zY', 's3', '0 1', {'s0' : {'0' : ['s0', 's1'], '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}})
        Traceback (most recent call last):
        ...
        NoSuchStateException: *STARTZUSTAND* frozenset(['zY']) ist nicht Teil der Menge der moeglichen Zustaende [s0,s1,s2,s3]
        >>> mini = NichtDeterministischerAutomat('s0 s1 s2 s3', 's0', 'zZ', '0 1', {'s0' : {'0' : ['s0', 's1'], '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}})
        Traceback (most recent call last):
        ...
        NoSuchStateException: *ENDZUSTAENDE* frozenset(['zZ']) ist nicht Teil der Menge der moeglichen Zustaende [s0,s1,s2,s3]
        >>> mini = NichtDeterministischerAutomat('s0 s1 s2 s3', 's0', 's3', '0 1', {'NotInAlphabet' : {'0' : ['s0', 's1'], '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}})
        Traceback (most recent call last):
        ...
        NoSuchStateException: *UEBERFUEHRUNGSFUNKTION* frozenset(['NotInAlphabet']) ist nicht Teil der Menge der moeglichen Zustaende [s0,s1,s2,s3]

        @param S: Endliche Menge der moeglichen Zustaende
        @param s0: Anfangszustaende
        @param F: Menge der Endzustaende
        @param Sigma: Endliche Menge der Eingabezeichen
        @param delta: Zustands-Ueberfuehrungstabelle/dict()
        @param name: Bezeichner fuer den Automaten
        @param beschreibung: Beschreibung fuer den Automaten
        """
        self._initLogging()

        # Umwandeln von Listen und Stringinhalte (whitespace-getrennt) in frozenset-Mengen
        S = self._toFrozenSet(S)
        F = self._toFrozenSet(F)
        Sigma = self._toFrozenSet(Sigma)
        s0 = self._toFrozenSet(s0)

        # Ueberpruefen I - S, s0, F, Sigma sowie delta duerfen nicht leer sein.
        if len(S) == 0:
            raise ValueError('Die "endliche Menge der möglichen Zustände" S des Automaten ist leer')
        if len(s0) == 0:
            raise ValueError('Die "Menge der Anfangszustände" des Automaten ist leer')
        if len(F) == 0:
            raise ValueError('Die "Menge der Endzustände" F ist leer')
        if len(Sigma) == 0:
            raise ValueError('Die "endliche Menge der Eingabezeichen, Alphabet" Σ (Sigma) ist leer')
        if len(delta) == 0:
            raise ValueError('Die "(determinierte) Zustands-Überführungsfunktion" δ (delta) ist leer')

        # Ueberpruefen II - s0 und F muessen Untermengen von S sein
        if not s0.issubset(S):
            raise NoSuchStateException(s0, S, hint="Startzustand")
        if not F.issubset(S):
            raise NoSuchStateException(F, S, hint="Endzustaende")

        self.S = S
        self.s0 = s0
        self.F = F
        self.Sigma = Sigma
        self.delta = self._fixDeltaMapping(delta)
        self.ableitungsPfad = list()

        # Ueberpruefen III - das delta Ueberfuehrungsregelwerk soll keine Uebergaenge fuer Zustaende
        #                    definieren, die nicht eine Untermenge von S sind
        fzDeltaKeys = frozenset(self.delta.keys())
        if not fzDeltaKeys.issubset(self.S):
            raise NoSuchStateException(fzDeltaKeys.difference(self.S), self.S, "Ueberfuehrungsfunktion")

        # Ueberpruefen IV - das delta Ueberfuehrungsregelwerk soll keine Uebergaenge fuer Zustaende
        #                    definieren, die Zeichen benutzen, die nicht in Sigma sind
        for zustand in fzDeltaKeys:
            zZeichen = self.delta[zustand].keys()
            zeichenSet = set()
            for item in zZeichen:
                addme = list(item)[0]
                zeichenSet.add(addme)
            self.log.debug('%s : %s, in Sigma: %s' % (zustand, zeichenSet, zeichenSet.issubset(self.Sigma)))

            if not zeichenSet.issubset(self.Sigma):
                raise NotInSigmaException(zeichenSet.difference(self.Sigma), self.Sigma)

        # Ein paar meta Daten ..
        self.name = name
        self.abbildungen = 0
        self.ZustandIndex = dict()
        if testWords:
            self.testWords = self._toList(testWords)
        else:
            self.testWords = None
            self.log.warning("[%s] No testwords provided." % self.name)
        self.verifyWords = verifyWords
        self.verifyRegExp = verifyRegExp
        self.beschreibung = beschreibung

        #: "Roh"-Daten des Ableitungspfades
        self.raw_ableitung = list()

        self.type = 'finite'
        if self.testWords == None:
            self.log.debug("Adding Test Words")
            self.testWords = self.testWorteGenerator()
        # Automat zuruecksetzen (aktuellen Zustand auf s0 setzen)
        self.reset()

    def _ableitungAppend(self, items):
        self.raw_ableitung.append(copy.deepcopy(items))

    # self.log.error("// + _ableitungAppend(%s)" % self.raw_ableitung[-1])

    def _ableitungReset(self):
        self.raw_ableitung = list()

    def _ableitungToString(self):
        return str(self.raw_ableitung)

    def _ableitungsPfad__str__(self):
        if len(self.ableitungsPfad) == 0:
            return ''
        items = list()
        for item in self.ableitungsPfad:
            items.append('{%s}' % ','.join(sorted(item)))
        return " Ableitung:\n %s" % ' -> '.join(items)

    def __str__(self):
        s = "%seterministischer Automat '%s'" % ((self.istDEA() and 'D' or 'Nichtd'), self.name)
        if EpsilonAutomat.EPSILON in self.Sigma:
            s += " (ε-Übergänge möglich)"
        s += "\n"
        if self.beschreibung:
            s += " %s\n" % self.beschreibung
        s += " Anfangszustand                          : %s\n" % self._fzString(self.s0)
        s += " Endliche Menge der möglichen Zustände S : %s\n" % self._fzString(self.S)
        s += " Menge der Endzustände F                 : %s\n" % self._fzString(self.F)
        s += " Endliche Menge der Eingabezeichen Σ     : %s\n" % self._fzString(self.Sigma)
        if '_getAsciiArtDeltaTable' in dir(self):
            s += self._getAsciiArtDeltaTable()
        s += " (%se Überführungsfunktion)\n" % (self.istDeltaVollstaendig() and 'vollständig' or 'partiell')
        return s

    def dump(self, delta=None):
        if not delta:
            delta = self.delta
        l = list()
        for zustand in sorted(delta):
            l.append("%s" % (zustand))
            for zeichenMenge in sorted(delta[zustand]):
                zielMenge = delta[zustand][zeichenMenge]
                l.append(" %-10s : %s" % (repr(zeichenMenge), repr(zielMenge)))
        return "\n".join(l)

    def reset(self):
        """
        Setzt den Automaten zurueck
        """
        self.Zustand = self.s0
        self._ableitungReset()
        self.ableitungsPfad = list()

    def istDEA(self):
        """
        Ein DEA zeichnet sich dadurch aus, dass
            * s0 ein einzelner Anfangszustand und
            * jedem Paar(s, a) aus [S kreuz Sigma] ein einzelner Funktionswert (Zustand)
        zugeordnet ist.

        >>> mini = NichtDeterministischerAutomat('s0 s1 s2 s3', 's0', 's3', '0 1', {'s0' : {'0' : 's0 s1', '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}})
        >>> mini.istDEA()
        False
        >>> m2 = NichtDeterministischerAutomat('s0 s1 s2 s3', 's0', 's3', '0 1', {'s0' : {'0' : 's0', '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}})
        >>> m2.istDEA()
        True
        """
        if (len(self.s0) != 1):
            return False
        for zustand in self.delta:
            for zeichen in self.delta[zustand]:
                if len(self.delta[zustand][zeichen]) != 1:
                    return False
        return True

    def istDeltaVollstaendig(self):
        """
        >>> mini = NichtDeterministischerAutomat('s0 s1 s2 s3', 's0', 's3', '0 1', {'s0' : {'0' : 's0 s1', '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}})
        >>> mini.istDeltaVollstaendig()
        False
        >>> m2 = NichtDeterministischerAutomat('s0 s1 s2 s3', 's0', 's3', '0 1', {'s0' : {'0' : 's0 s1', '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}, 's3' : {}})
        >>> m2.istDeltaVollstaendig()
        True
        """
        return len(self.F.difference(self.delta.keys())) == 0

    def testWorteGenerator(self, length=3, Sigma=None):
        """
        Generiert Testworte der gewuenschten Laenge bestehend aus dem Alphabet des Automaten.
        Optional kann Sigma angegeben werden

        >>> mini = NichtDeterministischerAutomat('s0 s1 s2 s3', 's0', 's3', '0 1', {'s0' : {'0' : 's0 s1', '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}})
        >>> mini.testWorteGenerator(length=1)
        ['1', '0', '11', '01', '10', '00']
        >>> mini.testWorteGenerator(Sigma=['a', 'b'], length=1)
        ['a', 'b', 'aa', 'ba', 'ab', 'bb']

        @param length: Maximal-Laenge der generierten Worte
        @param Sigma: (optional) Alternativ-Alphabet
        @return: Liste mit Testworten
        """
        if Sigma == None:
            Sigma = self.Sigma
        worte = list(Sigma)
        SigmaTmp = Sigma
        for i in xrange(length):
            SigmaTmp = [a + b for b in Sigma for a in SigmaTmp]
            worte += SigmaTmp
        return worte

    def _delta__str__(self, Zustand, Zeichen):
        """
        Delta Funktion, fuer Aufrufe innerhalb von __str__() Aufrufen verwendet werden kann.
        """
        return self._delta(Zustand, Zeichen)

    def _delta(self, Zustand, Zeichen):
        """
        Zustands-Ueberfuehrungsfunktion

        >>> mini = NichtDeterministischerAutomat('s0 s1 s2 s3', 's0', 's3', '0 1', {'s0' : {'0' : 's0 s1', '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}})
        >>> mini.S
        frozenset(['s3', 's2', 's1', 's0'])
        >>> mini.F
        frozenset(['s3'])
        >>> mini.Sigma
        frozenset(['1', '0'])
        >>> mini._delta(['s0', 's1'], 1)
        frozenset(['s2', 's0'])
        >>> mini._delta(frozenset(['s0', 's1']), 1)
        frozenset(['s2', 's0'])
        >>> mini._delta(['s0', 's1'], 1)
        frozenset(['s2', 's0'])
        >>> mini._delta(['s0', 's1', 's3'], 1)
        Traceback (most recent call last):
        ...
        NoRuleForStateException: 's3' hat keine definierten Regeln. [s0,s1,s2]
        >>> mini._delta('s0', '1')
        frozenset(['s0'])

        @param Zustand: Quell-Zustand (falls kein list()-Objekt: wird mittels str() umgewandelt)
        @param Zeichen: einzulesendes Zeichen (wird mittels str() umgewandelt)
        @return: Menge der erreichten Zustaende oder leere Menge
        """
        # Sicherstellen, dass Zeichen ein String ist
        Zeichen = str(Zeichen)
        # self.log.debug("_delta(%s, %s)" % (Zustand, Zeichen))

        if Zustand == frozenset([]):
            self.log.error("[%s] Zustand '%s' Ausgangszustand ist leere Menge!" % (self.name, repr(Zustand)))
            return frozenset([])

        # Pruefen, ob das zu lesende Zeichen ueberhaupt Teil der Menge der Eingabezeichen ist
        if Zeichen not in self.Sigma:
            self.log.debug(" '%s' nicht Teil des Alphabets (%s)" % (Zeichen, self._fzString(self.Sigma)))
            raise NotInSigmaException(Zeichen, self.Sigma)

        # Sonderbehandlung: Zustand kann auch eine Liste von Zustaenden sein
        if isinstance(Zustand, list):
            ziele = frozenset()
            for item in Zustand:
                ziele = ziele.union(self._delta(item, Zeichen))
            return ziele
        elif isinstance(Zustand, basestring):
            # Ansonsten: Zustand in frozenset verwandeln
            Zustand = frozenset([str(Zustand)])
        elif isinstance(Zustand, frozenset):
            if len(Zustand) > 1:
                # self.log.warning("!! Zustand: schon frozenset: %s %d" % (repr(Zustand), len(Zustand)))
                ziele = frozenset()
                for item in Zustand:
                    ziele = ziele.union(self._delta(item, Zeichen))
                return ziele
        else:
            self.log.warning("Zustand: nicht unterstuetzter Datentyp %s" % repr(Zustand))
            raise ValueError()

        # Da Namen der Zustaende Strings sind, brauchen wir den Zustand auch als String
        try:
            stringZustand = list(Zustand)[0]
        except Exception, e:
            self.log.error("[%s] Zustand '%s' Ausgangszustand ist leere Menge!" % (self.name, repr(Zustand)))
            return frozenset([])

        # Pruefen, ob der zu behandelnde Zustand ueberhaupt Teil der Zustandsmenge ist
        if not Zustand.issubset(self.S):
            # self.log.debug("Zustand '%s' nicht in der Zustandsmenge '%s' ?" % (Zustand, ','.join(sorted(self.S))))
            raise NoSuchStateException(stringZustand, self.S)

        # Keine Regeln fuer Zustand definiert
        if not Zustand.issubset(self.delta):
            raise NoRuleForStateException(stringZustand, self.delta.keys())

        for keyObject in self.delta[stringZustand].keys():
            if Zeichen in keyObject:
                return self.delta[stringZustand][keyObject]

        # self.log.debug("Kein Folgezustand fuer '%s' von '%s'." % (Zeichen, Zustand))
        return frozenset([])

    def check(self, Wort, doRaise=False):
        """
        Prüft, ob das gegebene Wort zur akzeptierten Sprache des Automaten gehoert
        >>> mini = NichtDeterministischerAutomat('z0 z1', 'z0', 'z1', 'a', {'z0' : {'a' : 'z1'}, 'z1' : {'a' : 'z1'}})
        >>> mini.check("a")
        True
        >>> mini.check("b")
        False
        >>> mini.check("aaaa")
        True
        >>> mini.check("aba")
        False
        >>> mini.check("aba", True)
        Traceback (most recent call last):
        ...
        NotInSigmaException: 'b' ist nicht Teil der Menge der Eingabezeichen [a]

        >>> mini2 = NichtDeterministischerAutomat('s0 s1 s2 s3', 's0', 's3', ['0', '1'], { 's0' : { "0" : 's1', "1" : 's0'}, 's1' : { '0' : 's2', '1' : 's0'}, 's2' : { '0' : 's2', '1' : 's3'}, 's3' : { '0' : 's3', '1' : 's3'} })
        >>> mini2.check("10011")
        True
        >>> mini2.check("a")
        False
        >>> mini2.check("111111111111")
        False
        >>> mini2.check("001")
        True
        >>> mini2.check("111111111111", True)
        Traceback (most recent call last):
        ...
        NoAcceptingStateException: frozenset(['s0']) ist nicht Teil der Menge der moeglichen Endzustaende [s3]
        >>> mini2.check("a", True)
        Traceback (most recent call last):
        ...
        NotInSigmaException: 'a' ist nicht Teil der Menge der Eingabezeichen [0,1]

        >>> mini3 = NichtDeterministischerAutomat('z0 z1', 'z0', 'z1', ['a', 'b'], {'z0' : {'a' : 'z1'}, 'z1' : {'a' : 'z1'}})
        >>> print mini3.Sigma
        frozenset(['a', 'b'])
        >>> mini3.check("ab", True)
        Traceback (most recent call last):
        ...
        NoAcceptingStateException: frozenset([]) ist nicht Teil der Menge der moeglichen Endzustaende [z0,z1]

        @param Wort: Das zu pruefende Wort
        @return: True oder False
        """
        self.reset()
        self.log.debug("Teste Wort '%s'" % Wort)
        Wort = str(Wort)

        for Zeichen in Wort:
            try:
                altZustand = self.Zustand
                self.Zustand = self._delta(self.Zustand, Zeichen)
                self.ableitungsPfad.append(self.Zustand)
                if len(self.Zustand) == 0:
                    msg = "Kein Ziel-Zustand fuer Zeichen '%s' (Alphabet: %s)" % (Zeichen, self._fzString(self.Sigma))
                    msg += " von Zustand %s definiert." % (self._fzString(altZustand))
                    self.log.debug(msg)
                    if doRaise:
                        raise NoAcceptingStateException(self.Zustand, self.S)
                    return False
            except NotInSigmaException, e:
                self.log.debug("Zeichen '%s' nicht Teil des Alphabet %s." % (Zeichen, self._fzString(self.Sigma)))
                if doRaise:
                    raise
                return False
            except NoRuleForStateException, e:
                self.log.debug("Zeichen '%s' nicht Teil des Alphabets." % Zeichen)
                if doRaise:
                    raise
                return False
            except EmptyStateException, e:
                self.log.error("Empty state ..")
                if doRaise:
                    raise
                return False
            except Exception, e:
                self.log.error("Sonstiger Fehler: %s" % e)
                if doRaise:
                    raise

        if len(self.Zustand.intersection(self.F)) == 0:
            self.log.debug("Kein Endzustand erreicht.")
            if doRaise:
                raise NoAcceptingStateException(self.Zustand, self.F)
            return False
        return True

    def checkVerbose(self, Wort, doRaise=False):
        raise NotImplementedError("checkVerbose not implemented")

    def checkStepByStep(self, Wort, doRaise=False):
        raise NotImplementedError("checkStepByStep not implemented")

    def checkWords(self, words, silence=False):
        resultset = list()
        words = self._toList(words)

        for word in words:
            result = 'OUCH'
            successful = False
            try:
                self.check(word, True)
                result = "Akzeptiert."
                successful = True
            except NotInSigmaException, e:
                result = "'%s' ist nicht im Alphabet." % e.value
            except NoSuchStateException, e:
                result = "Zustand '%s' ist nicht in Sigma." % e.value
            except NoAcceptingStateException, e:
                result = "Kein finaler Zustand erreicht."
            except NoRuleForStateException, e:
                result = "Kein finaler Zustand erreicht (Keine Regel definiert für '%s')." % e.value
            except Exception, e:
                result = "oh-oh, sonstiger Fehler .. '%s'" % e
            resultset.append((word, successful, result))

            if not silence:
                self.log.info(
                    "%-20s [%s] %-5s : %s" % (self.name, (successful and "SUCCESS" or "FAILURE"), word, result))
                self.log.debug(self._ableitungsPfad__str__())
        return resultset

    def _RegularExpressionTestWorte(self, worte, regexp=None):
        if not regexp:
            regexp = self.verifyRegExp
        if not regexp.startswith("^"):
            regexp = '^' + regexp
        if not regexp.endswith("$"):
            regexp += '$'
        pattern = re.compile(regexp)

        self.log.debug("RegExp : '%s'" % regexp)
        verifyWords = dict()
        for wort in worte:
            res = pattern.match(wort)
            verifyWords[wort] = pattern.match(wort) and True or False
            self.log.debug("         %s : %s" % (wort, verifyWords[wort]))
        return verifyWords

    def verifyByRegExp(self, testWords=None, regexp=None):
        if not testWords:
            testWords = self.testWords
        if not regexp and not self.verifyRegExp:
            self.log.debug("Cannot verify by Regular Expression, returning True")
            return True
        vWords = self._RegularExpressionTestWorte(testWords, regexp)
        self.log.debug("Verify by Regular Expression:")

        return self.verify(vWords, True)

    def verify(self, vWords=None, usingRegExp=False, doItVerbose=False):
        verified = True
        if vWords == None:
            vWords = self.verifyWords

        if vWords == None or (isinstance(vWords, dict) and len(vWords) == 0):
            self.log.warning("%s: Will not be verified. (No words to check)" % self.name)
            return

        for word in vWords:
            expectation = vWords[word]
            result = self.check(word)
            self.log.debug("[VERIFY] %-10s expecting: %-5s, got: %-5s" % (word, expectation, result))
            if expectation != result:
                self.log.warning("%s '%s' Verification FAILED! (expected: %s)" % (self.name, word, expectation))
                self.log.debug(self.ableitungsPfad)
                verified = False
            if doItVerbose:
                try:
                    self.checkStepByStep(word)
                except Exception, e:
                    pass

        logmessage = "Automat '%s' %sverifiziert%s. ('verifiziert' bedeutet: Erwartungen zumindest erfuellt!)." % (
        self.name,
        (not verified and 'NICHT ') or '',
        (usingRegExp and ' (via RE)') or '')
        if verified:
            self.log.info(logmessage)
        else:
            self.log.warning(logmessage)
        return verified

    def verifyVerbose(self, vWords=None, usingRegExp=False):
        return self.verify(vWords, usingRegExp, True)

    def EpsilonFrei(self):
        return self

    def Grammatik(self):
        if not self.istDEA:
            raise NotImplemented
        import grammatiken
        P = list()

        for zustand in sorted(self.delta):
            for zeichen in self.delta[zustand]:
                for ziel in self.delta[zustand][zeichen]:
                    for zeichenItem in zeichen:
                        P.append((zustand, zeichenItem, ziel))

        # G = (N, T, P, S)
        StartSymbol = list(self.s0)[0]
        return grammatiken.RechtslineareGrammatik(self.S, self.Sigma, P, StartSymbol, self.F)


class Automat(NichtDeterministischerAutomat):
    def __init__(self, S, s0, F, Sigma, delta, name="EinDEA", beschreibung='', testWords=None, verifyWords=None,
                 verifyRegExp=None):
        """
        >>> mini = Automat('s0 s1 s2 s3', 's0', 's3', '0 1', {'s0' : {'0' : 's0 s1', '1' : 's0'}, 's1' : {'0' : 's2', '1' : 's2'}, 's2' : { '0' : 's3', '1' : 's3'}})
        Traceback (most recent call last):
        ...
        Exception: Ich fuehle mich so nichtdeterministisch.

        >>> mini = Automat('z0 z1', 'z0', 'z1', 'a', {'z0' : {'a' : 'z1'}, 'z1' : {'a' : 'z1'}})
        >>> mini.check("a")
        True
        >>> mini.check("b")
        False
        >>> mini.check("aaaa")
        True
        >>> mini.check("aba")
        False
        >>> mini.check("aba", True)
        Traceback (most recent call last):
        ...
        NotInSigmaException: 'b' ist nicht Teil der Menge der Eingabezeichen [a]

        >>> mini2 = Automat('s0 s1 s2 s3', 's0', 's3', ['0', '1'], { 's0' : { "0" : 's1', "1" : 's0'}, 's1' : { '0' : 's2', '1' : 's0'}, 's2' : { '0' : 's2', '1' : 's3'}, 's3' : { '0' : 's3', '1' : 's3'} })
        >>> mini2.check("10011")
        True
        >>> mini2.check("a")
        False
        >>> mini2.check("111111111111")
        False
        >>> mini2.check("001")
        True
        >>> mini2.check("111111111111", True)
        Traceback (most recent call last):
        ...
        NoAcceptingStateException: frozenset(['s0']) ist nicht Teil der Menge der moeglichen Endzustaende [s3]
        >>> mini2.check("a", True)
        Traceback (most recent call last):
        ...
        NotInSigmaException: 'a' ist nicht Teil der Menge der Eingabezeichen [0,1]

        >>> mini3 = Automat('z0 z1', 'z0', 'z1', ['a', 'b'], {'z0' : {'a' : 'z1'}, 'z1' : {'a' : 'z1'}})
        >>> print mini3.Sigma
        frozenset(['a', 'b'])
        >>> mini3.check("ab", True)
        Traceback (most recent call last):
        ...
        NoAcceptingStateException: frozenset([]) ist nicht Teil der Menge der moeglichen Endzustaende [z0,z1]

        """
        NichtDeterministischerAutomat.__init__(self, S, s0, F, Sigma, delta, name, beschreibung, testWords, verifyWords,
                                               verifyRegExp)
        if not self.istDEA():
            raise Exception("Ich fuehle mich so nichtdeterministisch.")


class EpsilonAutomat(NichtDeterministischerAutomat):
    EPSILON = 'EPSILON'

    def __init__(self, S, s0, F, Sigma, delta, name="EinNDAe", beschreibung='', testWords=None, verifyWords=None,
                 verifyRegExp=None):
        """
        """
        Sigma = self._toList(Sigma)
        Sigma.append(EpsilonAutomat.EPSILON)
        NichtDeterministischerAutomat.__init__(self, S, s0, F, Sigma, delta, name, beschreibung, testWords, verifyWords,
                                               verifyRegExp)

    def _deltaEpsilonLookAhead(self, Zustand):
        leereMenge = frozenset([])
        eErreichbareZustaende = leereMenge

        # Zunaechst schauen wir, wie weit wir mit einem Epsilon vom gegebenen Zustand kommen
        eZustaendeEpsilon = NichtDeterministischerAutomat._delta(self, Zustand, EpsilonAutomat.EPSILON).difference(
            Zustand)
        while not (eZustaendeEpsilon == leereMenge):
            self.log.debug("** eZustaendeEpsilon     : %s %s" % (eZustaendeEpsilon, (eZustaendeEpsilon == leereMenge)))
            self.log.debug(" < eZustaendeEpsilon     : %s" % eZustaendeEpsilon)
            eErreichbareZustaende = eErreichbareZustaende.union(eZustaendeEpsilon).difference(Zustand)
            self.log.debug(" = eErreichbareZustaende : %s" % eErreichbareZustaende)
            eZustaendeEpsilon = NichtDeterministischerAutomat._delta(self, eZustaendeEpsilon,
                                                                     EpsilonAutomat.EPSILON).difference(
                eErreichbareZustaende)

        self.log.debug(">> eErreichbareZustaende : %s" % eErreichbareZustaende)
        return eErreichbareZustaende

    def _delta(self, Zustand, Zeichen):
        """
        >>> automatenString='Sigma: a b EPSILON; F:4; s0:0;'
        >>> automatenString += '0 a 2; 0 EPSILON 1; 1 EPSILON 3; 2 b 2; 3 a 4; 2 a 5; 2 EPSILON 7; 1 a 6; 6 a 6; 4 a 4; 5 a 5; 7 a 7;'
        >>> automatenString += 'AcceptedVerifyWords: a;FailingVerifyWords: b ba aa;Beschreibung:eAutomat;Name:eNEA'
        >>> L = automatenleser.AutomatenLeser(data=automatenString, dataDelimiter=';').automat()
        >>> print L._delta('0', 'a')
        frozenset(['2', '4', '7', '6'])
        >>> print L._delta('1', 'a')
        frozenset(['4', '6'])
        >>> print L._delta('1', 'b')
        frozenset([])
        >>> print L._delta('2', 'a')
        frozenset(['5', '7'])
        >>> automatenString='Sigma: a b EPSILON; F:2; s0:0;'
        >>> automatenString += '0 EPSILON 1; 1 EPSILON 0; 1 a 2; 2 EPSILON 0;'
        >>> L = automatenleser.AutomatenLeser(data=automatenString, dataDelimiter=';').automat()
        >>> print L._delta('0', 'a')
        frozenset(['1', '0', '2'])
        """
        self.log.debug("_delta<EpsilonAutomat>(%s, %s)" % (Zustand, Zeichen))
        leereMenge = frozenset([])

        eAusgangsZustaende = Zustand
        ausgangsZustaende = frozenset([Zustand])
        eErreichbareZustaende = leereMenge

        if Zeichen != EpsilonAutomat.EPSILON:
            eErreichbareZustaende = self._deltaEpsilonLookAhead(Zustand)
        else:
            self.log.debug("No Epsilon Lookahead")

        self.log.debug("! eErreichbareZustaende : %s" % eErreichbareZustaende)
        ausgangsZustaende = frozenset([Zustand]).union(eErreichbareZustaende.union(ausgangsZustaende)).difference(
            leereMenge)
        self.log.debug("! ausgangsZustaende : %s" % (ausgangsZustaende))

        if ausgangsZustaende == leereMenge:
            self.log.warning("Menge der Ausgangszustaende ist leer")
            return leereMenge

        erreichbareZustaende = leereMenge
        for item in ausgangsZustaende:
            # self.log.debug("item : %s" % item)
            fin = NichtDeterministischerAutomat._delta(self, item, Zeichen)
            eFin = leereMenge
            if fin != leereMenge:
                if Zeichen != EpsilonAutomat.EPSILON:
                    eFin = self._deltaEpsilonLookAhead(fin.difference(eErreichbareZustaende))
            # self.log.debug("+ eFin: %s" % eFin)
            erreichbareZustaende = erreichbareZustaende.union(fin, eFin)

        erreichbareZustaende = erreichbareZustaende.difference(leereMenge)
        if erreichbareZustaende == leereMenge:
            self.log.debug("Menge der erreichbaren Zustaende ist leer")

        erreichbareZustaende = erreichbareZustaende.difference(leereMenge)
        self.log.debug("Erreichbare Zustaende : %s" % erreichbareZustaende)

        return erreichbareZustaende

    def EpsilonFrei(self):
        """
        >>> automatenString='Sigma: a b EPSILON; F:2; s0:0;'
        >>> automatenString += '0 EPSILON 1; 1 EPSILON 0; 1 a 2; 2 EPSILON 0;'
        >>> L = automatenleser.AutomatenLeser(data=automatenString, dataDelimiter=';').automat()
        >>> print L.Sigma
        frozenset(['a', 'EPSILON', 'b'])
        >>> print L._delta('0', 'a')
        frozenset(['1', '0', '2'])
        >>> print L.delta
        {'1': {frozenset(['a']): frozenset(['2']), frozenset(['EPSILON']): frozenset(['0'])}, '0': {frozenset(['EPSILON']): frozenset(['1'])}, '2': {frozenset(['EPSILON']): frozenset(['0'])}}
        >>> N = L.EpsilonFrei()
        >>> print N._delta('0', 'a')
        frozenset(['1', '0', '2'])
        >>> print N.delta
        {'1': {frozenset(['a']): frozenset(['1', '0', '2'])}, '0': {frozenset(['a']): frozenset(['1', '0', '2'])}, '2': {frozenset(['a']): frozenset(['1', '0', '2'])}}
        >>> print N.Sigma
        frozenset(['a', 'b'])
        >>> L.check("a") == N.check("a")
        True
        >>> L._delta('0', 'a') == N._delta('0', 'a')
        True
        >>> L.F == N.F
        True
        >>> automatenString='Sigma: a b EPSILON; F:1; s0:0;'
        >>> automatenString += '0 EPSILON 1; 0 b 1; 1 EPSILON 1;'
        >>> L2 = automatenleser.AutomatenLeser(data=automatenString, dataDelimiter=';').automat()
        >>> N2 = L2.EpsilonFrei()
        >>> print L2.F
        frozenset(['1'])
        >>> print N2.F
        frozenset(['1', '0'])
        >>> L2 != N2
        True
        >>> print N2.delta
        {'1': {}, '0': {frozenset(['b']): frozenset(['1'])}}
        """
        neuDelta = dict()
        fzEpsilon = frozenset([EpsilonAutomat.EPSILON])

        for zustand in self.S:
            neuDelta[zustand] = dict()
            neuF = self.F
            for zeichen in self.Sigma.difference(fzEpsilon):
                ziele = self._delta(zustand, zeichen)
                if not ziele == frozenset([]):
                    neuDelta[zustand][zeichen] = ziele
                # Epsilon-Uebergaenge die zu einem Endzustand fuehren, sorgen dafuer, dass der
                # ausgangsZustand auch ein Endzustand werden muss
                eZiele = self._delta__str__(zustand, EpsilonAutomat.EPSILON)
                if self.F.intersection(eZiele) != frozenset([]):
                    neuF = neuF.union(frozenset([zustand]))

        # print neuDelta
        return NichtDeterministischerAutomat(self.S, self.s0, neuF, self.Sigma.difference(fzEpsilon), neuDelta,
                                             'eFrei ' + self.name, self.beschreibung, self.testWords, self.verifyWords,
                                             self.verifyRegExp)

    def _delta__str__(self, Zustand, Zeichen):
        """
        Delta Funktion, fuer Aufrufe innerhalb von __str__() Aufrufen verwendet werden kann.
        In diesem Fall werden Epsilon-Uebergaenge _nicht aufgeloest.
        """
        return NichtDeterministischerAutomat._delta(self, Zustand, Zeichen)

    def check(self, Wort, doRaise=False):
        try:
            result = NichtDeterministischerAutomat.check(self, Wort, doRaise=True)
            return result
        except NoAcceptingStateException, e:
            leereMenge = frozenset([])
            self.log.debug("Ende des Wortes, kein Endzustand erreicht, wir sind bei %s" % e.value)
            if e.value == leereMenge:
                self.log.debug("Wir sind bei leerer Menge, das wird also nichts mehr")
                if doRaise:
                    raise
                return False

            epsilonMenge = NichtDeterministischerAutomat._delta(self, e.value, EpsilonAutomat.EPSILON)
            self.log.debug("Mit epsilon gehts hierhin %s" % epsilonMenge)
            gesehen = dict()

            while epsilonMenge != leereMenge:
                inter = epsilonMenge.intersection(self.F)
                if inter != leereMenge:
                    self.log.debug("aber mit dem epsilon ..")
                    self.log.debug(inter)
                    return True
                if not gesehen.has_key(epsilonMenge):
                    gesehen[epsilonMenge] = 0
                gesehen[epsilonMenge] += 1
                if gesehen[epsilonMenge] > 1:
                    self.log.warning("loop %s" % gesehen)
                    raise
                epsilonMenge = NichtDeterministischerAutomat._delta(self, epsilonMenge, EpsilonAutomat.EPSILON)
            if doRaise:
                raise
        except Exception, e:
            if doRaise:
                raise
        self.log.debug("check(%s, %s) ----> FALSE" % (Wort, doRaise))
        return False

    def testWorteGenerator(self, length=3, Sigma=None):
        return NichtDeterministischerAutomat.testWorteGenerator(self, length,
                                                                self.Sigma - frozenset([EpsilonAutomat.EPSILON]))


if __name__ == '__main__':
    test()
