#!/usr/bin/python
# -*- coding: utf-8 -*-
#script pour fusionner des listes de termes




import parameters
import sys
import fonctions_bdd
import parseur
import os
import glob
import codecs
import unicodedata
import text_processing
import leven 
import misc 
from datetime import timedelta
from datetime import date
import treetaggerwrapper
import fonctions_lib
import math

print "--- initialisations terminees...\n"
###################################
#######0.quelques parametres#######
##################################

maxTermLength = parameters.maxTermLength
name_bdd = parameters.name_bdd
freqmin = parameters.freqmin
name_data = parameters.name_data 
requete = parameters.requete
name_data_real = parameters.name_data_real
lemmadictionary = parameters.lemmadictionary# si nul, on  calcule ou recalcule  le dico de lemmes sur la requete consideree sinon on ne calcule pas
treetagger_dir =parameters.treetagger_dir
path_req = parameters.path_req
language = parameters.language
ng_filter=parameters.ng_filter
top=parameters.top
sample=parameters.sample
user_interface=parameters.user_interface

#on recupere d'abord toutes les années
years=parameters.years_bins_no_overlap

def find_between( s, first, last ):
	try:
		start = s.index( first ) + len( first )
		end = s.index( last, start )
		return s[start:end]
	except ValueError:
		return "",0



def fusion(type_file):
	year= '[abc,def]'
	if type_file =='redond':
		filename_redond_leven =  path_req + requete +'years/'+ '_' + str(freqmin)+str(year) + '_' + '_' + 'liste_n-grammes_freq_divers_leven_noredond.csv'
		marqueur = ']_liste_n-grammes_freq_divers_leven_noredond.csv'
	else:
		file_freq_exact =  path_req + 'years/'+requete +str(year) + '_' + '_' +  'frequences_exactes.csv'
		marqueur = ']_frequences_exactes.csv'
	dir = path_req + 'years/'
	liste_fichiers={}
	years = parameters.years_bins_no_overlap
	if type_file =='redond':
		filename_redond_leven_out =  path_req+ requete + '_' + str(freqmin)+'_' + str(min(years[0])) + '_' +str(max(years[-1]))+ '_' + 'liste_n-grammes_freq_divers_leven_noredond_totalyears.csv'
	else:
		filename_redond_leven_out =  path_req +requete + '_' + str(freqmin)+'_' + str(min(years[0])) + '_' +str(max(years[-1]))+ '_' + '_' +  'frequences_exactes_totalyears.csv'
	for fich in [f for f in os.listdir(dir)]:
		print fich
		print 'icii'
		if marqueur in fich and fich[0] != '.':
			year = find_between(fich,'[',']')
			year= '[' + year + ']'
	
			try:  
				liste_fichiers[year] = fich
			except:
				pass
	liste_nlemme_freq={}
	liste_nlemme_forme={}
	for ye,fi in liste_fichiers.iteritems():
		fil = open(path_req+'years/'+fi,'r')
		for x in fil.readlines():
			x=x[:-1]
			x = x.split('\t')
			nb_champs = len(x) - 2
			#on ne prend que la fréquence
			nb_champs = 1
			ngramme = x[0]
			forme = x[1]
			valeurs = '\t'.join(x[2:])
			if type_file =='redond':
				valeurs = x[3]
			else:
				valeurs = x[2]
			if not ngramme in liste_nlemme_forme:
				liste_nlemme_forme[ngramme] = forme
				temp = [(ye,valeurs)]
				liste_nlemme_freq[ngramme] = temp
			else:
				temp =liste_nlemme_freq[ngramme]
				temp.append((ye,valeurs))
				liste_nlemme_freq[ngramme] = temp
	fi_out= open(filename_redond_leven_out,'w')
	yi = min(years[0])
	yf = max(years[-1])
	vide= ''

	for x in range(nb_champs):
		vide=vide + '\t'
	chaine = ''
	chaine = chaine + 'nlemme \t forme_principale\t'
	for ye in years:
		for col in range(nb_champs):
			chaine = chaine + str(ye)  + '\t'
	fi_out.write(chaine[:-1] + '\n')
	chaine = ''
	for x,y in liste_nlemme_freq.iteritems():
		chaine = x + '\t' + liste_nlemme_forme[x] + '\t'
		for ye in years:
			cl = 0
			for evo in y:
				if str(ye) in evo:
					cl=1
					chaine=chaine +str(evo[1]) + '\t'
		if cl == 0:
			chaine =chaine +vide 		
		chaine =chaine + '\n'
		fi_out.write(chaine) 