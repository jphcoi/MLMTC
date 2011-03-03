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
seuil=0.2
###################################
#######export #####################
###################################


def distribution_distance_build(p_cooccurrences,dico_termes,p_cooccurrences_lignes):
	epsilon = 0.0
	distribution_distance={}
	N = len(dico_termes.keys())
	Ncoocc = {}
	for x,t in p_cooccurrences_lignes.iteritems():
		Ncoocc[x]=sum(t.values())
	compt=0
	waiting_time= N
	for x in range(N):
		compt+=1
		if not compt%10:
			print '       (#'+str(compt)+' sur '+str(waiting_time)+")"		
		x=x+1
		for y in range(N):
			y=y+1
			if y>x:
				dist_xy = 0.
				occ_y = 0.
				occ_x =0.
				try:
					dic_ligne_x = p_cooccurrences_lignes[x]
					dic_ligne_y = p_cooccurrences_lignes[y]
					distribution_distance[(x,y)]  =  sum(fonctions_lib.merge_prod(dic_ligne_x, dic_ligne_y , lambda x,y:math.sqrt(float(x*y))).values()) / math.sqrt(float(Ncoocc[x])*float(Ncoocc[y]))
				except:
					pass
	return distribution_distance

def build_dico():
	lesidstermes = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'concepts','id')
	leslemmestermes = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'concepts','concepts')
	lestermes = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'concepts','forme_principale')
	dico_termes ={}
	dico_lemmes ={}
	for x,y,z in zip(lesidstermes,lestermes,leslemmestermes):
		dico_termes[x[0]]=y[0]
		dico_lemmes[x[0]]=z[0]
	print 'dictionnaire des termes écrit, taille: '+str(len(dico_termes))
	return dico_termes,dico_lemmes	
	




def init_dictionnary_list(taille,val):
	dico={}
	for x in range(taille):
		dico[x]=val
	return dico

def	check_unique(concepts_ids_list):
	deja = []
	for con in concepts_ids_list:
		if con in deja: 
			print 'alerte'
		else:
			deja.append(con)
		

def build_nbbillet(contenu,years_bin):
	#contenu = liste de [concepts_id,jours,id_billet]
	nb_billets,occurrences={},{}
	for cont in contenu:
		jour = cont[1]
		concepts_ids = cont[0]
		for inter, val in enumerate(years):
			if jour in val:
				concepts_ids_list = convert_clique_txt_2_list(concepts_ids)
				n_cl =  len(concepts_ids_list)
				#nb_billets[inter]=nb_billets[inter]+1
				nb_billets[inter]=nb_billets.get(inter,0)+n_cl*(n_cl-1)/2
				check_unique(concepts_ids_list)
				for concept in concepts_ids_list:
					temp = occurrences.get(inter,{})
					temp[concept] = temp.get(concept,0) + 1
					occurrences[inter]=temp
	return nb_billets,occurrences


def convert_clique_txt_2_list(clique_txt):
	if not str(clique_txt)=='None' and not len(str(clique_txt))<3:
		clique = clique_txt[1:-1].split(', ')
		return map(int,clique)
	else:
		return []

def build_voisins(contenu,years_bin,occurrences,top=20000):
	
	inter=years.index(years_bin)
	occurrences_sorted = sorted(occurrences[inter].iteritems(), key=itemgetter(1))
	occurrences_sorted_top = occurrences_sorted[-min(len(occurrences_sorted),top):]
	top_concepts_dic = dict(occurrences_sorted_top)
	top_concepts=top_concepts_dic.keys()

	#now: 		contenu = liste de [concepts_id,jours,id_billet]
	voisins={}
	#voisins[terme,intervalle] = array(termes co-présents)
	for cont in contenu:
		clique = convert_clique_txt_2_list(cont[0])
		for idx, con_1 in enumerate(clique):
			for con_2 in clique[idx:]:						
				if not con_1==con_2 and con_2 in top_concepts:
					temp = voisins.get((con_1,inter),[])
					temp.append(con_2)
					voisins[(con_1,inter)]=temp
				if not con_1==con_2 and con_1 in top_concepts:
					temp = voisins.get((con_2,inter),[])
					temp.append(con_1)
					voisins[(con_2,inter)]=temp
				#else:
				#	temp = voisins[(con_2,inter)]
				#	temp.append(con_1)
				#	voisins[(con_1,inter)]=temp
	return voisins,top_concepts_dic 

def unique(liste):
	liste_u=[]
	for x in liste:
		if not x in liste_u:
			liste_u.append(x)
	return liste_u
	

