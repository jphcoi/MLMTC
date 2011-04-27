#!/usr/bin/python
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
from operator import itemgetter
from copy import deepcopy
from hcluster import pdist, linkage, dendrogram,centroid,weighted,ward,linkage,complete,average
import matplotlib
import matplotlib.pyplot as plt
import jsonpickle
import spring
import scipy
import pylab
import random
import json
path_req = parameters.path_req
years_bins = parameters.years_bins
print years_bins
name_bdd = parameters.name_bdd
path_req=parameters.path_req
degmax=5
try:
	timelimit=parameters.timelimit
except:
	timelimit=2

dist_type=parameters.dist_type
sep_label = ' --- '


from math import modf, floor
 
def normalize_pos(pos_spatial0):
	x_max=-1000
	x_min = 1000

	for couple in pos_spatial0.values():
		x_max = max(couple[0],x_max)
		x_min = min(couple[0],x_min)
	for index,couple in pos_spatial0.iteritems():
		pos_spatial0[index][0]=float((couple[0]-x_min)) / float((x_max-x_min))
		pos_spatial0[index][1]=pos_spatial0[index][1]
	return pos_spatial0
def quantile(x, q,  qtype = 7, issorted = False):
    """
    Args:
       x - input data
       q - quantile
       qtype - algorithm
       issorted- True if x already sorted.
 
    Compute quantiles from input array x given q.For median,
    specify q=0.5.
 
    References:
       http://reference.wolfram.com/mathematica/ref/Quantile.html
       http://wiki.r-project.org/rwiki/doku.php?id=rdoc:stats:quantile
 
    Author:
	Ernesto P.Adorio Ph.D.
	UP Extension Program in Pampanga, Clark Field.
    """
    if not issorted:
        y = sorted(x)
    else:
        y = x
    if not (1 <= qtype <= 9): 
       return None  # error!
 
    # Parameters for the Hyndman and Fan algorithm
    abcd = [(0,   0, 1, 0), # inverse empirical distrib.function., R type 1
            (0.5, 0, 1, 0), # similar to type 1, averaged, R type 2
            (0.5, 0, 0, 0), # nearest order statistic,(SAS) R type 3
 
            (0,   0, 0, 1), # California linear interpolation, R type 4
            (0.5, 0, 0, 1), # hydrologists method, R type 5
            (0,   1, 0, 1), # mean-based estimate(Weibull method), (SPSS,Minitab), type 6 
            (1,  -1, 0, 1), # mode-based method,(S, S-Plus), R type 7
            (1.0/3, 1.0/3, 0, 1), # median-unbiased ,  R type 8
            (3/8.0, 0.25, 0, 1)   # normal-unbiased, R type 9.
           ]
 
    a, b, c, d = abcd[qtype-1]
    n = len(x)
    g, j = modf( a + (n+b) * q -1)
    if j < 0:
        return y[0]
    elif j >= n:           
        return y[n-1]   # oct. 8, 2010 y[n]???!! uncaught  off by 1 error!!!
 
    j = int(floor(j))
    if g ==  0:
       return y[j]
    else:
       return y[j] + (y[j+1]- y[j])* (c + d * g)    
 
def Test():
    x = [11.4, 17.3, 21.3, 25.9, 40.1, 50.5, 60.0, 70.0, 75]
 
    for qtype in range(1,10):
        print qtype, quantile(x, 0.35, qtype)
 


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
			stre = float(liens[6])
			dict_id = clusters[champ1]
			dico = dict_id.get(type_lien,{})
			if type_lien=='dia':
				dico[champ2] = stre * 10.
			else:
				dico[champ2] = stre
			dict_id[type_lien] = dico
			clusters[champ1] = dict_id
	return clusters

