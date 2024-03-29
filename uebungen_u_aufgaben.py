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
from optparse import OptionParser
import re

from automaten import *
from automatenausgabe import *
from automatenleser import *

DEFAULT_PREFIX_LIST = ['Script', 'Uebungsblatt1', 'Uebungsblatt2', 'Uebungsblatt3', 'Uebungsblatt4', 'Uebungsblatt10']


def int2bin(value, fill=0):
    result = list()
    while value:
        result.append(str(value & 1))
        value >>= 1
    result.reverse()
    return ''.join(result).zfill(fill)


def testWorte(Sigma, length=3):
    worte = list(Sigma)
    SigmaTmp = Sigma
    # [a + b for a in eins for b in eins]
    for i in xrange(length):
        SigmaTmp = [a + b for b in Sigma for a in SigmaTmp]
        # print SigmaTmp
        worte += SigmaTmp
    return worte


def RegularExpressionTestWorte(worte, regexp):
    if not regexp.startswith("^"):
        regexp = '^' + regexp
    if not regexp.endswith("$"):
        regexp += '$'
    pattern = re.compile(regexp)

    verifyWords = dict()
    for wort in worte:
        res = pattern.match(wort)
        verifyWords[wort] = pattern.match(wort) and True or False
    return verifyWords


# Einige von mehreren Automaten genutzte Testwort-Mengen
U1A2_Testworte = testWorte(['a', 'b'])
testZahlen1 = '0 1 2 +99 -99 9- a - +- -+ -+99 0019292'


def Script_Beispiel_1_1():
    S = 'aus an'
    s0 = 'aus'
    F = 'an'
    Sigma = '0 1'
    delta = {
        'aus': {
            "0": 'aus',
            "1": 'an',
        },
        'an': {
            '0': 'aus',
            '1': 'an',
        },
    }
    verifyWords = {'1': True, '0': False, '00': False}
    return Automat(S, s0, F, Sigma, delta,
                   name="Beispiel1.1",
                   beschreibung="Ein Schalter",
                   testWords=testWorte(['0', '1']),
                   verifyWords=verifyWords)


def Script_Beispiel_1_2():
    S = 's0 s1 s2 s3'
    s0 = 's0'
    F = 's3'
    Sigma = '0 1'
    delta = {
        's0': {
            "0": 's1',
            "1": 's0',
        },
        's1': {
            '0': 's2',
            '1': 's0',
        },
        's2': {
            '0': 's2',
            '1': 's3',
        },
        's3': {
            '0': 's3',
            '1': 's3',
        },
    }
    verifyWords = {'001': True, '010': False, '0001': True, '1001': True}
    return Automat(S, s0, F, Sigma, delta,
                   name="Beispiel1.2",
                   beschreibung="Ein endlicher deterministischer Automat für die Sprache L, die alle Wörter mit Teilwort 001 enthält",
                   testWords=testWorte(['0', '1']),
                   verifyWords=verifyWords
                   )


def Script_Beispiel_1_3():
    cS = 's0 s1 s2 s3 s4 s5 s6 s7'
    cs0 = 's0'
    cF = 's2 s4 s7'
    cSigma = '0 1 2 3 4 5 6 7 8 9 + - . e'
    cdelta = {
        's0': {
            ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'): 's2',
            ("+", '-'): 's1',
        },
        's1': {
            ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'): 's2',
        },
        's2': {
            ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'): 's2',
            ".": "s3",
            "e": "s5"
        },
        's3': {
            ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'): 's4',
        },
        's4': {
            ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'): 's4',
            "e": 's5',
        },
        's5': {
            ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'): 's7',
            ("+", '-'): "s6",
        },
        's6': {
            ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'): 's7',
        },
        's7': {
            ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'): 's7',
        },
    }
    verifyWords = {'1': True, '-': False, '0.1': True}
    return Automat(cS, cs0, cF, cSigma, cdelta,
                   name="Beispiel1.3",
                   beschreibung="Endlicher deterministischer Automat für die normierte Darstellung reeller Zahlen",
                   testWords='0 1 2 00.1 0.1 0.101. . 101 001 1.001.02',
                   verifyWords=verifyWords
                   )


def Script_Beispiel_1_4():
    S = 's0 s1 s2 s3'
    s0 = 's0'
    F = 's3'
    Sigma = '0 1'
    delta = {
        's0': {
            '0': 's0 s1',
            '1': 's0',
        },
        's1': {
            '0 1': 's2',
        },
        's2': {
            '0 1': 's3',
        },
        's3': {},
    }
    verifyWords = {'111': False, '000': True, '011': True, '0': False}
    A = NichtDeterministischerAutomat(S, s0, F, Sigma, delta,
                                      name="Beispiel1.4",
                                      beschreibung="Ein endlicher nichtdeterministischer Automat für die Menge aller Bitfolgen, deren drittletzte Ziffer eine 0 ist",
                                      testWords=testWorte(['0', '1']),
                                      verifyWords=verifyWords
                                      )
    return A


def Script_Beispiel_1_4intuitiv():
    S = '111 110 100 101 010 011 001 000'
    s0 = '111'
    F = '011 001 010 000'
    Sigma = '0 1'
    delta = {
        '111': {
            "0": '110',
            "1": '111',
        },
        '110': {
            "0": '100',
            "1": '101',
        },
        '100': {
            "0": '000',
            "1": '001',
        },
        '101': {
            "0": '010',
            "1": '011',
        },
        '010': {
            "0": '100',
            "1": '101',
        },
        '011': {
            "0": '110',
            "1": '111',
        },
        '001': {
            "0": '010',
            "1": '011',
        },
        '000': {
            "0": '000',
            "1": '001',
        },
    }
    verifyWords = {'111': False, '000': True, '011': True, '0': False}
    return Automat(S, s0, F, Sigma, delta,
                   name="Beispiel1.4 (intuitiv)",
                   beschreibung="Ein endlicher deterministischer Automat für die Menge aller Bitfolgen, deren drittletzte Ziffer eine 0 ist",
                   testWords=testWorte(['0', '1']),
                   verifyWords=verifyWords
                   )


def Script_Beispiel_1_5_DEA():
    S = '0 A B C D E F G'
    s0 = '0'
    F = 'D E F G'
    Sigma = '0 1'
    delta = {
        '0': {
            "0": 'A',
            "1": '0',
        },
        'A': {
            "0": 'C',
            "1": 'B',
        },
        'B': {
            "0": 'F',
            "1": 'G',
        },
        'C': {
            "0": 'D',
            "1": 'E',
        },
        'D': {
            "0": 'D',
            "1": 'E',
        },
        'E': {
            "0": 'F',
            "1": 'G',
        },
        'F': {
            "0": 'C',
            "1": 'B',
        },
        'G': {
            "0": 'A',
            "1": '0',
        },
    }
    verifyWords = {'111': False, '000': True, '011': True, '0': False}
    return Automat(S, s0, F, Sigma, delta,
                   name="Beispiel1.5 (DEA)",
                   beschreibung="Ein endlicher deterministischer Automat für die Menge aller Bitfolgen, deren drittletzte Ziffer eine 0 ist",
                   testWords=testWorte(['0', '1']),
                   verifyWords=verifyWords
                   )


