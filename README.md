# introduction
*automatentheorie* is an implementation of an automaton in python (see http://en.wikipedia.org/wiki/Automata_theory).
It was written for studying purposes, comes without warranty of any kind and is released under the GPL.
Most of comments, method names et al are in german. Feel free to translate. That's it, that's all.

# Einführung
*automatentheorie* ist eine Sammlung von Python Programmen rund um die Vorlesung 
"Automatentheorie und formale Sprachen" (an der FH Wiesbaden) und dient ausschliesslich meinen 
Lernbeduerftnissen.

Letzere beinhalten vor allem die (einigermassen ansehnliche) Ausgabe von Automaten und automatisiertes
Pruefen, ob ein Automat Woerter akzeptiert oder nicht. 

Implementiert sind (in unterschiedlichen Reifegraden und Funktionsumfaengen) folgende Automaten:
* Nicht deterministische Automaten (NEA)
* Deterministische Automaten (DEA)
* Nicht deterministische Automaten mit Epsilon-Uebergaengen (eNEA)

Automaten (Definition/Spezifikation) werden mit LaTeX (und dot) ausgegeben. Sie koennen entweder 
als Python code definiert werden, oder aus einfachen Textdateien eingelesen werden.

Beispiel Automaten Definition als Textdatei:

```
#-------------8<---------------------------------------------------------------
# Automatendefinition
# [Barth] Uebungsblatt 4, Aufgabe 3e)

Name: U4A3e (Test-Dings)
Beschreibung: Ein Automat, der nur Woerter akzeptiert, in denen 101 nicht vorkommt

# Alphabet definieren, muss mit Sigma: beginnen, durch whitespace getrennt
Sigma: 0 1

# Finale Zustaende definieren, durch whitespace getrennt
F: A B C

# Optional: Zustaende definieren, durch whitespace getrennt (werden ansonsten durch die Uebergaenge
# definiert)
S: A B C D

# Startzustand definieren, durch whitespace getrennt
s0: A

# Uebergaenge
# Zustand, Zeichen, Zielzustand (durch whitespace getrennt)
A	0	A
A	1	B

B	0	C
B	1	B

C	0	A
C	1	D

D	0	D
D	1	D

# Optional: Worte, die akzeptiert werden sollen
AcceptedVerifyWords: 0 1 11 00 110 1100

# Optional: Worte, die _nicht akzeptiert werden duerfen
FailingVerifyWords: 101 0101 0010101 10110 11010

## PDF-Datei generieren (pdflatex etc. benoetigt!):
# ./autool.py data/readme_demo -w o.pdf

## Automat verifizieren lassen:
# ./autool.py -v data/readme_demo

## Pruefen, ob Testworte akzeptiert werden wuerden:
# ./autool.py -t "haha hihi hoho 001" data/readme_demo

## Grammatik generieren (BETA!):
# ./autool.py -g data/readme_demo
#-------------8<---------------------------------------------------------------
```

Die verwendeten Automaten orientieren sich an der Vorlesung bzw. Uebung und koennen durchaus falsche
Ergebnisse produzieren. 