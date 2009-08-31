#!/usr/bin/env python
# -*- coding: utf-8 -*-
from automaten import *

def Script_Beispiel_1_2():
	S = 's0 s1 s2 s3'.split(' ')
	s0 = 's0'
	F = 's3'.split(' ')
	Sigma = '0 1'.split(' ')
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
	A = Automat(S, s0, F, Sigma, delta)
	A.createTeXDocument("texOutput/A.tex")

def Script_Beispiel_1_3():
	cS = 's0 s1 s2 s3 s4 s5 s6 s7'.split(' ')
	cs0 = 's0'
	cF = 's2 s4 s7'.split(' ')
	cSigma = '0 1 2 3 4 5 6 7 8 9 + - . e'.split(' ')
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
	C = Automat(cS, cs0, cF, cSigma, cdelta, name="C Automat")
	C.createTeXDocument("texOutput/C.tex")

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
	A1b = Automat(S, s0, F, Sigma, delta, name="Aufgabe1b")
	A1b.createTeXDocument("texOutput/A1b.tex")
	
	print A1b
	testStrings = ['101', 1, 2]
	for wort in testStrings:
		print "%-15s : %s" % (wort, A1b.check(wort))

if __name__ == '__main__':
	Script_Beispiel_1_2()
	Script_Beispiel_1_3()
	Aufgabe_1b()