def Script_Beispiel_1_6_NDA():
    S = 's0 s1 s2'
    s0 = 's0'
    F = 's2'
    Sigma = '0 1 2 3 4 5 6 7 8 9 + -'
    delta = {
        's0': {
            ('+', '-', EpsilonAutomat.EPSILON): 's1',
        },
        's1': {
            '0 1 2 3 4 5 6 7 8 9': 's2',
        },
        's2': {
            '0 1 2 3 4 5 6 7 8 9': 's2',
        },
    }
    verifyWords = {'a': False, '000': True, '011': True, '+0': True}
    return EpsilonAutomat(S, s0, F, Sigma, delta,
                          name="Beispiel 1.6.",
                          beschreibung="NEA, der Dezimalzahlen akzeptiert",
                          testWords=testZahlen1,
                          verifyWords=verifyWords
                          )


def Script_Beispiel_1_6_DEA():
    S = 's0 s1 s2'
    s0 = 's0'
    F = 's2'
    Sigma = '0 1 2 3 4 5 6 7 8 9 + -'
    delta = {
        's0': {
            '+ -': 's1',
            ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'): 's2',
        },
        's1': {
            ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'): 's2',
        },
        's2': {
            ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'): 's2',
        },
    }
    verifyWords = {'a': False, '000': True, '011': True, '+0': True}
    return Automat(S, s0, F, Sigma, delta,
                   name="Beispiel 1.6. (DEA)",
                   beschreibung="DEA, der Dezimalzahlen akzeptiert",
                   testWords=testZahlen1,
                   verifyWords=verifyWords
                   )


def Script_Beispiel_1_7():
    S = 's1 s2 s3 s4 s5 s6'
    s0 = 's1'
    F = 's3 s4 s5 s6'
    Sigma = '0 1'
    delta = {
        's1': {
            '0': 's2',
            '1': 's3',
        },
        's2': {
            '0': 's2',
            '1': 's4',
        },
        's3': {
            '0': 's1',
            '1': 's5',
        },
        's4': {
            '0': 's2',
            '1': 's5',
        },
        's5': {
            '0': 's2',
            '1': 's6',
        },
        's6': {
            '0': 's2',
            '1': 's1',
        },
    }
    verifyWords = {'0': False, '1': True}
    A = Automat(S, s0, F, Sigma, delta, name="Beispiel 1.7.",
                verifyWords=verifyWords)
    A.testWords = A.testWorteGenerator()
    return A


def Script_Beispiel_1_7reduziert():
    S = 's12 s34 s5 s6'
    s0 = 's12'
    F = 's34 s5 s6'
    Sigma = '0 1'
    delta = {
        's12': {
            '0': 's12',
            '1': 's34',
        },
        's34': {
            '0': 's12',
            '1': 's5',
        },
        's5': {
            '0': 's12',
            '1': 's6',
        },
        's6': {
            '0 1': 's12',
        },
    }
    verifyWords = {'0': False, '1': True}
    A = Automat(S, s0, F, Sigma, delta, name="Beispiel 1.7. reduziert",
                verifyWords=verifyWords)
    A.testWords = A.testWorteGenerator()
    return A


def Uebungsblatt1_Aufgabe_1b():
    S = 'z0 z1 z2 z3 z4'.split()
    s0 = 'z0'
    F = 'z2 z4'.split()
    Sigma = '0 1 + - .'.split()
    delta = {
        'z0': {
            ('0', '1'): 'z2',
            ('+', '-'): 'z1',
        },
        'z1': {
            ('0', '1'): 'z2',
        },
        'z2': {
            ('0', '1'): 'z2',
            '.': 'z3',
        },
        'z3': {
            ('0', '1'): 'z4',
        },
        'z4': {
            ('0', '1'): 'z4',
        },
    }
    A = Automat(S, s0, F, Sigma, delta,
                name="U1A1b",
                beschreibung="DEA, der Dezimalzahlen akzeptiert",
                testWords='0 1 -1 +1 2 -0 00.1 101 111 000 010 0.11.')
    return A


def Uebungsblatt1_Aufgabe_1c():
    S = 'z0 z1 z2 z3 z4 z5'.split()
    s0 = 'z0'
    F = 'z2 z4 z5'.split()
    Sigma = '0 1 + - .'.split()
    delta = {
        'z0': {
            '1': 'z2',
            '0': 'z5',
            ('+', '-'): 'z1',
        },
        'z1': {
            '1': 'z2',
            '0': 'z5',
        },
        'z2': {
            '1': 'z2',
            '0': 'z1',
            '.': 'z3',
        },
        'z3': {
            ('0', '1'): 'z4',
        },
        'z4': {
            ('0', '1'): 'z4',
        },
        'z5': {
            '1': 'z2',
            '.': 'z3',
        }
    }
    A = Automat(S, s0, F, Sigma, delta,
                name="U1A1c",
                beschreibung="Veränderter Automat U1A1, der keine führenden Nullen mehr akzeptiert",
                testWords='0 1 -1 +1 0.1 00.01 0000 101 +1.010 001')
    return A


def Uebungsblatt1_Aufgabe_2a():
    delta = {
        'z0': {
            ('a', 'b'): 'z1',
        },
        'z1': {
            'b': 'z2',
        },
        'z2': {
            ('a', 'b'): 'z2',
        },
    }
    A = Automat('z0 z1 z2', 'z0', 'z2', 'a b', delta,
                name="U1A2a",
                beschreibung="Akzeptiert alle Worte, die als zweites Zeichen ein b besitzen",
                testWords=U1A2_Testworte)
    return A


def Uebungsblatt1_Aufgabe_2b():
    delta = {
        'z0': {
            'a': 'z1',
            'b': 'z4'
        },
        'z1': {
            'b': 'z2',
        },
        'z2': {
            'b': 'z3',
        },
        'z3': {},
        'z4': {
            'a': 'z5',
        },
        'z5': {
            'a': 'z6',
        },
        'z6': {},
    }
    verifyWords = {'baa': True, 'ab': True, 'abb': True, 'a': False, 'ba': False}
    A = Automat('z0 z1 z2 z3 z4 z5 z6', 'z0', 'z2 z3 z6', 'a b', delta,
                name="U1A2b",
                beschreibung="Akzeptiert die drei Worte baa ab abb",
                testWords=U1A2_Testworte,
                verifyWords=verifyWords
                )
    return A


def Uebungsblatt1_Aufgabe_2c():
    delta = {
        'z0': {
            'a': 'z0',
            'b': 'z1'
        },
        'z1': {
            'a': 'z2',
            'b': 'z1',
        },
        'z2': {
            'a': 'z0',
            'b': 'z1',
        },
    }
    verifyWords = {'baa': True, 'ab': True, 'aba': False, 'a': True, 'ba': False}
    A = Automat('z0 z1 z2', 'z0', 'z0 z1', 'a b', delta,
                name="U1A2c",
                beschreibung="Akzeptiert alle Worte, die nicht mit ba enden",
                testWords=U1A2_Testworte,
                verifyWords=verifyWords
                )
    return A


