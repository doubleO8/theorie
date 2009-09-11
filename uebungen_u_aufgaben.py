#!/usr/bin/env python
# -*- coding: utf-8 -*-
from automaten import *
from automatenausgabe import *

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
	verifyWords = {'1' : True, '0' : False, '00' : False}
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
	verifyWords = {'001' : True, '010' : False, '0001' : True, '1001' : True}
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
	verifyWords = { '1' : True, '-' : False, '0.1' : True}
	return Automat(cS, cs0, cF, cSigma, cdelta, 
				name="Beispiel1.3",
				beschreibung="Endlicher deterministischer Automat für die normierte Darstellung reeller Zahlen",
				testWords='0 1 2 00.1 0.1 0.101. . 101 001 1.001.02',
				verifyWords = verifyWords
				)

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
						'0 1' : 's2',
						},
				's2' : {
						'0 1' : 's3',
						},
				's3' : {},
			}
	verifyWords = { '111' : False, '000' : True, '011' : True, '0' : False}
	A = NichtDeterministischerAutomat(S, s0, F, Sigma, delta,
				name="Beispiel1.4",
				beschreibung="Ein endlicher nichtdeterministischer Automat für die Menge aller Bitfolgen, deren drittletzte Ziffer eine 0 ist",
				testWords=testWorte(['0', '1']),
				verifyWords = verifyWords
				)
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
	verifyWords = { '111' : False, '000' : True, '011' : True, '0' : False}
	return Automat(S, s0, F, Sigma, delta,
				name="Beispiel1.4 (intuitiv)",
				beschreibung="Ein endlicher deterministischer Automat für die Menge aller Bitfolgen, deren drittletzte Ziffer eine 0 ist",
				testWords=testWorte(['0', '1']),
				verifyWords = verifyWords
				)

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
	verifyWords = { '111' : False, '000' : True, '011' : True, '0' : False}
	return Automat(S, s0, F, Sigma, delta,
				name="Beispiel1.5 (DEA)",
				beschreibung="Ein endlicher deterministischer Automat für die Menge aller Bitfolgen, deren drittletzte Ziffer eine 0 ist",
				testWords=testWorte(['0', '1']),
				verifyWords = verifyWords
				)

testZahlen1='0 1 2 +99 -99 9- a - +- -+ -+99 0019292'

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
						'0 1 2 3 4 5 6 7 8 9' : 's2',
						},
				's2' : {
						'0 1 2 3 4 5 6 7 8 9' : 's2',
						},
			}
	verifyWords = { 'a' : False, '000' : True, '011' : True, '+0' : True}
	return EpsilonAutomat(S, s0, F, Sigma, delta, 
							name="Beispiel 1.6.", 
							beschreibung="NEA, der Dezimalzahlen akzeptiert", 
							testWords=testZahlen1,
							verifyWords = verifyWords
							)

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
	verifyWords = { 'a' : False, '000' : True, '011' : True, '+0' : True}
	return Automat(S, s0, F, Sigma, delta,
					name="Beispiel 1.6. (DEA)",
					beschreibung="DEA, der Dezimalzahlen akzeptiert", 
					testWords=testZahlen1,
					verifyWords = verifyWords
					)