#on récupère les données utiles construites dans phylogenie.py
def load_data(orphan_number):
	champs=['id_cluster_1','periode_1','id_cluster_1_univ','id_cluster_2','periode_2','id_cluster_2_univ','strength']
	res_maps = fonctions_bdd.select_bdd_table_champ_complet(name_bdd,'maps',','.join(champs))
	champs=['id_cluster_1','periode_1','id_cluster_1_univ','id_cluster_2','periode_2','id_cluster_2_univ','strength']
	res_phylo = fonctions_bdd.select_bdd_table_champ_complet(name_bdd,'phylo',','.join(champs))
	champs=['id_cluster','periode','id_cluster_univ','label_1','label_2','level','concept','nb_fathers','nb_sons','label']
	res_cluster = fonctions_bdd.select_bdd_table_champ_complet(name_bdd,'cluster',','.join(champs))
	champs=['jours','concepts_id']
	occurrences_concepts = fonctions_bdd.select_bdd_table_champ_complet(name_bdd,'billets',','.join(champs))
	champs=['concept1','concept2','periode','distance0','distance1']
	reseau_termes = fonctions_bdd.select_bdd_table_champ_complet(name_bdd,'sem_weighted',','.join(champs))
	dico_termes=fonctions.lexique()#on cree le dictionnaire des termes

	#on les restructure pour plus de confort d'utilisation.
	clusters={}#on crée un dico de dico.
	years_bins_first = []
	res_termes={}#on crée un dico de dico dans lequel seront indiqués les distances
	for years in years_bins:
		years_bins_first.append(years[0])
	for lien_terme in reseau_termes:
		[concept1,concept2,periode,distance0,distance1] = lien_terme
		if distance0>0:
			res_termes_inter = res_termes.get(periode,{})
			dict_id1 = res_termes_inter.get(concept1,{})
			dict_id1[concept2] = distance0
			res_termes_inter[concept1]=dict_id1
			res_termes[periode] = res_termes_inter
			
		if distance1>0:
			res_termes_inter = res_termes.get(periode,{})
			dict_id2 = res_termes_inter.get(concept2,{})		
			dict_id2[concept1] = distance1#attention on rapporte les distances en double	
			res_termes_inter[concept2]=dict_id2		
			res_termes[periode] = res_termes_inter
		
	for cluster_terme in res_cluster:
		[id_cluster,periode,id_cluster_univ,label_1,label_2,level,concept,nb_fathers,nb_sons,label] = cluster_terme
		periode = years_bins_first.index(int(str(periode).split(' ')[0]))
		if nb_fathers+nb_sons >= orphan_number:
			if id_cluster_univ in clusters:
				dict_id = clusters[id_cluster_univ]
				temp_concept = dict_id['concepts']
				temp_concept.append(concept)
				dict_id['concepts'] = temp_concept
				clusters[id_cluster_univ] = dict_id
			else:
				dict_id={}
				#dict_id['id_cluster']=id_cluster
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
	for index in clusters.keys():
		if not 'syn' in  clusters[index]:
			clusters[index]['syn']={}
	#on construit la matrice temporelle d'occurrence des termes.
	occs = {}
	for occ in occurrences_concepts:	
		year = occ[0]
		if len(occ[1])>2:
			concept_list = list(map(int,occ[1][1:-1].split(', ')))
		else:
			concept_list=[]
		#print concept_list
		for conc in concept_list:
			occs_conc=occs.get(conc,{})
			occs_conc[year] = 1 + occs_conc.get(year,0)
			occs[conc]=occs_conc
	#on récupère dist_mat réseau des distances entre termes.
	name_date = str(years_bins[0][0]) + '_' + str(years_bins[0][-1]) + '_'+ str(years_bins[1][0])+ '_'+str(years_bins[-1][-1])
	#version longue et exacte
	#dist_mat = fonctions.dumpingout('dist_mat'+name_date)
	#version rapide et approchée:
	dist_mat = fonctions.dumpingout('dist_mat_10'+name_date)
	return dico_termes,clusters,dist_mat,res_termes

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


def score_label(res_termes_inter,concepts):
	scores={}
	score_computed = 0.
	for terme in concepts:
		for voisin in concepts:
			din,dout=0,0
			if terme==voisin:
				din,dout=1,1
			else:
				try:
					din=float(res_termes_inter[voisin])
				except:
					pass
					
				try:
					dout=float(res_termes_inter[terme])
				except:
					pass
			try:
				score_computed = score_computed +  float(din*dout)/(din+dout)
			except:
				pass
			scores[terme] = scores.get(terme,0.)+score_computed / (len(concepts))
	return scores

def return_label(scores,nb_label=2):
	l=scores.items()
	l.sort(key=itemgetter(1),reverse=True)
	label_edge=[]
	for (id_terme,sc) in l[:nb_label]:
		label_edge.append(dico_termes[id_terme])
	return " - ".join(label_edge)



# def	merge_label(scores_label,liste_univ):
# 	voisin = liste_univ[0]
# 	score_label_edge = scores_label[voisin]
# 	for noeud in liste_univ[1:]:
# 		score_labeln = scores_label[noeud]
# 		for con1,sc1 in score_labeln.iteritems():
# 			score_label_edge[con1] =  score_label_edge.get(con1,0.) + sc1
# 	return score_label_edge	

def reindex(univ2index,temp):
	temp_index={}
	for t,stre in temp.iteritems():
		temp_index[univ2index[t]] = stre
	return temp_index

def rec_retrieval(decalage,x):
	z=x
	while z in decalage:
		z = decalage[z]
	return z
	
