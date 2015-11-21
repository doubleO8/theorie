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
import re
from subprocess import *
import logging

import automaten
import crappy_logger
from crappy_logger import AutomatLogger


def test():
    """
    doctest (unit testing)
    """
    import doctest
    crappy_logger.AutomatLogger(logging.DEBUG).log
    failed, total = doctest.testmod()
    print("doctest: %d/%d tests failed." % (failed, total))


class AutomatenLeser(object):
    #: Regular Expression, die AutomatenLeser.doppelPunkte von Whitespace um sich herum befreit
    doppelPunkt = re.compile(r'\s+:\s+')

    def _getFileContent(self, filename):
        if not os.path.isfile(filename):
            raise IOError("Datei '%s' nicht gefunden." % (filename))
        return open(filename).readlines()

    def _strippedList(self, l):
        out = list()
        for item in l:
            item = item.strip()
            if item != '' and not item.startswith("#"):
                out.append(item)
        return out

    def _teileOderJaule(self, line, description='Etwas'):
        (field, sepp, data) = line.rpartition(':')
        if field != '' and sepp != '':
            return data.split()
        else:
            self.log.error("Konnte Definition von %s nicht aus '%s' lesen." % (description, data))
        return None

    def _parseLineSimple(self, line):
        for keyword in self.supportedKeywords:
            if line.startswith(keyword + ':'):
                if self._data.has_key(keyword):
                    self.log.debug("Bereits definiert : '%s' (wird ueberschrieben)" % keyword)
                self._data[keyword] = self._teileOderJaule(line, keyword)
                return True
        return False

    def parsePlaintext(self, lines=None, description='<Lines>'):
        if lines == None:
            lines = self.lines
        if self.filename:
            description = '<File> %s' % self.filename

        Sigma = None
        F = None
        s0 = None
        S = set()
        Sread = None
        delta = dict()
        name = 'EinAutomat'
        beschreibung = ''
        verifyWords = None
        testWords = None
        verifyRegExp = None
        failingWords = list()
        acceptedWords = list()

        for line in lines:
            line = AutomatenLeser.doppelPunkt.sub(':', line.lstrip(), count=1)

            if line.startswith("Sigma:"):
                if Sigma != None:
                    self.log.warning("Sigma bereits definiert (%s)" % Sigma)
                Sigma = self._teileOderJaule(line, 'Sigma')
            elif line.startswith("S:"):
                if Sread != None:
                    self.log.warning("Sread bereits definiert (%s)" % F)
                Sread = self._teileOderJaule(line, 'S')
            elif line.startswith("F:"):
                if F != None:
                    self.log.warning("F bereits definiert (%s)" % F)
                F = self._teileOderJaule(line, 'F')
            elif line.startswith("s0:"):
                if s0 != None:
                    self.log.warning("s0 bereits definiert (%s)" % s0)
                s0 = self._teileOderJaule(line, 's0')
            elif line.startswith("FailingVerifyWords:"):
                failingWords = self._teileOderJaule(line, 'Nicht akzeptierte Worte')
            elif line.startswith("AcceptedVerifyWords:"):
                acceptedWords = self._teileOderJaule(line, 'Zu akzeptierende Worte')
            elif line.startswith("TestWords:"):
                testWords = self._teileOderJaule(line, 'Testworte')

            elif line.startswith("RegularExpression:"):
                verifyRegExp = self._teileOderJaule(line, 'Regular Expression')[0]

            elif line.startswith("Name:"):
                data = self._teileOderJaule(line, 'Name')
                if data:
                    name = ' '.join(data).lstrip()
            elif line.startswith("Beschreibung:"):
                data = self._teileOderJaule(line, 'Beschreibung')
                if data:
                    beschreibung = ' '.join(data).lstrip()

            else:
                splatter = line.split()
                if len(splatter) != 3:
                    self.log.warning(
                        "%s: [%s] Konnte Ueberfuehrungsdefinition nicht aus '%s' lesen" % (description, name, line))
                else:
                    (zustand, zeichen, ziel) = splatter
                    S.add(zustand)
                    S.add(ziel)
                    if delta.has_key(zustand):
                        # self.log.debug("Zustand '%s' ist bereits in delta" % zustand)
                        pass
                    else:
                        delta[zustand] = dict()
                    dd = delta[zustand]

                    if zeichen.find(',') != -1:
                        # self.log.debug("Zeichen LISTE")
                        zListe = zeichen.split(',')
                    else:
                        zListe = list([zeichen])

                    for zeichen in zListe:
                        if dd.has_key(zeichen):
                            self.log.debug("Zustand '%s', Zeichen '%s' ist bereits in delta" % (zustand, zeichen))
                        else:
                            dd[zeichen] = set()

                        dd[zeichen].add(ziel)

        if len(failingWords) + len(acceptedWords) > 0:
            verifyWords = dict()
            for fail in failingWords:
                verifyWords[fail] = False
            for accept in acceptedWords:
                verifyWords[accept] = True

        if Sread:
            Sread = set(Sread)
            self.log.debug("S=%s wird erweitert um Sread=%s" % (S, Sread))
            S = S.union(Sread)
            for zustand in Sread:
                if not delta.has_key(zustand):
                    delta[zustand] = dict()
        self.log.debug("Name: '%s'" % name)
        self.log.debug("Beschreibung: '%s'" % beschreibung)
        self.log.debug("Sigma: %s" % Sigma)
        self.log.debug("S: %s" % S)
        self.log.debug("Sread: %s" % Sread)
        self.log.debug("s0: %s" % s0)
        self.log.debug("F: %s" % F)
        self.log.debug("delta: %s" % delta)
        self.log.debug("verifyWords: %s" % verifyWords)
        self.log.debug("testWords: %s" % testWords)
        self.log.debug("Regular Expression: %s" % verifyRegExp)

        return (S, s0, F, Sigma, delta, name, beschreibung, verifyWords, testWords, verifyRegExp)

    def _initLogging(self, log=None):
        if not log:
            self.log = crappy_logger.AutomatLogger().log
        else:
            self.log = log

    def automat(self):
        if self.type == 'finite':
            (S, s0, F, Sigma, delta, name, beschreibung, verifyWords, testWords, verifyRegExp) = self.parsePlaintext()
            if automaten.EpsilonAutomat.EPSILON in Sigma:
                return automaten.EpsilonAutomat(S, s0, F, Sigma, delta, name, beschreibung, verifyWords=verifyWords,
                                                testWords=testWords, verifyRegExp=verifyRegExp)
            return automaten.NichtDeterministischerAutomat(S, s0, F, Sigma, delta, name, beschreibung,
                                                           verifyWords=verifyWords, testWords=testWords,
                                                           verifyRegExp=verifyRegExp)
        elif self.type == 'pushdown':
            tmp = KellerautomatLeser(self.filename, contentList=self.lines, log=self.log, parentInit=False)
            return tmp.automat()
        elif self.type == 'turing':
            tmp = TuringLeser(self.filename, contentList=self.lines, log=self.log, parentInit=False)
            return tmp.automat()
        else:
            raise NotImplementedError("Unknown Type '%s'" % self.type)

    def _guessType(self, default='finite'):
        """
        Versucht den Automatentyp zu erraten
        """
        for line in self.lines:
            if line.startswith("Type:"):
                t = self._teileOderJaule(line, 'Type')[0]
                # self.log.warning(t)
                return t

        return default

    def __init__(self, filename=None, contentList=None, data=None, dataDelimiter="\n", log=None, defaultType='finite'):
        """
        >>> AutomatenLeser()
        Traceback (most recent call last):
        ...
        ValueError: Hmm .. ohne Daten wird's schwierig.
        >>> automatenString='Sigma			: 0 1; F             :  B              ;A                  1        B;A 0 A;s0:A;AcceptedVerifyWords: 01 1;FailingVerifyWords: 0 00 10;Beschreibung:DumbAutomat;Name:DumpDumb'
        >>> L = AutomatenLeser(data=automatenString, dataDelimiter=';').automat()
        >>> print L.Sigma
        frozenset(['1', '0'])
        >>> print L.S
        frozenset(['A', 'B'])
        >>> print L.F
        frozenset(['B'])
        >>> print L.delta
        {'A': {frozenset(['1']): frozenset(['B']), frozenset(['0']): frozenset(['A'])}}
        >>> L.verify()
        True
        >>> L.name
        'DumpDumb'
        >>> L.beschreibung
        'DumbAutomat'
        >>> Leser2 = AutomatenLeser(filename='data/geib_u10a1')
        >>> Leser2.type == 'pushdown'
        True
        >>> a = Leser2.automat()
        >>> len(a.rulesDict) > 0
        True
        """
        self._initLogging(log)

        #: Nicht-Kommentar-Zeilen
        self.lines = list()

        #: Name der eingelesenen Datei
        self.filename = None

        #: Temporaeres Content-Objekt
        content = list()

        if filename != None:
            self.filename = filename
            content = self._strippedList(self._getFileContent(filename))
        elif contentList != None:
            content = contentList
        elif data != None:
            content = data.split(dataDelimiter)
        else:
            raise ValueError("Hmm .. ohne Daten wird's schwierig.")

        if len(content) == 0:
            raise ValueError("content ist leer")
        else:
            self.lines = content

        #: Automat-Typ
        self.type = self._guessType(defaultType)