def Script_Beispiel_1_7():
	S = 's1 s2 s3 s4 s5 s6'
	s0 = 's1'
	F = 's3 s4 s5 s6'
	Sigma = '0 1'
	delta = {
				's1' : {
						'0' : 's2',
						'1' : 's3',
						},
				's2' : {
						'0' : 's2',
						'1' : 's4',
						},
				's3' : {
						'0' : 's1',
						'1' : 's5',
						},
				's4' : {
						'0' : 's2',
						'1' : 's5',
						},
				's5' : {
						'0' : 's2',
						'1' : 's6',
						},
				's6' : {
						'0' : 's2',
						'1' : 's1',
						},
			}
	verifyWords = {'0' : False, '1' : True}
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
				's12' : {
						'0' : 's12',
						'1' : 's34',
						},
				's34' : {
						'0' : 's12',
						'1' : 's5',
						},
				's5' : {
						'0' : 's12',
						'1' : 's6',
						},
				's6' : {
						'0 1' : 's12',
						},
			}
	verifyWords = {'0' : False, '1' : True}
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
	verifyWords = { 'baa' : True, 'ab' : True, 'abb' : True, 'a' : False, 'ba' : False}
	A = Automat('z0 z1 z2 z3 z4 z5 z6', 'z0', 'z2 z3 z6', 'a b', delta,
				name="U1A2b",
				beschreibung="Akzeptiert die drei Worte baa ab abb",
				testWords=U1A2_Testworte,
				verifyWords=verifyWords
				)
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
	verifyWords = { 'baa' : True, 'ab' : True, 'aba' : False, 'a' : True, 'ba' : False}
	A = Automat('z0 z1 z2', 'z0', 'z0 z1', 'a b', delta,
				name="U1A2c",
				beschreibung="Akzeptiert alle Worte, die nicht mit ba enden",
				testWords=U1A2_Testworte,
				verifyWords=verifyWords
				)
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
	verifyWords = { 'a' : False, 'aa' : True, 'abb' : True, 'aba' : False, 'aabb' : True}
	A = Automat('z0 z1 z2 z3 z4 z5 z6 z7', 'z0', 'z3 z6 z7', 'a b', delta,
				name="U1A2d",
				beschreibung="Akzeptiert alle Worte, die mit zwei gleichen Zeichen enden oder beginnen",
				testWords=U1A2_Testworte,
				verifyWords=verifyWords
				)
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
	verifyWords = { 'a' : False, 'aa' : True, 'abb' : True, 'aba' : False, 'aabb' : True}
	A = Automat('z1 z2 z3 z4 z5 z7 z8 z9 z10', 'z1', 'z3 z5 z8 z10', 'a b', delta,
				name="U1A2d (alternativ)",
				beschreibung="Akzeptiert alle Worte, die mit zwei gleichen Zeichen enden oder beginnen",
				testWords=U1A2_Testworte,
				verifyWords=verifyWords)
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
	verifyWords = { 'a' : True, 'aa' : False, 'abb' : True, 'aba' : False, 'aabb' : False}
	A = Automat('z0 z1', 'z0', 'z1', 'a b', delta,
				name="U1A2e",
				beschreibung="Akzeptiert alle Worte, die eine ungerade Anzahl von a's enthalten",
				testWords=U1A2_Testworte,
				verifyWords=verifyWords
				)
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

U2A1testWords = "0 1 +0 -0.001 0.1 0.1e-1 1.00e1 -0.0e0 - . ++ 0- 00. 001.0ee"
def Uebungsblatt2_Aufgabe_1():
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
						name="U2A1",
						beschreibung="NEA bei dem die epsilon-Übergänge zu eliminieren sind",
						testWords=U2A1testWords)

