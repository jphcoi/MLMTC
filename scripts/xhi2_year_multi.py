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
treetagger_dir =parameters.treetagger_dir
years_bins = parameters.years_bins
dist_type=parameters.dist_type
dated=parameters.dated
datef=parameters.datef
seuil=0.2
###################################
#######export #####################
###################################

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

#billets décrit les concepts utilisé chaque annee
#billet[annee]=array(id des billets publies)
#termes=array(id des termes présents)
def build_nbbillet(contenu,years_bin):
	#now: 		contenu = liste de [concepts_id,jours,id_billet]
	nb_billets = init_dictionnary_list(len(years_bins),0)
	for cont in contenu:
		jour = cont[1]
		concepts_ids = cont[0]
		for idx, val in enumerate(years_bins):
			if jour in val:
				n_cl =  len(convert_clique_txt_2_list(concepts_ids))
				#nb_billets[idx]=nb_billets[idx]+1
				nb_billets[idx]=nb_billets[idx]+n_cl*(n_cl-1)/2
	return nb_billets


def convert_clique_txt_2_list(clique_txt):
	if not str(clique_txt)=='None' and not len(str(clique_txt))<3:
		clique = clique_txt[1:-1].split(', ')
		return map(int,clique)
	else:
		return []

def build_voisins(contenu,years_bin):
	#now: 		contenu = liste de [concepts_id,jours,id_billet]
	voisins={}
	#voisins[terme,intervalle] = array(termes co-présents)
	for y_b in range(len(years_bins)):
		for ter in dico_termes:
			voisins[(ter,y_b)]=[]
	for cont in contenu:
		intervalle=-1
		for y_b in years_bins:
			intervalle+=1
			if cont[1] in y_b:
				clique = convert_clique_txt_2_list(cont[0])
				for idx, con_1 in enumerate(clique):
					for con_2 in clique[idx:]:						
						if not con_1==con_2:
							temp = voisins[(con_1,intervalle)]
							temp.append(con_2)
							voisins[(con_1,intervalle)]=temp

							temp = voisins[(con_2,intervalle)]
							temp.append(con_1)
							voisins[(con_2,intervalle)]=temp
						else:
							temp = voisins[(con_2,intervalle)]
							temp.append(con_1)
							voisins[(con_1,intervalle)]=temp
	return voisins 

def unique(liste):
	liste_u=[]
	for x in liste:
		if not x in liste_u:
			liste_u.append(x)
	return liste_u
	
def build_cooc(voisins,nb_billets):
	p_cooccurrences={}
	p_cooccurences_lignes={}
	p_cooccurrences_ordre1={}
	#p_cooccurrences[terme1,terme2,intervalle] = proba du terme
	compt=0
	waiting_time = len(voisins)
	for x,y in voisins.iteritems():
		compt+=1
		if not compt%100:
			print '       (#'+str(compt)+' sur '+str(waiting_time)+")"		
		N = nb_billets[x[1]]
		terme1 = x[0]
		inter = x[1]
		dict_temp={}
		for terme2 in y:
			dict_temp[terme2] = dict_temp.get(terme2,0)  + 1
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
	nb_billets = build_nbbillet(contenu,years_bin)
	print "        - "+str(nb_billets[0])+" billets : "
	print '\n'
	
	voisins = build_voisins(contenu,years_bin)
	print "variable voisins construite"
	print '\n'
	
	p_cooccurrences,p_cooccurrences_lignes,p_cooccurrences_ordre1=build_cooc(voisins,nb_billets)
	return p_cooccurrences,nb_billets,p_cooccurrences_lignes,p_cooccurrences_ordre1
	
	
