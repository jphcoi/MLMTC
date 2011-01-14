#!/usr/bin/env python
# encoding: utf-8
"""
db_builder.py

Created by Jean philippe cointet  on 2010-08-11.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""
try:
	import feedparser
except:
	pass
from datetime import timedelta
from datetime import date
import sys,os, math
sys.path.append("libraries")

print "database_builder v1.0 (20100831)"
print "--------------------------------\n"

import parameters
import fonctions_bdd

import fonctions_lib
import parseur
import text_processing
import shutil
import misc
from operator import itemgetter
###################################
#######0.quelques parametres#######
###################################

date_depart = parameters.date_depart
maxTermLength = parameters.maxTermLength
name_bdd = parameters.name_bdd
freqmin = parameters.freqmin
language = parameters.language

requete = parameters.requete
name_data = parameters.name_data 
name_data_real = parameters.name_data_real
lemmadictionary = parameters.lemmadictionary# si nul, on  calcule ou recalcule  le dico de lemmes sur la requete consideree sinon on ne calcule pas
path_req = parameters.path_req
sample = parameters.sample
top = parameters.top
print top
ng_filter = parameters.ng_filter
user_interface=parameters.user_interface
print "--- initialisations terminees...\n"
print "+++ processing raw database \""+name_data+"\" into sql_where database file \""+name_bdd+"\""

sep  = ' *** '
if 'lfl' in name_bdd:
	name_bdd_temp = '.'.join(name_bdd.split('.')[:-2]) + '_temp.' +'.'.join(name_bdd.split('.')[-2:])
	name_bdd_new = '.'.join(name_bdd.split('.')[:-2]) + '_new.' + '.'.join(name_bdd.split('.')[-2:])
else:
	name_bdd_new = '.'.join(name_bdd.split('.')[:-1]) + '_new.' + '.'.join(name_bdd.split('.')[-1:])
	name_bdd_temp = '.'.join(name_bdd.split('.')[:-1]) + '_temp.' +'.'.join(name_bdd.split('.')[-1:])


		
def nettoyer_site(chaine,chainel,site):
	sortie = fonctions_bdd.select_bdd_table_champ_complet(name_bdd,'billets','id,content,content_lemmatise','site',site)
	entree,entreel=[],[]
	for x in  sortie:
		idx = x[0]
		text = x[1]
		textl = x[2]
		n = text.find(chaine)
		nl = textl.find(chainel)
		if  n>0:
			entree.append((idx,n))
			entreel.append((idx,nl))
		print entree
	fonctions_bdd.insert_select_substring(name_bdd,'billets','billets',entree,'content')
	fonctions_bdd.insert_select_substring(name_bdd,'billets','billets',entreel,'content_lemmatise')
	
	
chaine = '... tags'
chainel = 'PU_... tags'
site='http://www.letelegramme.com/'

nettoyer_site(chaine,chainel,site)