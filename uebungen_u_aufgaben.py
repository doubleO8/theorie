#!/usr/bin/env python
# -*- coding: utf-8 -*-
from automaten import *

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

def testWorte(Sigma, length=3):
	worte = list(Sigma)
	SigmaTmp = Sigma
	#[a + b for a in eins for b in eins]
	for i in xrange(length):
		SigmaTmp = [ a + b for b in Sigma for a in SigmaTmp]
		#print SigmaTmp
		worte += SigmaTmp
	return worte

U1A2_Testworte = testWorte(['a', 'b'])

def Script_Beispiel_1_1():
	S = 'aus an'
	s0 = 'aus'
	F = 'an'
	Sigma = '0 1'
	delta = {
				'aus' : {
							"0" : 'aus',
							"1" : 'an',
						},
				'an' : {
							'0' : 'aus',
							'1' : 'an',
						},
			}
	return Automat(S, s0, F, Sigma, delta,
				name="Beispiel1.1",
				beschreibung="Ein Schalter",
				testWords=testWorte(['0', '1']))

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
				testWords=testWorte(['0', '1']))
	return A

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
				beschreibung="Endlicher deterministischer Automat für die normierte Darstellung reeller Zahlen",
				testWords='0 1 2 00.1 0.1 0.101. . 101 001 1.001.02')
	return C

def Script_Beispiel_1_4():
	S = 's0 s1 s2 s3'
	s0 = 's0'
	F = 's3'
	Sigma = '0 1'
	delta = {
				's0' : {
						'0' : 's0 s1',
						'1' : 's0',
						},
				's1' : {
						'0' : 's2',
						'1' : 's2',
						},
				's2' : {
						'0' : 's3',
						'1' : 's3',
						},
			}
	A = NichtDeterministischerAutomat(S, s0, F, Sigma, delta,
				name="Beispiel1.4",
				beschreibung="Ein endlicher nichtdeterministischer Automat für die Menge aller Bitfolgen, deren drittletzte Ziffer eine 0 ist",
				testWords=testWorte(['0', '1']))
	return A

def Script_Beispiel_1_4intuitiv():
	S = '111 110 100 101 010 011 001 000'
	s0 = '111'
	F = '011 001 010 000'
	Sigma = '0 1'
	delta = {
				'111' : {
							"0" : '110',
							"1" : '111',
						},
				'110' : {
							"0" : '100',
							"1" : '101',
						},
				'100' : {
							"0" : '000',
							"1" : '001',
						},
				'101' : {
							"0" : '010',
							"1" : '011',
						},
				'010' : {
							"0" : '100',
							"1" : '101',
						},
				'011' : {
							"0" : '110',
							"1" : '111',
						},
				'001' : {
							"0" : '010',
							"1" : '011',
						},
				'000' : {
							"0" : '000',
							"1" : '001',
						},
			}
	A = Automat(S, s0, F, Sigma, delta,
				name="Beispiel1.4 (intuitiv)",
				beschreibung="Ein endlicher deterministischer Automat für die Menge aller Bitfolgen, deren drittletzte Ziffer eine 0 ist",
				testWords=testWorte(['0', '1']))
	return A

def Script_Beispiel_1_5_DEA():
	S = '0 A B C D E F G'
	s0 = '0'
	F = 'D E F G'
	Sigma = '0 1'
	delta = {
				'0' : {
							"0" : 'A',
							"1" : '0',
						},
				'A' : {
							"0" : 'C',
							"1" : 'B',
						},
				'B' : {
							"0" : 'F',
							"1" : 'G',
						},
				'C' : {
							"0" : 'D',
							"1" : 'E',
						},
				'D' : {
							"0" : 'D',
							"1" : 'E',
						},
				'E' : {
							"0" : 'F',
							"1" : 'G',
						},
				'F' : {
							"0" : 'C',
							"1" : 'B',
						},
				'G' : {
							"0" : 'A',
							"1" : '0',
						},
			}
	A = Automat(S, s0, F, Sigma, delta,
				name="Beispiel1.5 (DEA)",
				beschreibung="Ein endlicher deterministischer Automat für die Menge aller Bitfolgen, deren drittletzte Ziffer eine 0 ist",
				testWords=testWorte(['0', '1']))
	return A