class KellerautomatLeser(AutomatenLeser):
    def __init__(self, filename=None, contentList=None, data=None, dataDelimiter="\n", log=None, parentInit=True):
        if parentInit:
            AutomatenLeser.__init__(self, filename, contentList, data, dataDelimiter, log)
        else:
            # Daten wurden schon gelesen, geparst, also: Nur im Objekt speichern und logging einrichten.
            self.filename = filename
            self.lines = contentList
            self._initLogging(log)
        self.supportedKeywords = ['Sigma', 'S', 'F', 'K', 'k0', 's0', 'AcceptedVerifyWords', 'FailingVerifyWords']
        self._data = dict()

    def automat(self):
        """
        >>> K = KellerautomatLeser('data/barth_keller_51')
        >>> K.parsePlaintext()
        >>> len(K._data) > 0
        True
        >>> a = K.automat()
        >>> a.check("aaabbb", False)
        True
        >>> a.check("aabbb")
        False
        >>> a.verify()
        True
        >>> K2 = KellerautomatLeser('data/geib_u10a1')
        >>> K2.parsePlaintext()
        >>> len(K2._data) > 0
        True
        >>> a = K2.automat()
        >>> a.checkVerbose("aaabb")
        False
        >>> a.checkVerbose("aabbb")
        False
        >>> a.checkVerbose("abab")
        False
        >>> a.checkVerbose("aabb")
        True
        """
        import kellerautomaten
        self.parsePlaintext()

        a = kellerautomaten.DeterministischerKellerautomat(
            self._data['S'],
            self._data['s0'],
            self._data['F'],
            self._data['Sigma'],
            self._data['K'],
            self._data['k0'],
            name=self._data['name'],
            beschreibung=self._data['beschreibung'],
            verifyWords=self._data['verifyWords'],
        )
        for rule in self._data['rules']:
            (zustand, bandzeichen, kellerzeichen, zustandStrich, kellerzeichenStrich) = rule
            a.addRule(zustand, bandzeichen, kellerzeichen, zustandStrich, kellerzeichenStrich)
        return a

    def parsePlaintext(self, lines=None, description='<Lines>'):
        """
        """
        self._data = {
            'rules': list(),
            'FailingVerifyWords': list(),
            'AcceptedVerifyWords': list(),
            'k0': 'k0',
            'name': 'SomePDA',
            'beschreibung': '',
            'verifyWords': None
        }

        if lines == None:
            lines = self.lines
        if self.filename:
            description = '<File> %s' % self.filename

        for line in lines:
            line = AutomatenLeser.doppelPunkt.sub(':', line.lstrip(), count=1)
            if self._parseLineSimple(line):
                # self.log.debug("(line parsed)")
                pass

            elif line.startswith("Name:"):
                data = self._teileOderJaule(line, 'Name')
                if data:
                    self._data['name'] = ' '.join(data).lstrip()
            elif line.startswith("Beschreibung:"):
                data = self._teileOderJaule(line, 'Beschreibung')
                if data:
                    self._data['beschreibung'] = ' '.join(data).lstrip()
            elif line.startswith("Type"):
                pass
            else:
                splatter = line.split()
                if len(splatter) != 5:
                    self.log.warning("%s: [%s] Konnte Ueberfuehrungsdefinition nicht aus '%s' lesen" % (
                    description, self._data['name'], line))
                else:
                    (zustand, bandZeichen, kellerZeichen, zustandStrich, kellerStrich) = splatter
                    self._data['rules'].append((zustand, bandZeichen, kellerZeichen, zustandStrich, kellerStrich))

        if len(self._data['FailingVerifyWords']) + len(self._data['AcceptedVerifyWords']) > 0:
            self._data['verifyWords'] = dict()
            for fail in self._data['FailingVerifyWords']:
                self._data['verifyWords'][fail] = False
            for accept in self._data['AcceptedVerifyWords']:
                self._data['verifyWords'][accept] = True

        # s0 darf keine liste sein..
        if isinstance(self._data['s0'], list):
            self._data['s0'] = self._data['s0'][0]

        for keyword in sorted(self.supportedKeywords + ['name', 'beschreibung', 'rules']):
            if self._data.has_key(keyword):
                self.log.debug("%s: %s" % (keyword, repr(self._data[keyword])))
            else:
                self.log.debug("%s: n/a" % keyword)