def Uebungsblatt1_Aufgabe_2d():
    delta = {
        'z0': {
            'a': 'z1',
            'b': 'z4'
        },
        'z1': {
            'a': 'z6',
            'b': 'z2',
        },
        'z2': {
            'a': 'z5',
            'b': 'z3',
        },
        'z3': {
            'a': 'z5',
            'b': 'z3',
        },
        'z4': {
            'a': 'z5',
            'b': 'z6',
        },
        'z5': {
            'a': 'z7',
            'b': 'z2',
        },
        'z6': {
            ('a', 'b'): 'z6',
        },
        'z7': {
            'a': 'z7',
            'b': 'z2',
        },
    }
    verifyWords = {'a': False, 'aa': True, 'abb': True, 'aba': False, 'aabb': True}
    A = Automat('z0 z1 z2 z3 z4 z5 z6 z7', 'z0', 'z3 z6 z7', 'a b', delta,
                name="U1A2d",
                beschreibung="Akzeptiert alle Worte, die mit zwei gleichen Zeichen enden oder beginnen",
                testWords=U1A2_Testworte,
                verifyWords=verifyWords
                )
    return A


def Uebungsblatt1_Aufgabe_2d1():
    delta = {
        'z1': {
            'a': 'z2',
            'b': 'z4',
        },
        'z2': {
            'a': 'z3',
            'b': 'z9',
        },
        'z3': {
            ('a', 'b'): 'z3',
        },
        'z4': {
            'a': 'z7',
            'b': 'z5',
        },
        'z5': {
            ('a', 'b'): 'z5',
        },
        'z7': {
            'a': 'z8',
            'b': 'z9',
        },
        'z8': {
            'a': 'z8',
            'b': 'z9',
        },
        'z9': {
            'a': 'z7',
            'b': 'z10',
        },
        'z10': {
            'a': 'z7',
            'b': 'z10',
        },
    }
    verifyWords = {'a': False, 'aa': True, 'abb': True, 'aba': False, 'aabb': True}
    A = Automat('z1 z2 z3 z4 z5 z7 z8 z9 z10', 'z1', 'z3 z5 z8 z10', 'a b', delta,
                name="U1A2d (alternativ)",
                beschreibung="Akzeptiert alle Worte, die mit zwei gleichen Zeichen enden oder beginnen",
                testWords=U1A2_Testworte,
                verifyWords=verifyWords)
    return A


def Uebungsblatt1_Aufgabe_2e():
    delta = {
        'z0': {
            'a': 'z1',
            'b': 'z0'
        },
        'z1': {
            'a': 'z0',
            'b': 'z1',
        },
    }
    verifyWords = {'a': True, 'aa': False, 'abb': True, 'aba': False, 'aabb': False}
    A = Automat('z0 z1', 'z0', 'z1', 'a b', delta,
                name="U1A2e",
                beschreibung="Akzeptiert alle Worte, die eine ungerade Anzahl von a's enthalten",
                testWords=U1A2_Testworte,
                verifyWords=verifyWords
                )
    return A


def Uebungsblatt1_Aufgabe_3a():
    delta = {
        'z0': {
            '0': 'z0',
            '1': 'z1'
        },
        'z1': {
            '0': 'z0',
            '1': 'z1',
        },
    }
    tw = list()
    verifyWords = dict()
    for i in xrange(10):
        add = int2bin(i)
        tw.append(add)
        if i % 2 == 0:
            verifyWords[add] = True
        else:
            verifyWords[add] = False

    A = Automat('z0 z1', 'z0', 'z0', '0 1', delta,
                name="U1A3a",
                beschreibung="DEA, der für eine ganze Zahl in Binärdarstellung entscheidet, ob die Zahl durch 2 ohne Rest teilbar ist",
                testWords=tw,
                verifyWords=verifyWords
                )
    return A


def Uebungsblatt1_Aufgabe_3b():
    delta = {
        'z0': {
            '0': 'z1',
            '1': 'z2',
        },
        'z1': {
            '0': 'z1',
            '1': 'z2',
        },
        'z2': {
            '0': 'z3',
            '1': 'z1',
        },
        'z3': {
            '0': 'z2',
            '1': 'z3',
        },
    }
    tw = list()
    verifyWords = dict()
    for i in xrange(20):
        add = int2bin(i)
        tw.append(add)
        if i % 3 == 0:
            verifyWords[add] = True
        else:
            verifyWords[add] = False

    A = Automat('z0 z1 z2 z3', 'z0', 'z1', '0 1', delta,
                name="U1A3b",
                beschreibung="DEA, der für eine ganze Zahl in Binärdarstellung entscheidet, ob die Zahl durch 3 ohne Rest teilbar ist",
                testWords=tw,
                verifyWords=verifyWords
                )
    return A


def Sonstige_Aufgabe_3x1():
    delta = {
        'z0': {
            '0': 'z1',
            '1': 'z0'
        },
        'z1': {
            '0': 'z2',
            '1': 'z0',
        },
        'z2': {
            '0': 'z2',
            '1': 'z0',
        },
    }
    tw = list()
    for i in xrange(20):
        tw.append(int2bin(i))

    A = Automat('z0 z1 z2', 'z0', 'z2', '0 1', delta,
                name="U1A3x1",
                beschreibung="DEA, der für eine ganze Zahl in Binärdarstellung entscheidet, ob die Zahl durch 4 ohne Rest teilbar ist",
                testWords=tw)
    return A


def Sonstige_Aufgabe_3x2():
    delta = {
        'z0': {
            '0': 'z1',
            '1': 'z0'
        },
        'z1': {
            '0': 'z2',
            '1': 'z0',
        },
        'z2': {
            '0': 'z3',
            '1': 'z0',
        },
        'z3': {
            '1': 'z0',
            '0': 'z3'
        },
    }
    tw = list()
    for i in xrange(100):
        tw.append(int2bin(i))

    A = Automat('z0 z1 z2 z3', 'z0', 'z3', '0 1', delta,
                name="U1A3x2",
                beschreibung="DEA, der für eine ganze Zahl in Binärdarstellung entscheidet, ob die Zahl durch 8 ohne Rest teilbar ist",
                testWords=tw)
    return A


def Sonstige_Aufgabe_3x3():
    delta = {
        'z0': {
            '0': 'z1',
            '1': 'z2',
        },
        'z1': {
            '0': 'z4',
            '1': 'z2',
        },
        'z2': {
            '0': 'z3',
            '1': 'z1',
        },
        'z3': {
            '0': 'z2',
            '1': 'z3',
        },
        'z4': {
            '0': 'z4',
            '1': 'z2',
        },
    }
    tw = list()
    for i in xrange(20):
        tw.append(int2bin(i, 8))
    for i in xrange(20, 200):
        if i % 6 == 0:
            tw.append(int2bin(i, 8))

    A = Automat('z0 z1 z2 z3 z4', 'z0', 'z4', '0 1', delta,
                name="U1A3x2",
                beschreibung="DEA, der für eine ganze Zahl in Binärdarstellung entscheidet, ob die Zahl durch 6 ohne Rest teilbar ist",
                testWords=tw)
    return A