def h_clustering(clusters,nb_level=6):
	multi_level_net={}
	#on reformate les similarités entre champs pour les transformer en distance
	dist_tot = []#aggrège toutes les distances entre champs
	univ2index={}
	index2univ={}

	
	max_periode = 0
	for i,univ in enumerate(clusters.keys()):
		univ2index[univ] = i
		index2univ[i] = univ
		max_periode = max(max_periode,clusters[univ].get('periode',0))
	#on renumérote pour plus de confort:
	clusters_index={}
	for univ,clu in clusters.iteritems():
		index = univ2index[univ]
		clusters_index[index]=clu
		if 'syn' in clu:
			temp = clu['syn']
			temp_index = reindex(univ2index,temp)
			clusters_index[index]['syn'] = temp_index
		if 'dia' in clu:
			temp = clu['dia']
			temp_index = reindex(univ2index,temp)
			clusters_index[index]['dia'] = temp_index

	#on prépare les niveaux supérieurs.
	#on divise dans un premier temps les liens synchros en n quantiles
	sync_strenghts={}
	for index,clu in clusters_index.iteritems():
		voisins = clu['syn']
		for voisin,stre in voisins.iteritems():
			sync_strenghts[(index,voisin)] = stre


	for i,champ1 in enumerate(clusters_index.keys()[:-1]):
		for champ2 in clusters_index.keys()[i+1:]:
				dist_tot.append(float(1.-  max(sync_strenghts.get((champ2,champ1),0.),sync_strenghts.get((champ1,champ2),0.))))			
				
	#print dist_tot
	Z = weighted(dist_tot)
	#print Z
	print '***on calcule le dendrogramme associe'
#	dd = dendrogram(Z)
#	matplotlib.pyplot.show()
	#res_niv_0 = Network(champs_liste,champs_dist) 
	
	#Z ressemble à : [
	#		 [  2.           6.           0.36216925   2.        ]
	# 		 [ 10.          15.           0.42559153   2.        ]
	# 		 [  8.          13.           0.43538316   2.        ]
	# 		 [  0.          19.           0.43583879   2.        ]

	pas = len(Z)/min(len(Z),nb_level)
	next_step=pas
	level = 0
	cluster_level={}
	champs_courants=clusters_index.keys()
	N=len(champs_courants[:])-1
	clusters_level={}
	below,above={},{}
	print len(Z)
	decalage={}
	m=10000
	for i,ev_fusion in enumerate(Z[:-max_periode]):


		if i>=len(Z)*level/nb_level -1:
			print i,level
			#on fige le réseau dans son état.
			if level>0:
				for x in clusters_level[level-1]:
					if x in champs_courants:
						m+=1
						champs_courants.remove(x)
						champs_courants.append(m)
						decalage[x]=m
						above[x]=m
						below.setdefault(m,[]).append(x)
			clusters_level[level]=champs_courants[:]
			level +=1		
		
		fusion_level = ev_fusion[2]#niveau de la fusion
		N += 1

		
		ch1=rec_retrieval(decalage,int(ev_fusion[0]))
		ch2=rec_retrieval(decalage,int(ev_fusion[1]))
		
		champs_courants.remove(ch1)
		champs_courants.remove(ch2)
		champs_courants.append(N)
		below.setdefault(N,[]).append(ch1)
		below.setdefault(N,[]).append(ch2)
		above[ch1]=N
		above[ch2]=N	
				
		if i==len(Z)-max_periode-1:
			print i,level
			#on fige le réseau dans son état.
			if level>0:
				for x in clusters_level[level-1]:
					if x in champs_courants:
						m+=1
						champs_courants.remove(x)
						champs_courants.append(m)
						decalage[x]=m
						above[x]=m
						below.setdefault(m,[]).append(x)
			clusters_level[level]=champs_courants[:]
			
	return clusters_index,clusters_level,below,above

def recup(above,index,pertinents):
	while not index in pertinents:
		index = above[index]
	return index

def get_attribute(list_index,attribute,clusters_complet,type={}):
	attributes=[]
	for x in list_index:
		attributes.append(clusters_complet[x].get(attribute,type))
	return attributes

def get_attribute_dict(list_index,attribute,clusters_complet):
	attributes=[]
	for x in list_index:
		attributes.append(clusters_complet[x].get(attribute,{}))
	return attributes




def merge_dicts_list(list_dicts):
	dict0 = list_dicts[0]
	for dicti in list_dicts[1:]:
		for cle,val in dicti.iteritems():
			dict0[cle] =  dict0.get(cle,0.) + val
	return dict0

def merge_list_list(list_list):
	total_list=[]
	for x in list_list:
		total_list=total_list+x
	return total_list


def filter_level(clusters_complet,i):
	cluster_level={}
	for x, clu in clusters_complet.iteritems():
		if clu['level']==i:
			cluster_level[x]=clu
	return cluster_level


class Tube:
	pass

class Edge:
	pass

def export_json(clusters_complet,label_edges,years_bins,nb_level):
	r = {}
	r["meta"] = {}
	r["nodes"] = clusters_complet
	r["meta"]["tubes_count"] = len(pos)
	r["meta"]["steps"] = len(years_bins)
	r["meta"]["start"] = years_bins[0][0]
	r["meta"]["step"] = years_bins[1][0]-years_bins[0][0]
	r["meta"]["depth"] = nb_level
	r["edges"] = []
	for edge,edge_label in label_edges.iteritems():
		e= Edge()
		e.node_parent=edge[0]
		e.node_child=edge[1]
		e.label= edge_label
		r["edges"].append(e)
	file_json=open('tubes.json','w')
	file_json.write(jsonpickle.encode(r))