#muti[(terme1,terme2,intervalle)]=MI(t1,t2,t)
def build_mutual_information(p_cooccurrences,p_cooccurrences_ordre1,nb_billets):
	muti={}
	for x in p_cooccurrences_ordre1:
		terme1=x[0]
		inter =x[1]
		for x2 in p_cooccurrences_ordre1:
			if x2[0] != terme1 and inter == x2[1]:
 				terme2 = x2[0]
				#muti[x]=math.log((y-T)*(y-T)/T,2)
				expected = nb_billets[inter] *  p_cooccurrences_ordre1[(terme1,inter)]*p_cooccurrences_ordre1[(terme2,inter)]
				xhi2 = ( nb_billets[inter]*p_cooccurrences.get((terme1,terme2,inter),0.) - expected)**2 / expected
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

def dedoubler(dico_termes,years_bins):
	dico_termes_temp={}
	for inter in range(len(years_bins)):
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
		

def xhi2(muti,thres):
	xhi2val={}
	for x in muti:
		xhi2val[x[0]]=0.
	for x,y in muti.iteritems():
		if y>thres:
			xhi2val[x[0]]=xhi2val[x[0]]+y
	return xhi2val
			


def distribution_distance_build(p_cooccurrences,dico_termes,p_cooccurrences_lignes):
	epsilon = 0.0
	distribution_distance={}
	N = len(dico_termes.keys())
	Ncoocc = {}
	for x,t in p_cooccurrences_lignes.iteritems():
		Ncoocc[x]=sum(t.values())
#	print p_cooccurrences_lignes[1]
#	print Ncoocc
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
	
def export_concepts_xhi2 (xhi2val,p_cooccurrences,dico_termes,dico_lemmes,year):
	conceptxhi2 = open(path_req +'years/'+ requete +str(year) + '_'  + 'conceptsxhi2.csv','w')
	for x in dico_termes:
		try:
			#conceptxhi2.write(dico_lemmes[x] + '\t' + dico_termes[x] + '\t' + str(p_cooccurrences[(x,x,0)]).replace('.',',') + '\t' + str(xhi2val[x]).replace('.',',')+ '\t' + str(xhi2val[x]*p_cooccurrences[(x,x,0)]).replace('.',',') + '\n' )
			conceptxhi2.write(dico_lemmes[x] + '\t' + dico_termes[x] + '\t' +str(p_cooccurrences[(x,x,years.index(year))]).replace('.',',')+  '\t' + str(xhi2val[x]).replace('.',',')+ '\t' +  '\n' )
		except:
			#conceptxhi2.write(dico_lemmes[x] + '\t' + dico_termes[x] + '\t' + '\t' + '\t' +  '\t'+ '\t' + '\t' + '\n' )
			conceptxhi2.write(dico_lemmes[x] + '\t' + dico_termes[x] + '\t' + '\t' + '\t' +  '\t' + '\n' )
		
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
	p_cooccurrences,nb_billets,p_cooccurrences_lignes,p_cooccurrences_ordre1 = build_cooc_matrix(contenu,year)
	print 'coocc fabriquées'
	timeapres = timeavt
	timeavt = time()
	print 'duree de la derniere etape : ' + str( timeavt-timeapres) + '\n'
	distribution_distance = distribution_distance_build(p_cooccurrences,dico_termes,p_cooccurrences_lignes)
	print '\nrapprochements suggérés:\n'
	timeapres = timeavt
	timeavt = time()
	print 'duree de la derniere etape : ' + str(timeavt-timeapres) + '\n'
	
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

	muti = build_mutual_information(p_cooccurrences,p_cooccurrences_ordre1,nb_billets)
#	print muti
	thres=0.
	xhi2val = xhi2(muti,thres)
	export_concepts_xhi2(xhi2val,p_cooccurrences,dico_termes,dico_lemmes,year)
	
# 	
pool_size = int(multiprocessing.cpu_count())
pool = multiprocessing.Pool(processes=pool_size)
print years
pool.map(xhi2_comp, years)
# for year in years:
# 	xhi2_comp(year)
fusion_years.fusion('conceptsxhi2')