def Uebungsblatt1_Aufgabe_5b():
    delta = {
        '1': {
            'a': '2',
        },
        '2': {
            'a': '2',
            'b': 'A',
        },
        'A': {
            'a': 'B',
            'b': 'C',
        },
        'B': {
            'a': '2',
            'b': 'A',
        },
        'C': {
            'a': 'B',
            'b': 'C',
        },
    }
    A = Automat('1 2 A B C', '1', 'B C', 'a b', delta,
                name="U1A5b",
                beschreibung="Akzeptiert alle Worte, die mit a beginnen und als zweitletztes Zeichen ein b besitzen",
                testWords=U1A2_Testworte)
    return A


U2A1testWords = "0 1 +0 -0.001 0.1 0.1e-1 1.00e1 -0.0e0 - . ++ 0- 00. 001.0ee"


def Uebungsblatt2_Aufgabe_1():
    delta = {
        'z0': {
            ('+', '-', EpsilonAutomat.EPSILON): 'z1',
        },
        'z1': {
            '0 1': 'z2'
        },
        'z2': {
            '.': 'z3',
            EpsilonAutomat.EPSILON: 'z1 z4',
        },
        'z3': {
            '0 1': 'z4',
        },
        'z4': {
            'e': 'z5',
            EpsilonAutomat.EPSILON: 'z3 z7',
        },
        'z5': {
            ('+', '-', EpsilonAutomat.EPSILON): 'z6',
        },
        'z6': {
            '0 1': 'z7',
        },
        'z7': {
            EpsilonAutomat.EPSILON: 'z6',
        },
    }

    return EpsilonAutomat('z0 z1 z2 z3 z4 z5 z6 z7', 'z0', 'z7', '0 1 + - . e', delta,
                          name="U2A1",
                          beschreibung="NEA bei dem die epsilon-Übergänge zu eliminieren sind",
                          testWords=U2A1testWords)


def Uebungsblatt2_Aufgabe_1_eliminiert():
    delta = {
        'z0': {
            '+ -': 'z1',
            '0 1': 'z2',
        },
        'z1': {
            '0 1': 'z2',
        },
        'z2': {
            '.': 'z3',
            '0 1': 'z4',
        },
        'z3': {
            '0 1': 'z4',
        },
        'z4': {
            '0 1': 'z4 z7',
            'e': 'z5',
        },
        'z5': {
            '0 1': 'z7',
            '+ -': 'z6',
        },
        'z6': {
            '0 1': 'z7',
        },
        'z7': {
            '0 1': 'z7'
        },
    }

    return NichtDeterministischerAutomat('z0 z1 z2 z3 z4 z5 z6 z7', 'z0', 'z2 z4 z7', '0 1 + - . e', delta,
                                         name="U2A1eliminiert",
                                         beschreibung="NEA Aufgabe 1 mit eliminierten epsilon-Übergänge",
                                         testWords=U2A1testWords)


def Uebungsblatt2_Aufgabe_2a():
    S = '1 2 3'
    s0 = '1'
    F = S
    Sigma = 'a b c'
    delta = {
        '1': {
            'a': '1',
            EpsilonAutomat.EPSILON: '2',
        },
        '2': {
            'b': '2',
            EpsilonAutomat.EPSILON: '3',
        },
        '3': {
            'c': '3',
        },
    }

    e = EpsilonAutomat(S, s0, F, Sigma, delta,
                       name="U2A2a",
                       beschreibung="eNEA zur Erkennung aller Zeichenketten, die aus beliebig vielen as, gefolgt von beliebig vielen bs, gefolgt von beliebig vielen cs bestehen")
    e.testWords = e.testWorteGenerator(Sigma=['a', 'b', 'c'])
    return e


def Uebungsblatt2_Aufgabe_2b():
    return AutomatenLeser('data/u2a2b').automat()


def Uebungsblatt2_Aufgabe_2c():
    S = '0 1 2 3 4 5 6 7 8 9 10'
    s0 = '0'
    F = '10'
    Sigma = '0 1'
    delta = {
        '0': {
            '0': '6',
            '1': '1',
            EpsilonAutomat.EPSILON: '10',
        },
        '1': {
            '0': '6',
            '1': '2',
        },
        '2': {
            EpsilonAutomat.EPSILON: '7',
            '1': '3',
        },
        '3': {
            EpsilonAutomat.EPSILON: '8',
            '1': '4',
        },
        '4': {
            '0': '10',
            '1': '5',
        },
        '5': {
            '0': '6',
            '1': '1',
        },
        '6': {
            '0': '7',
            EpsilonAutomat.EPSILON: '10',
        },
        '7': {
            '0': '8',
            EpsilonAutomat.EPSILON: '10',
        },
        '8': {
            EpsilonAutomat.EPSILON: '10',
        },
        '9': {
            '0': '10',
        },
        '10': {
            '0': '10',
            '1': '6',
            EpsilonAutomat.EPSILON: '6',
        }
    }
    e = EpsilonAutomat(S, s0, F, Sigma, delta,
                       beschreibung="eNEA zur Erkennung aller Zeichenketten, bei denen mindestns eines der letzten fünf Zeichen eine 0 ist")
    e.testWords = e.testWorteGenerator(5, Sigma=['0', '1'])
    return e


def Uebungsblatt2_Aufgabe_4():
    S = 'z0 z1 z2 z3 z4 zF'
    s0 = 'z0'
    F = 'z3 z4'
    Sigma = '0 1'
    delta = {
        'z0': {
            '0': 'z1',
            '1': 'z2',
        },
        'z1': {
            '0': 'z1',
            '1': 'z3',
        },
        'z2': {
            '0': 'z2',
            '1': 'z4',
        },
        'z3': {
            '0': 'z2',
            '1': 'zF',
        },
        'z4': {
            '0': 'z1',
            '1': 'zF',
        },
        'zF': {
            '0': 'zF',
            '1': 'zF',
        },
    }
    A = Automat(S, s0, F, Sigma, delta,
                name="U2A4",
                beschreibung="DEA x")
    A.testWords = A.testWorteGenerator(5, Sigma=['0', '1'])
    return A


def Uebungsblatt2_Aufgabe5a():
    S = 'a1 a2'
    s0 = 'a1'
    F = 'a1'
    Sigma = 'a b'
    delta = {
        'a1': {
            'a': 'a2',
            'b': 'a1',
        },
        'a2': {
            'a': 'a1',
            'b': 'a2',
        }
    }
    verifyWords = {'': True, 'a': False, 'aa': True, 'ab': False, 'aab': True}
    A = Automat(S, s0, F, Sigma, delta,
                name="U2A5a",
                beschreibung="DEA, der alle Worte über a,b akzeptiert, die eine gerade Anzahl von a's (inklusive leeres Wort) haben",
                verifyWords=verifyWords
                )
    A.testWords = A.testWorteGenerator(3)
    return A