testZahlen1='0 1 2 +99 -99 9- a -'

def Script_Beispiel_1_6_NDA():
	S = 's0 s1 s2'
	s0 = 's0'
	F = 's2'
	Sigma = '0 1 2 3 4 5 6 7 8 9 + -'
	delta = {
				's0' : {
						('+', '-', EpsilonAutomat.EPSILON) : 's1',
						},
				's1' : {
						('0', '1', '2', '3', '4', '5', '6', '7', '8', '9') : 's2',
						},
				's2' : {
						('0', '1', '2', '3', '4', '5', '6', '7', '8', '9') : 's2',
						},
			}
	return EpsilonAutomat(S, s0, F, Sigma, delta, testWords=testZahlen1)

def Script_Beispiel_1_6_DEA():
	S = 's0 s1 s2'
	s0 = 's0'
	F = 's2'
	Sigma = '0 1 2 3 4 5 6 7 8 9 + -'
	delta = {
				's0' : {
						'+ -' : 's1',
						('0', '1', '2', '3', '4', '5', '6', '7', '8', '9') : 's2',
						},
				's1' : {
						('0', '1', '2', '3', '4', '5', '6', '7', '8', '9') : 's2',
						},
				's2' : {
						('0', '1', '2', '3', '4', '5', '6', '7', '8', '9') : 's2',
						},
			}
	return Automat(S, s0, F, Sigma, delta, testWords=testZahlen1)
	
def Uebungsblatt1_Aufgabe_1b():
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
	return A

def Uebungsblatt1_Aufgabe_2a():
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
				testWords=U1A2_Testworte)
	return A

def Uebungsblatt1_Aufgabe_2b():
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
				testWords=U1A2_Testworte)
	return A

def Uebungsblatt1_Aufgabe_2c():
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
							'a' : 'z0',
							'b' : 'z1',
						},
			}
	A = Automat('z0 z1 z2', 'z0', 'z0 z1', 'a b', delta,
				name="U1A2c",
				beschreibung="Akzeptiert alle Worte, die nicht mit ba enden",
				testWords=U1A2_Testworte)
	return A

def Uebungsblatt1_Aufgabe_2d():
	delta = {
				'z0' : {
							'a' : 'z1',
							'b' : 'z4'
						},
				'z1' : {
							'a' : 'z6',
							'b' : 'z2',
						},
				'z2' : {
							'a' : 'z5',
							'b' : 'z3',
						},
				'z3' : {
							'a' : 'z5', 
							'b' : 'z3',
						},
				'z4' : {
							'a' : 'z5',
							'b' : 'z6',
						},
				'z5' : {
							'a' : 'z7',
							'b' : 'z2',
						},
				'z6' : {
							('a', 'b') : 'z6',
						},
				'z7' : {
							'a' : 'z7',
							'b' : 'z2',
						},
			}
	A = Automat('z0 z1 z2 z3 z4 z5 z6 z7', 'z0', 'z3 z6 z7', 'a b', delta,
				name="U1A2d",
				beschreibung="Akzeptiert alle Worte, die mit zwei gleichen Zeichen enden oder beginnen",
				testWords=U1A2_Testworte)
	return A

