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

name_bdd_new = '.'.join(name_bdd.split('.')[:-2]) + '_new.' + '.'.join(name_bdd.split('.')[-2:])



def select_query(query=[]):
	#on définit une nouvelle table et une table billets temporaires
	name_bdd_temp = '.'.join(name_bdd.split('.')[:-2]) + '_temp.' +'.'.join(name_bdd.split('.')[-2:])


	#specific_nlemmes est la requête de base issue de query.csv.
	if len(query)==0:
		specific_nlemme = misc.lire_dico_classes(path_req + 'query.csv',language)
		specific_nlemmes=[]
		for x in specific_nlemme:
			specific_nlemmes=specific_nlemmes+x.split('***')
	else:
		specific_nlemmes = query
	print specific_nlemmes
	print '\n' + str(len(specific_nlemmes)) +' terms in the query '
	#on récupère les ids des concepts présents dans la requête dans query_ids
	query_ids =[]

	try:
		concepts = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'concepts','id,concepts')
		for con in concepts:
			if con[1] in specific_nlemmes:
				query_ids.append(con[0])
	except:
		#il se peut que la base n'est jamais été indexée
		pass

	try:
		#tous les termes de la query ont déjà été indexés
		sous_corpus_idb_vect = fonctions_bdd.select_bdd_table_champ_simple(*************jesaispas*********,name_bdd,'concept2billets','id_b', ' where concept in '+ str(query_ids).replace('[','(').replace(']',')'))
		sous_corpus_idb=[]
		for x in sous_corpus_idb_vect:
			if not x[0] in sous_corpus_idb:
				sous_corpus_idb.append(x[0])
	except:
		#tous les termes de la query n'ont pas encore été indexés, on passe à une méthode like.
		where_like = " where content_lemmatise like '%"
		where_like = where_like + "%' or  content_lemmatise like '%".join(specific_nlemmes) + "%'"
		print where_like
		sous_corpus_idb = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'billets','id',where_like )

	print str(len(sous_corpus_idb)) +' documents retrieved \n'
	sql_where = " id in " + str(sous_corpus_idb).replace('[','(').replace(']',')')
	#print sql_where


	print 'creation de la nouvelle base de données ' + name_bdd_new
	shutil.copy(name_bdd, name_bdd_temp)
	try:
		fonctions_bdd.detruire_table(name_bdd,'billets2')
	except:
		pass
	try:
		fonctions_bdd.add_column(name_bdd,'billets','concepts_id','text')#et lui adjoindre le champ concepts_id
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
	return specific_nlemmes

def fast_ngram_counter(name_bdd,concept_list=''):	
	Nb_rows = fonctions_bdd.count_rows(name_bdd,'billets')
	size_seq = 200
	nb_sequences = Nb_rows/size_seq
	dictionnaire_gramme = {}#initialisation du dictionnaire de lemmes
	billetprocessed_after_requete=0 #counts the number of processed posts
	for x in range(nb_sequences+1):
		
		dictionnaire_gramme_x={}
		lim_d = str(size_seq*x)
		if x<nb_sequences:
			duration = str(size_seq)
		else:
			duration = str(min(Nb_rows - size_seq*x,sample))
		where=1
		contenu = fonctions_bdd.select_bdd_table_where_limite(name_bdd,'billets','content_lemmatise',sample,requete,where,lim_d+','+duration,Nb_rows)
		for billetlemm in contenu:
			billetprocessed_after_requete=1+billetprocessed_after_requete
			if not billetprocessed_after_requete%500 or billetprocessed_after_requete == len(contenu) : 
				print '---------'+str(billetprocessed_after_requete)+ ' traités (export ngrammes sur '+str(Nb_rows)+ ' billets)'
			billet_lemmatise =  billetlemm[0]
			if concept_list=='':
				dictionnaire_gramme_x = text_processing.ngramme_build(billet_lemmatise.split(),maxTermLength,dictionnaire_gramme_x,language,'billet')
			else:
				dictionnaire_gramme_x = text_processing.ngramme_find(billet_lemmatise,dictionnaire_gramme_x,concept_list)
		dictionnaire_gramme=fonctions_lib.merge(dictionnaire_gramme, dictionnaire_gramme_x, lambda x,y:x+y)
	if concept_list=='':
		dictionnaire_gramme = misc.freq_tri(dictionnaire_gramme,freqmin,int(math.floor(top*1.1)),language,ng_filter)#on effectue le tri de notre dictionnaire
	return dictionnaire_gramme

def trier_dictionnaire(dico):
	l = dico.items()
	l.sort(key=itemgetter(1),reverse=False)
	return l

def out_doc(dico_new,dico):
	ratio={}
	for x,y in dico_new.iteritems():
		norm = dico[x]
		ratio[x] = norm-y
	return ratio

def add_query(query,x):
	if x not in query:
		query.append(x)
		print x + ' added to the query '
	return query

def query_exander(query):
	encore=1
	while encore==1:
		dico_new=0
		dico=0
		#construit la base name_bdd_new en fonction de la query
		id_new_list = fonctions_bdd.select_bdd_table_champ_simple(name_bdd_new,'billets','id')
		id_new=[]
		for x in  id_new_list:
			id_new.append(x[0])
		dico_new = fast_ngram_counter(name_bdd_new,'')
		print len(dico_new.keys())
		dico= fast_ngram_counter(name_bdd,dico_new.keys())
		print len(dico.keys())
		ratio= out_doc(dico_new,dico)
		ratio_l = trier_dictionnaire(ratio)
		steps=100000
		nb_question=0
		champs_name = "(id,title,date,permalink,site,categorie1,categorie2,categorie3,content,content_lemmatise,href,requete,identifiant_unique)"#on n'enregistre pas le html brut
		for x in ratio_l:
			if nb_question<steps:
				val = x[1]
				if val>0:
					info ='\n'

					nouveaux_billets = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'billets',champs_name[1:-1],"where content_lemmatise like '%" + x[0]  +"%'")
					
					for billets in nouveaux_billets[:9]:
						if not billets[0] in id_new:
							info=info +  '*** '+ billets[1] + '(' + billets[4]  + ')' + '\n'
					print info
					print dico_new[x[0]]
					print dico[x[0]]

					var = raw_input('Do you wish to add "' + x[0] + '" ('+str(x[1])+ ') '+' to the query ?')
					if var=='y':
						query =  add_query(query,x[0])
						fonctions_bdd.remplir_table(name_bdd_new,'billets',nouveaux_billets,champs_name)
						nb_question=nb_question+1
					if var=='s':
						steps=0
			else:
				pass
		print 'query finale'
		print query
		var = raw_input('Do you wish to perform a new indexation of the database based on the new query ?')
		if var == 'n':
			encore=0
	return query

query = select_query()
print query_exander(query)
			
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