def Uebungsblatt2_Aufgabe5b():
    S = 'b1 b2'
    s0 = 'b1'
    F = 'b2'
    Sigma = 'a b'
    delta = {
        'b1': {
            'a': 'b1',
            'b': 'b2',
        },
        'b2': {
            'a': 'b2',
            'b': 'b1',
        }
    }
    verifyWords = {'': False, 'b': True, 'bb': False, 'ab': True, 'aab': True}
    A = Automat(S, s0, F, Sigma, delta,
                name="U2A5b",
                beschreibung="DEA, der alle Worte über a,b akzeptiert, die eine ungerade Anzahl von b's haben",
                verifyWords=verifyWords
                )
    A.testWords = A.testWorteGenerator(3)
    return A


def Uebungsblatt2_Aufgabe5():
    S = 'a1b1 a2b1 a1b2 a2b2'
    s0 = 'a1b1'
    F = 'a1b1 a1b2 a2b2'
    Sigma = 'a b'
    delta = {
        'a1b1': {
            'a': 'a2b1',
            'b': 'a1b2',
        },
        'a2b1': {
            'a': 'a1b1',
            'b': 'a2b2',
        },
        'a1b2': {
            'a': 'a2b2',
            'b': 'a1b1',
        },
        'a2b2': {
            'a': 'a1b2',
            'b': 'a2b1',
        },
    }
    verifyWords = dict()
    aA = Uebungsblatt2_Aufgabe5a()
    for item in aA.verifyWords:
        if aA.verifyWords[item] == True:
            verifyWords[item] = True

    bA = Uebungsblatt2_Aufgabe5b()
    for item in bA.verifyWords:
        if bA.verifyWords[item] == True:
            verifyWords[item] = True

    A = Automat(S, s0, F, Sigma, delta,
                name="U2A5 (verbunden)",
                beschreibung="DEA, der alle Worte über a,b akzeptiert, die eine ungerade Anzahl von b's oder eine gerade Anzahl von a's (inkl. leeres Wort) haben",
                verifyWords=verifyWords
                )
    A.testWords = A.testWorteGenerator(3)
    return A


def Uebungsblatt2_Aufgabe5minimiert1():
    S = '12 34'
    s0 = '12'
    F = S
    Sigma = 'a b'
    delta = {
        '12': {
            'a': '12',
            'b': '34',
        },
        '34': {
            'a': '34',
            'b': '12',
        }
    }
    vA = Uebungsblatt2_Aufgabe5()
    verifyWords = vA.verifyWords
    A = Automat(S, s0, F, Sigma, delta,
                name="U2A5b (minimiert 1)",
                beschreibung="DEA, der alle Worte über a,b akzeptiert, die eine ungerade Anzahl von b's oder eine gerade Anzahl von a's (inkl. leere Menge) haben",
                verifyWords=verifyWords
                )
    A.testWords = A.testWorteGenerator(3)
    return A


def Uebungsblatt2_Aufgabe5minimiert2():
    S = 'X'
    s0 = 'X'
    F = S
    Sigma = 'a b'
    delta = {
        'X': {
            'a b': 'X',
        },
    }
    vA = Uebungsblatt2_Aufgabe5()
    verifyWords = vA.verifyWords
    A = Automat(S, s0, F, Sigma, delta,
                name="U2A5b (minimiert 2)",
                beschreibung="DEA, der alle Worte über a,b akzeptiert, die eine ungerade Anzahl von b's oder eine gerade Anzahl von a's (inkl. leere Menge) haben",
                verifyWords=verifyWords
                )
    A.testWords = A.testWorteGenerator(3)
    return A


def Uebungsblatt3_Aufgabe2_M1():
    S = 'z0 z1 z2'
    s0 = 'z0'
    F = 'z2'
    Sigma = '0 1'
    delta = {
        'z0': {
            '1': 'z1',
        },
        'z1': {
            '1': 'z2',
        },
        'z2': {
            '0 1': 'z2',
        },
    }
    verifyWords = {'1': False, '11': True, '111': True, '110': True}
    A = Automat(S, s0, F, Sigma, delta,
                name="U3A2 (M1)",
                beschreibung="DEA, der alle Worte über 0,1 akzeptiert, die mit 11 beginnen",
                verifyWords=verifyWords
                )
    A.testWords = A.testWorteGenerator(3)
    return A


def Uebungsblatt3_Aufgabe2_M2():
    S = 's0 s1'
    s0 = 's0'
    F = 's1'
    Sigma = '0 1'
    delta = {
        's0': {
            '0': 's0',
            '1': 's1',
        },
        's1': {
            '0': 's0',
            '1': 's1',
        },
    }
    verifyWords = {'0': False, '01': True, '1': True, '11': True, '111': True, '110': False}
    A = Automat(S, s0, F, Sigma, delta,
                name="U3A2 (M2)",
                beschreibung="DEA, der alle Worte über 0,1 akzeptiert, die mit 1 enden",
                verifyWords=verifyWords
                )
    A.testWords = A.testWorteGenerator(3)
    return A


def Uebungsblatt3_Aufgabe2_zusammen_M1M2():
    S = 'z0s0 z1s1 z2s1 z2s0'
    s0 = 'z0s0'
    F = 'z2s1'
    Sigma = '0 1'
    delta = {
        'z0s0': {
            '1': 'z1s1',
        },
        'z1s1': {
            '1': 'z2s1',
        },
        'z2s1': {
            '0': 'z2s0',
            '1': 'z2s1'
        },
        'z2s0': {
            '0': 'z2s0',
            '1': 'z2s1'
        },
    }
    M1verifyWords = Uebungsblatt3_Aufgabe2_M1().verifyWords
    M2verifyWords = Uebungsblatt3_Aufgabe2_M2().verifyWords
    verifyWords = dict()

    for word in set(M1verifyWords.keys() + M2verifyWords.keys()):
        if (word in M2verifyWords) and (word in M1verifyWords):
            r1 = M1verifyWords[word]
            r2 = M2verifyWords[word]
            verifyWords[word] = r1 and r2

    A = Automat(S, s0, F, Sigma, delta,
                name="U3A2 (M1 und M2 kombiniert)",
                beschreibung="DEA, der alle Worte über 0,1 akzeptiert, die mit 11 beginnen und mit 1 aufhoeren. Schnittmenge aus L(M1) und L(M2)",
                verifyWords=verifyWords
                )
    A.testWords = A.testWorteGenerator(3)
    return A


def Uebungsblatt3_Aufgabe3():
    S = 'z0s0 z1s1 z2s1 z2s0'
    s0 = 'z0s0'
    F = 'z0s0 z1s1 z2s0'
    Sigma = '0 1'
    delta = {
        'z0s0': {
            '1': 'z1s1',
        },
        'z1s1': {
            '1': 'z2s1',
        },
        'z2s1': {
            '0': 'z2s0',
            '1': 'z2s1'
        },
        'z2s0': {
            '0': 'z2s0',
            '1': 'z2s1'
        },
    }

    M1M2verifyWords = Uebungsblatt3_Aufgabe2_zusammen_M1M2().verifyWords
    verifyWords = dict()

    for word in M1M2verifyWords:
        verifyWords[word] = not M1M2verifyWords[word]

    A = Automat(S, s0, F, Sigma, delta,
                name="U3A3",
                beschreibung="DEA, der alle Worte über 0,1 akzeptiert, die NICHT mit 11 beginnen und NICHT mit 1 aufhoeren. Umkehrung von Schnittmenge aus L(M1) und L(M2)",
                verifyWords=verifyWords
                )
    A.testWords = A.testWorteGenerator(3)
    return A