class TuringLeser(AutomatenLeser):
    def __init__(self, filename=None, contentList=None, data=None, dataDelimiter="\n", log=None, parentInit=True):
        if parentInit:
            AutomatenLeser.__init__(self, filename, contentList, data, dataDelimiter, log)
        else:
            # Daten wurden schon gelesen, geparst, also: Nur im Objekt speichern und logging einrichten.
            self.filename = filename
            self.lines = contentList
            self._initLogging(log)
        self.supportedKeywords = ['Sigma', 'S', 'F', 'B', 's0', 'AcceptedVerifyWords', 'FailingVerifyWords']
        self._data = dict()

    def automat(self):
        """
        >>> TL = TuringLeser('data/geib_u12a3')
        >>> TL.parsePlaintext()
        >>> len(TL._data) > 0
        True
        >>> a = TL.automat()
        >>> a.check("01", False)
        True
        >>> a.check("001")
        False
        >>> a.verify()
        True
        """
        import turingmachine
        self.parsePlaintext()

        a = turingmachine.TuringMachine(
            self._data['S'],
            self._data['s0'],
            self._data['F'],
            self._data['Sigma'],
            self._data['B'],
            name=self._data['name'],
            beschreibung=self._data['beschreibung'],
            verifyWords=self._data['verifyWords'],
        )
        for rule in self._data['rules']:
            (zustand, bandzeichen, zustandStrich, bandzeichenStrich, aktion) = rule
            a.addRule(zustand, bandzeichen, zustandStrich, bandzeichenStrich, aktion)
        return a

    def parsePlaintext(self, lines=None, description='<Lines>'):
        """
        """
        self._data = {
            'rules': list(),
            'FailingVerifyWords': list(),
            'AcceptedVerifyWords': list(),
            'name': 'SomeTM',
            'beschreibung': '',
            'verifyWords': None
        }

        if lines == None:
            lines = self.lines
        if self.filename:
            description = '<File> %s' % self.filename

        for line in lines:
            line = AutomatenLeser.doppelPunkt.sub(':', line.lstrip(), count=1)
            if self._parseLineSimple(line):
                # self.log.debug("(line parsed)")
                pass

            elif line.startswith("Name:"):
                data = self._teileOderJaule(line, 'Name')
                if data:
                    self._data['name'] = ' '.join(data).lstrip()
            elif line.startswith("Beschreibung:"):
                data = self._teileOderJaule(line, 'Beschreibung')
                if data:
                    self._data['beschreibung'] = ' '.join(data).lstrip()
            elif line.startswith("Type"):
                pass
            else:
                splatter = line.split()
                if len(splatter) != 5:
                    self.log.warning("%s: [%s] Konnte Ueberfuehrungsdefinition nicht aus '%s' lesen" % (
                    description, self._data['name'], line))
                else:
                    (zustand, bandzeichen, zustandStrich, bandzeichenStrich, aktion) = splatter
                    self._data['rules'].append((zustand, bandzeichen, zustandStrich, bandzeichenStrich, aktion))

        if len(self._data['FailingVerifyWords']) + len(self._data['AcceptedVerifyWords']) > 0:
            self._data['verifyWords'] = dict()
            for fail in self._data['FailingVerifyWords']:
                self._data['verifyWords'][fail] = False
            for accept in self._data['AcceptedVerifyWords']:
                self._data['verifyWords'][accept] = True

        # s0 darf keine liste sein..
        if isinstance(self._data['s0'], list):
            self._data['s0'] = self._data['s0'][0]

        for keyword in sorted(self.supportedKeywords + ['name', 'beschreibung', 'rules']):
            if self._data.has_key(keyword):
                self.log.debug("%s: %s" % (keyword, repr(self._data[keyword])))
            else:
                self.log.debug("%s: n/a" % keyword)


if __name__ == '__main__':
    test()
