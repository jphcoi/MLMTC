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
import sys,os
sys.path.append("libraries")

print "database_builder v1.0 (20100831)"
print "--------------------------------\n"

import parameters
import fonctions_bdd
import parseur
import text_processing
import shutil
import misc
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
user_interface=parameters.user_interface
print "--- initialisations terminees...\n"
print "+++ processing raw database \""+name_data+"\" into sql_where database file \""+name_bdd+"\""

sep  = ' *** '



#on définit une nouvelle table et une table billets temporaires
name_bdd_new = '.'.join(name_bdd.split('.')[:-2]) + '_new.' + '.'.join(name_bdd.split('.')[-2:])
name_bdd_temp = '.'.join(name_bdd.split('.')[:-2]) + '_temp.' +'.'.join(name_bdd.split('.')[-2:])

#on définit une série de nlemme qui forment la requête
#specific_nlemmes=['NO_an AD_lors','NO_scène','NO_expert'] 
specific_nlemmes = misc.lire_dico_classes(path_req + 'query.txt',language)
print specific_nlemmes
#on récupère les ids des concepts présents dans la requête dans query_ids
concepts = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'concepts','id,concepts')
query_ids =[]


for con in concepts:
	if con[1] in specific_nlemmes:
		query_ids.append(con[0])
print '\n' + str(len(query_ids)) + ' terms in the query.'
sous_corpus_idb_vect = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'concept2billets','id_b', ' where concept in '+ str(query_ids).replace('[','(').replace(']',')'))
sous_corpus_idb=[]
for x in sous_corpus_idb_vect:
	if not x[0] in sous_corpus_idb:
		sous_corpus_idb.append(x[0])


print str(len(sous_corpus_idb)) +' documents \n'
sql_where = " id in " + str(sous_corpus_idb).replace('[','(').replace(']',')')



print 'creation de la nouvelle base de données ' + name_bdd_new
shutil.copy(name_bdd, name_bdd_temp)
try:
	fonctions_bdd.detruire_table(name_bdd,'billets2')
except:
	pass
try:
	fonctions_bdd.creer_table_billets(name_bdd,'billets2')#creer une table billet2
	fonctions_bdd.add_column(name_bdd,'billets2','concepts_id','text')#et lui adjoindre le champ concepts_id
except:
	pass

	
fonctions_bdd.insert_select(name_bdd,'billets','billets2',sql_where)
fonctions_bdd.detruire_table(name_bdd,'billets')
fonctions_bdd.renommer_table(name_bdd,'billets2','billets')
shutil.copy(name_bdd, name_bdd_new)
shutil.copy(name_bdd_temp, name_bdd)
os.remove(name_bdd_temp)




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
	
	
# chaine = 'avant'
# chainel = 'avant'
# site='http://zolucider.blogspot.com/'

#nettoyer_site(chaine,chainel,site)