def Uebungsblatt1_Aufgabe_2d1():
	delta = {
				'z1' : {
							'a' : 'z2',
							'b' : 'z4',
						},
				'z2' : {
							'a' : 'z3',
							'b' : 'z9',
						},
				'z3' : {
							('a', 'b') : 'z3',
						},
				'z4' : {
							'a' : 'z7',
							'b' : 'z5',
						},
				'z5' : {
							('a', 'b') : 'z5',
						},
				'z7' : {
							'a' : 'z8',
							'b' : 'z9',
						},
				'z8' : {
							'a' : 'z8',
							'b' : 'z9',
						},
				'z9' : {
							'a' : 'z7',
							'b' : 'z10',
						},
				'z10' : {
							'a' : 'z7',
							'b' : 'z10',
						},
			}
	A = Automat('z1 z2 z3 z4 z5 z7 z8 z9 z10', 'z1', 'z3 z5 z8 z10', 'a b', delta,
				name="U1A2d (alternativ)",
				beschreibung="Akzeptiert alle Worte, die mit zwei gleichen Zeichen enden oder beginnen",
				testWords=U1A2_Testworte)
	return A

def Uebungsblatt1_Aufgabe_2e():
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
				testWords=U1A2_Testworte)
	return A

def Uebungsblatt1_Aufgabe_3a():
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
	return A

def Uebungsblatt1_Aufgabe_3b():
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
	return A

def Sonstige_Aufgabe_3x1():
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
	return A

def Sonstige_Aufgabe_3x2():
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
	return A

def Sonstige_Aufgabe_3x3():
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
	return A

def Uebungsblatt1_Aufgabe_5b():
	delta = {
				'1' : {
							'a' : '2',
						},
				'2' : {
							'a' : '2',
							'b' : 'A',
						},
				'A' : {
							'a' : 'B',
							'b' : 'C',
						},
				'B' : {
							'a' : '2',
							'b' : 'A',
						},
				'C' : {
							'a' : 'B',
							'b' : 'C',
						},
			}
	A = Automat('1 2 A B C', '1', 'B C', 'a b', delta,
				name="U1A5b",
				beschreibung="Akzeptiert alle Worte, die mit a beginnen und als zweitletztes Zeichen ein b besitzen",
				testWords=U1A2_Testworte)
	return A

def Uebungsblatt2_Aufgabe1():
	delta = {
				'z0' : { 
							('+', '-', EpsilonAutomat.EPSILON) : 'z1',
						},
				'z1' : {
						'0 1' : 'z2'
						},
				'z2' : {
						'.' : 'z3',
						EpsilonAutomat.EPSILON : 'z1 z4',
						},
				'z3' : {
						'0 1' : 'z4',
						},
				'z4' :{
						'e' : 'z5',
						EpsilonAutomat.EPSILON : 'z3 z7',
						},
				'z5' :{
						('+', '-', EpsilonAutomat.EPSILON) : 'z6',
						},
				'z6' :{
						'0 1' : 'z7',
						},
				'z7' :{
						EpsilonAutomat.EPSILON : 'z6',
						},
			}

	return EpsilonAutomat('z0 z1 z2 z3 z4 z5 z6 z7', 'z0', 'z7', '0 1 + - . e', delta, 
						testWords="0 1 0.1 0.1e-1")

def Sonstige_Aufgabe_EidTI_U6():
	"""
	boese: schlecht erarbeitet und hingewuergt.
	"""
	delta = {
				'A' : {
							('a', 'e', 'g', 'X') : 'A',
							'b' : 'AB',
						},
				'AB' : {
							'a' : 'AC',
							'b' : 'AB',
							('e', 'g', 'X') : 'A',
						},
				'AC' : {
							('a', 'e', 'g', 'X') : 'A',
							'b' : 'ABD',
						},
				'ABD' : {
							'a' : 'ACE',
							'b' : 'ABC',
							('e', 'g', 'X') : 'A',
						},
				'ACE' : {
							'a' : 'A',
							'b' : 'ABD',
							('e', 'X') : 'A',
							'g' : 'AG',
						},
				'ABC' : {
							'a' : 'ACE',
							'b' : 'ABD',
							('e', 'g', 'X') : 'A',
						},
				'AG' : {
							'a' : 'A',
							'b' : 'AB',
							('g', 'X') : 'A',
							'e' : 'AH',
						},
				'AH' : {
							'a' : 'A',
							'b' : 'AB',
							('e', 'g', 'X') : 'A',
						},
			}
	A = Automat('A AB AC ABD ACE ABC AG AH', 'A', 'AH', 'a b e g X', delta,
				name="EidTIU6",
				beschreibung="Akzeptiert alle Worte, die mit babbage aufhoeren",
				testWords=testWorte(['a', 'b', 'babbage']))
	return A

