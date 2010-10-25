#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by  on 2010-10-05.
"""
import sys

sys.path.append("../scripts/libraries")
sys.path.append("../scripts")

import os
import parameters
from hcluster import pdist, linkage, dendrogram,centroid,weighted
import numpy
import fonctions
from numpy.random import rand
import numpy as np
import math
import matplotlib
import matplotlib.pyplot as plt

import fonctions_lib
from class_def import *
path_req = parameters.path_req
years_bins = parameters.years_bins
name_bdd = parameters.name_bdd
path_req=parameters.path_req
timelimit='1'

dist_type=parameters.dist_type

# on peut définir des méthode globales aussi pour toutes les classes.
def aff(tru):
	return 'jkl' + str(tru)



def score_compute(type_score,champ,dist_mat,terme,inter):
#definition du meilleur label d'un champ en fonction des distances entrantes/sortantes de l'ensembles des termes les uns avec les autres
	score_computed = 0.
	interu=unique(inter)
	if type_score=='combine':
		for voisin in champ:
			for inte in interu:
				multi_inter = inter.count(inte)
				din,dout=0,0
				if terme==voisin:
					din,dout=1,1
				else:
				
					din=float(dist_mat.get((terme,voisin,inte),0.))
					dout=float(dist_mat.get((voisin,terme,inte),0.))
				try:
					score_computed = score_computed +  float(float(din*dout)/(din+dout) * float(multi_inter))
				except:
					pass
	return score_computed
	
	
def label(champ,dist_mat,inter,nb_label,champs=[]):
	nb_termes_chp = len(champ)
	score=[]
	#etape 2, on calcule les statistiques du nombre d'apparition des termes dans les champs
	termes=[]
	#termes, c'est pour chaque périoden un vecteur qui aggrège tous les termes qui occurrent eventuellement n fois
	##version avec pondération par le nombre total d'occurrence des termes dans tous les champs
	##for ch in champs:
	##	for ter in ch:
	##		termes.append(ter)
	#print champ
	for terme in champ:
		#print terme
		#version complexe du calcul qui nécessite un décompte précis de la fréquence de présence du terme dans son champ et dans tous les champs, pb, ça change le label en fonction de l'ensemble des champs => on simplifie donc
		##version avec pondération par le nombre total d'occurrence des termes dans tous les champs
		##doc_total = termes.count(terme)
		##doc_champ = champ.count(terme)
		##ratio = (float(doc_champ)/nb_termes_chp) / (float(doc_total)/len(termes))
		##ponderation = math.log10(ratio)
		##version sans la pondération par le nombre total d'occurrence des termes dans tous les champs
		ponderation=1.
		#le ratio c'est la proportion  du terme dans le champ normalisee par sa proportion dans tous les champs 
		#et là on calcule le score a proprement parler:
		if type(inter)==int:
			inter=[inter]
		meilleur_voisin = score_compute('combine',champ,dist_mat,terme,inter)
		meilleur_voisin=meilleur_voisin*ponderation
		score.append(meilleur_voisin)
	#print score 
	scoretrie = score[:]
	scoretrie.sort()
	scomax=[]
	j=0
	label_int_old='-1219129'
	i=-1
	while len(scomax)<nb_label:
		i=i+1
		if champ[int(score.index(scoretrie[-i-1]))] != label_int_old:
			scomax.append(champ[int(score.index(scoretrie[-i-1]))])
			label_int_old = champ[int(score.index(scoretrie[-i-1]))]
			champ.remove(champ[int(score.index(scoretrie[-i-1]))])
			score.remove((scoretrie[-i-1]))
			scoretrie.remove((scoretrie[-i-1]))
			i=i-1
	#temp = scores.get(inter,[])
	#temp.append(scomax)
	#scores[inter] = temp
	return scomax		
	
def obtain_label(termes_ids,inter,champs_termes_ids=[]):	
	terme_comp = []
	for ter in termes_ids:
		terme_comp.append(Terme(ter,dico[ter]))
	terme_comp = Liste_termes(terme_comp)
	#on calcule maintenant le label de nos champs:
	lab = label(termes_ids,dist_mat,inter,2,champs_termes_ids)
	lab_comp=[]
	for la in lab:
		lab_comp.append(Terme(la,dico[la]))
	lab_comp = Liste_termes(lab_comp)
	return lab_comp,terme_comp
	
def construire_champ(termes_ids,numerotation,inter,niveau,champs_termes_ids=[]):
	lab_comp,terme_comp=obtain_label(termes_ids,inter,champs_termes_ids=[])
	#lab_comp.afficher_liste_termes()
	return Champ(numerotation,inter,niveau,lab_comp,terme_comp)

def symmetriser(liste_liens):
	liste_liens_sym={}
	for couple,force in liste_liens.iteritems():
		coupleinv = (couple[1],couple[0])
		moy = float(liste_liens.get(couple,0.) + liste_liens.get(coupleinv,0.)) / 2.
		liste_liens_sym[couple] = moy
		liste_liens_sym[coupleinv] = moy
	return liste_liens_sym
	
def import_cfpipe():
	#simple fonction de recuperation des donnees issues de l'etape de clusterisation
	niveau=2
	champs_liste=[]
	nets={} #dictionnaire des réseaux rangés par période
	for inter in range(len(years_bins)):
		numerotation = -1
		champs_courants={}#indexés par leur id local
		liste_liens={}#dle dictionnaire des couples de champs liés dont la valeur = force
		print " temps : "+str(inter)
		fichier_lex=open(path_req + 'lexique'  +'/' + 'lexique_' + 'niv_' + str(niveau) + '_' + dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt','r')
		print 'on recupere la composition des champs dans: \n\t'+path_req + 'lexique'  +'/' + 'lexique_' + 'niv_' + str(niveau) + '_' + dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt'
		lignes_lex= fichier_lex.readlines()
		#reseau inter-niveau ou plutôt description micro de chaque niveau
		element_dessous=[]
		#etape 1, on liste simplement la compisition des champs et on agrege ça dans champs
		champs_ids=[]
		for ligne in lignes_lex:
			lignev=ligne[:-1].split('\t')
			composition_termes=map(int,lignev[1].split(' '))
			champs_ids.append(composition_termes)
		#etape 3 on réunit toutes les informations utiles sur les champs
		for ligne in lignes_lex:
			lignev=ligne[:-1].split('\t')
			composition_termes=map(int,lignev[1].split(' '))
			numerotation = numerotation + 1
			champs_courants[int(lignev[0])] = construire_champ(composition_termes,numerotation,inter,[numerotation],champs_ids)
		 	
		#	print '**********************'
		#	print champs_courants[int(lignev[0])].print_elements()
		#	print champs_courants[int(lignev[0])].print_label()
		#	print '**********************\n'
			#on a tous nos champs dans champs_courants
		try:
			fichier_res=open(path_req +'reseau' + '/'+ 'reseauCF_'+'niv_'+str(niveau)+'_'+dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt','r')
			print path_req +'reseau' + '/'+ 'reseauCF_'+'niv_'+str(niveau)+'_'+dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt'
		except:
			break
		lignes_res= fichier_res.readlines()
		#reseau à un niveau donné
		for ligne in lignes_res:
			lignev=ligne[:-1].split('\t')
			force_lien = str(lignev[2])
			liste_liens[(champs_courants[int(lignev[0])],champs_courants[int(lignev[1])])]=float(force_lien)
		liste_liens = symmetriser(liste_liens)	
		print champs_courants.values()
		nets[inter] = Network(champs_courants.values(),liste_liens) 
			#map_edges[(indexs[str(niveau)+'_'+lignev[0]+'_'+str(inter)],indexs[str(niveau)+'_'+lignev[1]+'_'+str(inter)])]=str(lignev[2])
					
	return nets


# 
# class Terme(object):
# 	"""Class Terme"""
# 	def __init__(self,index,label):
# 		"""Method docstring."""
# 		self.index = index
# 		self.label=label
# 	def __str__(self):
# 		"""Method docstring."""
# 		return "Terme: index({0}), label({1})".format(self.index, self.label)
# 	def get_label(self):
# 		return self.label
# 	def get_index(self):
# 		return self.index
# 		
# class Dictionnaire_Terme(Terme):
# 	"""Class Dictionnaire de Terme"""
# 	def __init__(self,liste_termes):
# 		"""Method docstring."""
# 		print 'importation du dictionnaire des termes'
# 		self.liste_termes = liste_termes
# 	def __str__(self):
# 		"""Method docstring."""
# 		return "Liste de Termes longueur: {0}".format(str(len(self.liste_termes))) 	
# 
# 
# 	
# class Liste_termes(object):
# 	"""Class Liste de Terme"""
# 	def __init__(self,liste_termes):
# 		self.liste_termes = liste_termes
# 	def afficher_liste_termes(self):
# 		chaine =''
# 		for x in self.liste_termes:
# 			chaine = chaine + ' ' + str(x.label) + ';' 
# 		return chaine[:-1]


def addnfields(fields_liste,idx,inter):
	index=idx
	periode = fields_liste[0].periode
	fields_liste_liste_termes=[]
	nivel = [] 
	for field in fields_liste:
		fields_liste_liste_termes.append(field.termes)
		for niv in field.niveau:
			nivel.append(niv)
	termes = concatener_liste_termes(fields_liste_liste_termes)
	termes_ids =  map(Terme.get_index,termes.liste_termes)
	return construire_champ(termes_ids,index,inter,nivel)
	
		
		 
# 			
# class Champ(Liste_termes):
# 	"""Class Champ."""
# 	def __init__(self,index,periode,niveau,label,termes):
# 		"""Method docstring."""
# 		self.index = index
# 		self.periode=periode
# 		#niveau denombre le nombre de clusters sous-jacents
# 		self.niveau=niveau
# 		self.label=label
# 		self.termes=termes
# 	def __str__(self):
# 		"""Method docstring."""
# 		return "Champ: niveau({0}), periode({1}), label({2},index({3}))".format(self.niveau, self.periode, map(Terme.get_label,self.label.liste_termes),self.index)
# 	def print_elements(self):
# 		"""Method docstring."""
# 		chaine  = '\n\t* champ de la periode ' + str(self.periode)+ ' dont les elements sont: '
# 		chaine =  chaine+self.termes.afficher_liste_termes()
# 		chaine = chaine + ' et le label: ' + Liste_termes.afficher_liste_termes(self.label)
# 		return chaine		
# 		
# class Tube(object):
# 	def __init__(self,liste_champs,label):
# 		"""Method docstring."""
# 		self.liste_champs = liste_champs
# 		self.label=label
# 	def print_elements(self):
# 		"""Method docstring."""
# 		chaine  = '\nTube de label: '+ Liste_termes.afficher_liste_termes(self.label) +' dont les ' + str(len(self.liste_champs))+ ' champ(s) est (sont): '
# 		return chaine  +', '.join(map(Champ.print_elements,self.liste_champs))
# 		
# 		
# class Network(Champ):
# 	"""Class Network, il peut être composé de champs ou de termes"""
# 	def __init__(self,champs_liste,champs_dist):
# 		"""Method docstring."""
# 		self.champs_liste = champs_liste
# 		self.champs_dist = champs_dist
# 	def __str__(self):
# 		"""Method docstring."""
# 		return "Network: nombre de champs({0}), nombre de liens({1})".format(len(self.champs_liste), len(self.champs_dist))
# 	def afficher_champs(self):
# 		for champ in self.champs_liste:
# 			champ.print_label()

def	description_multilevel(Z,champs):
	N = len(champs)
	intersections,origine,dessous={},{},{}
	for x in Z:
		id_champ1 = int(x[0])
		id_champ2 = int(x[1])
		niveau = x[2]
		id_new_champ = N
		N=N+1
		intersections[niveau]=id_new_champ
		dessous[id_new_champ] = (id_champ1,id_champ2)
		temp1 = origine.get(id_champ1,[id_champ1])
		temp2 = origine.get(id_champ2,[id_champ2])
		origine[id_new_champ] = temp1+temp2
	return intersections,origine,dessous

	
def unique(liste):
	liste_u=[]
	for x in liste:
		if not x in liste_u:
			liste_u.append(x)
	return liste_u

def hierarchical_clustering(nets):
	multi_level_dyn_net={}
	for inter,net in nets.iteritems():
		print 'periode : ' + str(inter)
		#print net
		#net.afficher_champs()
		# on veut construire la liste des distances des champs de la periode consideree
		dist_tot = []
		champs_liste = net.champs_liste
		champs_dist = net.champs_dist
		#for x in champs_liste:
		#	print x
		ii = -1
		for champ1 in champs_liste[:-1]:
			ii=ii+1
			for champ2 in champs_liste[ii+1:]:
					dist_tot.append(float(1.-champs_dist.get((champ1,champ2),0.)))			
		Z = weighted(dist_tot)
		N=len(champs_liste)-1
		res_niv_0= Network(champs_liste,champs_dist) 
		multi_level_dyn_net[(inter,0)] = Network(champs_liste[:],champs_dist) 
		
		for ev_fusion in Z:
			N=N+1
			dessous={}
			fusion_couple = [int(ev_fusion[0]),int(ev_fusion[1])]
			fusion_level = ev_fusion[2]
			fields_rm_liste=[]
			for champ in champs_liste[:]:
				if champ.index in fusion_couple:
					champs_liste.remove(champ)
					fields_rm_liste.append(champ)
				else:
					dessous[champ] = [champ]
			new_champ  = addnfields(fields_rm_liste,N,inter)
			#print 'on a construit: ' + str(new_champ)
			dessous[new_champ]=fields_rm_liste
			champs_liste.append(new_champ)
			new_champs_dist={}
			ii = 0 
			for champ1 in champs_liste[:-1]:
				ii=ii+1
				for champ2 in champs_liste[ii:]:
					if champ1 != champ2:
						if (champ1, champ2) in champs_dist:
							new_champs_dist[(champ1, champ2)] = champs_dist[(champ1, champ2)]
							new_champs_dist[(champ2, champ1)] = champs_dist[(champ2, champ1)]
						else:
							stre=0.
							nivel=0
							#print 'fusion des champs'
							#on invese les champs de façon à mettre le fusionne en seconde position
							if len(dessous[champ1])>1:
								champ1_new = champ1
								champ2_new = champ2
								champ1=champ2_new
								champ2=champ1_new
							#print 'premier champ: ' + str(champ1)
							for y in dessous[champ2]:
								#print 'second champ: ' + str(y)
								stre = stre  + champs_dist.get((champ1,y),0.) * float(len(y.niveau))
								nivel = nivel+len(y.niveau)
							#print nivel	
							new_champs_dist[(champ1, champ2)] = stre / float(nivel)
							new_champs_dist[(champ2, champ1 )] = stre / float(nivel)
			champs_dist=new_champs_dist
			multi_level_dyn_net[(inter,fusion_level)] = Network(champs_liste[:],champs_dist) 
	return multi_level_dyn_net

################################################################################################################################################
#Il faudra étendre la fonction de labellisation de façon a ce qu'elle ne dépende plus du temps, inter dans champ...
################################################################################################################################################
#TBD
################################################################################################################################################
#on passe maintenant au mapping inter-temporel des clusters.
################################################################################################################################################

def build_zoom(resolution):
	loupe = range(resolution)
	zoom = []
	for grade in loupe:
		zoom.append(float(grade)/float(resolution))
	return zoom

def nearest_zoom(fusion_level,zoom):
	init = -1
	ii = -1
	while fusion_level>=init:
		ii = ii + 1
		try:
			init = zoom[ii]
		except:
			break
	return zoom[ii-1]
		
##################################
#qqchose pour remplir les niveaux manquants.	Mais sans doute est-ce que ce serait plus facile de faire ça plus tard
##################################

def extension_lev_max(lev_max,zoom):
	for zoo in zoom:
		for inter in range(len(years_bins)):
			if not (inter,zoo) in lev_max:
				lev_max[(inter,zoo)]  = lev_max[(inter,zoom[zoom.index(zoo)-1])]
	return lev_max
	
def get_lev_max(multi_level_dyn_net,zoom):
	lev_max={}
	for couple in multi_level_dyn_net.keys():
		inter = couple[0]
		fusion_level = couple[1]
		nn = nearest_zoom(fusion_level,zoom)
		if not (inter,nn) in lev_max or fusion_level > lev_max[(inter,nn)]:
			lev_max[(inter,nn)] = fusion_level
	return extension_lev_max(lev_max,zoom)

def under_net_termes(liste_terme_chp,inter,seuil):
	res_termes = {}
	for x in liste_terme_chp:
		for y in liste_terme_chp:
			if x!=y:
				if (x.index,y.index,inter) in dist_mat:
					if float(dist_mat[(x.index,y.index,inter)]) > seuil:
						res_termes[(x.index,y.index)] =  res_termes.get((x.index,y.index),0)+1.
			else:
						res_termes[(x.index,y.index)] =  res_termes.get((x.index,y.index),0)+0.5
	return res_termes

def overlap_pondere(x,y):
	poids_total = 0
	poids_comm = 0
	#version jaccard avec les liens:
	for item_x,poid_x in x.iteritems():
		if item_x  in y:
			poids_comm = poids_comm + min(x[item_x],y[item_x])
			poids_total = poids_total + max(x[item_x],y[item_x])
		else:
			poids_total = poids_total + x[item_x]
	for item_y,poid_y in y.iteritems():			
		if not item_y  in x:
			poids_total = poids_total + y[item_y]
	if poids_total>0:
		return float(poids_comm) / float(poids_total)
	else:
		return 0.
		


def find_fathers(ch_now,champs_liste_old,dist_mat,seuil,seuil_intertemp,type_dist_inter):
	periode_now = ch_now.periode	
	periode_old = periode_now - 1
	score_overlap={}
	if type_dist_inter == 'prox':
		inter = ch_now.periode
		liste_chp_old_termes={}
		ch_now_termes_index = map(Terme.get_index,ch_now.termes.liste_termes)
		for i,ch_old in enumerate(champs_liste_old): 
			ch_old_termes_index = map(Terme.get_index,ch_old.termes.liste_termes)
			liste_chp_old_termes[i] = ch_old_termes_index
			score_overlap[i]=(fonctions.calcul_distance(ch_now_termes_index,ch_old_termes_index,dist_mat,inter,'moy')+fonctions.calcul_distance(ch_old_termes_index,ch_now_termes_index,dist_mat,inter,'moy'))/2.
	if type_dist_inter == 'jaccard':	
		# on construit le reseau de termes du champ courant now.
		res_termes_now=under_net_termes(ch_now.termes.liste_termes,periode_now,seuil)
		# res_termes_now est de type liste de liens.
		liste_res_termes_old=[]
		for ch_old in champs_liste_old:
			liste_res_termes_old.append(under_net_termes(ch_old.termes.liste_termes,periode_old,seuil))
		i=-1
		for res_termes_old in liste_res_termes_old:	
			i=i+1
			score_overlap[i] = overlap_pondere(res_termes_now,res_termes_old)
	#score_overlap decrit ici l'overlap en nombre de liens entre clusters passes et futurs.
	keymax =  (max(score_overlap, key=score_overlap.get))
	keymax=[keymax]
	valmax = score_overlap[keymax[0]]
	#puis on fait une deuxième passe pour chercher des couples de clusters éventuels.
	ix = -1
	for ante1 in score_overlap.keys()[:-1]:
		ix = ix+1
		if score_overlap[ante1]>0:
			for ante2 in score_overlap.keys()[ix+1:]:
				if score_overlap[ante2]>0:	
					if type_dist_inter == 'prox':
						ch_olds_termes_index = unique(liste_chp_old_termes[ante1] + liste_chp_old_termes[ante2])
						score = fonctions.calcul_distance(ch_now_termes_index,ch_olds_termes_index,dist_mat,inter,'moy')
						score = score+fonctions.calcul_distance(ch_olds_termes_index,ch_now_termes_index,dist_mat,inter,'moy')
						score = score / 2.
					if type_dist_inter == 'jaccard':				
						res_termes_old_union = fonctions_lib.merge(liste_res_termes_old[ante1], liste_res_termes_old[ante2], lambda x,y:max(x,y))# a priori si 2 fois la même clé alors la valeur est identifique, puisque c'est la même période ...
						score = overlap_pondere(res_termes_now,res_termes_old_union)
					if score>valmax:
						valmax  = score
						keymax = [ante1,ante2]	
	if valmax >seuil_intertemp:
		return keymax,valmax
	else:
		return [],0
	
def build_intertemp_links(net_now,net_old,dist_mat,seuil_netermes,seuil_intertemp,type_dist_inter):
	champs_liste_now = net_now.champs_liste
	champs_liste_old = net_old.champs_liste
	res_intertemp={}
	for ch_now in champs_liste_now:
		keymax,valmax = find_fathers(ch_now,champs_liste_old,dist_mat,seuil_netermes,seuil_intertemp,type_dist_inter)
		for keym in keymax:
			res_intertemp[(champs_liste_old[keym],ch_now)]=valmax
	return res_intertemp
	
def build_dynnet(zoom,multi_level_dyn_net):
	lev_max=get_lev_max(multi_level_dyn_net,zoom)	
	dyn_net_zoom={}
	for zoo in zoom:
		print '* on construit le réseau inter-temporel du niveau '  + str(zoo)
		dyn_net = {}
		# dyn_net c'est le réseau du niveau de zoom courant
		for couple,net in multi_level_dyn_net.iteritems():
			inter = couple[0]
			fusion_level = couple[1]
			nn = nearest_zoom(fusion_level,zoom)
			if lev_max.get((inter,zoo),-1.) == fusion_level:
				#alors on est tombé sur la bonne description et on rajoute le reseau dans notre descripteur
				dyn_net[inter] = net
		dyn_net_zoom[zoo]=dyn_net
	return dyn_net_zoom

def build_res_intertemp(zoom,seuil_intertemp,dyn_net_zoom,type_dist_inter):
	res_intertemp_zoo={}
	for zoo in zoom:
		dyn_net=dyn_net_zoom[zoo]
		for retni in range(len(years_bins))[:-1]:
			inter = len(years_bins) - retni - 1
			net_now = dyn_net[inter]
			net_old = dyn_net[inter-1]
			res_intertemp = build_intertemp_links(net_now,net_old,dist_mat,seuil_netermes,seuil_intertemp,type_dist_inter)
		res_intertemp_zoo[zoo]=	res_intertemp
	return res_intertemp_zoo


def composantes_connexes(dyn_net_zoom,res_intertemp_zoom,zoom):
	comp_simple_zoom={}
	for zoo in zoom:
		#on sélectionne d'abord les réseaux dynamiques du niveau de zoom considéré
		dyn_net = dyn_net_zoom[zoo]
		#on en extrait les noeuds:
		champs_liste=[]
		for net in dyn_net.values():
			#print net.champs_liste
			champs_liste = champs_liste + net.champs_liste
			#print len(champs_liste)
		comp = {}
		noeuds_attribues=[]
		#on regroupe les noeuds lies
		for x in res_intertemp_zoom[zoo].keys():
			ori = x[0]
			des = x[1]
			#print str(noeuds_attribues) + 'deja rangés'
			if ori in noeuds_attribues and not des in noeuds_attribues:
				for x,y in comp.iteritems():
					if ori in y:
						y.append(des)
						comp[x]=y
						noeuds_attribues.append(des)
			if not ori in noeuds_attribues and des in noeuds_attribues:
				for x,y in comp.iteritems():
					if des in y:
						y.append(ori)
						comp[x]=y
						noeuds_attribues.append(ori)
			if ori in noeuds_attribues and des in noeuds_attribues:
				for x,y in comp.iteritems():
					if des in y:
						x_1 = x
					if ori in y:
						x_2 = x
				if not x_1==x_2:
					temp  = comp[x_1]
					temp.extend(comp[x_2])
					comp[x_1] = temp
					comp[x_2] = []
			if not ori in noeuds_attribues and not des in noeuds_attribues:
				noeuds_attribues.append(ori)
				noeuds_attribues.append(des)
				comp[len(comp)+1] = [ori,des]
		#print comp
		for x in champs_liste:
			if not x in noeuds_attribues:
				comp[len(comp)+1] = [x]
		comp_nonvide={}
		for idxn,co in comp.iteritems():
			if not len(co)==0:
				comp_nonvide[len(comp_nonvide)+1]=co
		comp_simple_zoom[zoo]=comp_nonvide
	return comp_simple_zoom	

def build_tubes(multi_level_dyn_net,resolution_niveau,resolution_continuite,seuil_netermes):
	zoom_niveau = build_zoom(resolution_niveau)
	dyn_net_zoom=build_dynnet(zoom_niveau,multi_level_dyn_net)
	zoom_continuite = build_zoom(resolution_continuite)
	tubes={}
	for seuil_intertemp in zoom_continuite:
		# for zoo,dyn_net in dyn_net_zoom.iteritems():
		# 	print 'niveau: '+str(zoo)
		# 	for dyn,net in  dyn_net.iteritems():
		# 		print '\tperiode ' + str(dyn)+ ', ' + str(net)
		# print '\n'

		type_dist_inter = 'prox'
		type_dist_inter = 'jaccard'
		res_intertemp_zoom =  build_res_intertemp(zoom_niveau,seuil_intertemp,dyn_net_zoom,type_dist_inter)
		comp_simple_zoom = composantes_connexes(dyn_net_zoom,res_intertemp_zoom,zoom_niveau)
		#print comp_simple_zoom
		tubes_zoo = []
		for zoo,compo in comp_simple_zoom.iteritems():
			tube_listezoo =[]
			for idx, chps_liste in compo.iteritems():
				termes_ids = []
				inter = []
				for ch in chps_liste:

					termes_ids = termes_ids + map(Terme.get_index,ch.termes.liste_termes)

					inter.append(ch.periode)
					#inter est ici une liste de périodes éventuellement redondantes (de sorte de pondérer les distances lors du calcul des lables par ex)...
				niveau = [-1]
				label_tube,rebut = obtain_label(termes_ids,inter)

				Liste_termes.afficher_liste_termes(label_tube)
				tube = Tube(chps_liste,label_tube)
				print Tube.print_elements(tube)
				tube_listezoo.append(tube)
		tubes[seuil_intertemp] = tube_listezoo
		#tubes[seuil_intertemp]=comp_simple_zoom
		print '\n'
		print 'seuil_intertemp: '+str(seuil_intertemp)
		#print comp_simple_zoom
		for x,y in comp_simple_zoom.iteritems():
			tot = 0
			for z,w in y.iteritems():
				tot=tot + len(w)
			print 'niveau ' + str(x)+ ', nombre de tubes: ' + str(len(y)) +  ' sur ' +str(tot) + ' champs'
	return tubes

################################################################################################################################################
#on importe la matrice de distance et les dictionnaires utiles
################################################################################################################################################
try:
	print 'on essaye de recupérer un multi_level_dyn_net déjà calculé'
	multi_level_dyn_net = fonctions.dumpingout('multi_level_dyn_net')
	print 'on a recupéré un multi_level_dyn_net déjà calculé'
	dist_mat = fonctions.dumpingout('dist_mat')
	dico = fonctions.dumpingout('dico')
	tubes = fonctions.dumpingin('tubes')
	

except:
	import context_process 
	dico=context_process.dico_termes

	dist_mat = context_process.dist_mat
	################################################################################################################################################
	#on importe maintenant les champs au premier niveau.
	################################################################################################################################################
	nets = import_cfpipe()
	################################################################################################################################################
	#on construit le réseau multi-échelle à l'aide de l'algorithme de clustering.
	################################################################################################################################################
	multi_level_dyn_net = hierarchical_clustering(nets)
	#multi_level_dyn_net[(inter,fusion_level)] = Network(champs_liste[:],champs_dist) 
	fonctions.dumpingin(multi_level_dyn_net,'multi_level_dyn_net')
	fonctions.dumpingin(dist_mat,'disst_mat')
	fonctions.dumpingin(dico,'dico')

	################################################################################################################################################
	#il ne reste plus qu'a construire nos tubes, en veillant à bien labelliser ceux-ci!!!
	################################################################################################################################################

	resolution_niveau = 4
	seuil_netermes=  0.5


	resolution_continuite = 2	
	tubes = build_tubes(multi_level_dyn_net,resolution_niveau,resolution_continuite,seuil_netermes)
	fonctions.dumpingin(tubes,'tubes')
	print tubes
