#!/usr/bin/python
# -*- coding: utf-8 -*-

print "db_processing_rel v0.2 (ccr) (20091102)"
print "---------------------------------------\n"
print "calcul des tables relationnelles après indexation"
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
#on alimente ensuite la table socsem liant les index des acteurs aux index des concepts ainsi qu'au jour du lien







def aggreger_periode(liensem):
	#lienssem.append([con1,con2,jours,b_id,requete,str(b_id)+'_' + str(con1) + '_' + str(con2)])
	#fonctions_bdd.remplir_table(name_bdd,'sem_weighted',lienssem_weighted,"(concept1,concept2,periode,cooccurrences,requete,identifiant_unique)")
	years_bins=parameters.years_bins
	lienssem_weighted_dict={}
	lienssem_weighted=[]
	requete=''
	for ligne in lienssem:
		con1 =ligne[0]
		con2 =ligne[1]
		j =ligne[2]
		requete=ligne[4]
		
		for periode,years in enumerate(years_bins):
			#uniq = con1+'_'+con2+'_'+str(periode)
			if int(j) in years:
				lienssem_weighted_dict[(con1,con2,str(periode))]=lienssem_weighted_dict.get((con1,con2,str(periode)),0)+1
	for cle,valeurs in lienssem_weighted_dict.iteritems():
		cooc = list(cle)
		if valeurs>=parameters.seuil_cooccurrences:
			cooc.append(str(valeurs))
		#cooc.append(requete)
		#cooc.append('_'.join(list(map(str,cle))))
			lienssem_weighted.append(cooc)
	return lienssem_weighted


print "    + creation des tables relationnelles socsem, sem, soc..."
recreer_table_nets=1
if recreer_table_nets ==1:
	try: fonctions_bdd.detruire_table(name_bdd,'socsem')
	except: pass
	try: 
	#	fonctions_bdd.detruire_table(name_bdd,'sem')
		fonctions_bdd.detruire_table(name_bdd,'sem_weighted')
	except: pass
	fonctions_bdd.creer_table_sociosem(name_bdd,'socsem')
	#fonctions_bdd.creer_table_sem(name_bdd,'sem')
	fonctions_bdd.creer_table_sem_periode_valuee(name_bdd,'sem_weighted')


# on construit les reseaux sociosemantique et semantique a partir de la liste des ngrammes associes a chaque index de billet

def decoupe_segment(taille_total,taille_segment):
	decoupe = (taille_total/taille_segment)
	vec=[]
	for x in range(decoupe):
		vac = []
		for j in range(taille_segment):
			vac.append(j+x*taille_segment)
		vec.append(vac)
	vac= []
	for j in range(taille_total-decoupe*taille_segment):
		vac.append(j+decoupe*taille_segment)
	if len(vac)>0:
		vec.append(vac)
	return vec


contenu = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'billets','id,concepts_id')
billets_id=[]
ngrammes_fit_index=[]
for con in contenu:
	billets_id.append(con[0])
	ngrammes_fit_index.append(con[1].replace('[','').replace(']','').split(', '))

ll = len(billets_id)
vecteurs=decoupe_segment(ll,10000)
lienssem=[]
for x in vecteurs:
	print 'on traite les billets: ' + str(x[0])+ ' a ' + str(x[-1]) +' (sur ' + str(ll) +' billets)'
	lienssocsem,lienssem_x = misc.build_semantic_nets(billets_id[x[0]:x[-1]],ngrammes_fit_index[x[0]:x[-1]],name_bdd,requete,sep)
	lienssem = lienssem+lienssem_x
	##on remplit la table socsem
	fonctions_bdd.remplir_table(name_bdd,'socsem',lienssocsem,"(auteur,concept,jours,id_b,requete,identifiant_unique)")
	# ##on remplit la table sem
	#fonctions_bdd.remplir_table(name_bdd,'sem',lienssem,"(concept1,concept2,jours,id_b,requete,identifiant_unique)")
	#ex('CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,concept1 INTEGER,concept2 INTEGER,periode INTEGER,cooccurrences INTEGER,distance float,requete VARCHAR(200),identifiant_unique VARCHAR(20) unique)')


print 'on remplit maintenant la table sem_weighted'

lienssem_weighted=aggreger_periode(lienssem)
fonctions_bdd.remplir_table(name_bdd,'sem_weighted',lienssem_weighted,"(concept1,concept2,periode,cooccurrences)")
	
print "\n--- finished inserting data in tables socsem & sem."


###################################
####construction des liens#########
###################################

#on alimente enfin la table soc liant les index des acteurs entre eux ainsi qu'au jour du lien
try: 
	fonctions_bdd.detruire_table(name_bdd,'soc')
except: 
	pass
fonctions_bdd.creer_table_soc(name_bdd,'soc')
lienssoc = misc.build_social_net(requete,name_bdd,sep,name_data)
fonctions_bdd.remplir_table(name_bdd,'soc',lienssoc,"(auteur1,auteur2,jours,id_b,requete,identifiant_unique)")
print "\n--- finished inserting data in table soc."



