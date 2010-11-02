#!/usr/bin/python
# -*- coding: utf-8 -*-
#recupere les liens des trois reseaux pour exporter les reseaux au format texte
import sys
import math
from copy import deepcopy
sys.path.append("/libraries")
sys.path.append("../map_builder")
from operator import itemgetter

print "export_networks v0.2 (20091102)"
print "--------------------------------\n"

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
		for idx, val in enumerate(years_bins):
			if jour in val:
				nb_billets[idx]=nb_billets[idx]+1
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

	
def build_cooc(voisins,nb_billets):
	p_cooccurrences={}
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
		voisinage = set(y)
		dict_temp={}
		for terme2 in voisinage:
			dict_temp[terme2] = 0
		for terme2 in y:
			dict_temp[terme2] = dict_temp[terme2]  + 1
		for terme2 in voisinage:
			p_cooccurrences[(terme1,terme2,inter)] = float(dict_temp[terme2]) / N
		
	#print p_cooccurrences
	print '\n'
	
	print 'matrice temporelle de cooccurrence ecrite'
	print '\n'
	
	return p_cooccurrences








def build_cooc_matrix(contenu, years_bin):
	nb_billets = build_nbbillet(contenu,years_bin)
	print "        - "+str(nb_billets[0])+" billets : "
	print '\n'
	
	voisins = build_voisins(contenu,years_bin)
	print "variable voisins construite"
	print '\n'
	
	p_cooccurrences=build_cooc(voisins,nb_billets)
	return p_cooccurrences,nb_billets[0]
	
	
#muti[(terme1,terme2,intervalle)]=MI(t1,t2,t)
def build_mutual_information(p_cooccurrences):
	muti={}
	for x,y in p_cooccurrences.iteritems():
		T=p_cooccurrences[(x[0],x[0],x[2])]*p_cooccurrences[(x[1],x[1],x[2])]
		muti[x]=math.log10( y/T )
		#version andrei
		#muti[x]=(y-T)*(y-T)/T
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
			

def distribution_distance_build(p_cooccurrences,dico_termes):
	epsilon = 0.0
	distribution_distance={}
	N = len(dico_termes.keys())
	for x in range(N):
		x=x+1
		for y in range(N):
			y=y+1
			if y>x:
				dist_xy = 0.
				occ_y = 0.
				occ_x =0.
				
				for z in range(N):
					z=z+1
					dist_x=p_cooccurrences.get((x,z,0),0.)
					# try:
					# 	dist_x = float(p_cooccurrences[])
					# except:
					# 	dist_x = epsilon
					dist_y=p_cooccurrences.get((y,z,0),0.)
					# try:	
					# 	dist_y = float(p_cooccurrences[(y,z,0)])
					# except:
					# 	dist_y = epsilon
					occ_y=float(occ_y+dist_y)
					occ_x=float(occ_x+dist_x)
					dist_xy = float(dist_xy  +math.sqrt(float(dist_x*dist_y)))
				if dist_xy>0:
					distribution_distance[(x,y)]=  - math.log(dist_xy/ math.sqrt(float(occ_x*occ_y)))
	return distribution_distance
	
def export_concepts_xhi2 (xhi2val,p_cooccurrences,dico_termes,dico_lemmes):
	conceptxhi2 = open(path_req + 'conceptsxhi2.csv','w')
	for x in dico_termes:
		try:
			conceptxhi2.write(dico_lemmes[x] + '\t' + dico_termes[x] + '\t' + str(p_cooccurrences[(x,x,0)]).replace('.',',') + '\t' + str(xhi2val[x]).replace('.',',')+ '\t' + str(xhi2val[x]*p_cooccurrences[(x,x,0)]).replace('.',',') + '\n' )
		except:
			conceptxhi2.write(dico_lemmes[x] + '\t' + dico_termes[x] + '\t' + '\t' + '\t' +  '\t'+ '\t' + '\t' + '\n' )
		
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
years_bins = []
#traite le multi-type des variables:
try:
	datef=datef[0]
	dated=dated[0]
except:
	pass
	
for y in range(datef-dated+1):
	years_bins.append(y+dated)
years_bins=[years_bins]
contenu = fonctions_bdd.select_bdd_table(name_bdd,'billets','concepts_id,jours,id',requete)
print "contenu importé"
print '\n'

p_cooccurrences,NN = build_cooc_matrix(contenu,years_bins)
print 'coocc fabriquées'
distribution_distance = distribution_distance_build(p_cooccurrences,dico_termes)
print '\nrapprochements suggérés:\n'
ytot = 0.
h =0
for x,y in distribution_distance.iteritems():
	ytot = ytot + y
	h = h+1
ytot = float(ytot / float(h))

l = distribution_distance.items()
l.sort(key=itemgetter(1),reverse=True)
dico_final_top={}

synonymes_potentiels = open(path_req + 'synonymes.txt','w')

for x in l[:10000]:
	couple=x[0]
	if p_cooccurrences[(couple[0],couple[0],0)]*NN>freqmin and p_cooccurrences[(couple[1],couple[1],0)]*NN>freqmin:
		print dico_termes[couple[0]] + '\t'+dico_termes[couple[1]] + '\t' + str(float(distribution_distance[couple] / ytot)) 
		synonymes_potentiels.write(dico_termes[couple[0]] + '\t'+dico_termes[couple[1]] + '\t' + str(float(distribution_distance[couple] / ytot))  + '\n')
print "matrice de cooccurrence construite"


# muti = build_mutual_information(p_cooccurrences)
# thres=0.
# xhi2val = xhi2(muti,thres)
# export_concepts_xhi2(xhi2val,p_cooccurrences,dico_termes,dico_lemmes)
