#!/usr/bin/env python
# -*- coding: utf-8 -*-
from automaten import *

def Script_Beispiel_1_2():
	S = 's0 s1 s2 s3'.split()
	s0 = 's0'
	F = 's3'.split()
	Sigma = '0 1'.split()
	delta = {
				's0' : {
							"0" : 's1',
							"1" : 's0',
						},
				's1' : {
							'0' : 's2',
							'1' : 's0',
						},
				's2' : {
							'0' : 's2',
							'1' : 's3',
						},
				's3' : {
							'0' : 's3',
							'1' : 's3',
						},
			}
	A = Automat(S, s0, F, Sigma, delta,
				name="Beispiel1.2",
				beschreibung="Ein endlicher deterministischer Automat für die Sprache L, die alle Wörter mit Teilwort 001 enthält",
				testWords='001 01 1 100 1001 0011 1000 1001 10001')
	A.createTeXDocument()

def Script_Beispiel_1_3():
	cS = 's0 s1 s2 s3 s4 s5 s6 s7'.split()
	cs0 = 's0'
	cF = 's2 s4 s7'.split()
	cSigma = '0 1 2 3 4 5 6 7 8 9 + - . e'.split()
	cdelta = {
				's0' : {
							('0', '1', '2', '3', '4', '5', '6', '7', '8', '9') : 's2',
							("+", '-') : 's1',
						},
				's1' : {
							('0', '1', '2', '3', '4', '5', '6', '7', '8', '9') : 's2',
						},
				's2' : {
							('0', '1', '2', '3', '4', '5', '6', '7', '8', '9') : 's2',
							"." : "s3",
							"e" : "s5"
						},
				's3' : {
							('0', '1', '2', '3', '4', '5', '6', '7', '8', '9') : 's4',
						},
				's4' : {
							('0', '1', '2', '3', '4', '5', '6', '7', '8', '9') : 's4',
							"e" : 's5',
						},
				's5' : {
							('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'): 's7',
							("+", '-') : "s6",
						},
				's6' : {
							('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'): 's7',
						},
				's7' : {
							('0', '1', '2', '3', '4', '5', '6', '7', '8', '9') : 's7',
						},
			}
	C = Automat(cS, cs0, cF, cSigma, cdelta, 
				name="Beispiel1.3",
				beschreibung="Endlicher deterministischer Automat für die normierte Darstellung reeler Zahlen",
				testWords='0 1 2 00.1 0.1 0.101. . 101 001 1.001.02')
	C.createTeXDocument()

def Aufgabe_1b():
	S = 'z0 z1 z2 z3 z4'.split()
	s0 = 'z0'
	F = 'z2 z4'.split()
	Sigma = '0 1 + - .'.split()
	delta = {
				'z0' : {
							('0', '1') : 'z2',
							('+', '-') : 'z1',
						},
				'z1' : {
							('0', '1') : 'z2',
						},
				'z2' : {
							('0', '1') : 'z2',
							'.' : 'z3',
						},
				'z3' : {
							('0', '1') : 'z4',
						},
				'z4' : {
							('0', '1') : 'z4',
						},
			}
	A1b = Automat(S, s0, F, Sigma, delta, 
					name="U1A1b",
					beschreibung="DEA, der Dezimalzahlen akzeptiert",
					testWords='0 1 -1 +1 2 -0 00.1 101 111 000 010 0.11.')
	A1b.createTeXDocument()

def Aufgabe_1c():
	S = 'z0 z1 z2 z3 z4 z5'.split()
	s0 = 'z0'
	F = 'z2 z4 z5'.split()
	Sigma = '0 1 + - .'.split()
	delta = {
				'z0' : {
							'1' : 'z2',
							'0' : 'z5',
							('+', '-') : 'z1',
						},
				'z1' : {
							'1' : 'z2',
							'0' : 'z5',
						},
				'z2' : {
							'1' : 'z2',
							'0' : 'z1',
							'.' : 'z3',
						},
				'z3' : {
							('0', '1') : 'z4',
						},
				'z4' : {
							('0', '1') : 'z4',
						},
				'z5' : {
							'1' : 'z2',
							'.' : 'z3',
						}
			}
	A = Automat(S, s0, F, Sigma, delta,
				name="U1A1c", 
				beschreibung="Veränderter Automat U1A1, der keine führenden Nullen mehr akzeptiert",
				testWords = '0 1 -1 +1 0.1 00.01 0000 101 +1.010 001')
	A.createTeXDocument()

