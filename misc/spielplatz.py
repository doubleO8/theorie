#!/usr/bin/env python
# -*- coding: utf-8 -*-
from automaten import *
from automatenausgabe import *
from automatenleser import *

import re


def int2bin(value, fill=0):
    result = list()
    while value:
        result.append(str(value & 1))
        value >>= 1
    result.reverse()
    return ''.join(result).zfill(fill)


def quersumme(value):
    result = 0
    value = str(value)
    for z in value:
        result += int(z)
    return result


def binaere_zahlen(end=20, modulo=3, showOnlyModulo=False):
    for i in xrange(end):
        hit = (i % modulo == 0) and '*' or ''

        # i binaer
        binaer = int2bin(i)

        # letzte zwei ziffern
        lpCount = 1 + modulo % 2
        lastPortion = binaer[-2:]

        if hit or not showOnlyModulo:
            s = ["%3d : %-8s" % (i, binaer)]
            # s.append("%1s" % hit)
            s.append("%-8s" % int2bin(quersumme(i)))
            s.append(binaer.replace('0', ''))
            print ' '.join(s)
        # print("%3d : %-8s %1s %2s %-5s" % (i, binaer, hit, lastPortion, binaer.replace('0', '')))


def uCross(set1, set2):
    resulting_set = set()
    for s1 in set1:
        for s2 in set2:
            fz = frozenset([s1, s2])
            if len(fz) > 1:
                resulting_set.add(fz)
    return resulting_set


def Tester():
    a = Uebungsblatt2_Aufgabe_4()
    U = set()
    S = set(a.S)
    F = set(a.F)
    SmF = S - F
    U = uCross(SmF, F).union(uCross(F, SmF))

    print "S:"
    print S
    print "F:"
    print F
    print "S - F :"
    print SmF
    print "U:"
    print U
    print "S x S:"
    SxS = uCross(S, S)
    print SxS
    print "S x S - U:"
    print SxS.intersection(U)
    changed = True
    N = set()
    Uprev = U.copy()
    while changed:
        changed = False
        for st in SxS.intersection(U):
            if len(st) == 2:
                (s, t) = list(st)
                print "Vergleiche %s und %s" % (s, t)
                for zeichen in a.Sigma:
                    first = list(a._delta(s, zeichen))[0]
                    second = list(a._delta(t, zeichen))[0]
                    fz = frozenset([first, second])
                    print " d(%s, %s), d(%s, %s) => %s,%s             --*--        %s" % (
                    s, zeichen, t, zeichen, first, second, fz)
                    if len(fz) > 1 and fz not in U:
                        # print " >> (%s,%s) in U: %s" % (first, second, U)
                        U.add(st)
                        changed = True
                        print "changed"

    print "Resultierendes U:"
    for item in U:
        print sorted(item)
    print "=="
    print "N:"
    for item in N:
        print "%s %s" % (item, item in SxS - Uprev)
