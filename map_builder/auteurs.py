#!/usr/bin/python
# -*- coding: utf-8 -*- 
import os
import sys
sys.path.append("../scripts/libraries")
sys.path.append("../scripts")

print "socio-semantic analysis v0.1 (20100220)"
print "--------------------------------\n"

import fonctions_bdd
import parameters
import os
import sys
import math
import gexf
import fonctions
import pickle
import pprint

path_req = parameters.path_req
years_bins = parameters.years_bins
name_bdd = parameters.name_bdd
path_req=parameters.path_req
timelimit='1'
requete = parameters.requete


dist_type=parameters.dist_type
sep_label = ' --- '



def load_dico():
	try:	
		dico_auteurs = fonctions.dumpingout('dico_auteurs')
	except:	
		lesauteurs = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'auteurs','auteurs')
		lesidsauteurs = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'auteurs','id')
		dico_auteurs ={}
		for x,y in zip(lesidsauteurs,lesauteurs):
			dico_auteurs[x[0]]=y[0]
		fonctions.dumpingin(dico_auteurs,'dico_auteurs')
	return dico_auteurs
	
	

def load_contenu_socsem():
	try:
		auteurs_billets = fonctions.dumpingout('auteurs_billets')
		contenu_socsem =fonctions.dumpingout('contenu_socsem')
	except:
		contenu_socsem = fonctions_bdd.select_bdd_table(name_bdd,'socsem','auteur,concept,jours,id_b',requete)
		auteurs_billets={}
		#auteurs_billets associe à chaque auteur les billets auxquels il a contribué
		for cont in contenu_socsem:
			auteur = cont[0]
			id_b = cont[3]
			if auteurs_billets.has_key(auteur):
				temp=auteurs_billets[auteur]
				if not id_b in temp:
					temp.append(id_b)
					auteurs_billets[auteur] = temp
			else:
				arr = []
				arr.append(id_b)
				auteurs_billets[auteur] = arr
		fonctions.dumpingin(contenu_socsem,'contenu_socsem')
		fonctions.dumpingin(auteurs_billets,'auteurs_billets')
	return auteurs_billets,contenu_socsem





def select_auteurs_pertinent(auteurs_billets,nb_art):
	auteurs_pert=[]
	for x,y in auteurs_billets.iteritems():
		if len(y)>nb_art:
			auteurs_pert.append(x)
			#print dico_auteurs[x]
	return auteurs_pert


def load_distance_mat():
	try:
		dist_mat = fonctions.dumpingout('dist_mat')
	except:
		import context_process
		dist_mat = context_process.dist_mat#on recupere la matrice de distance entre termes
		fonctions.dumpingin(dist_mat,'dist_mat')
	print 'matrice de distance importée'
	return dist_mat
		


#pprint contenu_socsem
def def_intervalle(jou,years_bins):
	inter=-1
	for x in years_bins:
		inter+=1
		if jou in x:
			return inter
			
def bagage_sem(contenu_socsem,auteurs_pert):
	soc_sem = {}
	for x in auteurs_pert:
		for y in range(len(years_bins)):
			soc_sem[(x,y)]=[]
	for cont in contenu_socsem:
		aut,con,jou = cont[0],cont[1],cont[2]
		if aut in auteurs_pert:
			inter = def_intervalle(jou,years_bins)
			temp = soc_sem.get((aut,inter),[])
			temp.append(con)
			soc_sem[(aut,inter)]=temp
	return soc_sem 
			
def load_soc_sem():		
	try:
		soc_sem = fonctions.dumpingout('soc_sem')
	except:
		auteurs_billets,contenu_socsem=load_contenu_socsem()
		auteurs_pert = select_auteurs_pertinent(auteurs_billets,6)
		print len(auteurs_pert)
		soc_sem = bagage_sem(contenu_socsem,auteurs_pert)	
		fonctions.dumpingin(soc_sem,'soc_sem')	
	return soc_sem

def load_projection(niv):
	try:
		projection_aut2chp = fonctions.dumpingout('projection_aut2chp_'+str(niv))
		projection_chp2aut = fonctions.dumpingout('projection_chp2aut_'+str(niv))
		
	except:
		dist_mat = load_distance_mat()
		champs=fonctions.dumpingout('champs_'+str(niv))
		#champs[inter] = liste des champs de la période 
		#dist_champ=fonctions.dumpingout('distance_champ_'+str(niv))
		projection_aut2chp ={}
		projection_chp2aut ={}
		for x,bagage in soc_sem.iteritems():
			auteur = x[0]
			inter = x[1]
			champs_inter=champs[inter]
			print x
			for champ in champs_inter:
				dist = fonctions.calcul_distance_max(bagage,champ,dist_mat,inter)
				projection_aut2chp[(auteur,champs_inter.index(champ),inter)]=dist
				dist = fonctions.calcul_distance_max(champ,bagage,dist_mat,inter)
				projection_chp2aut[(champs_inter.index(champ),auteur,inter)]=dist
		fonctions.dumpingin(projection_aut2chp,'projection_aut2chp_'+str(niv))
		fonctions.dumpingin(projection_chp2aut,'projection_chp2aut_'+str(niv))
	return projection_aut2chp,projection_chp2aut


#dico_auteurs = load_dico()
#soc_sem=load_soc_sem()
#niv = 1
#projection_aut2chp,projection_chp2aut = load_projection(niv)