#marche pas.
def build_cooc(voisins,nb_billets,inter):
	p_cooccurrences={}
	p_cooccurences_lignes={}
	p_cooccurrences_ordre1={}
	#p_cooccurrences[terme1,terme2,intervalle] = proba du terme
	#print occurrences[inter]
	waiting_time = len(voisins)
	compt=0
	for x,y in voisins.iteritems():
		compt+=1
		if not compt%100:
			print '       (#'+str(compt)+' sur '+str(waiting_time)+")"		
		terme1 = x[0]
		N = nb_billets[inter]
		dict_temp={}
		for terme2 in y:
			if terme1!=terme2:
				dict_temp[terme2] = dict_temp.get(terme2,0)  + 0.5
		p_cooccurences_lignes[terme1] = dict_temp
		for terme2 in dict_temp:
			p_cooccurrences[(terme1,terme2,inter)] = float(dict_temp[terme2]) / N
	for x,y in p_cooccurrences.iteritems():
		terme1 = x[0]
		inter= x[2]
		p_cooccurrences_ordre1[(terme1,inter)] = p_cooccurrences_ordre1.get((terme1,inter),0.) + y
	
	#print p_cooccurrences
	print '\n'
	
	print 'matrice temporelle de cooccurrence ecrite'
	print '\n'
	
	return p_cooccurrences,p_cooccurences_lignes,p_cooccurrences_ordre1








def build_cooc_matrix(contenu, years_bin):
	inter=years.index(years_bin)
	nb_billets,occurrences = build_nbbillet(contenu,years_bin)
	print "        - "+str(nb_billets[inter])+" cooccurrences"
	print '\n'
	
	voisins,top_concepts_dict = build_voisins(contenu,years_bin,occurrences)
	print "variable voisins construite"
	print '\n'
	
	p_cooccurrences,p_cooccurrences_lignes,p_cooccurrences_ordre1=build_cooc(voisins,nb_billets,inter)
	return p_cooccurrences,nb_billets,p_cooccurrences_lignes,p_cooccurrences_ordre1,occurrences,top_concepts_dict
	
	
#muti[(terme1,terme2,intervalle)]=MI(t1,t2,t)
def build_mutual_information(p_cooccurrences,p_cooccurrences_ordre1,nb_billets,occurrences,top_concepts_dict,version="andrei"):
	muti={}
	#rajouter contrainte sur positivité de l'écart (pas besoin de calculer le théorique.)
	#sur la version actuelle rajouter, pi = sum_j pij 
	if version=='chinois':
		norm = float(sum(top_concepts_dict.values()))
		print 'norm:' + str(norm)
		for x in p_cooccurrences_ordre1:
			terme1=x[0]
			inter =x[1]
			for x2,freq2 in top_concepts_dict.iteritems():
				terme2 = x2
				if terme2 != terme1:
 				
					#expected = nb_billets[inter] *  p_cooccurrences_ordre1[(terme1,inter)]*p_cooccurrences_ordre1[(terme2,inter)]
					expected = nb_billets[inter] *  p_cooccurrences_ordre1[(terme1,inter)]*freq2/norm
					xhi2 = (nb_billets[inter]*p_cooccurrences.get((terme1,terme2,inter),0.) - expected)**2 / expected
					#if xhi2>25000:
					#	print dico_termes[terme1],'\t',dico_termes[terme2],'\t',xhi2
					muti[x] = xhi2
	if version=='andrei': 
		norm=0.
		for x in p_cooccurrences_ordre1.values():
			norm += x
		print 'norm:' + str(norm)
		for x,cooc in p_cooccurrences.iteritems():
			terme1=x[0]
			terme2=x[1]
			inter =x[2]
			if terme2 != terme1:
 					expected = p_cooccurrences_ordre1[(terme1,inter)] * p_cooccurrences_ordre1[(terme2,inter)] / norm
					#expected = nb_billets[inter] *  p_cooccurrences_ordre1[(terme1,inter)]*p_cooccurrences_ordre1[(terme2,inter)]
					#expected = nb_billets[inter] *  p_cooccurrences_ordre1[(terme1,inter)]*freq2/norm
					xhi2 = (cooc - expected)**2 / expected
					#if xhi2>25000:
					#	print dico_termes[terme1],'\t',dico_termes[terme2],'\t',xhi2
					muti[x] = xhi2
	return muti

def lire_dist_mat_file(fichier_CF):
	dist_mat_temp={}
	file=open(fichier_CF,'r')
	for line in file.readlines():
		linev = line.split('\t')
		dist_mat_temp[(linev[0],linev[1])]=linev[2][:-1]
	return dist_mat_temp

def dedoubler(dico_termes,years):
	dico_termes_temp={}
	for inter in range(len(years)):
		for x,y in dico_termes.iteritems():
			dico_termes_temp[(inter,x)]=y
	return dico_termes_temp

def compare_dictionnaire(dist_mat_temp_old,dist_mat_temp):
		commun = 0
		total_old = len(dist_mat_temp_old)
		total_new = len(dist_mat_temp)
		for x in dist_mat_temp_old:
			if x in dist_mat_temp:
				commun += 1
		return commun, total_old, total_new
		

def xhi2(muti):
	xhi2val={}
	for x,y in muti.iteritems():
		xhi2val[x[0]]=xhi2val.get(x[0],0.)+y
	return xhi2val
			


def weirdrep(chaine):
	return chaine.replace('``','?').replace('"','?')