def Aufgabe_2a():
	delta = {
				'z0' : {
							('a', 'b') : 'z1',
						},
				'z1' : {
							'b' : 'z2',
						},
				'z2' : {
							('a', 'b') : 'z2',
						},
			}
	A = Automat('z0 z1 z2', 'z0', 'z2', 'a b', delta,
				name="U1A2a",
				beschreibung="Akzeptiert alle Worte, die als zweites Zeichen ein b besitzen",
				testWords="a b c ab ba bb aa bba bab bbb aaa")
	A.createTeXDocument()

def Aufgabe_2b():
	delta = {
				'z0' : {
							'a' : 'z1',
							'b' : 'z4'
						},
				'z1' : {
							'b' : 'z2',
						},
				'z2' : {
							'b' : 'z3',
						},
				'z3' : {},
				'z4' : {
							'a' : 'z5',
						},
				'z5' : {
							'a' : 'z6',
						},
				'z6' : {},
			}
	A = Automat('z0 z1 z2 z3 z4 z5 z6', 'z0', 'z2 z3 z6', 'a b', delta,
				name="U1A2b",
				beschreibung="Akzeptiert die drei Worte baa ab abb",
				testWords="baa ab abb aaa baab bab aa aab")
	A.createTeXDocument()

def Aufgabe_2c():
	delta = {
				'z0' : {
							'a' : 'z0',
							'b' : 'z1'
						},
				'z1' : {
							'a' : 'z2',
							'b' : 'z1',
						},
				'z2' : {
							('a', 'b') : 'z0',
						},
			}
	A = Automat('z0 z1 z2', 'z0', 'z0 z1', 'a b', delta,
				name="U1A2c",
				beschreibung="Akzeptiert alle Worte, die nicht mit ba enden",
				testWords="ab ba aba abaa bbbb aaaa aaaaaaaaaaaaaaaaaaaaaaaaba bbbbbbbbba")
	A.createTeXDocument()

def Aufgabe_2d():
	delta = {
				'z0' : {
							'a' : 'z1',
							'b' : 'z4'
						},
				'z1' : {
							'a' : 'z2',
							'b' : 'z0',
						},
				'z2' : {
							('a', 'b') : 'z3',
						},
				'z3' : {
							('a', 'b') : 'z3',
						},
				'z4' : {
							'b' : 'z5',
							'a' : 'z0'
						},
				'z5' : {
							('a', 'b') : 'z3',
						},
			}
	A = Automat('z0 z1 z2 z3 z4 z5', 'z0', 'z2 z3 z5', 'a b', delta,
				name="U1A2d",
				beschreibung="Akzeptiert alle Worte, die mit zei gleichen Zeichen enden oder beginnen",
				testWords="ab ba aba abaa bbbb aaaa aaaaaaaaaaaaaaaaaaaaaaaaba bbbbbbbbba")
	A.createTeXDocument()

def Aufgabe_2e():
	delta = {
				'z0' : {
							'a' : 'z1',
							'b' : 'z0'
						},
				'z1' : {
							'a' : 'z0',
							'b' : 'z1',
						},
			}
	A = Automat('z0 z1', 'z0', 'z1', 'a b', delta,
				name="U1A2e",
				beschreibung="Akzeptiert alle Worte, die eine ungerade Anzahl von a's enthalten",
				testWords="ab ba aba abaa bbbb aaaa aaaaaaaaaaaaaaaaaaaaaaaaba bbbbbbbbba")
	A.createTeXDocument()

def Aufgabe_3a():
	delta = {
				'z0' : {
							'0' : 'z0',
							'1' : 'z1'
						},
				'z1' : {
							'0' : 'z0',
							'1' : 'z1',
						},
			}
	tw = list()
	for i in xrange(20):
		tw.append(int2bin(i))

	A = Automat('z0 z1', 'z0', 'z1', '0 1', delta,
				name="U1A3a",
				beschreibung="DEA, der für eine ganze Zahl in Binärdarstellung entscheidet, ob die Zahl durch 2 ohne Rest teilbar ist",
				testWords=tw)
	A.createTeXDocument()