def Uebungsblatt3_Aufgabe5a():
    S = list("01234567")
    s0 = '0'
    F = '3 7'
    Sigma = list("abewy")
    delta = {
        '0': {
            'a b y': '0',
            'w': '1',
            'e': '4',
        },
        '1': {
            'e': '2',
            EpsilonAutomat.EPSILON: '0',
        },
        '2': {
            'b': '3',
            EpsilonAutomat.EPSILON: '0',
        },
        '3': {
            'a b e w y': '3',
        },
        '4': {
            'b': '5',
            EpsilonAutomat.EPSILON: '0',
        },
        '5': {
            'a': '6',
            EpsilonAutomat.EPSILON: '0',
        },
        '6': {
            'y': '7',
            EpsilonAutomat.EPSILON: '0',
        },
        '7': {
            'a b e w y': '7',
        },
    }
    verifyWords = {'ebay': True, 'web': True}
    testWords = ['eeeebay', 'webay', 'weeeebay', 'we', 'bay', 'webebay', 'webwebweb']
    e = EpsilonAutomat(S, s0, F, Sigma, delta,
                       name='U3A5a',
                       beschreibung="Sucht in einem Text die Worte web und ebay",
                       verifyWords=verifyWords,
                       testWords=testWords
                       )
    return e


def Uebungsblatt3_Aufgabe5b1():
    S = "0 1 2 3 4 5 6 7 05 06 07 47 17 057 067 03 34 13 035 036 037 0347 0357 137 0367 347 42"
    s0 = '0'
    F = '3 7 07 47 17 057 067 03 34 13 035 036 037 0347 0357 137 0367 347'
    Sigma = list("abewy")
    delta = {
        '0': {
            'a b y': '0',
            'e': '4',
            'w': '1',
        },
        '1': {
            'a b y': '0',
            'e': '42',
            'w': '1',
        },
        '2': {
            'a y': '0',
            'b': '0 3',
            'e': '4',
            'w': '1',
        },
        '3': {
            'a b e w y': '3',
        },
        '4': {
            'a y': '0',
            'b': '0 5',
            'e': '4',
            'w': '1',
        },
        '5': {
            'a': '0 6',
            'b y': '0',
            'e': '4',
            'w': '1',
        },
        '6': {
            'a b': '0',
            'y': '0 7',
            'w': '1',
            'e': '4',
        },
        '7': {
            'a b e w y': '7',
        },
        '05': {
            'a': '06',
            'b': '0',
            'e': '4',
            'w': '1',
            'y': '0',
        },
        '06': {
            'a': '0',
            'b': '0',
            'e': '4',
            'w': '1',
            'y': '07',
        },
        '07': {
            'a': '07',
            'b': '07',
            'e': '47',
            'w': '17',
            'y': '07',
        },
        '47': {
            'a': '07',
            'b': '057',
            'e': '47',
            'w': '17',
            'y': '07',
        },
        '17': {
            'a': '07',
            'b': '07',
            'e': '47',
            'w': '17',
            'y': '07',
        },
        '057': {
            'a': '067',
            'b': '07',
            'e': '47',
            'w': '17',
            'y': '07',
        },
        '067': {
            'a': '07',
            'b': '07',
            'e': '47',
            'w': '17',
            'y': '07',
        },
        '03': {
            'a': '03',
            'b': '03',
            'e': '34',
            'w': '13',
            'y': '03',
        },
        '34': {
            'a': '03',
            'b': '035',
            'e': '34',
            'w': '13',
            'y': '03',
        },
        '13': {
            'a': '03',
            'b': '03',
            'e': '34',
            'w': '13',
            'y': '03',
        },
        '035': {
            'a': '036',
            'b': '03',
            'e': '34',
            'w': '13',
            'y': '03',
        },
        '036': {
            'a': '03',
            'b': '03',
            'e': '34',
            'w': '13',
            'y': '037',
        },
        '037': {
            'a': '037',
            'b': '037',
            'e': '0347',
            'w': '137',
            'y': '037',
        },
        '0347': {
            'a': '037',
            'b': '0357',
            'e': '347',
            'w': '137',
            'y': '037',
        },
        '0357': {
            'a': '0367',
            'b': '0357',
            'e': '347',
            'w': '137',
            'y': '037',
        },
        '137': {
            'a': '037',
            'b': '037',
            'e': '347',
            'w': '137',
            'y': '037',
        },
        '0367': {
            'a': '037',
            'b': '037',
            'e': '347',
            'w': '137',
            'y': '037',
        },
        '347': {
            'a': '037',
            'b': '0357',
            'e': '347',
            'w': '137',
            'y': '037',
        },
        '42': {
            'a y': '0',
            'b': '035',
            'e': '4',
            'w': '1',
        }
    }
    verifyWords = {'ebay': True, 'web': True}
    testWords = ['eeeebay', 'webay', 'weeeebay', 'we', 'bay', 'webebay', 'webwebweb']
    e = NichtDeterministischerAutomat(S, s0, F, Sigma, delta,
                                      name='U3A5b',
                                      beschreibung="Sucht in einem Text die Worte web und ebay",
                                      verifyWords=verifyWords,
                                      testWords=testWords
                                      )
    return e


def Uebungsblatt3_Aufgabe5b2():
    S = list("014ABCDEFGHI")
    s0 = '0'
    F = list('BCDEFG')
    Sigma = list("abewy")
    delta = {
        '0': {
            'a b y': '0',
            'e': '4',
            'w': '1',
        },
        '1': {
            'a b y': '0',
            'e': 'A',
            'w': '1',
        },
        '4': {
            'a y': '0',
            'b': 'H',
            'e': '4',
            'w': '1',
        },
        'A': {
            'a y': '0',
            'b': 'B',
            'e': '4',
            'w': '1',
        },
        'B': {
            'a': 'C',
            'b': 'D',
            'e': 'E',
            'w': 'F',
            'y': 'D',
        },
        'C': {
            'a': 'D',
            'b': 'D',
            'e': 'E',
            'w': 'F',
            'y': 'D',
        },
        'D': {
            'a': 'D',
            'b': 'D',
            'e': 'E',
            'w': 'F',
            'y': 'D',
        },
        'E': {
            'a': 'D',
            'b': 'B',
            'e': 'E',
            'w': 'F',
            'y': 'D',
        },
        'F': {
            'a': 'D',
            'b': 'D',
            'e': 'G',
            'w': 'F',
            'y': 'D',
        },
        'G': {
            'a': 'D',
            'b': 'B',
            'e': 'E',
            'w': 'F',
            'y': 'D',
        },
        'H': {
            'a': 'I',
            'b': '0',
            'e': '4',
            'w': '1',
            'y': '0',
        },
        'I': {
            'a': '0',
            'b': '0',
            'e': '4',
            'w': '1',
            'y': 'D',
        },

    }
    verifyWords = {'ebay': True, 'web': True}
    testWords = ['eeeebay', 'webay', 'weeeebay', 'we', 'bay', 'webebay', 'webwebweb']
    e = NichtDeterministischerAutomat(S, s0, F, Sigma, delta,
                                      name='U3A5b2',
                                      beschreibung="Sucht in einem Text die Worte web und ebay",
                                      verifyWords=verifyWords,
                                      testWords=testWords
                                      )
    return e


