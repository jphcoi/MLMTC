#!/Library/Frameworks/Python.framework/Versions/2.6/bin/python
# -*- coding: utf-8 -*-

print "db_processing_net v0.2 (ccr) (20091102)"
print "---------------------------------------\n"

import parameters

import fonctions_bdd
import parseur
import os
import glob
import sys
import codecs
import unicodedata
import text_processing 
import misc 
from datetime import timedelta
from datetime import date
import parameters
import fonctions_lib
import fusion_years
import multiprocessing
###################################
#######0.quelques parametres#######
###################################

maxTermLength = parameters.maxTermLength
name_bdd = parameters.name_bdd
freqmin = parameters.freqmin
name_data = parameters.name_data 
requete = parameters.requete
user_interface=parameters.user_interface
name_data_real = parameters.name_data_real
#lemmadictionnary = parameters.lemmadictionary# si nul, on  calcule ou recalcule  le dico de lemmes sur la requete consideree sinon on ne calcule pas
path_req = parameters.path_req
sep = parameters.sep
build_link_tables=parameters.build_link_tables
language = parameters.language
###################################
#######3.Indexer les billets#######
###################################

#on crée la table concepts
#marche une fois sur deux, zarbo, peut-etre unique?...
try: 
	fonctions_bdd.detruire_table(name_bdd,'concepts')
	print "on detruit la table concept"
except: 
	print "pas de tabe  concept"

print "    + creation de la table \"concepts\" (qui fait office de dictionnaire)..."
fonctions_bdd.creer_table_concepts(name_bdd,'concepts')

# on indexe a partir de la liste des ngrammes tries

filename = path_req + requete + '_' + str(freqmin) + '_' + 'liste_n-grammes_freq_comparatif'  +'_trie' + '.csv' #fichier d'entree trie (rajouter _trie a la fin de la sortie standard)
#print filename
if os.path.isfile(filename) == 1:
	print '--- on indexe a partir du fichier \"' + filename+"\""
else:
	filename = path_req + 'concepts.csv' #fichier d'entree trie (rajouter _trie a la fin de la sortie standard)
	if not os.path.isfile(filename) == 1:
		filename_leven_redond =  path_req + requete + '_' + str(freqmin) + '_' + 'liste_n-grammes_freq_divers_leven_noredond.csv'
		filename = filename_leven_redond
		
		
print '--- on indexe a partir du fichier \"' + filename+"\""
#on lit le fichier des n-grammes a indexer
ngrammes = misc.lire_dico_classes(filename,language)
#pour plus de sûreté
ngrammes = misc.lire_dico_classes(filename,language)
#pour plus de sûreté
ngrammes = misc.lire_dico_classes(filename,language)


#affichage de la liste des 10 premiers concepts
print "--- les 10 premiers concepts (sur " +str(len(ngrammes))+") : "
for gra in ngrammes[:10]:
	try:
		print "    ",str([gra])
	except:
		print "encodage error"

if len(ngrammes)>1000:
	print "vous avez "+str(len(ngrammes)) + ' concepts, au-delà de 2000 concepts, le script peut devenir tres long'
	if user_interface =='y':
		var = raw_input('reduire la liste avant de lancer l\'indexation ? (y pour arreter, tout autre touche pour continuer)')
	else:
		var = 'n'
	if var=='y':
		exit()
###################################
#####indexation des billets########
###################################

def extension(x,y):
	x.extend(y)
	return list(set(x))
	
#il faut découper ici car ça prend trop de RAM


#decoupage annuel:
#on recupere d'abord toutes les années en base
years=parameters.years_bins_no_overlap

#puis on itere sur chaque tranche:
ngrammes_auteurs_fit_year={}
ngramme_billets_fit_year={}
formes_fit_year={}
formes=  {}
#for y,year in enumerate(years):
def ngramme_fit(year):
	Nb_rows = fonctions_bdd.count_rows_where(name_bdd,'billets'," where jours IN ('" + "','".join(list(map(str,year))) + "') ")
	#Nb_rows = fonctions_bdd.count_rows(name_bdd,'billets')
	Nb_auteurs = fonctions_bdd.count_rows(name_bdd,'auteurs')
	size_seq = 1000
	nb_sequences = Nb_rows/size_seq
	billets_id=[]
	ngramme_billets_fit=[]
	ngrammes_auteurs_fit={}
	formes_fit={}
	#for x in range(nb_sequences+1):
	for x in range(nb_sequences+1):
		lim_d = str(size_seq*x)
		if x<nb_sequences:
			duration = str(size_seq)
		else:
			duration = str(size_seq)
		where = " jours IN ('" + "','".join(list(map(str,year))) + "') "
		sample = '1000000000'
		contenu = fonctions_bdd.select_bdd_table_where_limite(name_bdd,'billets','id,content_lemmatise,content,auteur_id',sample,requete,where,lim_d+','+duration,Nb_rows)
		#on indexe chaque billet et on recupere un triplet qui donne: la liste des ngrammes pour chaque billet, la liste des index des ngrammes pour chaque billet, et l'id des billets - ce script permet egalement de calculer les formes des n-lemmes.
		include=1 #le parametre include permet d'activer ou non l'overlap de lemmes dans le comptage: si 1, les nicolas sarkozy ne forment pas de sarkozy 
		ngramme_billets_fit_x,billets_id_x,formes_x,ngrammes_auteurs_fit_x = text_processing.indexer_billet(contenu,ngrammes,maxTermLength,include)
		billets_id = billets_id + billets_id_x
		ngramme_billets_fit = ngramme_billets_fit + ngramme_billets_fit_x
		formes_fit=fonctions_lib.merge(formes_fit, formes_x, lambda x,y: fonctions_lib.merge(x,y,lambda x,y:x+y))
		ngrammes_auteurs_fit=fonctions_lib.merge(ngrammes_auteurs_fit,ngrammes_auteurs_fit_x,lambda x,y : extension(x,y))
		print "    + billets numéros "+ str(int(lim_d)+1)+ " à "+  str(int(lim_d)+int(duration)) +" indexés (sur "+ str(Nb_rows) +")"
	return ngrammes_auteurs_fit, ngramme_billets_fit,formes_fit
	
	
