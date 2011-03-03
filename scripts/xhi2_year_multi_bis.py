#!/Library/Frameworks/Python.framework/Versions/2.6/bin/python
# -*- coding: utf-8 -*-
#recupere les liens des trois reseaux pour exporter les reseaux au format texte
import sys
import math
from copy import deepcopy
sys.path.append("/libraries")
sys.path.append("../map_builder")
from operator import itemgetter
import fusion_years
import multiprocessing
print "export_networks v0.2 (20091102)"
print "--------------------------------\n"

import parameters
import fonctions_bdd
import fonctions_lib
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
freqmin = parameters.freqmin
from operator import itemgetter

###################################
#######0.quelques parametres#######
###################################

maxTermLength = parameters.maxTermLength
name_bdd = parameters.name_bdd
freqmin = parameters.freqmin
name_data = parameters.name_data 
requete = parameters.requete
name_data_real = parameters.name_data_real
path_req = parameters.path_req
#treetagger_dir =parameters.treetagger_dir
years_bins = parameters.years_bins
dist_type=parameters.dist_type
dated=parameters.dated
datef=parameters.datef


###################################
#######code #######################
###################################


def print_extrait_dico(dico_termes,dico_lemmes):
	print "extrait du dictionnaire : " 
	try:
		ii = 0
		while ii < 10:
			ii = ii+1
			print '- ' +dico_termes[ii] +' ('+dico_lemmes[ii]+')' 
	except:
		pass
	print "\n"

def build_dico():
	concepts_triplets = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'concepts','id,concepts,forme_principale')
	dico_termes,dico_lemmes ={},{}
	for triplets in concepts_triplets:
		dico_termes[triplets[0]] = triplets[2]
		dico_lemmes[triplets[0]] = triplets[1]
	print 'dictionnaire des termes écrit, taille: '+str(len(dico_termes))
	print_extrait_dico(dico_termes,dico_lemmes)
	return dico_termes,dico_lemmes	
	
def	check_unique(concepts_ids_list):
	deja = []
	for con in concepts_ids_list:
		if con in deja: 
			print 'alerte'
		else:
			deja.append(con)
		


def convert_clique_txt_2_list(clique_txt):
	if not str(clique_txt)=='None' and not len(str(clique_txt))<3:
		clique = clique_txt[1:-1].split(', ')
		return map(int,clique)
	else:
		return []

def build_cooc(contenu):
	nb_cooc=0
	cooccurrences,cooccurrences_somme,occurrences={},{},{}
	compt=0
	for cont in contenu:
		clique = convert_clique_txt_2_list(cont[0])
		for x in clique:
			occurrences[x] = occurrences.get(x,0) + 1
		if len(clique)>1:
			for idx, terme1 in enumerate(clique[:-1]):
				for terme2 in clique[idx+1:]:
					cooccurrences[(terme1,terme2)] = cooccurrences.get((terme1,terme2),0) + 1
					cooccurrences[(terme2,terme1)] = cooccurrences.get((terme2,terme1),0) + 1
					cooccurrences_somme[terme1] =  cooccurrences_somme.get(terme1,0) + 1
					cooccurrences_somme[terme2] =  cooccurrences_somme.get(terme2,0) + 1		
					nb_cooc = nb_cooc + 2
	return cooccurrences,nb_cooc,cooccurrences_somme,occurrences




#muti[(terme1,terme2,intervalle)]=MI(t1,t2,t)
def build_mutual_information(cooccurrences,cooccurrences_somme,nb_cooc,occurrences,version="andrei"):
	muti={}
	#rajouter contrainte sur positivité de l'écart (pas besoin de calculer le théorique.)
	#sur la version actuelle rajouter, pi = sum_j pij 
	if version=='chinois':
		#norm = float(sum(top_concepts_dict.values()))
		#print 'norm:' + str(norm)
		for x,freq1 in cooccurrences_somme.iteritems():
			terme1=x[0]
			inter =x[1]
			for x2,freq2 in cooccurrences_somme.iteritems():
				terme2 = x2
				if terme2 != terme1:
 					#expected = nb_cooc[inter] *  cooccurrences_somme[(terme1,inter)]*cooccurrences_somme[(terme2,inter)]
					expected =   freq1*freq2 / nb_cooc
					xhi2 = (cooccurrences.get((terme1,terme2),0.) - expected)**2 / expected
					muti[x] = xhi2
	if version=='andrei': 
		for x,cooc in cooccurrences.iteritems():
			terme1=x[0]
			terme2=x[1]
			if terme2 != terme1:
 					expected = float(cooccurrences_somme[terme1]) * (float(cooccurrences_somme[terme2]) / float(nb_cooc))
					if cooc>expected:
						xhi2 = (cooc - expected)**2 / expected
						muti[terme1] = muti.get(terme1,0.) + xhi2
	return muti



def export_concepts_xhi2 (xhi2val,cooccurrences,cooccurrences_somme,dico_termes,dico_lemmes,year,occurrences):
	try:
		os.mkdir(path_req +'years')
	except:
		pass
	conceptxhi2 = open(path_req +'years/'+ requete +str(year) + '_'  + 'conceptsxhi2.csv','w')
	inter=years.index(year)
	for x in dico_termes:
		try:
			conceptxhi2.write(dico_lemmes[x] + '\t' + dico_termes[x] + '\t' +str(cooccurrences_somme[(x)]).replace('.',',')+  '\t' + str(xhi2val[x]).replace('.',',')+ '\t' +  '\n' )
		except:
			conceptxhi2.write(dico_lemmes[x] + '\t' + dico_termes[x] + '\t' + '\t' + '\t' +  '\t' + '\n' )
		
dico_termes,dico_lemmes=build_dico()
years=parameters.years_bins_no_overlap

def xhi2_comp(year):
	print "periode " + str(year)
	where = " jours IN ('" + "','".join(list(map(str,year))) + "') "
	contenu = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'billets','concepts_id,jours,id',where)
	print "content imported: " + str(len(contenu)) + " notices \n"
	cooccurrences,nb_cooc,cooccurrences_somme,occurrences = build_cooc(contenu)
	print str(nb_cooc) + ' total cooccurrences computed'
	print str(sum(occurrences.values())) + ' total occurrences computed'
	
	xhi2val = build_mutual_information(cooccurrences,cooccurrences_somme,nb_cooc,occurrences)
	export_concepts_xhi2(xhi2val,cooccurrences,cooccurrences_somme,dico_termes,dico_lemmes,year,occurrences)
	
 	
pool_size = int(multiprocessing.cpu_count())
pool = multiprocessing.Pool(processes=pool_size)
print years
pool.map(xhi2_comp, years)
# for year in years:
# 	xhi2_comp(year)
fusion_years.fusion('conceptsxhi2')