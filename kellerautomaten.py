#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging, logging.config, os, sys, re
import automaten
import automatenausgabe, automatenleser


def test():
    """
    doctest (unit testing)
    """
    import doctest
    automaten.AutomatLogger(logging.DEBUG).log
    failed, total = doctest.testmod()
    print("doctest: %d/%d tests failed." % (failed, total))


class DeterministischerKellerautomat(automatenausgabe.OLaTeXKellerAutomat, automatenausgabe.OAsciiKellerAutomat,
                                     automatenausgabe.OPlaintextKellerAutomat, automaten.Automat):
    EPSILON = 'EPSILON'
    DELIMITER = '#'

    ACCEPT_BY_FINALSTATE_AND_EMPTYSTACK = 0
    ACCEPT_BY_FINALSTATE = 1
    ACCEPT_BY_EMPTYSTACK = 2
    ACCEPT_BY_ALL = 3

    #: Beschreibung des Verfahrens zum Akzeptieren eines Wortes
    ACCEPT_DESCRIPTION = ['Finaler Zustand und leerer Keller', 'Erreichen eines finalen Zustandes', 'Leerer Keller',
                          'Finaler Zustand, Keller und Band leer']

    #: Uebergaenge mit Epsilon hinzufuegen fuer bereits definierte Regeln erlauben ?
    ALLOW_EPSILON_RULES = True

    #: strict mode: Warnung bei DELIMITER <=> EPSILON Austausch etc.
    strict = True

    def __init__(self, S, s0, F, Sigma, K, k0='k0', delta=None,
                 name="EinDPDA", beschreibung='',
                 testWords=None, verifyWords=None, verifyRegExp=None, accept=0):
        self._initLogging()

        # Umwandeln von Listen und Stringinhalte (whitespace-getrennt) in frozenset-Mengen
        self.S = self._toFrozenSet(S)
        self.s0 = s0
        self.F = self._toFrozenSet(F)
        self.Sigma = self._toFrozenSet(Sigma)
        self.K = self._toFrozenSet(K)
        self.k0 = k0
        if delta == None:
            delta = dict()
        self.delta = delta
        self.keller = [k0]
        self.zustand = self.s0
        self.name = name
        self.beschreibung = beschreibung
        self.verifyWords = verifyWords
        self.testWords = testWords

        self.abbildungen = 0

        #: Verfahren, das angewendet werden soll, um zu bestimmen, ob ein Wort akzeptiert wird oder nicht
        self.accept = accept

        #: Automatentyp
        self.type = 'pushdown'

        self.rulesCounter = 1
        #: Dict mit den Ableitungsregeln, so dass
        # Ableitungsregeln wie folgt aufgelistet werden koennen ..
        # (Zustand, Bandinhalt, Kellerinhalt) |- #<NUMMER> (Zustand', Bandinhalt', Kellerinhalt')
        self.rulesDict = dict()

        self.reset()

    def reset(self):
        automaten.Automat.reset(self)
        self.keller = [self.k0]
        self.zustand = self.s0

    def addRule(self, zustand, bandzeichen, kellerzeichen, zustandStrich, kellerzeichenStrich):
        """
        >>> S = ['s0', 's1', 's2', 's3']
        >>> Sigma = ['a', 'b']
        >>> F = ['s0', 's3']
        >>> k0 = 'k0'
        >>> K = [k0, 'a']
        >>> s0 = 's0'
        >>> PDA = DeterministischerKellerautomat(S, s0, F, Sigma, K, k0)
        >>> PDA.addRule('s44', 'a', 'k0', 's1', 'a+k0')
        Traceback (most recent call last):
        ...
        NoSuchStateException: 's44' ist nicht Teil der Menge der moeglichen Zustaende [s0,s1,s2,s3]
        >>> PDA.addRule('s0', 'X', 'k0', 's1', 'a+k0')
        Traceback (most recent call last):
        ...
        NotInSigmaException: 'X' ist nicht Teil der Menge der Eingabezeichen [a,b]
        >>> PDA.addRule('s0', 'a', 'b', 's1', 'a+k0')
        Traceback (most recent call last):
        ...
        NotInKException: 'b' ist nicht Teil der Menge der Kellerzeichen [a,k0]
        >>> PDA.addRule('s0', 'a', 'k0', 's2', 'a')
        True
        >>> PDA.addRule('s0', 'a', 'k0', 's1', 'a+k0')
        True
        >>> PDA.delta['s0'][('a', 'k0')] == ('s1', ['a', 'k0'])
        True
        >>> PDA.flushRules()
        0
        >>> PDA.addRule('s0', 'a', 'k0', 's1', 'a+k0')
        True
        >>> PDA.addRule('s0', 'a', 'k0', 's1', ['a', k0])
        True
        >>> PDA.addRule('s1', 'a', 'a', 's1', 'a+a')
        True
        >>> PDA.addRule('s1', 'b', 'a', 's2', 'EPSILON')
        True
        >>> PDA.addRule('s2', 'b', 'a', 's2', 'EPSILON')
        True
        >>> PDA.addRule('s2', 'EPSILON', 'k0', 's3', 'k0')
        True
        """
        if zustand not in self.S:
            raise automaten.NoSuchStateException(zustand, self.S)
        if bandzeichen not in self.Sigma and (bandzeichen != self.EPSILON):
            raise automaten.NotInSigmaException(bandzeichen, self.Sigma)
        if kellerzeichen not in self.K:
            raise automaten.NotInKException(kellerzeichen, self.K)

        if self.delta.has_key(zustand):
            if self.delta[zustand].has_key((bandzeichen, kellerzeichen)):
                (altZustandStrich, altKellerzeichenStrich) = self.delta[zustand][(bandzeichen, kellerzeichen)]
                self.log.debug("Overriding rule: delta(%s, %s, %s) = (%s, %s)" % (
                    zustand, bandzeichen, kellerzeichen, altZustandStrich, altKellerzeichenStrich))
                self.log.debug("           with: delta(%s, %s, %s) = (%s, %s)" % (
                    zustand, bandzeichen, kellerzeichen, zustandStrich, kellerzeichenStrich))

            if not DeterministischerKellerautomat.ALLOW_EPSILON_RULES:
                if self.delta[zustand].has_key((DeterministischerKellerautomat.EPSILON, kellerzeichen)):
                    self.log.error("Schon EPSILON-Uebergang definiert: delta(%s, %s, %s) = (%s, %s)" % (
                        zustand, DeterministischerKellerautomat.EPSILON, kellerzeichen, zustandStrich,
                        kellerzeichenStrich))
                    raise automaten.NonDeterministicKellerautomatRule(zustand, bandzeichen, kellerzeichen,
                                                                      DeterministischerKellerautomat.EPSILON)
                elif bandzeichen == DeterministischerKellerautomat.EPSILON:
                    for zeichen in self.Sigma:
                        if self.delta[zustand].has_key((zeichen, kellerzeichen)):
                            raise automaten.NonDeterministicKellerautomatRule(zustand,
                                                                              DeterministischerKellerautomat.EPSILON,
                                                                              kellerzeichen, zeichen)
        else:
            self.delta[zustand] = dict()

        if not isinstance(kellerzeichenStrich, list):
            if len(kellerzeichenStrich) == 1:
                kellerzeichenStrich = list(kellerzeichenStrich)
            else:
                kellerzeichenStrich = kellerzeichenStrich.split('+')

        self.delta[zustand][(bandzeichen, kellerzeichen)] = (zustandStrich, kellerzeichenStrich)

        self.rulesDict[
            (zustand, bandzeichen, kellerzeichen, zustandStrich, ''.join(kellerzeichenStrich))] = self.rulesCounter
        self.rulesCounter += 1

        return True

    def flushRules(self):
        """
        Ableitungsregeln loeschen
        """
        self.delta = dict()
        return len(self.delta)

    def push(self, items):
        """
        Zeichen auf den Keller schmeissen
        """
        items = list(reversed(items))
        if items != [DeterministischerKellerautomat.EPSILON]:
            # self.log.debug("Pushing: %s" % repr(items))
            self.keller += items

    def pop(self):
        """
        Oberstes Kellerzeichen lesen und loeschen
        """
        return self.keller.pop()

    def _stackEmpty(self):
        """
        Ist der Keller leer ?
        """
        return self.keller == [self.k0]

    def _bandEmpty(self):
        """
        Ist das Band leer ?
        ACHTUNG: DELIMITER auf Band wird auch als 'leer' interpretiert.
        """
        if (len(self.CHK_Word[self.CHK_Index:]) == 0) or (
                    self.CHK_Word[self.CHK_Index:] == DeterministischerKellerautomat.DELIMITER):
            return True
        return False

    def step(self, zustandStrich, kellerzeichenStrich=None):
        """
        Zustand aendern:
            * Oberstes Kellerzeichen loeschen
            * Zustand wechseln
            * Neue kellerzeichen auf den Keller schmeissen
        """
        if isinstance(zustandStrich, tuple):
            (zustandStrich, kellerzeichenStrich) = zustandStrich
        self.pop()
        self.push(kellerzeichenStrich)
        self.zustand = zustandStrich
        self.stepper()

    def __str__(self):
        s = "Deterministischer Kellerautomat '%s'" % (self.name)
        s += "\n"
        if self.beschreibung:
            s += " %s\n" % self.beschreibung
        s += " Anfangszustand                          : %s\n" % self.s0
        s += " Endliche Menge der möglichen Zustände S : %s\n" % self._fzString(self.S)
        s += " Menge der Endzustände F                 : %s\n" % self._fzString(self.F)
        s += " Endliche Menge der Eingabezeichen Σ     : %s\n" % self._fzString(self.Sigma)
        s += " Endliche Menge der Kellerzeichen k      : %s\n" % self._fzString(self.K)
        s += " Kellerstartzeichen                      : %s\n" % self.k0

        if '_getAsciiArtDeltaTable' in dir(self):
            s += self._getAsciiArtDeltaTable()

        return s

    def _ableitungToString(self):
        pfad = list()
        wordLength = len(self.CHK_Word)
        for kfgList in self.raw_ableitung[:-1]:
            pfad.append(self._getKonfiguration(kfgList[:3], wordLength))
        return " |- ".join(pfad)

    def _getKonfiguration(self, kfgList, wordLength=12):
        fmtKonfiguration = ['(%2s, ', '%' + str(wordLength) + 's, ', '%s)']
        konfiguration = ''
        kfgList[2] = ''.join(kfgList[2])
        for (f, s) in zip(fmtKonfiguration, kfgList):
            konfiguration += f % s
        return konfiguration

    def _fixWord(self, Wort):
        """
        Fuegt ggf einen Wortdelimiter hinzu
        *HEREBEDRAGONS*
        """
        if Wort[-1] != DeterministischerKellerautomat.DELIMITER:
            # self.log.warn("Adding Delimiter '%s'" % DeterministischerKellerautomat.DELIMITER)
            Wort += DeterministischerKellerautomat.DELIMITER
        return Wort

    def accepted(self, condition=None):
        """
        doctest ist etwas sinnfrei .. HEREBEDRAGONS
        >>> S2 = ['s0', 's1', 's2']
        >>> Sigma2 = ['a', 'b']
        >>> F2 = ['s2']
        >>> k0 = 'k0'
        >>> K2 = [k0, 'b']
        >>> s02 = 's0'
        >>> PDA2 = DeterministischerKellerautomat(S2, s02, F2, Sigma2, K2, k0)
        >>> PDA2.addRule('s0', 'a', 'k0', 's0', 'b+k0')
        True
        >>> PDA2.addRule('s0', 'b', 'k0', 's1', 'b+k0')
        True
        >>> PDA2.addRule('s0', 'b', 'b', 's1', 'b+b')
        True
        >>> PDA2.addRule('s0', 'a', 'b', 's0', 'b+b')
        True
        >>> PDA2.addRule('s1', 'b', 'b', 's1', 'b+b')
        True
        >>> PDA2.addRule('s1', 'EPSILON', 'b', 's2', 'b')
        True
        >>> PDA2.accept = DeterministischerKellerautomat.ACCEPT_BY_FINALSTATE
        >>> PDA2.check("abb")
        False
        >>> PDA2.accept = DeterministischerKellerautomat.ACCEPT_BY_EMPTYSTACK
        >>> PDA2.check("abb")
        False
        >>> PDA2.accept = DeterministischerKellerautomat.ACCEPT_BY_ALL
        >>> PDA2.check("abb")
        False
        """
        result = False

        if not self.accept in range(len(DeterministischerKellerautomat.ACCEPT_DESCRIPTION)):
            self.accept = 0
            self.log.error("!! self.accept not in range, fallen back to '%d' (%s)" % (
                self.accept, DeterministischerKellerautomat.ACCEPT_DESCRIPTION[self.accept]))

        if condition == None:
            condition = self.accept

        if condition == DeterministischerKellerautomat.ACCEPT_BY_FINALSTATE_AND_EMPTYSTACK:
            result = (self.zustand in self.F) and self._stackEmpty()
        elif condition == DeterministischerKellerautomat.ACCEPT_BY_FINALSTATE:
            result = (self.zustand in self.F)
        elif condition == DeterministischerKellerautomat.ACCEPT_BY_EMPTYSTACK:
            result = self._stackEmpty()
        elif condition == DeterministischerKellerautomat.ACCEPT_BY_ALL:
            result = ((self.zustand in self.F) and self._stackEmpty() and self._bandEmpty())

        self.log.debug("ACCEPTED: %s (%s)" % (result, DeterministischerKellerautomat.ACCEPT_DESCRIPTION[condition]))
        return result

    def checkVerbose(self, Wort):
        """
        Ruft die check()-Funktion mit 'Geschwaetzig'-Parameter auf.
        """
        return self.check(Wort, doItVerbose=True)

    def checkStepByStep(self, Wort, doRaise=False):
        return self.check(Wort, stepByStep=True)

    def stepper(self, immediateOutput=None):
        if immediateOutput == None:
            immediateOutput = self.stepByStepImmediateOutput

        bandWidth = 12
        wordLength = len(self.CHK_Word)
        lines = list()
        if wordLength > bandWidth:
            bandWidth = wordLength + 2

        fmt = ['%7s', '%7s', '%' + str(bandWidth) + 's', '%' + str(bandWidth) + 's', '%7s', '%s']

        # Header hinzufuegen
        if self.stepCount == 0:
            parts = list()
            desc = ['Schritt', 'GI(...)', 'Eingabeband', 'Kellerband', 'Zustand', 'Konfiguration']
            for (f, s) in zip(fmt, desc):
                parts.append(f % s)
            lines += [' | '.join(parts), "-" * 80]

        markedWord = self.CHK_Word
        if self.CHK_Index >= 0:
            newWord = ''
            i = 0
            for c in markedWord:
                if i == self.CHK_Index:
                    newWord += '[%s]' % c
                else:
                    newWord += c
                i += 1
            markedWord = newWord

        kfgList = [self.zustand, self.CHK_Word[self.CHK_Index:], list(reversed(self.keller)), self.CHK_Rule]
        # Ableitung sichern
        self._ableitungAppend(kfgList)

        konfiguration = self._getKonfiguration(kfgList, wordLength)

        msg = list()
        msg.append(self.stepCount)
        msg.append((self.CHK_Rule >= 0 and self.CHK_Rule or ' '))
        msg.append(markedWord)
        msg.append(''.join(reversed(self.keller)))
        msg.append(self.zustand)
        msg.append(konfiguration)

        parts = list()
        for (f, s) in zip(fmt, msg):
            parts.append(f % s)

        lines.append(' | '.join(parts))
        self.stepCount += 1

        self.stepByStepOutput += lines
        if immediateOutput:
            print "\n".join(lines)

    def checkWordsX(self, words, silence=False):
        resultset = list()
        words = self._toList(words)
        for word in words:
            result = 'OUCH'
            successful = False
            try:
                self.check(word, True)
                result = 'Akzeptiert.'
                successful = True
            except automaten.NotInSigmaException, e:
                result = "'%s' ist nicht im Alphabet." % e.value
            except automaten.NoSuchStateException, e:
                result = "Zustand '%s' ist nicht in Sigma." % e.value
            except automaten.NoAcceptingStateException, e:
                result = "Kein finaler Zustand erreicht."
            except automaten.NoRuleForStateException, e:
                result = "Kein finaler Zustand erreicht (Keine Regel definiert für '%s')." % e.value
            except Exception, e:
                result = str(e)
                self.log.error(e)
            resultset.append((word, successful, result, self.raw_ableitung))
            if not silence:
                self.log.info(
                    "%-20s [%s] %-5s : %s" % (self.name, (successful and "SUCCESS" or "FAILURE"), word, result))
                self.log.debug(self._ableitungsPfad__str__())
        return resultset

    def check(self, Wort, doRaise=False, doItVerbose=False, stepByStep=False):
        """
        >>> S = ['s0', 's1', 's2', 's3']
        >>> Sigma = ['a', 'b']
        >>> F = ['s0', 's3']
        >>> k0 = 'k0'
        >>> K = [k0, 'a']
        >>> s0 = 's0'
        >>> PDA = DeterministischerKellerautomat(S, s0, F, Sigma, K, k0)
        >>> PDA.addRule('s0', 'a', 'k0', 's1', 'a+k0')
        True
        >>> PDA.addRule('s1', 'a', 'a', 's1', 'a+a')
        True
        >>> PDA.addRule('s1', 'b', 'a', 's2', 'EPSILON')
        True
        >>> PDA.addRule('s2', 'b', 'a', 's2', 'EPSILON')
        True
        >>> PDA.addRule('s2', 'EPSILON', 'k0', 's3', 'k0')
        True
        >>> PDA.check("aaabbb")
        True
        >>> PDA.check("aaabb", True)
        Traceback (most recent call last):
        ...
        NoKellerautomatRule: Keine Ueberfuehrungsregel (s2, #, a)
        >>> PDA.check("a")
        False
        >>> PDA.check("aaaaaab")
        False
        >>> PDA.checkVerbose("aaabbb")
        True
        >>> PDA.accept = DeterministischerKellerautomat.ACCEPT_BY_EMPTYSTACK
        >>> PDA.checkVerbose("aaabbb")
        True
        >>> PDA.accept = DeterministischerKellerautomat.ACCEPT_BY_FINALSTATE
        >>> PDA.checkVerbose("aaabbb")
        True
        """
        self.reset()
        accepted = False
        Wort = self._fixWord(Wort)

        # ein paar Meta-Variablen
        self.CHK_Word = Wort
        self.CHK_Rule = -1
        self.CHK_Index = 0

        # "Step" Meta-Werte
        self.stepCount = 0
        self.stepByStepOutput = list()
        self.stepByStepImmediateOutput = False

        self.stepper()

        n = len(Wort)
        i = 0

        while i <= n:
            (zustandStrich, kellerzeichenStrich) = (None, None)
            bandzeichen = Wort[i]

            self.log.debug("--- Step # %2d ---" % (self.stepCount))
            self.log.debug("%s%s%s" % (Wort[:i], Wort[i], Wort[i + 1:]))
            self.log.debug("%s%s" % (" " * i, '^'))

            # Index erhoehen
            self.CHK_Index = i + 1

            # Oberstes Kellerzeichen lesen (ohne pop())
            kellerzeichen = self.keller[-1]

            # 			if self.validDelta(self.zustand, DeterministischerKellerautomat.EPSILON, kellerzeichen):
            # 				# Ueberfuehrung ohne Zeichen (siehe Barth, Kap. 5.2., Seite 58)
            # 				bandzeichen = DeterministischerKellerautomat.EPSILON
            # 				self.log.debug("== Ueberfuehrung OHNE Zeichen (mit '%s') ==" % bandzeichen)
            if self.validDelta(self.zustand, bandzeichen, kellerzeichen):
                self.log.debug("== Ueberfuehrung MIT Zeichen  ==")
                i += 1
            elif self.validDelta(self.zustand, DeterministischerKellerautomat.EPSILON, kellerzeichen):
                # Ueberfuehrung ohne Zeichen (siehe Barth, Kap. 5.2., Seite 58)
                bandzeichen = DeterministischerKellerautomat.EPSILON
                self.log.debug("== Ueberfuehrung OHNE Zeichen (mit '%s') ==" % bandzeichen)
            else:
                self.log.debug("== Ueberfuehrung nicht mehr definiert  ==")
                if doRaise and (bandzeichen != DeterministischerKellerautomat.DELIMITER):
                    self.log.debug(
                        "Das Bandzeichen ist '%s'. (Wir werfen jetzt eine NoKellerautomatRule-Exception ..)" % bandzeichen)
                    raise automaten.NoKellerautomatRule(self.zustand, bandzeichen, kellerzeichen)
                else:
                    self.log.debug(
                        "Das Bandzeichen ist DELIMITER '%s'. (Wortende erreicht)" % DeterministischerKellerautomat.DELIMITER)
                self.log.debug("")
                break

            (zustandStrich, kellerzeichenStrich) = self._delta(self.zustand, bandzeichen, kellerzeichen)
            self.step((zustandStrich, kellerzeichenStrich))
            self.log.debug("")

        if Wort[i] != DeterministischerKellerautomat.DELIMITER:
            self.log.error(
                "[%s] Wortende von '%s' nicht erreicht. (i=%d/%d), Wort[i]='%s'" % (self.name, Wort, i, n, Wort[i]))
            if doRaise:
                raise automaten.EndOfWordKellerautomatException(i, Wort)
        else:
            if self.accepted():
                accepted = True
            elif doRaise:
                raise automaten.NoAcceptingStateException(self.zustand, self.F)

        # Print Step By Step Table
        if stepByStep and (self.stepByStepImmediateOutput == False):
            print "\n".join(self.stepByStepOutput)

        if doItVerbose:
            self.log.info("%-10s: %-105s => %sKZEPTIERT." % (
                ("'%s'" % Wort), self._ableitungToString(), (accepted and 'A' or 'NICHT A')))
        else:
            self.log.info("Wort '%s' : %skzeptiert. (%s)" % (
                Wort[:-1], (accepted and "A" or "Nicht a"),
                DeterministischerKellerautomat.ACCEPT_DESCRIPTION[self.accept]))
        self.log.debug(self._ableitungToString())

        return accepted

    def validDelta(self, zustand, zeichen, kellerzeichen):
        if self.delta.has_key(zustand):
            return self.delta[zustand].has_key((zeichen, kellerzeichen))
        return False

    def _delta(self, Zustand, Zeichen, Kellerzeichen):
        """
        Ueberfuehrungsfunktion
        """
        logmessage = "(%s, %s, %s) = " % (Zustand, Zeichen, Kellerzeichen)

        if self.validDelta(Zustand, Zeichen, Kellerzeichen):
            (zustandStrich, kellerzeichenStrich) = self.delta[Zustand][(Zeichen, Kellerzeichen)]
            logmessage += "(%s, %s)" % (zustandStrich, ''.join(kellerzeichenStrich))
            # Regel-Nummer herausfinden:
            rNum = self.rulesDict[(Zustand, Zeichen, Kellerzeichen, zustandStrich, ''.join(kellerzeichenStrich))]
            self.CHK_Rule = rNum
            logmessage = '#%-2d %s' % (rNum, logmessage)
            self.log.debug(logmessage)
            return self.delta[Zustand][(Zeichen, Kellerzeichen)]
        else:
            logmessage += "(?!, ?!)"

        self.log.debug(logmessage)
        raise automaten.NoRuleForStateException(Zustand, explanation='hat keine definierten Regeln fuer (%s, %s)' % (
            Zeichen, Kellerzeichen))

    def verifyByRegExp(self, testWords=None, regexp=None):
        raise NotImplementedError("Verify By Regular Expression: not applicable.")


if __name__ == '__main__':
    test()