def count_dist(years_cover):
	years_cover_dist={}
	for x in years_cover:
		years_cover_dist[x] = years_cover_dist.get(x,0)+1
	return years_cover_dist

def count_links(cluster_level):
	n=0
	for x,clu in cluster_level.iteritems():
		if 'dia' in clu:
			n = n + len(clu['dia'].keys())
	return n


def dumpjson(clusters0,target_level):
	data ={}
	nodes={}
	edges={}
	fields={}
	meta={}
	meta['steps']=10
	meta['begin']=1992
	meta['interval']=2
	meta['level_nb']=target_level+1
	data['meta']=meta
	edge_id=-1
	for index,clu in clusters0.iteritems():
		if clu['level']<=target_level:
			nodes[index]={}
			nodes[index]['label'] = clu['label']
			nodes[index]['x'] = str(clu['x'])
			nodes[index]['y'] = str(clu['y'])
			nodes[index]['epaisseur'] = str(clu['epaisseur'])
			nodes[index]['level'] = str(clu['level'])
			
			syn = clu.get('syn',{})
			for y,stre in syn.iteritems():
				edge_id+=1
				edges[edge_id]={}
				edges[edge_id]['parent'] = str(index)
				edges[edge_id]['child'] = str(y)
				edges[edge_id]['strength'] = str(float(stre))		
				edges[edge_id]['type'] = 'syn'
			dia = clu.get('dia',{})
			for y,stre in dia.iteritems():
				edge_id+=1
				edges[edge_id]={}
				edges[edge_id]['parent'] = str(index)
				edges[edge_id]['child'] = str(y)
				edges[edge_id]['strength'] = str(float(stre))		
				edges[edge_id]['type'] = 'dia'
	data['nodes']=nodes
	data['edges']=edges		

 	return data
	
	
	
def cut_intervalle(intervalle,nb,lambada): 
	lambada = math.sqrt(lambada)
	int_lenght = (intervalle[1]-intervalle[0])/float(lambada)
	int_lenght_dessous = int_lenght  / float(nb)
	intervalles_dessous=[]
	xmin = intervalle[0] + (intervalle[1]-intervalle[0])/2. * (1.-1./float(lambada))
	for n in range(nb):
		intervalle = [xmin,xmin+int_lenght_dessous]
		intervalles_dessous.append(intervalle)
		xmin = xmin+int_lenght_dessous
	return intervalles_dessous
	
	
def strongest_link(clusters):
	clusters2 = {}
	for id_univ,clu in clusters.iteritems():
		if 'dia' in clu:
			dia = clu['dia']
			l=dia.items()
			l.sort(key=itemgetter(1),reverse=True)
			#print l[:2]
			dia2 = {}
			if len(l)>0:
			#	print l[0][0],l[0][1]
				dia2[l[0][0]]=l[0][1]
				clu['dia'] = dia2
		clusters2[id_univ] = clu
	return clusters2


def  symetric_links(clusters):
	for id_univ,clu in clusters.iteritems():
		if 'dia' in clu:
			dia = clu['dia']
		for x,stre in dia.iteritems():
			dia2  = clusters[x].get('dia',{})
			dia2[id_univ]=stre
			clusters[x]['dia'] = dia2
	return clusters

def inverse(components):
	components_belong={}
	for i,list_c in components.iteritems():
		for c in list_c:
			 components_belong[c]=i
	print components_belong
	return components_belong
	
def averag(components,clusters):
	components_belong = inverse(components)
	distance_components={}
	for i,cluster_list in components.iteritems():
		distance_components[i]={}
		voisins = merge_dicts_list(get_attribute(cluster_list,'syn',clusters,0.))
		for voisin,stre in voisins.iteritems(): 
			distance_components[i][components_belong[voisin]]=distance_components[i].get(components_belong[voisin],0.) + stre
		
	#on normalise ensuite
	timesteps = {}	
	for i,cluster_list in components.iteritems():
		for cluster in cluster_list:
			timesteps.setdefault(i,[]).append(clusters[cluster]['periode'])
	
	for i,distances in distance_components.iteritems():
		for j,dist in distances.iteritems():
			overlap = 0
			for tps_i in list(set(timesteps[i])):
				if tps_i in list(set(timesteps[j])):
					overlap += timesteps[i].count(tps_i) * timesteps[j].count(tps_i)
			distance_components[i][j] = dist/float(overlap)
	
	return distance_components,components_belong

def top(dict,n=1):
	l=dict.items()
	l.sort(key=itemgetter(1),reverse=True)
	return l[:n]

