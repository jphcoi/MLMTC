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
	
def h_clustering(clusters):
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


	nb_level = 6
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
	Z = average(dist_tot)
	#print Z
	print '***on calcule le dendrogramme associe'
	#dd = dendrogram(Z)
	#matplotlib.pyplot.show()
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
	dessus= above[index]
	while not dessus in pertinents:
		dessus = above[dessus]
	return dessus

def get_attribute(list_index,attribute,clusters_complet,type={}):
	attributes=[]
	for x in list_index:
		attributes.append(clusters_complet[x].get(attribute,type))
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
		total_list+=x
	return total_list
	
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
		clusters[x]['epaisseur']=y

	liens_totaux_syn_0=[]
	liens_totaux_dia_0=[]
	scores_label={}
	
	#on ordonne les distances dans l'ordre croissant
	clusters,clusters_level,below,above=h_clustering(clusters)
	#print below
	#print above
	#on nettoie above et below qui contiennent des clusters inutiles, et on complète clusters avec les champs que l'on vient de créer.
	above_propre={}
	below_propre={}
	clusters_complet={}
	for level,clusts in clusters_level.iteritems():
		print 'level:'+str(level)+':'+str(len(clusts))+' nodes\n'		
		for index in clusts:
			if index in above:
				dessus = recup(above,index,clusters_level[level+1]) 
				above_propre[index] = dessus
				below_propre.setdefault(dessus,[]).append(index)
			
					
	#on a bien identifié la composition des champs niveau après niveau. 
	#Il ne reste plus qu a calculer les labels de ces champs puis leur position, mais on spatialise d abord a partir du niveau 0
	
	#on prépare d'abord les scores des labels des noeuds du niveau 0
	for id_univ,clu in clusters.iteritems():
		sc_lab = score_label(res_termes[clu['periode']],clu['concepts'])
		scores_label[id_univ]=sc_lab
		clusters[id_univ]['sc_lab'] = sc_lab
	print 'label scores computed for every clusters'
	
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
			clu = clusters.get(index,{})
			clu['node_parent']=above_propre.get(index,'')
			clu['node_child']=','.join(list(map(str,below_propre.get(index,[]))))
			clu['level']=int(level)
 			if level>0:#pour les nouveaux noeuds on complète les informations.
				clu['periode']=clusters_complet[below_propre[index][0]]['periode']
			#	138 {'periode': 7, 'level': 0, 'node_parent': 223, 'epaisseur': 10.165800510883372, 'syn': {137: 0.59753930429199997, 139: 0.65850649307499998, 140: 0.52342390664600003}, 'dia': {171: 42.460694525999997, 174: 34.644702170000002}, 'concepts': [329, 387, 5, 140, 235, 21, 42, 341], 'node_child': '', 'nb_fathers': 1, 'label': u'porc --- s\xe9curit\xe9 sanitaire', 'nb_sons': 1}
				clu['epaisseur'] = sum(get_attribute(below_propre[index],'epaisseur',clusters_complet,0.))
				
				clu['syn']=merge_dicts_list(get_attribute(below_propre[index],'syn',clusters_complet))
				clu['dia']=merge_dicts_list(get_attribute(below_propre[index],'dia',clusters_complet))
				clu['concepts'] = merge_list_list(get_attribute(below_propre[index],'concepts',clusters_complet))
				clu['sc_lab']=merge_dicts_list(get_attribute(below_propre[index],'sc_lab',clusters_complet))
				
				dia_below = merge_dicts_list(get_attribute(below_propre[index],'dia',clusters_complet))
				dia_below_above={}
				for x,val in dia_below.iteritems():
					dia_below_above[above[x]]=val
				#print 'dia',dia_below,dia_below_above
				clu['dia']=dia_below_above
				
				syn_below = merge_dicts_list(get_attribute(below_propre[index],'syn',clusters_complet))
				syn_below_above={}
				for x,val in syn_below.iteritems():
					syn_below_above[above[x]]=val
				clu['syn']=syn_below_above
				clu['label_nodes'] = return_label(scores_label[id_univ],level+2)#on assigne un label composé des 40 premiers termes à l'échelle du noeud			
			clusters_complet[index] = clu
	nb=0
	
	for level,clusts in clusters_level.iteritems():
		print 'level:'+str(level)+':'+str(len(clusts))+' nodes\n'		

		for index in clusts:
			try:
				print level,clusters_complet[below_propre[index][0]]['level']
			except:
				pass

			try:
				print level,clusters_complet[above_propre[index][0]]['level']
			except:
				pass


	#on prépare la liste des liens asyncrhones au niveau 0
	for id_univ,clu in clusters.iteritems():
		#clusters[id_univ]['label_nodes'] = return_label(scores_label[id_univ],40)#on assigne un label composé des 40 premiers termes à l'échelle du noeud		
		if 'dia' in clu:#on traite les liens asynchro
			voisins = clu['dia']
			for voisin,stre in voisins.iteritems():
				liens_totaux_dia_0.append((id_univ,voisin,stre))
	try:
		pos=fonctions.dumpingout('pos'+ str(orphan_number))
		
		
	except:
		pos = network_layout.get_pos(liens_totaux_syn_0,liens_totaux_dia_0,clusters)
		fonctions.dumpingin(pos,'pos'+ str(orphan_number))
	
	
	
	#on moyenne les positions et on calcule les label_edges
	pos_x={}
	for index,x in pos.iteritems():
		pos_x[index] = x[0]
	print pos_x
	h=0
	for level,clusts in clusters_level.iteritems():
		print 'level:'+str(level)+':'+str(len(clusts))+' nodes\n'		
		for index in clusts:
			h +=h
			clu = clusters_complet[index]
			
			if index in pos_x:
				clu['x'] = pos_x[index]
			else:
				pos_moy=[]
				for under in below_propre[index]:
					pos_moy.append(clusters_complet[under]['x'])					
				clu['x'] = sum(pos_moy) / float(len(pos_moy))
			clusters_complet[index] = clu

	print h
	print len(clusters_complet.keys())
	
	#for id,clu in clusters_complet.iteritems():
#		if id>0 and id<310:
			#print id
			#for voisin,stre in clu['syn'].iteritems():
				#print clusters_complet[voisin]['x'],stre

	#labellisation effective des liens sur l'ensemble des clusters
	label_edges={}
	for id_univ,clu in clusters_complet.iteritems():
		#clusters[id_univ]['label_nodes'] = return_label(scores_label[id_univ],40)#on assigne un label composé des 40 premiers termes à l'échelle du noeud		
		if 'dia' in clu:#on traite les liens asynchro
			voisins = clu['dia']
			sc_lab_1 = clu['sc_lab']
			for voisin,stre in voisins.iteritems():
			#	print voisin
			#	print clusters_complet[voisin]
				sc_lab_2 = clusters_complet[voisin]['sc_lab']
			#	print sc_lab_2
				label_edges[id_univ,voisin]=return_label(merge_dicts_list([sc_lab_1,sc_lab_2]))#on assigne un label sur chaque lien intertemporel
				

	
				
				
	
	
	
	
	#on reconstruit la composition micro; la position et les labels des métachamps.

	#on dump.
	fonctions.dumpingin(liens_totaux_syn_0,'liens_totaux_syn' + str(orphan_number))
	fonctions.dumpingin(liens_totaux_dia_0,'liens_totaux_dia'+ str(orphan_number))
	fonctions.dumpingin(label_edges,'liens_totaux_label'+ str(orphan_number))
	#fonctions.dumpingin(clusters,'clusters'+ str(orphan_number))
	fonctions.dumpingin(years_bins,'years_bins'+ str(orphan_number))




		