def Uebungsblatt3_Aufgabe5b2minimiert():
    S = list("014AXHI")
    s0 = '0'
    F = list('X')
    Sigma = list("abewy")
    delta = {
        '0': {
            'a b y': '0',
            'e': '4',
            'w': '1',
        },
        '1': {
            'a b y': '0',
            'e': 'A',
            'w': '1',
        },
        '4': {
            'a y': '0',
            'b': 'H',
            'e': '4',
            'w': '1',
        },
        'A': {
            'a y': '0',
            'b': 'X',
            'e': '4',
            'w': '1',
        },
        'X': {
            'a b e w y': 'X',
        },
        'H': {
            'a': 'I',
            'b': '0',
            'e': '4',
            'w': '1',
            'y': '0',
        },
        'I': {
            'a': '0',
            'b': '0',
            'e': '4',
            'w': '1',
            'y': 'X',
        },

    }
    verifyWords = {'ebay': True, 'web': True}
    testWords = ['eeeebay', 'webay', 'weeeebay', 'we', 'bay', 'webebay', 'webwebweb']
    e = NichtDeterministischerAutomat(S, s0, F, Sigma, delta,
                                      name='U3A5b2minimiert',
                                      beschreibung="Sucht in einem Text die Worte web und ebay",
                                      verifyWords=verifyWords,
                                      testWords=testWords
                                      )
    return e


def Uebungsblatt4_Aufgabe1a():
    S = '0 2 4'
    s0 = '0'
    F = S
    Sigma = 'a b'
    delta = {
        '0': {
            'a': '2',
            'b': '4',
        },
        '2': {
            'a': '2',
            'b': '4',
        },
        '4': {
            'b': '4',
        },
    }
    verifyWords = {'': True, 'b': True, 'ba': False, 'aaaa': True}
    return Automat(S, s0, F, Sigma, delta,
                   name='U4A1a',
                   beschreibung="Regular Expression $a*b*$",
                   verifyWords=verifyWords,
                   )


def Uebungsblatt4_Aufgabe1b():
    S = 's 2 4 e'
    s0 = 's'
    F = 's e'
    Sigma = 'a b'
    delta = {
        's': {
            'a': '2',
            'b': '4',
        },
        '2': {
            'b': 'e',
        },
        '4': {
            'a': 'e',
        },
        'e': {
            'a': '2',
            'b': '4',
        },
    }
    verifyWords = {'': True, 'b': False, 'ba': True, 'aaaa': False, 'abba': True, 'ab': True}
    return Automat(S, s0, F, Sigma, delta,
                   name='U4A1b',
                   beschreibung="Regular Expression $(ab|ba)*$",
                   verifyWords=verifyWords,
                   )


def Uebungsblatt4_Aufgabe1bminimiert():
    S = '2 4 es F'
    s0 = 'es'
    F = 'es'
    Sigma = 'a b'
    delta = {
        'es': {
            'a': '2',
            'b': '4',
        },
        '2': {
            'a': 'F',
            'b': 'es',
        },
        '4': {
            'a': 'es',
            'b': 'F',
        },
        'F': {
            'a b': 'F',
        },
    }
    verifyWords = {'': True, 'b': False, 'ba': True, 'aaaa': False, 'abba': True, 'ab': True}
    return Automat(S, s0, F, Sigma, delta,
                   name='U4A1b (minimiert)',
                   beschreibung="Regular Expression $(ab|ba)*$",
                   verifyWords=verifyWords,
                   )


def Uebungsblatt4_Aufgabe1c():
    S = 'H B C Cy y F'
    s0 = 'H'
    F = 'y Cy'
    Sigma = 'a b'
    delta = {
        'H': {
            'a': 'C',
            'b': 'B',
        },
        'B': {
            'a': 'Cy',
            'b': 'C',
        },
        'C': {
            'a': 'C',
            'b': 'y',
        },
        'Cy': {
            'a': 'C',
            'b': 'F',
        },
        'y': {
            'a b': 'F',
        },
        'F': {
            'a b': 'F',
        },
    }
    # verifyWords = { '' : False, 'ba' : True, 'ab' : True, 'bbab' : True, 'abba' : False }
    worte = [''] + 'ba ab bbab abba'.split()
    pattern = re.compile('^ba|(a|bb)a*b$')

    verifyWords = dict()
    for wort in worte:
        res = pattern.match(wort)
        verifyWords[wort] = pattern.match(wort) and True or False

    return NichtDeterministischerAutomat(S, s0, F, Sigma, delta,
                                         name='U4A1c',
                                         beschreibung="Regular Expression $ba|(a|bb)a*b$",
                                         verifyWords=verifyWords,
                                         )


def Uebungsblatt4_Aufgabe2():
    S = 'z0 z1 z2 z3 z4'
    s0 = 'z0'
    F = 'z2 z4'
    Sigma = '0 1 + - .'
    delta = {
        'z0': {
            '+ -': 'z1',
            '0 1': 'z2',
        },
        'z1': {
            '0 1': 'z2',
        },
        'z2': {
            '0 1': 'z2',
            '.': 'z3',
        },
        'z3': {
            '0 1': 'z4',
        },
        'z4': {
            '0 1': 'z4',
        },
    }

    # Testworte mittels regular expression modul von python testen
    verifyWords = RegularExpressionTestWorte(['0', '1', '+0.1', '-00.1', 'xx'],
                                             r'(0|1)|(\+|-)(0|1)(0|1)*|(0|1)|(\+|-)(0|1)(0|1)*.(0|1)(0|1)*')

    return NichtDeterministischerAutomat(S, s0, F, Sigma, delta,
                                         name='U4A2',
                                         beschreibung="Regular Expression fuer Automaten generieren",
                                         verifyWords=verifyWords,
                                         )


def Uebungsblatt4_Aufgabe3a():
    S = '0 1 2 3'
    s0 = '0'
    F = '2'
    Sigma = 'a b c'
    delta = {
        '0': {
            'a': '1',
            'b': '3',
            'c': '0',
        },
        '1': {
            'a c': '1',
            'b': '2',
        },
        '3': {
            'b c': '3',
            'a': '2',
        },
        '2': {
            'a b c': '2',
        }
    }

    # Testworte mittels regular expression modul von python testen
    worte = ['a', 'b', 'ab', 'abc', 'cab', 'cc', 'bca']
    verifyWords = RegularExpressionTestWorte(worte, r'c*a(a|c)*b(a|b|c)*|c*b(b|c)*a(a|b|c)*')

    return NichtDeterministischerAutomat(S, s0, F, Sigma, delta,
                                         name='U4A3a',
                                         beschreibung="Regular Expression fuer Automaten generieren, der die Menge aller Woerter ueber a,b,c akzeptiert, die mindestens ein a und ein b enthalten",
                                         verifyWords=verifyWords,
                                         )