def mergeAndOpenPDF(files, output="/Users/wolf/Desktop/automaten.pdf"):
	if len(files) == 0:
		print "merge WHAT exactly ?"
		return
	baseCmd = 'gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile="%s" ' % output
	command = baseCmd + ' '.join(files) + '&& open "%s"' % output
	call(command, shell=True)

def erstelleAutomatenPDFs(automaten):
	opFiles = list()
	for automat in automaten:
		outputFile = automat.createTeXDocument()
		if outputFile:
			opFiles.append(outputFile)
		else:
			print("Fehler: %s" % automat.name)
	return opFiles

def erstelleAutomatenFuer(prefix):
	automaten = list()
	fNames = list()
	for item in globals().keys():
		if item.startswith(prefix + '_'):
			#print "%s : %s" % (repr(item), globals()[item])
			fNames.append(item)
	
	for item in sorted(fNames):
		automaten.append(eval(item + '()'))
	return automaten

def Uebungsblatt1():
	automaten = erstelleAutomatenFuer('Uebungsblatt1')
	for automat in automaten:
		print automat
		if automat.testWords:
			print "TEST:\n%s" % ('-' * 80)
			for (word, successful, result) in automat.checkWords(automat.testWords):
				print "[%2s] %-10s : %s" % ((successful and 'ok' or 'KO'), word, result)
			print "\n"
	return erstelleAutomatenPDFs(automaten)

def ScriptBeispiele():
	automaten = erstelleAutomatenFuer('Script')
	for automat in automaten:
		print automat
		if automat.testWords:
			print "TEST:\n%s" % ('-' * 80)
			for (word, successful, result) in automat.checkWords(automat.testWords):
				print "[%2s] %-10s : %s" % ((successful and 'ok' or 'KO'), word, result)
			print "\n"
	return erstelleAutomatenPDFs(automaten)

def Sonstige():
	automaten = erstelleAutomatenFuer('Sonstige')
# 	for automat in automaten:
# 		print automat
# 		if automat.testWords:
# 			print "TEST:\n%s" % ('-' * 80)
# 			for (word, successful, result) in automat.checkWords(automat.testWords):
# 				print "[%2s] %-10s : %s" % ((successful and 'ok' or 'KO'), word, result)
# 			print "\n"
	return erstelleAutomatenPDFs(automaten)

def Tester():
	automaten = [Script_Beispiel_1_6_NDA(), Script_Beispiel_1_6_DEA(), Uebungsblatt2_Aufgabe1()]
	#erstelleAutomatenFuer('Script')
	for automat in automaten:
		print automat
		if automat.testWords:
			print "\nTEST:\n%s" % ('-' * 80)
			for (word, successful, result) in automat.checkWords(automat.testWords):
				print "[%2s] %-10s : %s" % ((successful and 'ok' or 'KO'), word, result)
			print "\n"

if __name__ == '__main__':
	#binaere_zahlen(100, 3, True)

	#mergeAndOpenPDF(Uebungsblatt1(), "/Users/wolf/Desktop/Automaten Übungsblatt1.pdf")

	#mergeAndOpenPDF(ScriptBeispiele(), "/Users/wolf/Desktop/Automaten Script Beispiele.pdf")

	#mergeAndOpenPDF(Sonstige(), "/Users/wolf/Desktop/Automaten Sonstige.pdf")
	
	#mergeAndOpenPDF(Aktuell(), "/Users/wolf/Desktop/Aktuell.pdf")
	Tester()
	