def Uebungsblatt2_Aufgabe_1_eliminiert():
	delta = {
				'z0' : { 
							'+ -' : 'z1',
							'0 1' : 'z2',
						},
				'z1' : {
						'0 1' : 'z2',
						},
				'z2' : {
						'.' : 'z3',
						'0 1' : 'z4',
						},
				'z3' : {
						'0 1' : 'z4',
						},
				'z4' :{
						'0 1' : 'z4 z7',
						'e' : 'z5',
						},
				'z5' :{
						'0 1' : 'z7',
						'+ -' : 'z6',
						},
				'z6' :{
						'0 1' : 'z7',
						},
				'z7' :{
						'0 1' : 'z7'
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
				'1' : { 
							'a' : '1', 
							EpsilonAutomat.EPSILON : '2',
						},
				'2' : { 
							'b' : '2', 
							EpsilonAutomat.EPSILON : '3',
						},
				'3' : { 
							'c' : '3', 
						},
			}

	e = EpsilonAutomat(S, s0, F, Sigma, delta,
						name="U2A2a",
						beschreibung="eNEA zur Erkennung aller Zeichenketten, die aus beliebig vielen as, gefolgt von beliebig vielen bs, gefolgt von beliebig vielen cs bestehen")
	e.testWords = e.testWorteGenerator(Sigma=['a', 'b', 'c'])
	return e

def Uebungsblatt2_Aufgabe_2b():
	S = '1 2 3 4 5 6 7 8'
	s0 = '1'
	F = '4 8'
	Sigma = '0 1'
	delta = {
				'1' : { 
							EpsilonAutomat.EPSILON : '2',
							EpsilonAutomat.EPSILON : '5',
						},
				'2' : { 
							'0' : '3', 
						},
				'3' : { 
							'1' : '4', 
						},
				'4' : { 
							EpsilonAutomat.EPSILON : '2',
						},
				'5' : { 
							'0' : '6', 
						},
				'6' : { 
							'1' : '7', 
						},
				'7' : {
							'0' : '8',
						},
				'8' : { 
							EpsilonAutomat.EPSILON : '5',
						},
			}

	e = EpsilonAutomat(S, s0, F, Sigma, delta,
						name="U2A2b",
						beschreibung="eNEA zur Erkennung aller Zeichenketten, die aus der ein- oder mehrmaligen Wiederholung von 01 oder 010 bestehen")
	e.testWords = e.testWorteGenerator(2, Sigma=['01', '010'])
	return e

def Uebungsblatt2_Aufgabe_2c():
	S = '0 1 2 3 4 5 6 7 8 9 10'
	s0 = '0'
	F = '10'
	Sigma = '0 1'
	delta = {
				'0' : { 
							'0' : '6',
							'1' : '1',
							EpsilonAutomat.EPSILON : '10',
						},
				'1' : {
							'0' : '6',
							'1' : '2',
						},
				'2' : { 
							EpsilonAutomat.EPSILON : '7',
							'1' : '3', 
						},
				'3' : { 
							EpsilonAutomat.EPSILON : '8',
							'1' : '4',
						},
				'4' : { 
							'0' : '10',
							'1' : '5',
						},
				'5' : {
							'0' : '6',
							'1' : '1',
						},
				'6' : {
							'0' : '7',
							EpsilonAutomat.EPSILON : '10',
						},
				'7' : { 
							'0' : '8',
							EpsilonAutomat.EPSILON : '10',
						},
				'8' : { 
							EpsilonAutomat.EPSILON : '10',
						},
				'9' : { 
							'0' : '10',
						},
				'10' : {
							'0' : '10',
							'1' : '6',
							EpsilonAutomat.EPSILON : '6',
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
				'z0' : { 
							'0' : 'z1',
							'1' : 'z2',
						},
				'z1' : {
							'0' : 'z1',
							'1' : 'z3',
						},
				'z2' : { 
							'0' : 'z2',
							'1' : 'z4', 
						},
				'z3' : { 
							'0' : 'z2',
							'1' : 'zF',
						},
				'z4' : { 
							'0' : 'z1',
							'1' : 'zF',
						},
				'zF' : {
							'0' : 'zF',
							'1' : 'zF',
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
				'a1' : {
						'a' : 'a2',
						'b' : 'a1',
						},
				'a2' : {
						'a' : 'a1',
						'b' : 'a2',
						}
			}
	verifyWords = { '' : True, 'a' : False, 'aa' : True, 'ab' : False, 'aab' : True}
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
				'b1' : {
						'a' : 'b1',
						'b' : 'b2',
						},
				'b2' : {
						'a' : 'b2',
						'b' : 'b1',
						}
			}
	verifyWords = { '' : False, 'b' : True, 'bb' : False, 'ab' : True, 'aab' : True}
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
				'a1b1' : {
							'a' : 'a2b1',
							'b' : 'a1b2',
						},
				'a2b1' : {
							'a' : 'a1b1',
							'b' : 'a2b2',
						},
				'a1b2' : {
							'a' : 'a2b2',
							'b' : 'a1b1',
						},
				'a2b2' : {
							'a' : 'a1b2',
							'b' : 'a2b1',
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
				'12' : {
						'a' : '12',
						'b' : '34',
						},
				'34' : {
						'a' : '34',
						'b' : '12',
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
				'X' : {
						'a b' : 'X',
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
				'z0' : {
						'1' : 'z1',
						},
				'z1' : {
						'1' : 'z2',
						},
				'z2' : {
						'0 1' : 'z2',
						},
			}
	verifyWords = { '1' : False, '11' : True, '111' : True, '110' : True}
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
				's0' : {
						'0' : 's0',
						'1' : 's1',
						},
				's1' : {
						'0' : 's0',
						'1' : 's1',
						},
			}
	verifyWords = { '0' : False, '01': True, '1' : True, '11' : True, '111' : True, '110' : False}
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
				'z0s0' : {
						'1' : 'z1s1',
						},
				'z1s1' : {
						'1' : 'z2s1',
						},
				'z2s1' : {
						'0' : 'z2s0',
						'1' : 'z2s1'
						},
				'z2s0' : {
						'0' : 'z2s0',
						'1' : 'z2s1'
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
				'z0s0' : {
						'1' : 'z1s1',
						},
				'z1s1' : {
						'1' : 'z2s1',
						},
				'z2s1' : {
						'0' : 'z2s0',
						'1' : 'z2s1'
						},
				'z2s0' : {
						'0' : 'z2s0',
						'1' : 'z2s1'
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

def erstelleAutomatenFuer(prefix):
	automaten = list()
	fNames = list()
	for item in globals().keys():
		if item.startswith(prefix + '_'):
			fNames.append(item)
	
	for item in sorted(fNames):
		automaten.append(eval(item + '()'))
	return automaten

def automatenReport(automaten, finalFileBase='AutomatReport', WORKINGDIR = '/Users/wolf/Documents/programming/theorie', TEMPLATESDIR = os.path.join(WORKINGDIR, 'texOutput')):
	if len(automaten) == 0:
		print "Automatenliste ist mir zu leer."
		return

	o = AusgebenderAutomat()
	t = SelfRemovingTempdir(workDir = WORKINGDIR)
	tmpDir = t.tmp
	base = t.getRandomFilename()

	texTarget = base + '.tex'
	pdfTarget = base + '.pdf'
	finalFile = os.path.join(WORKINGDIR, finalFileBase + '.pdf')
	
	contentS = ''
	for automat in automaten:
		contentS += automat._toTeX(os.path.join(TEMPLATESDIR, 'template.tex'))
	content = list()
	
	for line in contentS.split("\n"):
		line = line.strip()
		if not line.startswith("%") and line != '':
			content.append(line)

	binder = o._readTemplate(os.path.join(TEMPLATESDIR, 'binder.tex'))
	binder = binder.replace("%%__CONTENT__", "\n".join(content))
	
	try:
		out = open(texTarget, "w")
		out.write(binder)
		out.close()
	except Exception, e:
		print e

	(rc, out, err) = runCommand('pdflatex', ('"%s"' % texTarget), workDir=tmpDir)
	if rc != 0:
		print err
		print "----------------------"
		print out

	if rc == 0:
		(rc, out, err) = runCommand('pdflatex', ('"%s"' % texTarget), workDir=tmpDir)
		if rc != 0:
			print err
			print "----------------------"
			print out
		if rc == 0 and os.path.isfile(pdfTarget):
			shutil.move(pdfTarget, finalFile)
			runCommand('open', '"%s"' % finalFile)

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
	U = uCross(SmF, F).union(uCross(F,SmF))
	
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
				print "Vergleiche %s und %s" % (s,t)
				for zeichen in a.Sigma:
					first = list(a._delta(s, zeichen))[0]
					second = list(a._delta(t, zeichen))[0]
					fz = frozenset([first, second])
					print " d(%s, %s), d(%s, %s) => %s,%s             --*--        %s" % (s, zeichen, t, zeichen, first, second, fz)
					if len(fz) > 1 and fz not in U:
						#print " >> (%s,%s) in U: %s" % (first, second, U)
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

def AutomatenBlatt(prefix):
	if not isinstance(prefix, list):
		prefix = [prefix]

	for item in prefix:
		automaten = erstelleAutomatenFuer(item)
		automatenReport(automaten, finalFileBase=item)

if __name__ == '__main__':
	blaetterwald = ['Uebungsblatt1', 'Uebungsblatt2', 'Uebungsblatt3', 'Script', 'Sonstige']
	blaetterwald = ['Uebungsblatt3']
	AutomatenBlatt(blaetterwald)