orphan_number = 1
try:
	liens_totaux_syn_0,liens_totaux_dia_0,clusters,years_bins,label_edges = fonctions.dumpingout('qliens_totaux_syn'+ str(orphan_number)),fonctions.dumpingout('liens_totaux_dia'+ str(orphan_number)),fonctions.dumpingout('clusters'+ str(orphan_number)),fonctions.dumpingout('years_bins'+ str(orphan_number)),fonctions.dumpingout( 'liens_totaux_label'+ str(orphan_number))
	print 'data loaded'
except:	
	print 'tubes coordinates being computed'
	try:
		dico_termes =fonctions.dumpingout('dico_termes' + str(orphan_number))
		clusters=fonctions.dumpingout('clusters'+ str(orphan_number))
		dist_mat=fonctions.dumpingout('dist_mat'+ str(orphan_number))
		res_termes=fonctions.dumpingout('res_termes'+ str(orphan_number))
		biparti_champsnotices=fonctions.dumpingout('biparti_champsnotices'+ str(orphan_number))
		biparti_noticeschamps=fonctions.dumpingout('biparti_noticeschamps'+ str(orphan_number))
		epaisseur=fonctions.dumpingout('epaisseur'+ str(orphan_number))
		print 'dumped data loaded'
	except:
		dico_termes,clusters,dist_mat,res_termes = load_data(orphan_number)
		epaisseur,biparti_noticeschamps,biparti_champsnotices=width(clusters)	
		fonctions.dumpingin(dico_termes,'dico_termes' + str(orphan_number))
		fonctions.dumpingin(clusters,'clusters'+ str(orphan_number))
		fonctions.dumpingin(dist_mat,'dist_mat'+ str(orphan_number))
		fonctions.dumpingin(res_termes,'res_termes'+ str(orphan_number))
		fonctions.dumpingin(biparti_champsnotices,'biparti_champsnotices'+ str(orphan_number))
		fonctions.dumpingin(biparti_noticeschamps,'biparti_noticeschamps'+ str(orphan_number))
		fonctions.dumpingin(epaisseur,'epaisseur'+ str(orphan_number))
		
	for x,y in epaisseur.iteritems():
		clusters[x]['epaisseur']=math.sqrt(1+y)
	
	print 'on regarde la tête d epaisseur'
	array = scipy.array(epaisseur.values())
