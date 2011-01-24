#!/Library/Frameworks/Python.framework/Versions/2.6/bin/python
# -*- coding: utf-8 -*- 
import os
import sys
sys.path.append("../scripts/libraries")
sys.path.append("../scripts")

print "tube v0.6 (20110220)"
print "--------------------------------\n"

import fonctions_bdd
import parameters
import os
import sys
import math
import gexf
import fonctions
import maps_union
from sets import Set
import auteurs
import fonctions_lib
import network_layout
path_req = parameters.path_req
years_bins = parameters.years_bins
name_bdd = parameters.name_bdd
path_req=parameters.path_req
degmax=5
try:
	timelimit=parameters.timelimit
except:
	timelimit=1

dist_type=parameters.dist_type
sep_label = ' --- '


def str_list(str_bdd):
	try:
		jour=int(str_bdd[2])
	except:
		jour=-1
	numero = int(str_bdd[0])
	str_bdd=str_bdd[1]
	str_bdd=str_bdd.replace('[','').replace(']','')
	try:
		return (numero,map(int,str_bdd.split(', ')),jour)
	except:
		return(numero,[],jour)

def add_link(clusters,reseau,type_lien):
	for liens in reseau:
		champ1 = liens[2]
		champ2 = liens[5]
		if champ1 in clusters and champ2 in clusters:
			stre = liens[6]
			dict_id = clusters[champ1]
			dico = dict_id.get(type_lien,{})
			dico[champ2] = stre
			dict_id[type_lien] = dico
			clusters[champ1] = dict_id
	return clusters

#on récupère les données utiles construites dans phylogenie.py
def load_data():
	champs=['id_cluster_1','periode_1','id_cluster_1_univ','id_cluster_2','periode_2','id_cluster_2_univ','strength']
	res_maps = fonctions_bdd.select_bdd_table_champ_complet(name_bdd,'maps',','.join(champs))
	champs=['id_cluster_1','periode_1','id_cluster_1_univ','id_cluster_2','periode_2','id_cluster_2_univ','strength']
	res_phylo = fonctions_bdd.select_bdd_table_champ_complet(name_bdd,'phylo',','.join(champs))
	champs=['id_cluster','periode','id_cluster_univ','label_1','label_2','level','concept','nb_fathers','nb_sons','label']
	res_cluster = fonctions_bdd.select_bdd_table_champ_complet(name_bdd,'cluster',','.join(champs))
	dico_termes=fonctions.lexique()#on cree le dictionnaire des termes

	#on les restructure pour plus de confort d'utilisation.
	clusters={}#on crée un dico de dico.
	years_bins_first = []
	for years in years_bins:
		years_bins_first.append(years[0])
	for cluster_terme in res_cluster:
		[id_cluster,periode,id_cluster_univ,label_1,label_2,level,concept,nb_fathers,nb_sons,label] = cluster_terme
		periode = years_bins_first.index(int(str(periode).split(' ')[0]))
		if nb_fathers+nb_sons>0:
			if id_cluster_univ in clusters:
				dict_id = clusters[id_cluster_univ]
				temp_concept = dict_id['concepts']
				temp_concept.append(concept)
				dict_id['concepts'] = temp_concept
				clusters[id_cluster_univ] = dict_id
			else:
				dict_id={}
				dict_id['id_cluster']=id_cluster
				dict_id['periode']=periode
				dict_id['label']=[label_1,label_2]
				dict_id['nb_fathers']=nb_fathers
				dict_id['nb_sons']=nb_sons
				dict_id['concepts'] = [concept]
				dict_id['label'] = label
				clusters[id_cluster_univ] = dict_id
	#clusters[id_cluster_univ]['id_cluster'/'periode'/'label'/'nb_sons'/'nb_fathers'/'concepts']
	add_link(clusters,res_phylo,'dia')
	add_link(clusters,res_maps,'syn')

	#on récupère dist_mat réseau des distances entre termes.
	name_date = str(years_bins[0][0]) + '_' + str(years_bins[0][-1]) + '_'+ str(years_bins[1][0])+ '_'+str(years_bins[-1][-1])
	#version longue et exacte
	#dist_mat = fonctions.dumpingout('dist_mat'+name_date)
	#version rapide et approchée:
	dist_mat = fonctions.dumpingout('dist_mat_10'+name_date)
	return dico_termes,clusters,dist_mat

#fixer k=kmin=4

#calcul des épaisseurs de champs.
def width(clusters):
	notices_str = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'billets','id,concepts_id,jours')
	notices = map(str_list,notices_str)
	biparti_noticeschamps={}
	biparti_champsnotices={}
	for notice in notices:
		numero = int(notice[0])
		champ1 = notice[1]
		jour =  notice[2]
		for inter,years in enumerate(years_bins):
			if jour in years:
				for id_univ,clu in clusters.iteritems():
					if clu['periode'] == inter:
						if len(set(champ1) & set(clu['concepts']))>0:
							dist = fonctions.calcul_distance(champ1,clu['concepts'],dist_mat,inter,type_distance='moy')
							dico = biparti_noticeschamps.get(numero,{})
							dicoinv = biparti_champsnotices.get(id_univ,{})
							if dist > 0.1:
								dico[id_univ] = dist
								dicoinv[numero] = dist
								biparti_noticeschamps[numero] = dico
								biparti_champsnotices[id_univ] = dicoinv
	epaisseur={}
	for id_univ,clu in clusters.iteritems():
		try:
			epaisseur[id_univ]=sum(biparti_champsnotices[id_univ].values())
		except:
			print 'taille nulle'
	return epaisseur,biparti_noticeschamps,biparti_champsnotices	

try:
	liens_totaux_syn,liens_totaux_dia,clusters = fonctions.dumpingout('liens_totaux_syn'),fonctions.dumpingout('liens_totaux_dia'),fonctions.dumpingout('clusters')
except:
	
	dico_termes,clusters,dist_mat = load_data()
	epaisseur,biparti_noticeschamps,biparti_champsnotices=width(clusters)	

	for x,y in epaisseur.iteritems():
		clusters[x]['epaisseur']=y

	liens_totaux_syn=[]
	liens_totaux_dia=[]
	for id_univ,clu in clusters.iteritems():
		try:
			voisins = clu['syn']
			for voisin,stre in voisins.iteritems():
				liens_totaux_syn.append((id_univ,voisin,stre))
		except:
			pass

		try:
			voisins = clu['dia']
			for voisin,stre in voisins.iteritems():
				liens_totaux_dia.append((id_univ,voisin,stre))
		except:
			pass
 

	fonctions.dumpingin(liens_totaux_syn,'liens_totaux_syn')
	fonctions.dumpingin(liens_totaux_dia,'liens_totaux_dia')
	fonctions.dumpingin(clusters,'clusters')
network_layout.plot_graph(liens_totaux_syn,liens_totaux_dia,clusters)