def export_concepts_xhi2 (xhi2val,p_cooccurrences,p_cooccurrences_ordre1,dico_termes,dico_lemmes,year,occurrences):
	conceptxhi2 = open(path_req +'years/'+ requete +str(year) + '_'  + 'conceptsxhi2.csv','w')
	inter=years.index(year)
	for x in dico_termes:
		try:
			#conceptxhi2.write(dico_lemmes[x] + '\t' + dico_termes[x] + '\t' + str(p_cooccurrences[(x,x,0)]).replace('.',',') + '\t' + str(xhi2val[x]).replace('.',',')+ '\t' + str(xhi2val[x]*p_cooccurrences[(x,x,0)]).replace('.',',') + '\n' )
			conceptxhi2.write(weirdrep(dico_lemmes[x]) + '\t' + weirdrep(dico_termes[x]) + '\t' +str(p_cooccurrences_ordre1[(x,inter)]).replace('.',',')+  '\t' + str(xhi2val[x]).replace('.',',')+ '\t' +  '\n' )
			#print dico_lemmes[x] + '\t' + dico_termes[x] + '\t' +str(occurrences[inter][x]).replace('.',',')+  '\t' + str(xhi2val[x]).replace('.',',')+ '\t' +  '\n'
		except:
			print dico_termes[x]
			try:
				print 'occ:'+str(occurrences[inter][x]).replace('.',',')
			except:
				pass
			try:
				print 'xhi2:' + str(xhi2val[x]).replace('.',',')
			except:
				pass
				
			#conceptxhi2.write(dico_lemmes[x] + '\t' + dico_termes[x] + '\t' + '\t' + '\t' +  '\t'+ '\t' + '\t' + '\n' )
			conceptxhi2.write(weirdrep(dico_lemmes[x]) + '\t' + weirdrep(dico_termes[x]) + '\t' + '\t' + '\t' +  '\t' + '\n' )
		
print '\n'		
dico_termes,dico_lemmes=build_dico()
print "extrait du dictionnaire : " 
try:
	ii = 0
	while ii < 10:
		ii = ii+1
		print '- ' +dico_termes[ii] +' ('+dico_lemmes[ii]+')'
except:
	pass
print '\n'



years=parameters.years_bins_no_overlap

def xhi2_comp(year):
	print year
#	contenu = fonctions_bdd.select_bdd_table(name_bdd,'billets','concepts_id,jours,id',requete)
	where = " jours IN ('" + "','".join(list(map(str,year))) + "') "
	print where
	contenu = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'billets','concepts_id,jours,id',where)
	
	print "contenu importé"
	print '\n'
	from time import time
	timeavt = time()
	p_cooccurrences,nb_billets,p_cooccurrences_lignes,p_cooccurrences_ordre1,occurrences,top_concepts_dict = build_cooc_matrix(contenu,year)
	somme=0.
	for x in p_cooccurrences_ordre1.values():
		somme += x
	print 'somme'
	print somme
	#print occurrences
	print 'coocc fabriquées'
	#timeapres = timeavt
	#timeavt = time()
	#print 'duree de la derniere etape : ' + str( timeavt-timeapres) + '\n'
	#distribution_distance = distribution_distance_build(p_cooccurrences,dico_termes,p_cooccurrences_lignes)
	#print '\nrapprochements suggérés:\n'
	#timeapres = timeavt
	#timeavt = time()
	#print 'duree de la derniere etape : ' + str(timeavt-timeapres) + '\n'
	
	# 
	# l = distribution_distance.items()
	# l.sort(key=itemgetter(1),reverse=True)
	# dico_final_top={}
	# 
	# synonymes_potentiels = open(path_req + 'synonymes.txt','w')
	# 
	# for x in l[:10000]:
	# 	couple=x[0]
	# 	#if p_cooccurrences[(couple[0],couple[0],0)]*NN>freqmin and p_cooccurrences[(couple[1],couple[1],0)]*NN>freqmin:
	# 		#print dico_termes[couple[0]] + '\t'+dico_termes[couple[1]] + '\t' + str(float(distribution_distance[couple])) 
	# 	synonymes_potentiels.write(dico_termes[couple[0]] + '\t'+dico_termes[couple[1]] + '\t' + str(float(distribution_distance[couple]))  + '\n')
	# 
	# timeapres = timeavt
	# timeavt = time()
	# print 'duree de la derniere etape : ' + str(timeavt-timeapres) + '\n'
	# print "matrice de cooccurrence construite"

	muti = build_mutual_information(p_cooccurrences,p_cooccurrences_ordre1,nb_billets,occurrences,top_concepts_dict)
	xhi2val = xhi2(muti)
	export_concepts_xhi2(xhi2val,p_cooccurrences,p_cooccurrences_ordre1,dico_termes,dico_lemmes,year,occurrences)
	
# 	
# pool_size = int(multiprocessing.cpu_count())
# pool = multiprocessing.Pool(processes=pool_size)
# print years
# pool.map(xhi2_comp, years)
for year in years:
	xhi2_comp(year)
fusion_years.fusion('conceptsxhi2')