pool_size = int(multiprocessing.cpu_count() / 2 * 3)
pool = multiprocessing.Pool(processes=pool_size)
pool_outputs = pool.map(ngramme_fit, years)
for y,x in enumerate(pool_outputs):		
	ngrammes_auteurs_fit_year[y]=x[0]
	ngramme_billets_fit_year[y]=x[1]
	formes_fit_year[y]=x[2]

	
formes={}
for formes_x in formes_fit_year.values():
	formes=fonctions_lib.merge(formes, formes_x, lambda x,y: fonctions_lib.merge(x,y,lambda x,y:x+y))
dictionnaire_treetagged__formes_name = path_req  + "Treetagger_n-lemmes_formes.txt"  
dictionnaire_treetagged__formemajoritaire_name = path_req  + "Treetagger_n-lemmes_formemajoritaire.txt"
text_processing.extraire_forme_majoritaire(0,formes,dictionnaire_treetagged__formes_name,dictionnaire_treetagged__formemajoritaire_name)

#N  = float(len(ngramme_billets_fit))
#print "    +" + str(N) + " billets indexés"


## on alimente la table concepts avec la liste des concepts trie et leur forme principale
file_concepts=codecs.open(dictionnaire_treetagged__formemajoritaire_name,'r','utf-8')
liste_concepts=[]
correspondance_lemme_forme={}
for ligne in file_concepts.readlines():
	lignev = ligne.split('\t')
	liste_concepts.append((lignev[0].encode('utf-8','replace'),lignev[1].encode('utf-8','replace')))
	correspondance_lemme_forme[lignev[0].encode('utf-8','replace')]=lignev[1].encode('utf-8','replace')
print "&&&",len(liste_concepts),"concepts now."
##si necessaire on recree la table concepts


#on remplit la table concept
#print liste_concepts
fonctions_bdd.remplir_table(name_bdd,'concepts',liste_concepts,"(concepts,forme_principale)")



contenu = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'concepts','id,concepts')
liste_concepts_dico={}
for con in contenu:
	liste_concepts_dico[con[1]]=con[0]

def freq_comp(year):
	y=years.index(year)
#for y,year in enumerate(years):
	#on construit la liste des index des concepts dans l'ordre 
	ngrammes_fit_index=[]
	Nb_auteurs = fonctions_bdd.count_rows(name_bdd,'auteurs')

	ngramme_billets_fit =ngramme_billets_fit_year[y]
	ngrammes_auteurs_fit=ngrammes_auteurs_fit_year[y]
	#on calcule nos stats à l'échelle des auteurs aussi, freq = nombre de blogs parlant d'un terme 
	dictionnaire_frequence_exact_auteur={}
	dictionnaire_frequence_exact={}
	N = fonctions_bdd.count_rows_where(name_bdd,'billets'," where jours IN ('" + "','".join(list(map(str,year))) + "') ")
	for terme in liste_concepts:
		dictionnaire_frequence_exact[terme[0]]=0
		dictionnaire_frequence_exact_auteur[terme[0]]=0
	
	for clique in ngramme_billets_fit:
		clique_index=[]
		for terme in set(clique):
			clique_index.append(liste_concepts_dico[terme])
			dictionnaire_frequence_exact[terme]=dictionnaire_frequence_exact[terme]+1
		ngrammes_fit_index.append(clique_index)
	print "    + liste des index des concepts creee"


	for aut,clique in ngrammes_auteurs_fit.iteritems():
		for terme in set(clique):
			dictionnaire_frequence_exact_auteur[terme]=dictionnaire_frequence_exact_auteur[terme]+1
	print "    + liste des index des concepts creee"

	file_freq_exact =  path_req +'years/'+ requete +str(year) + '_'  +  'frequences_exactes.csv'
	fichier_out =file(file_freq_exact,'w')
	def format(value):
	    return "%.9f" % value

	for x in dictionnaire_frequence_exact:	
	#	print str(x) + '\t' + str(correspondance_lemme_forme[x]) +'\t' + (str(format(float(dictionnaire_frequence_exact[x])/N))).replace('.',',') +'\t' + (str(format(float(dictionnaire_frequence_exact_auteur[x])/float(Nb_auteurs)))).replace('.',',')+  '\n'
		fichier_out.write(str(x) + '\t' + str(correspondance_lemme_forme[x]) +'\t' + (str(format(float(dictionnaire_frequence_exact[x])/N))).replace('.',',') +'\t' + (str(format(float(dictionnaire_frequence_exact_auteur[x])/float(Nb_auteurs)))).replace('.',',')+  '\n')
	print "    + frequences exactes calculees   "+ file_freq_exact

try: 
	os.mkdir(path_req +'years/')
except:
	pass

pool_size = int(multiprocessing.cpu_count() / 2 * 3)
pool = multiprocessing.Pool(processes=pool_size)
pool.map(freq_comp, years)

	
fusion_years.fusion('freq')