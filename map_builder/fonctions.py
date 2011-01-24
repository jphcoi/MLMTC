#!/usr/bin/python
# -*- coding: utf-8 -*-
#recupere les liens des trois reseaux pour exporter les reseaux au format texte
import sys
import math
import gexf
sys.path.append("../scripts/libraries")
sys.path.append("../scripts")


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
import gexf
from datetime import timedelta
from datetime import date
import pickle
import pprint
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
treetagger_dir =parameters.treetagger_dir
years_bins = parameters.years_bins
dist_type=parameters.dist_type

def build_dico():
	lesidstermes = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'concepts','id')
	lestermes = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'concepts','forme_principale')
	dico_termes ={}
	for x,y in zip(lesidstermes,lestermes):
		dico_termes[x[0]]=y[0]
	print 'dictionnaire des termes écrit, taille: '+str(len(dico_termes))
	return dico_termes
	
def lexique():
	lesidstermes = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'concepts','id')
	lestermes = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'concepts','forme_principale')
	dico_termes ={}
	for x,y in zip(lesidstermes,lestermes):
		dico_termes[x[0]]=y[0]
	return dico_termes

def ecrire_reseau(dist_mat,years_bins,dist_type,seuil,niveau,legende_noeuds):		 
	for inter  in range(len(years_bins)):
		try:
			os.mkdir(path_req+'reseau')
		except:
			pass
		fichier=open(path_req + 'reseau'  +'/' + 'reseau_' + 'niv_' + str(niveau) + '_' + dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt','w')
		for x,y in dist_mat.iteritems():
			if x[2]==inter:
				if float(dist_mat[x])>seuil:
					fichier.write(legende_noeuds[(inter,x[0])].replace(' ','_') + '\t' + legende_noeuds[(inter,x[1])].replace(' ','_') + '\t' + str(y) + '\n')
		print '------- fichier: ' +str('reseau_'+dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt')+ ' ecrit dans le repertoire: '+path_req + 'reseau/'

def ecrire_reseau_CF(dist_mat,years_bins,dist_type,seuil,niveau):		 
	for inter  in range(len(years_bins)):
		try:
			os.mkdir(path_req+'reseau')
		except:
			pass
		fichier_CF=open(path_req +'reseau' + '/'+ 'reseauCF_'+'niv_'+str(niveau)+'_'+dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt','w')
		for x,y in dist_mat.iteritems():
			if x[2]==inter:
				if float(dist_mat[x])>seuil:
					fichier_CF.write(str(x[0])+ '\t' + str(x[1]) + '\t' + str(y) + '\n')
#					print 'out'
		print '------- fichier: ' +str('reseauCF_'+dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt')+ ' ecrit dans le repertoire: '+path_req + 'reseau/'

def ecrire_dico(champs,dico_transition,dico_termes,niveau):

	for inter  in range(len(years_bins)):
		try:
			os.mkdir(path_req+'lexique')
		except:
			pass
		try:
			os.mkdir(path_req+'legendes')
		except:
			pass
		fichier=open(path_req + 'lexique'  +'/' + 'lexique_' + 'niv_' + str(niveau) + '_' + dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt','w')
		fichier_os=open(path_req + 'lexique'  +'/' + 'lexique_one_step_' + 'niv_' + str(niveau) + '_' + dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt','w')
		
		if niveau==1:
			fichier_leg=open(path_req + 'legendes'  +'/' + 'legendes' + 'niv_' + str(niveau) + '_' + dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt','w')
		#print champs
		for x,y in champs.iteritems():
			if niveau==1:
				fichier.write(str(x)+'\t'+str(x)+'\n')
				fichier_leg.write(str(x)+'\t'+dico_termes[x]+'\n')
				fichier_os.write(str(x)+'\t'+str(x)+'\n')
			else:# version 1er niveau, la matrice de transition c'est simplement x->x!
				if x==inter:
					for ch in y:
						chaine = ''
						chaine_os=''
						for te in ch:
							chaine_os = chaine_os + str(te) + ' '
							for temoins in dico_transition[(inter,int(te))]:
								chaine = chaine + str(temoins) + ' '
						fichier.write(str(y.index(ch))+'\t'+ chaine[:-1]+'\n')
						fichier_os.write(str(y.index(ch))+'\t'+ chaine_os[:-1]+'\n')
	#	print '------- fichier: reseau_' +str( 'lexique'  +'/' + 'lexique_' + 'niv_' + str(niveau) + '_' + dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt')+ ' ecrit dans le repertoire: '+path_req + 'lexique/'
	#	print '------- fichier: reseau_' +str( 'lexique'  +'/' + 'lexique_one_step_' + 'niv_' + str(niveau) + '_' + dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt')+ ' ecrit dans le repertoire: '+path_req + 'lexique/'

def ecrire_legende(champs,legendes,legendes_id,niveau,years_bins):
	for inter  in range(len(years_bins)):
		try:
			os.mkdir(path_req+'legendes')
		except:
			pass
		fichier=open(path_req + 'legendes'  +'/' + 'legendes' + 'niv_' + str(niveau) + '_' + dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt','w')
		fichier_id=open(path_req + 'legendes'  +'/' + 'legendes_id_' + 'niv_' + str(niveau) + '_' + dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt','w')
		for x,y in champs.iteritems():
			if x==inter:
				for ch in y:
					fichier.write(str(y.index(ch))+'\t'+str(legendes[(inter,y.index(ch))])+'\n')
					fichier_id.write(str(y.index(ch))+'\t'+' '.join(legendes_id[(inter,y.index(ch))])+'\n')
	



def mean(nums):
	if len(nums):
		return float( sum(nums) / len(nums))
	else:
		return 0.0

def calcul_distance_moy(champ1,champ2,dist_mat,inter1):
	dist = 0.
	inter1= int(inter1)
	if len(champ1)>0 and len(champ2)>0:
		for terme1 in champ1:
			for terme2 in champ2:
				if terme1==terme2:
					dist1=dist+1
				else:
					dist = dist+float(dist_mat.get((int(terme1),int(terme2),int(inter1)),0))
		dist=float(dist)/(len(champ1)*len(champ2))
	return dist

def calcul_distance(champ1,champ2,dist_mat,inter,type_distance='moy'):
	dist = 0.
	inter= int(inter)
	if len(champ1)>0 and len(champ2)>0:
		for terme1 in champ1:
			terme1=int(terme1)
			dist1=[]
			for terme2 in champ2:
				terme2=int(terme2)
				if terme1==terme2:
					dist1.append(1)
					#ce sont des similarites que l'on regarde
				else:
					dist1.append(float(dist_mat.get((terme1,terme2,inter),0)))
			if type_distance=='max':
				dist=dist+max(dist1)
			elif type_distance=='moy':
				dist=dist+mean(dist1)
			elif type_distance=='min':
				dist=dist+min(dist1)
		dist=float(dist)/(len(champ1))
	return dist


def map_champs(champs0,dist_mat,type_distance):
	#version simple de la distance entre champs prise comme une moyenne terme à terme:
	distance_champ={}
	for inter1,champs1 in champs0.iteritems():
		for champ1 in champs1:
			for inter2,champs2 in champs0.iteritems():
				for champ2 in champs2:
					if inter2==inter1 and champ1 != champ2:
						#dist = calcul_distance_moy(champ1,champ2,dist_mat,inter1)
						dist = calcul_distance(champ1,champ2,dist_mat,inter1,type_distance)
						distance_champ[(champs1.index(champ1),champs2.index(champ2),inter1)]=dist
	return distance_champ	
	

def dumpingin(data,datastr):
	try:
		os.mkdir('../../inout/pkl/'+requete)
	except:
		pass
	output = open('../../inout/pkl/'+requete+'/'+datastr+'.pkl', 'wb')
	# Pickle dictionary using protocol 0.
	pickle.dump(data, output)
	output.close()


def dumpingout(datastr):
	pkl_file = open('../../inout/pkl/'+requete+'/'+datastr+'.pkl', 'rb')
	data = pickle.load(pkl_file)
	return data

def invert_dict(d):
    return dict([(v, k) for k, v in d.iteritems()])

def get_label_annees(inter):
	annees = years_bins[inter]
	annee_d=str(annees[0])
	annee_f=str(annees[-1])
	return annee_d + ' '+annee_f


def ecrire_tables_cluster_phylo(nodes,edges,sortie,level,time,attribut,sonsbis,fathersbis,dico_termes,indexs_inv,map_dessous,transition,sep_label):
	dico_termes_inv = invert_dict(dico_termes)
	transition_inv = invert_dict(transition)
	variables_cluster=[]
	variables_phylo=[]
	variables_maps=[]
	try:
		print 'path_req' + 'site'
		os.mkdir(path_req + 'site')
	except:
		pass
	
	fichier_dot=open(path_req + 'site'  +'/' + 'ExportPhyloDetails.dot','w')	
	fichier_dot.write('digraph arbre_phylogenetique {\n')
	labels_annees=[]
	ranks = {}	
	for idx,lab in nodes.iteritems():
		#print idx
		id_cluster_univ=transition_inv[idx]
		tim = time[idx]
		lev = level[idx]
		att = attribut[idx]
		son = sonsbis[idx]
		fat = fathersbis[idx]
		labv = lab.split(sep_label)
		labv.sort()
		lab1 = labv[0]
		lab2 = labv[1]
		
		lab_1 = dico_termes_inv[lab1]
		lab_2 = dico_termes_inv[lab2]
		label_annee = get_label_annees(tim)
		index_local = indexs_inv[id_cluster_univ]
		[niv,numero,inter] = index_local.split('_')
		if not label_annee in labels_annees:
			labels_annees.append(label_annee)
			
			ranks[str(tim)]=['P' + str(tim)]
			fichier_dot.write('P' + str(tim) +' [shape = rect ,fontsize=22,label="'+label_annee.replace(' ','-')+ '"]\n')
			if len(labels_annees)>1:
				fichier_dot.write('P' + str(tim) + ' -> ' + mem + '\n')
			mem = 'P' + str(tim)
			fichier_dot.write
		temp =  ranks[str(tim)]
		temp.append('C' + str(tim) + '_' + str(numero))
		ranks[str(tim)]=temp
		fichier_dot.write('C' + str(tim) + '_' + str(numero)  +'  [style=filled,fontname=Arial,fontsize=12,peripheries=2,color=lightblue2    ,shape=rect, label="')
		for con in map_dessous[id_cluster_univ]:
			con = indexs_inv[con].split('_')[1]
			variables_cluster.append([idx,numero,lab_1,lab_2,lab,att,lev,label_annee,fat,son,idx,con])
			fichier_dot.write('\\n'+dico_termes[int(con)])
		fichier_dot.write('",fontsize=12]\n')
			
	#	ex('CREATE TABLE '+ name_table +' (id INTEGER ,id_cluster INTEGER,label_1 INTEGER,label_2 INTEGER,label VARCHAR(300),attribut VARCHAR(300),level INTEGER,periode VARCHAR(50),concept INT, pseudo VARCHAR(10), cluster_size INT, density VARCHAR(10), nb_fathers INT, nb_sons INT, lettre VARCHAR(3), identifiant_unique VARCHAR(20))')
	variables_cluster_names = "(id_cluster_univ,id_cluster,label_1,label_2,label,attribut,level,periode,nb_fathers , nb_sons,identifiant_unique,concept)"#concept,pseudo , cluster_size , density ,  lettre , ))"
	fonctions_bdd.remplir_table(name_bdd,'cluster',variables_cluster,variables_cluster_names)
	
	for source,streng in edges.iteritems():
		id_cluster_1_univ=transition_inv[source[0]]
		id_cluster_2_univ=transition_inv[source[1]]
		[niv_1,id_cluster_1,inter_1] = indexs_inv[id_cluster_1_univ].split('_')
		[niv_2,id_cluster_2,inter_2] = indexs_inv[id_cluster_2_univ].split('_')
		label_annee_1 = get_label_annees(int(inter_1))
		label_annee_2 = get_label_annees(int(inter_2))
		if niv_1 == niv_2:
			if inter_1 == inter_2:
				variables_maps.append([id_cluster_1,label_annee_1,source[0],id_cluster_2,label_annee_2,source[1],str(streng)])
				#print streng
				#activer liens intra temporelles
				#if float(streng)>0.:			
					#fichier_dot.write('C'+str(inter_1) + '_' + str(id_cluster_1) + '->' + 'C'+str(inter_2) + '_' + str(id_cluster_2) + ' '  + '[style="setlinewidth(2)",color=green]\n')
			else:
				variables_phylo.append([id_cluster_1,label_annee_1,source[0],id_cluster_2,label_annee_2,source[1],str(streng)])
				fichier_dot.write('C'+str(inter_1) + '_' + str(id_cluster_1) + '->' + 'C'+str(inter_2) + '_' + str(id_cluster_2) + ' '  + '[style="setlinewidth(2)",color=red]\n')
	for inter,ra in ranks.iteritems():
		fichier_dot.write('{rank=same;')
		for x in ra:
			fichier_dot.write(str(x)+' ')
		fichier_dot.write('}\n')
	fichier_dot.write('}\n')
	variables_phylo_names = "(id_cluster_1,periode_1,id_cluster_1_univ,id_cluster_2,periode_2,id_cluster_2_univ,strength)"
	variables_maps_names = "(id_cluster_1,periode_1,id_cluster_1_univ,id_cluster_2,periode_2,id_cluster_2_univ,strength)"
	fonctions_bdd.remplir_table(name_bdd,'phylo',variables_phylo,variables_phylo_names)
	fonctions_bdd.remplir_table(name_bdd,'maps',variables_maps,variables_maps_names)


def seuiller(res,degmax):
	res_seuil = {}
	for terme in res:
		l = res[terme].items()
		l.sort(key=itemgetter(1),reverse=True)
		res_seuil[terme]=l[:degmax] 
	return res_seuil