def Aufgabe_3b():
	delta = {
				'z0' : {
							'0' : 'z1',
							'1' : 'z2',
						},
				'z1' : {
							'0' : 'z1',
							'1' : 'z2',
						},
				'z2' : {
							'0' : 'z3',
							'1' : 'z1',
						},
				'z3' : {
							'0' : 'z2',
							'1' : 'z3',
						},
			}
	tw = list()
	for i in xrange(10):
		tw.append(int2bin(i))
	for i in xrange(10, 300):
		if i % 3 == 0:
			tw.append(int2bin(i))

	A = Automat('z0 z1 z2 z3', 'z0', 'z1', '0 1', delta,
				name="U1A3b",
				beschreibung="DEA, der für eine ganze Zahl in Binärdarstellung entscheidet, ob die Zahl durch 3 ohne Rest teilbar ist",
				testWords=tw)
	A.createTeXDocument()

def Aufgabe_3x1():
	delta = {
				'z0' : {
							'0' : 'z1',
							'1' : 'z0'
						},
				'z1' : {
							'0' : 'z2',
							'1' : 'z0',
						},
				'z2' : {
							'0' : 'z2',
							'1' : 'z0',
						},
			}
	tw = list()
	for i in xrange(20):
		tw.append(int2bin(i))

	A = Automat('z0 z1 z2', 'z0', 'z2', '0 1', delta,
				name="U1A3x1",
				beschreibung="DEA, der für eine ganze Zahl in Binärdarstellung entscheidet, ob die Zahl durch 4 ohne Rest teilbar ist",
				testWords=tw)
	A.createTeXDocument()

def Aufgabe_3x2():
	delta = {
				'z0' : {
							'0' : 'z1',
							'1' : 'z0'
						},
				'z1' : {
							'0' : 'z2',
							'1' : 'z0',
						},
				'z2' : {
							'0' : 'z3',
							'1' : 'z0',
						},
				'z3' : {
							'1' : 'z0',
							'0' : 'z3'
						},
			}
	tw = list()
	for i in xrange(100):
		tw.append(int2bin(i))

	A = Automat('z0 z1 z2 z3', 'z0', 'z3', '0 1', delta,
				name="U1A3x2",
				beschreibung="DEA, der für eine ganze Zahl in Binärdarstellung entscheidet, ob die Zahl durch 8 ohne Rest teilbar ist",
				testWords=tw)
	A.createTeXDocument()

def Aufgabe_3x3():
	delta = {
				'z0' : {
							'0' : 'z1',
							'1' : 'z2',
						},
				'z1' : {
							'0' : 'z4',
							'1' : 'z2',
						},
				'z2' : {
							'0' : 'z3',
							'1' : 'z1',
						},
				'z3' : {
							'0' : 'z2',
							'1' : 'z3',
						},
				'z4' : {
							'0' : 'z4',
							'1' : 'z2',
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
	A.createTeXDocument()
	#A.createDotDocument()

def int2bin(value, fill=0):
	result = list()
	while value:
		result.append(str(value & 1))
		value >>= 1
	result.reverse()
	return ''.join(result).zfill(fill) 

def quersumme(value):
	result = 0
	value=str(value)
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
			#s.append("%1s" % hit)
			s.append("%-8s" % int2bin(quersumme(i)))
			s.append(binaer.replace('0', ''))
			print ' '.join(s)
			#print("%3d : %-8s %1s %2s %-5s" % (i, binaer, hit, lastPortion, binaer.replace('0', '')))

if __name__ == '__main__':
	#Script_Beispiel_1_2()
	#Script_Beispiel_1_3()
	#Aufgabe_1b()
	#Aufgabe_1c()
	#Aufgabe_2a()
	#Aufgabe_2b()
	#Aufgabe_2c()
	#Aufgabe_2d()
	#Aufgabe_2e()
	#Aufgabe_3a()
	#Aufgabe_3b()
	#Aufgabe_3x1()
	#Aufgabe_3x2()
	#Aufgabe_3x3()
	#binaere_zahlen(100, 3, True)