#	pylab.figure()
#	pylab.hist(array, 1000)
	
	liens_totaux_syn_0=[]
	liens_totaux_dia_0=[]
	scores_label={}
	nb_level=12
	print str(len(clusters.keys())) + 'noeuds au niveau 0'
	#on ordonne les distances dans l'ordre croissant
	clusters,clusters_level,below,above=h_clustering(clusters,nb_level)
	#pour l'instant les id des clusters sont tous dans clusters_level, clusters ne contient que le niveau 0

	#on nettoie above et below qui contiennent des clusters inutiles
	above_propre={}
	below_propre={}
	clusters_complet={}
	for level,clusts in clusters_level.iteritems():
		print 'level:'+str(level)+':'+str(len(clusts))+' nodes\n'		
		for index in clusts:
			clusters_complet[index]=clusters.get(index,{})#on initialise le dictionnaire des clusters de taille supérieure à 1
			if index in above:
				dessus = recup(above,index,clusters_level[level+1])
				above_propre[index] = dessus
				below_propre.setdefault(dessus,[]).append(index)
				
	#check_below_propre()
	#check_above_propre(clusters_complet.keys())
					
	#on a bien identifié la composition des champs niveau après niveau. 
	#Il ne reste plus qu a calculer les labels de ces champs puis leur position, , et on complète clusters avec les champs que l'on vient de créer.
	
	#on prépare d'abord les scores des labels des noeuds du niveau 0
	for id_univ,clu in clusters.iteritems():
		sc_lab = score_label(res_termes[clu['periode']],clu['concepts'])
		scores_label[id_univ]=sc_lab
		clusters_complet[id_univ]['sc_lab'] = sc_lab
	print 'label scores computed for every clusters'
	
	
	#############################################
	###########METHOD FIRST LOW##################
	#############################################
	#on calcule les positions des champs par niveau décroissant
	
	#on moyenne les positions et on calcule les label_edges
	#on devrait moyenner par la composition en nombre de champs de niveau minimal!!!!!!!!!!!TBD
	pos_type='chelou'
	
	
	if pos_type=='from_above':
		levels=range(nb_level+1)
		levels.reverse()
		for level in levels:

			if level==nb_level:
				for index in clusters_level[level]:
					print index
					clu = clusters_complet[index]
					clu['x'] = 0.5
					clu['intervalle']=[0,1]
					clusters_complet[index]=clu
			else:
				for index in clusters_level[level+1]:
					clu_dessus = clusters_complet[index]
					x_dessus = clu_dessus['x']
					intervalle_dessus = clu_dessus['intervalle']
					nb_dessous = len(below_propre[index])
					print nb_dessous
					print intervalle_dessus
					intervalles_dessous =  cut_intervalle(intervalle_dessus,nb_dessous,nb_level+1-level)
					
					for dessous,int_d in zip(below_propre[index],intervalles_dessous):
						print dessous,int_d,(int_d[1]-int_d[0]) / 2.
						clu = clusters_complet[dessous]
						clu['x'] = int_d[0]+(int_d[1]-int_d[0]) / 2.
						clu['intervalle'] = int_d
						clusters_complet[dessous]=clu
			#for x in clust_index_level:
			#	above[x]
		
	
	
	#############################################
	###########METHOD FIRST HIGH##################
	#############################################
	#on calcule les positions au niveau 0
	if pos_type=='from_below':
		try:
			pos=fonctions.dumpingout('pos'+ str(orphan_number))
		except:
			pos = network_layout.get_pos(liens_totaux_syn_0,liens_totaux_dia_0,clusters)
			fonctions.dumpingin(pos,'pos'+ str(orphan_number))
	#on moyenne les positions et on calcule les label_edges
	#on devrait moyenner par la composition en nombre de champs de niveau minimal!!!!!!!!!!!TBD
		pos_x={}
		for index,x in pos.iteritems():
			pos_x[index] = x[0]
	
	#puis on récupère les liens et leurs labels.
	for id_univ,clu in clusters.iteritems():
		if 'syn' in clu:#on traite les liens synchro
			voisins = clu['syn']
			for voisin,stre in voisins.iteritems():
				try:#on symétrise les liens synchrones
					sym=clusters[voisin]['syn'][id_univ]
				except:
					sym=0.
				liens_totaux_syn_0.append((id_univ,voisin,max(stre,sym)))
	for level,clusts in clusters_level.iteritems():
		print 'level:'+str(level)+':'+str(len(clusts))+' nodes\n'		
		for index in clusts:
			clu = clusters_complet[index]
			clu['node_parent']=above_propre.get(index,'')
			clu['node_child']=','.join(list(map(str,below_propre.get(index,[]))))
			clu['level']=int(level)
			
			if int(level)==0:
				if pos_type=='from_below':
					clu['x']= pos_x[index]
				clu['y']=clu['periode']
	 		else:#pour les nouveaux noeuds on complète les informations.
				clu['periode']=clusters_complet[below_propre[index][0]]['periode']
				clu['y']=clu['periode']
				clu['epaisseur'] = sum(get_attribute(below_propre[index],'epaisseur',clusters_complet,0.))
				if pos_type=='from_below':
					clu['x'] = sum(get_attribute(below_propre[index],'x',clusters_complet,0.))/float(len(below_propre[index]))
				clu['concepts'] = merge_list_list(get_attribute(below_propre[index],'concepts',clusters_complet,{}))
				# print "level"+str(level)
				# for x in below_propre[index]:
				# 	print clusters_complet[x]['level']
				clu['sc_lab']=merge_dicts_list(get_attribute(below_propre[index],'sc_lab',clusters_complet,{}))
				dia_below = merge_dicts_list(get_attribute(below_propre[index],'dia',clusters_complet,{}))
				dia_below_above={}
				for x,val in dia_below.iteritems():
					dia_below_above[above_propre[x]]=dia_below_above.get(above_propre[x],0.)+val
				clu['dia']=dia_below_above				
				syn_below = merge_dicts_list(get_attribute(below_propre[index],'syn',clusters_complet,{}))
				syn_below_above={}
				for x,val in syn_below.iteritems():
					syn_below_above[above_propre[x]]=val
				clu['syn']=syn_below_above
				clu['label'] = return_label(clu['sc_lab'],2)#on assigne un label composé des 40 premiers termes à l'échelle du noeud			
			clusters_complet[index] = clu
		
	#on prépare la liste des liens asyncrhones au niveau 0
	for id_univ,clu in clusters.iteritems():
		#clusters[id_univ]['label_nodes'] = return_label(scores_label[id_univ],40)#on assigne un label composé des 40 premiers termes à l'échelle du noeud		
		if 'dia' in clu:#on traite les liens asynchro
			voisins = clu['dia']
			for voisin,stre in voisins.iteritems():
				liens_totaux_dia_0.append((id_univ,voisin,stre))
	
	#labellisation effective des liens sur l'ensemble des clusters
	label_edges={}
	for id_univ,clu in clusters_complet.iteritems():
		if 'dia' in clu:#on traite les liens asynchro
			voisins = clu['dia']
			sc_lab_1 = clu['sc_lab']
			level = clu['level']
			for voisin,stre in voisins.iteritems():
				sc_lab_2 = clusters_complet[voisin]['sc_lab']
				label_edges[id_univ,voisin]=return_label(merge_dicts_list([sc_lab_1,sc_lab_2]),level+2)#on assigne un label sur chaque lien intertemporel
				
	
	#enfin, on efface sc_lab qui est inutile maitenant ainsi que clu['label'] remplacé par clu['label_node'], on rajoute également les attributs nb_sons, nb_fathers
	for id_univ,clu in clusters_complet.iteritems():
		if not 'nb_fathers' in clusters_complet[id_univ]:
			clusters_complet[id_univ]['nb_fathers']=0
		clusters_complet[id_univ]['nb_sons']=0
		del clu['sc_lab']
		if 'dia' in clu:
			clusters_complet[id_univ]['nb_sons'] = len(clu['dia'].keys())
			for pere in clu['dia'].keys():
				clusters_complet[pere]['nb_fathers']=clusters_complet[pere].get('nb_fathers',0)+1
	
	#on reconstruit la composition micro; la position et les labels des métachamps.
	
	# #on dump.
	# 	fonctions.dumpingin(liens_totaux_syn_0,'liens_totaux_syn' + str(orphan_number))
	# 	fonctions.dumpingin(liens_totaux_dia_0,'liens_totaux_dia'+ str(orphan_number))
	# 	fonctions.dumpingin(label_edges,'liens_totaux_label'+ str(orphan_number))
	# 	#fonctions.dumpingin(clusters,'clusters'+ str(orphan_number))
	# 	fonctions.dumpingin(years_bins,'years_bins'+ str(orphan_number))
	# fonctions.dumpingin(nb_level,'nb_level' + str(orphan_number))
	# fonctions.dumpingin(clusters_complet,'clusters_complet' + str(orphan_number))
	# fonctions.dumpingin(label_edges,'label_edges' + str(orphan_number))
	# fonctions.dumpingin(years_bins,'years_bins' + str(orphan_number))
	
	
	
	# export_json(clusters_complet,label_edges,years_bins,nb_level)
	
	
	pos_type='chelou'
	if pos_type=='chelou':
		print 'in chelou'
		target_level=9
		#1. on construit le squelette
		cluster_level_target = filter_level(clusters_complet,target_level)#on sélectionne
		cluster_level_target = symetric_links(cluster_level_target)#on symétrise
		cluster_level_target = strongest_link(cluster_level_target)#on sélectionne le lien maximal.
		#connected_components=connected_comp(cluster_level_target)
		
		#network_layout.plot_graph_pos(cluster_level_target,59929)
		
		#on dégage les composantes connexes
		G  = network_layout.get_G(cluster_level_target)
		components = {}
	 	for i,x in enumerate(network_layout.connect(G)):
			components[i]=x
		
		
		
		#on calcule les liens entre composantes
		distance_components,components_belong = averag(components,cluster_level_target)
		print str(len(distance_components.keys())) + ' composantes !!!'

		#
		#network_layout.plot_graph_G(G,vpos,float(i+1))
		
		import networkx as nx

		import numpy as np
		import matplotlib.pyplot as plt
		#spatialisation en 2d puis projection sur 0x

		G,vpos  = spring.get_G_pos_random(distance_components)
		widthw=[]
		for x,y in G.edges():
			widthw.append(G[x][y]['weight']*10)
		pos2d=nx.drawing.layout.spring_layout(G, dim=2, pos=None, fixed=None, iterations=80, weighted=True, scale=1)
	
		network_layout.plot_graph_G(G,pos2d,'dim2')
		print 'les positions des composantes connexes de départs sont les suivantes:'
		for x in pos2d:
			print x,pos2d[x][0]
		

		#spatialisation directement en 1d
		# G,vpos  = spring.get_G_pos_random(distance_components)
		# print vpos
		# #pos2d=nx.drawing.layout.spring_layout(G, dim=1, pos=None, fixed=None, iterations=500, weighted=True, scale=1)
		# pos2d = spring.spring_layout_1d(G, iterations=200, dim=2, node_pos=vpos,t=1)
		# pos1d=spring.get_random_pos(G)
		# j=0
		# for x in pos1d:
		# 	j+=1
		# 	pos1d[x][0]=pos2d[x][0]
		# 	pos1d[x][1]=0 + float(j)/50
		# print pos1d
		# nx.draw(G,node_size=10,pos=pos1d,width=widthw)
		# plt.savefig(path_req + str('dim1') + '.png')
		
		# for i in range(4):
		#  	vposh = spring.spring_layout_1d(G, iterations=200, dim=2, node_pos=vpos,t=0.2)
		#  	network_layout.plot_graph_G(G,vposh,float(i+1))
		
		# 
		# 
		# #puis on étend le réseau
		
		G_total = network_layout.get_G(cluster_level_target,syn=True)
		posxy = spring.get_random_pos(G_total)
		posx = {}
		print 'avant la mise à jour\n'	
		for x in cluster_level_target:
			dico=posxy[x]
			dico[0]=pos2d[components_belong[x]][0] + random.randint(1, 20)/1000
			dico[1]=cluster_level_target[x]['periode']
			posxy[x] = dico
		print 'aprus la mise à jour et avant spatialisation'						
		network_layout.plot_graph_G(G_total,posxy,'initial pos')
		
		print '\n'						
		vpos = spring.spring_layout_1d(G_total, iterations=20, dim=2, node_pos=posxy,t=0.05)
		print 'aprus la spatialisation\n'						
		vpos=normalize_pos(vpos)
		network_layout.plot_graph_G(G_total,vpos,'niveau target spatial')
		
		levels_below = range(target_level+1)
		levels_below.reverse()
		for i in levels_below:
			print 'level',i
			attributed={}
			cluster_level_target = filter_level(clusters_complet,i)#on sélectionne
			if i<target_level:
				for index,clu in cluster_level_target.iteritems():
					syn = clu.get('syn',{})
					synk = syn.keys()
					above = above_propre[index]
					belows = below_propre[above]
					allowed_above = clusters_complet[above]['syn'].keys()
					allowed=[]
					for a in allowed_above:
						allowed += below_propre[a]
				#	print 'allowed',allowed
				#	print 'synk',synk
					for k in synk:
						if k not in allowed:
							del(syn[k])
					
					dia = clu.get('dia',{})
					diak = dia.keys()
					above = above_propre[index]
					belows = below_propre[above]
					allowed_above = clusters_complet[above]['dia'].keys()
					allowed=[]
					for a in allowed_above:
						allowed += below_propre[a]
				#	print 'allowed',allowed
				#	print 'diak',diak

					for k in diak:
						if k not in allowed:
							del(dia[k])
					
					print index,len(synk),len(syn.keys())
					cluster_level_target[index]['syn']=syn
					cluster_level_target[index]['dia']=dia
				
				G_total = network_layout.get_G(cluster_level_target,syn=True)
				posxy = spring.get_random_pos(G_total)
				posx = {}
				print 'avant la mise à jour\n'	
				for x in cluster_level_target:
					above=above_propre[x]
					under_card=len(below_propre[above])
					if under_card==1:
						posxy[x][0]=vpos[above][0]
						posxy[x][1]=vpos[above][1]
					else:

						places=range(-under_card,under_card)
						posxy[x][0]=vpos[above][0] + places[2*attributed.get(above,0)] * float(i) * 0.003
						posxy[x][1]=vpos[above][1]
						attributed[above]=attributed.get(above,0)+1
				print 'aprus la mise à jour et avant spatialisation'						
				network_layout.plot_graph_G(G_total,posxy,'initial pos'+str(i))

				print '\n'						
				vpos = spring.spring_layout_1d(G_total, iterations=float(4), dim=2, node_pos=posxy,t=0.05/(target_level-i))
				print 'aprus la spatialisation\n'						
				vpos=normalize_pos(vpos)
				network_layout.plot_graph_G(G_total,vpos,'niveau target spatial' + str(i))
			
			for index,clu in  cluster_level_target.iteritems():
				clu['x']=vpos[index][0]
				clu['y']=vpos[index][1]
				clu['dia']=cluster_level_target[index]['dia']
				clu['syn']=cluster_level_target[index]['syn']
				clusters_complet[index]=clu
			
	
	
		machin=json.dumps(dumpjson(clusters_complet,target_level))
		file_out = open('/Users/jean-philippecointet/Dropbox/cortext/tubes/tubes.json','w')
		file_out.write(machin)

	
	
	
	
	
	
	
	
	
	
	
	
	
	# 
	# 
	# for i in range(nb_level+1):
	# 	cluster_level={}
	# 	cluster_level = filter_level(clusters_complet,i)
	# 	years_cover=[]
	# 	j = 0
	# 	# for x,clu in cluster_level.iteritems():
	# 	# 	j=j+1
	# 	# 	years_cover.append(clu['nb_fathers'])
	# 	print len(cluster_level.keys())
	# 	print count_links(cluster_level)
	# 	network_layout.plot_graph_pos(cluster_level,i)
	# 	
	# 	
		#print j,count_dist(years_cover)
	# print 'periodes'
	# for level,clusts in clusters_level.iteritems():
	# 	print level
	# 	y=[]
	# 	for x in clusts:
	# 		y.append(clusters_complet[x]['periode'])
	# 	print count_dist(y)
	# print 'nb_under'		
	# for level,clusts in clusters_level.iteritems():
	# 	print level
	# 	y=[]
	# 	for x in clusts:
	# 		y.append(len(below_propre.get(x,[])))
	# 	print count_dist(y)
		
	# for x,clu in clusters_complet.iteritems():
	# 	#if x<400 and x>390:
	# 		#print x, clusters_complet[x]
	# 		#print clusters_complet[x].keys()
	# 	if 'dia' in clu:
	# 		links = clu['dia']
	# 	
	# 		for l in links:
	# 			if l in clusters_level[clu['level']]:
	# 				print 'ok'
	# 			else:
	# 				print 'aïe'
	# 