def Uebungsblatt4_Aufgabe3b():
    S = list('ABCDEF')
    s0 = 'A'
    F = 'F'
    Sigma = '0 1'
    delta = {
        'A': {
            '0': 'A',
            '1': 'A B',
        },
        'B': {
            '0 1': 'C',
        },
        'C': {
            '0 1': 'D',
        },
        'D': {
            '0 1': 'E',
        },
        'E': {
            '0 1': 'F',
        },
        'F': {
        },
    }

    # Testworte mittels regular expression modul von python testen
    worte = ['0', '1', '10000', '010000', '111111111111111111111']
    verifyWords = RegularExpressionTestWorte(worte, r'(0|1)*1(0|1)(0|1)(0|1)(0|1)')

    return NichtDeterministischerAutomat(S, s0, F, Sigma, delta,
                                         name='U4A3b',
                                         beschreibung="Regular Expression fuer Automaten generieren, der die Menge aller Woerter ueber 0,1 akzeptiert, deren fuenftes Symbol von rechts eine 1 ist",
                                         verifyWords=verifyWords,
                                         )


def Uebungsblatt4_Aufgabe3c():
    S = list('ABC')
    s0 = 'A'
    F = 'C'
    Sigma = '0 1'
    delta = {
        'A': {
            '0': 'A',
            '1': 'A B',
        },
        'B': {
            '1': 'C',
        },
        'C': {
            '0 1': 'C',
        },
    }

    # Testworte mittels regular expression modul von python testen
    worte = ['0', '1', '10', '01100', '11']
    verifyWords = RegularExpressionTestWorte(worte, r'(0|1)*11(0|1)*')

    return NichtDeterministischerAutomat(S, s0, F, Sigma, delta,
                                         name='U4A3c',
                                         beschreibung="Regular Expression fuer Automaten generieren, der die Menge aller Woerter ueber 0,1 akzeptiert, die mindestens ein 11-Paar enthalten",
                                         verifyWords=verifyWords,
                                         )


def Uebungsblatt4_Aufgabe3d():
    S = list('ABCDEF')
    s0 = 'A'
    F = S
    Sigma = '0 1'
    delta = {
        'A': {
            '0': 'B',
            '1': 'C',
        },
        'B': {
            '0': 'A',
            '1': 'C',
        },
        'C': {
            '0': 'F',
            '1': 'D',
        },
        'D': {
            '0': 'E',
            '1': 'D',
        },
        'E': {
            '1': 'D',
        },
        'F': {
            '1': 'D',
        },
    }

    # Testworte mittels regular expression modul von python testen
    worte = ['0', '1', '00100', '11000', '111101', '001101010']
    verifyWords = RegularExpressionTestWorte(worte,
                                             r'0|0(0*)|1|(0(0*)|0(0*)1)|(0(0*)10|0(0*)101(1*))|(0(0*)11(1*))|(0(0*)11(1*)01)|(0(0*)11(1*)0)|00*111*011*|00*111*011*0|00*101')

    return NichtDeterministischerAutomat(S, s0, F, Sigma, delta,
                                         name='U4A3d',
                                         beschreibung="Regular Expression fuer Automaten generieren, der die Menge aller Woerter ueber 0,1 akzeptiert, deren 00-Paare vor allen 11-Paaren steht",
                                         verifyWords=verifyWords,
                                         )


def Uebungsblatt4_Aufgabe3e_Vorarbeit():
    A = AutomatenLeser(filename='data/u4a3e_inverted').automat()
    A.testWords = A.testWorteGenerator(Sigma=list(['0', '1', '101']))
    return A


def Uebungsblatt4_Aufgabe3e():
    A = AutomatenLeser(filename='data/u4a3e').automat()
    A.testWords = A.testWorteGenerator(Sigma=list(['0', '1', '101']))
    return A


def erstelleAutomatenListeFuer(prefix):
    if not isinstance(prefix, list):
        prefix = [prefix]
    automaten = list()
    fNames = list()
    for item in globals().keys():
        for aPrefix in prefix:
            if item.startswith(aPrefix):
                fNames.append(item)
    return sorted(fNames)


def erstelleAutomaten(automatenListe):
    automaten = list()
    for item in automatenListe:
        automaten.append(eval(item + '()'))
    return automaten


def erstelleAutomatenFuer(prefix):
    automatenListe = erstelleAutomatenListeFuer(prefix)
    return erstelleAutomaten(automatenListe)


def AutomatenBlatt(automatenListe, finalFileBase='AutomatenReport'):
    automaten = erstelleAutomaten(automatenListe)
    automatenReport(automaten, finalFileBase=finalFileBase)


def AutomatenPlaintext(automatenListe, targetDir='.'):
    automaten = erstelleAutomaten(automatenListe)
    for automat in automaten:
        automat.writePlaintext(targetDir=targetDir)


# parse options et al
parser = OptionParser()

parser.add_option('-a', "--print",
                  action="store_true", default=False,
                  help="Print ASCII representation of the automaton",
                  dest="ascii")

parser.add_option('-d', "--dump",
                  action="store_true", default=False,
                  help="Print raw data",
                  dest="dump")

parser.add_option('-l', "--list",
                  action="store_true", default=False,
                  help="List automatons",
                  dest="list")

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

parser.add_option('-o', "--write-plaintext",
                  default=False,
                  help="write plaintext automaton to DIR",
                  dest="dir")

parser.add_option("--prefix",
                  default='all',
                  help="""Prefix to use.
                    Possible values:
                    %s""" % ', '.join(DEFAULT_PREFIX_LIST),
                  dest="prefix")

parser.add_option('-t', "--test-words",
                  default=False,
                  help="Test words (seperated by whitespace)",
                  dest="testWords")

parser.add_option('-v', "--verify",
                  action="store_true", default=False,
                  help="Verify automaton",
                  dest="verify")

parser.add_option('-w', "--write-pdf",
                  default=False,
                  help="Create automaton report PDF",
                  dest="pdf")

(options, files) = parser.parse_args()

# Logging init
logger = AutomatLogger(options.loglevel).log

if options.prefix == 'all':
    options.prefix = DEFAULT_PREFIX_LIST

automatenListe = erstelleAutomatenListeFuer(options.prefix)

if options.dump or options.ascii or options.verify or options.testWords:
    automaten = erstelleAutomaten(automatenListe)
    for A in automaten:
        if options.dump:
            print A.dump()

        if options.ascii:
            print A

        if options.verify:
            A.verify()
            A.verifyByRegExp()

        if options.testWords:
            words = options.testWords.split()
            A.checkWords(words)
            A.verifyByRegExp(words)

if options.list:
    for aName in automatenListe:
        logger.info("%s" % aName)

if options.dir:
    AutomatenPlaintext(automatenListe, targetDir=options.dir)

if options.pdf:
    filebase = options.pdf
    if options.pdf.lower().endswith('.pdf'):
        filebase = options.pdf[:-4]
    AutomatenBlatt(automatenListe, finalFileBase=filebase)
