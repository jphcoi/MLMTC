#!/usr/bin/env python
# encoding: utf-8
"""
clean_doublon.py

Created by Jean philippe cointet  on 2010-08-11.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

file_in = open("leven-classes_frencho.txt",'r')
file_out = open("leven-classes_frencho_nodoublon.txt",'w')

lignes = []
for ligne in file_in.readlines():
	if not ligne in lignes:
		lignes.append(ligne)
		file_out.write(ligne)


file_in = open("leven-classes_englisho.txt",'r')
file_out = open("leven-classes_englisho_nodoublon.txt",'w')

lignes = []
for ligne in file_in.readlines():
	if not ligne in lignes:
		lignes.append(ligne)
		file_out.write(ligne)


