#!/usr/bin/env python
# -*- coding: utf-8 -*-
from automaten import *

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
	A1b = Automat(S, s0, F, Sigma, delta)
	A1b.createTeXDocument("texOutput/A1b.tex")
	
	print A1b
	testStrings = ['101', 1, 2]
	for wort in testStrings:
		print "%-15s : %s" % (wort, A1b.pruefWort(wort))

if __name__ == '__main__':
	Aufgabe_1b()