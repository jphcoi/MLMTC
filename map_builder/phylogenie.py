#!/usr/bin/python
# -*- coding: utf-8 -*- 
import os
import sys
sys.path.append("../scripts/libraries")
sys.path.append("../scripts")

print "export_maps v0.1 (20100220)"
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
seuil=0.0



def renverser_index(x,indexsinv):
	noeud = indexsinv[x]
	noeud_v = noeud.split('_')
	n_niv = noeud_v[0]
	n_inter = int(noeud_v[2])
	n_index=noeud_v[1] 
	return n_niv,n_inter,n_index
	
def overlap(x,y):
	union_x = x|y
	inter_x = x&y
	if len(union_x)>0:
		return float(len(inter_x))/len(union_x)
	else:
		return 0

def overlap_pondere(liens_past,liens_actuels,liens_past_force,liens_forces_actuels):
	union,inter = 0.,0.
	commun_past=[]
	for i,lien in enumerate(liens_actuels):
		if lien in liens_past:
			j=liens_past.index(lien)
			union = union + max(float(liens_past_force[j]),float(liens_forces_actuels[i]))
			inter = inter + min(float(liens_past_force[j]),float(liens_forces_actuels[i]))
			commun_past.append(j)
		else:
			union = union + float(liens_forces_actuels[i])
	for i,lien_force in enumerate(liens_past_force):
		if not i in commun_past:
			union = union + float(lien_force)
	return inter/union


	
def reindex(liens,map_corr_noeuds,inter):
	#cette fonction permet de reecrire les liens de chaque champ en prenant en compte le glissement de l'index
	index_retro={}
	index_passe = map_corr_noeuds[(int(inter)-1,1)]
	index_actuel = map_corr_noeuds[(int(inter),1)]
	for x,y in zip (index_actuel,index_passe):
		index_retro[x]=y
	return index_retro
	
def reindexf(liens,map_corr_noeuds,inter):
	#cette fonction permet de reecrire les liens de chaque champ en prenant en compte le glissement de l'index
	index_futur={}
	index_apres = map_corr_noeuds[(int(inter)+1,1)]
	index_actuel = map_corr_noeuds[(int(inter),1)]
	for x,y in zip (index_actuel,index_apres):
		index_futur[x]=y
	return index_futur

def reindex_retro(liens,index_retro):
	lien_reindexe=[]
	for noeud in liens:
		temp=[]
		for lien in noeud:
			temp.append((index_retro[lien[0]],index_retro[lien[1]]))
		lien_reindexe.append(temp)
	return lien_reindexe



def garderniveau(noeuds_label,map_edges,levels,times,indexsinv,niveau,sons,fathers):
	noeuds_labelbis={}
	map_edgesbis={}
	indexbis = 0
	transition={}
	transition_inv={}
	levelsbis={}
	timesbis = {}
	attribut={}
	sonsbis = {}
	fathersbis={}
	for x,y in levels.iteritems():
		if y in niveau:
			indexbis += 1
			noeuds_labelbis[indexbis] = noeuds_label[x]
			transition[x]=indexbis
			transition_inv[indexbis]=x
			timesbis[indexbis]=times[x]
			levelsbis[indexbis]=levels[x]
			if x in sons:
				sonsbis[indexbis]='1'#sons[x]
			else:
				sonsbis[indexbis]='0'
			if x in fathers:
				fathersbis[indexbis]='1'#fathers[x]			
			else:
				fathersbis[indexbis]='0'
			n_niv,n_inter,n_index=renverser_index(x,indexsinv)
			attribut[indexbis]= 'cluster.php?id_cluster='+str(n_index)+'&amp;periode='+str(years_bins[n_inter][0])+'-'+str(years_bins[n_inter][-1])
	for x,y in map_edges.iteritems():
		if x[0] in transition.keys() and x[1] in transition.keys():
			map_edgesbis[(transition[x[0]],transition[x[1]])]=y	
	return noeuds_labelbis,map_edgesbis,levelsbis,timesbis,attribut,sonsbis,fathersbis,transition, transition_inv

def garderniveau_aut(noeuds_label,map_edges,levels,times,indexsinv,niveau,projection_chp2aut,indexs,auteur):
	noeuds_labelbis={}
	map_edgesbis={}
	indexbis = 0
	transition={}
	levelsbis={}
	timesbis = {}
	attribut={}
	for x,y in levels.iteritems():
		if y in niveau:
			indexbis += 1
			noeuds_labelbis[indexbis] = noeuds_label[x]
			transition[x]=indexbis
			timesbis[indexbis]=times[x]
			levelsbis[indexbis]=levels[x]
			n_niv,n_inter,n_index=renverser_index(x,indexsinv)
			attribut[indexbis]=  int(6*projection_chp2aut[(int(n_index),auteur,n_inter)])
	for x,y in map_edges.iteritems():
		if x[0] in transition.keys() and x[1] in transition.keys():
			map_edgesbis[(transition[x[0]],transition[x[1]])]=y

	return noeuds_labelbis,map_edgesbis,levelsbis,timesbis,attribut


def enlever_niveau0(noeuds_label,map_edges,levels,times):
	#on enleve le niveau 0:
	noeuds_labelbis={}
	map_edgesbis={}
	indexbis = 0
	transition={}
	levelsbis={}
	timesbis = {}
	for x,y in levels.iteritems():
		if y>1:
			indexbis += 1
			noeuds_labelbis[indexbis] = noeuds_label[x]
			transition[x]=indexbis
			timesbis[indexbis]=times[x]
			levelsbis[indexbis]=levels[x]

	for x,y in map_edges.iteritems():
		if x[0] in transition.keys() and x[1] in transition.keys():
			map_edgesbis[(transition[x[0]],transition[x[1]])]=y
	
	return noeuds_labelbis,map_edgesbis,levelsbis,timesbis
	
def dupliquer_niveau0(noeuds_label,map_edges,levels,times):
	#on enleve le niveau 0:
	noeuds_labelbis,map_edgesbis,transition,levelsbis,timesbis,indexbis={},{},{},{},{},0
	intermax =  max(times.itervalues())
	for x,y in levels.iteritems():

		if y>1:	
			indexbis += 1
			noeuds_labelbis[indexbis] = noeuds_label[x]
			transition[x]=indexbis
			timesbis[indexbis]=times[x]
			levelsbis[indexbis]=levels[x]
		else:
			for inter in range(intermax+1):
				indexbis += 1
				noeuds_labelbis[indexbis] = noeuds_label[x]
				transition[x]=transition.get(x,[]).append(indexbis)
				timesbis[indexbis]=inter
				levelsbis[indexbis]=1
				
				
	for x,y in map_edges.iteritems():
		if x[0] in transition.keys() and x[1] in transition.keys():
			map_edgesbis[(transition[x[0]],transition[x[1]])]=y

	return noeuds_labelbis,map_edgesbis,levelsbis,timesbis

def afficher_reseau(map_edgesbis,timesbis,levelsbis,noeuds_labelbis):
	for couple,poids in map_edgesbis.iteritems():
		noeud1 = couple[0]
		noeud2 = couple[1]
		if levelsbis[noeud1]==2:
		#if 1:
			if timesbis[noeud1]!=timesbis[noeud2]:
				print  ' -time:' + str(timesbis[noeud1]) + ' ' +' level:' + str(levelsbis[noeud1]) + ' ' + noeuds_labelbis[noeud1]+ ' -> time:' + str(timesbis[noeud2]) + ' ' +' level:' + str(levelsbis[noeud1]) + ' ' + noeuds_labelbis[noeud2]
			#else:
			#	print  ' -time:' + str(timesbis[noeud1]) + ' ' +' level:' + str(levelsbis[noeud1]) + ' ' + noeuds_labelbis[noeud1]+ ' -> time:' + str(timesbis[noeud2]) + ' ' +' level:' + str(levelsbis[noeud2]) + ' ' + noeuds_labelbis[noeud2]

def add_itemlist_dico(dico,x,item):
	temp=dico.get(x,[])
	temp.append(item)
	dico[x]=temp

def phylogenie(niv_max):
	#simple fonction de recuperation des donnees et de mise au format
	print 'data construction'
	map_corr={}	#[(inter,niveau)] donne pour chaque communauté à un niveau n, la liste des liens entre ses éléments au niveau 1 sous forme d'index, attention c'est le seuillé via CFpipe avec degmax
	map_corr_force={} #map_corr_force[(inter,niveau)] fournit la force des liens en question, attention c'est le seuillé via CFpipe avec degmax 
	map_corr_noeuds={} #map_corr_noeuds[(inter,niveau)] donne la liste des labels des champs/noeuds sous la forme de leur index unique:  indexs[str(niveau)+'_'+str(lignev[0])+'_'+str(inter)]
	indexs={} # c'est l'index unique de tous nos noeuds, qqsoit le niveau, ou le temps, indexs[str(niveau)+'_'+str(lignev[0])+'_'+str(inter)]=index
	indexsinv={} # c'est l'index inversé
	times={} #dictionnaire indéxé sur l'index universel des périodes
	levels={} #dictionnaire indéxé sur l'index universel des niveaux
	noeuds_label={} #dictionnaire indéxé sur l'index universel des labels
	map_edges={} #dictionnaire des liens entre couple de noeuds indexés sur leur index universel, seules les distances au même niveau et à la même période sont prises en compte map_edges[(indexs[str(niveau)+'_'+lignev[0]+'_'+str(inter)],indexs[str(niveau)+'_'+lignev[1]+'_'+str(inter)])]=str(lignev[2])
	map_dessous={} # dictionnaire qui a chaque noeud (index universel) associe la liste de ses composants du niveau en dessous (toujours en index universel)
	index=0
	for inter  in range(len(years_bins)):
		print " step : "+str(inter)
		for niveau in range(niv_max):
			niveau=niveau+1
			try:
				fichier_leg=open(path_req + 'legendes'  +'/' + 'legendes' + 'niv_' + str(niveau) + '_' + dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt','r')
			except:
				break			
			lignes= fichier_leg.readlines()
			for ligne in lignes:
				lignev=ligne[:-1].split('\t')
				if 1:
					index=index+1
					indexs[str(niveau)+'_'+str(lignev[0])+'_'+str(inter)]=index
					indexsinv[index]=str(niveau)+'_'+str(lignev[0])+'_'+str(inter)
					noeuds_label[index] = lignev[1]
					levels[index] = niveau
					times[index] = inter
		for niveau in range(niv_max):
			niveau=niveau+1
			try:
				fichier_res=open(path_req +'reseau' + '/'+ 'reseauCF_'+'niv_'+str(niveau)+'_'+dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'_degmax_'+str(degmax)+'.txt','r')
			except:
				break	
			lignes_res= fichier_res.readlines()
			#reseau à un niveau donné
			for ligne in lignes_res:
				lignev=ligne[:-1].split('\t')
				map_edges[(indexs[str(niveau)+'_'+lignev[0]+'_'+str(inter)],indexs[str(niveau)+'_'+lignev[1]+'_'+str(inter)])]=str(lignev[2])
			fichier_lex=open(path_req + 'lexique'  +'/' + 'lexique_' + 'niv_' + str(niveau) + '_' + dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt','r')
			lignes_lex= fichier_lex.readlines()
			#reseau inter-niveau ou plutôt description micro de chaque niveau
			if niveau>0:
				for ligne in lignes_lex:
					lignev=ligne[:-1].split('\t')
					element_dessous=[]
					for dessous in lignev[1].split(' '):
						#on recrupere la description micro du champ courant
						element_dessous.append(indexs[str(1)+'_'+str(dessous)+'_'+str(inter)])
					liens=[]
					force_liens=[]
					for item1 in element_dessous:
						for item2 in element_dessous:
							try:
								if float(map_edges[item1,item2])>seuil:
									liens.append((item1,item2))
									force_liens.append(map_edges[item1,item2])
							except:
								pass
					#map_corr donne pour chaque communauté à un niveau n, la liste des liens entre ses éléments au niveau 1 sous forme d'index
					couple_inter_niveau=(inter,niveau)
					add_itemlist_dico(map_corr,couple_inter_niveau,liens)
					add_itemlist_dico(map_corr_force,couple_inter_niveau,force_liens)
					add_itemlist_dico(map_corr_noeuds,couple_inter_niveau,indexs[str(niveau)+'_'+str(lignev[0])+'_'+str(inter)])
			#reseau inter-niveau d'un échellon à l'autre
			fichier_lex_os=open(path_req + 'lexique'  +'/' + 'lexique_one_step_' + 'niv_' + str(niveau) + '_' + dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt','r')
			lignes_lex_os= fichier_lex_os.readlines()
			if niveau>1:
				for ligne in lignes_lex_os:
					lignev=ligne[:-1].split('\t')
					for dessous in lignev[1].split(' '):
						map_edges[(indexs[str(niveau)+'_'+str(lignev[0])+'_'+str(inter)],indexs[str(niveau-1)+'_'+str(dessous)+'_'+str(inter)])]='1.0001'
						map_edges[(indexs[str(niveau-1)+'_'+str(dessous)+'_'+str(inter)],indexs[str(niveau)+'_'+str(lignev[0])+'_'+str(inter)])]='1.0001'
						temp = map_dessous.get(indexs[str(niveau)+'_'+str(lignev[0])+'_'+str(inter)],[])
						temp.append(indexs[str(niveau-1)+'_'+str(dessous)+'_'+str(inter)])
						map_dessous[indexs[str(niveau)+'_'+str(lignev[0])+'_'+str(inter)]] = temp
	print 'data built'		
	return map_corr,map_corr_force,map_corr_noeuds,map_edges,noeuds_label,levels,times,indexsinv,indexs,map_dessous


def comparaison_inter_temporelle(liens_actuels,liens_forces_actuels,list_liens_past,list_liens_forces_past,seuil_intertemp,prehistory):
	mapping={}
	keymax,valmax=[],0
	cluster_past_id = -1
	for liens_past,liens_past_force in zip(list_liens_past,list_liens_forces_past):
		cluster_past_id = cluster_past_id +1
		nb_liens_communs=len(set(liens_past)&set(liens_actuels))
		if float(nb_liens_communs) / float(min(len(liens_past),len(liens_actuels)))>1./8.:
			over=overlap_pondere(liens_past,liens_actuels,liens_past_force,liens_forces_actuels)
			if over>seuil_intertemp:
				mapping[cluster_past_id] = over
				print 'nb_liens_communs' + str(nb_liens_communs)  + '\t nb_liens_past: ' + str(len(liens_past)) + '\t nb_liens_present: ' + str(len(liens_actuels)) + '\t overlap: ' + str(over) 
			
	#mapping decrit ici l'overlap en nombre de liens entre clusters passes et futurs.
	if len(mapping.keys())>0:
		keymax =  (max(mapping, key=mapping.get))
		valmax = mapping[keymax]
		keymax=[keymax]
	#puis on fait une deuxième passe pour chercher des couples de clusters éventuels.
	if prehistory==1:
		for ante1  in mapping.keys():
			for ante2 in mapping.keys():
				if ante2 > ante1:					
					liens1=list_liens_past[ante1]
					liens2=list_liens_past[ante2]
					liens1_force=list_liens_forces_past[ante1]
					liens2_force=list_liens_forces_past[ante2]
					dico1 ={}
					for x,y in zip(liens1,liens1_force):
						dico1[x] = y
					dico2 ={}
					for x,y in zip(liens2,liens2_force):
						dico2[x] = y
					dico_union=dico2
					for lien1,force1 in dico1.iteritems():
						if lien1 in dico2:
							dico_union[lien1] = max(dico1[lien1],dico2[lien1])
						else:
							dico_union[lien1] = force1 
					score= overlap_pondere(dico_union.keys(),liens_actuels,dico_union.values(),liens_forces_actuels)		
					if score>valmax:
						valmax  = score
						keymax = [ante1,ante2]	

	return keymax,valmax

	
def intertemporel(map_corr,map_corr_force,map_corr_noeuds,map_edges,seuil_intertemp):
	#on souhaite produire les liens inter-temporels,
	intertemp={}	
	k=0
	j=0
	inter_mem = 0
	dico_list_liens_forces_past={}
	dico_list_liens_past={}
	for x,noeuds in map_corr_noeuds.iteritems():
		inter = int(x[0])
		niveau =x[1]
		if int(inter)>0:
			#on définit d'abord le passé, à chaque fois qu'on change de période
			if inter_mem != inter:
				inter_mem=inter
				descendants = 0
			for idx,noeud in enumerate(noeuds):
				liens_temp = map_corr[x]#on initialise avec les index des liens de la periode courante
				liens_forces_actuels_temp = map_corr_force[x]
				keymax,valmax=[],0
				try:
					delta = 1
					while valmax==0 and delta<min(inter+1,timelimit):#delta<=5:#liens à longue distance temporelle					 		
							t_past = inter-delta
							index_retro = reindex(liens_temp,map_corr_noeuds,t_past+1)
					 		liens_temp = reindex_retro(liens_temp,index_retro)
					 		liens_actuels = liens_temp[idx]
							liens_forces_actuels=liens_forces_actuels_temp[idx]
							keymax,valmax = comparaison_inter_temporelle(liens_actuels,liens_forces_actuels,map_corr[(t_past,niveau)],map_corr_force[(t_past,niveau)],seuil_intertemp,delta)
							delta=delta+1
				except:
					keymax,valmax=[],0
				if len(keymax)>0:
					descendants = descendants+1
					intertemp[noeud]=[]
					for keym in keymax:
						intertemp[noeud].append(((map_corr_noeuds[(t_past,niveau)])[keym],1.0001+20*valmax))
						k=k+1
						#intertemp donne les antecendents des champs directement sous leur forme labellisee
				if niveau==1:
					intertemp[noeud]=[(map_corr_noeuds[(int(inter)-1,1)][idx],0.1)]
		if niveau==2:
			print 'periode: '+str(inter) +  ", niveau : " + str(niveau) +', peres: ' + str(descendants)
	return intertemp




nivmax= 3
map_corr,map_corr_force,map_corr_noeuds,map_edges,noeuds_label,levels,times,indexsinv,indexs,map_dessous=phylogenie(nivmax)
#seuil_intertemp=0.03
seuil_intertemp=0.07
intertemp = intertemporel(map_corr,map_corr_force,map_corr_noeuds,map_edges,seuil_intertemp)

#enfin on fusionne les  trois types de liens:
#print intertemp
sons={}
fathers={}
for actu,ante in intertemp.iteritems():
	for ant in ante:
		map_edges[(ant[0],actu)]=ant[1]
		fathers[ant[0]]=fathers.get(ant[0],0)+1
		sons[actu]=sons.get(actu,0)+1

#noeuds_labelbis,map_edgesbis,levelsbis,timesbis,attribut=garderniveau2(noeuds_label,map_edges,levels,times,indexsinv)
niveau=[3]#meta commm
niveau=[2]#commm


noeuds_labelbis,map_edgesbis,levelsbis,timesbis,attribut,sonsbis,fathersbis,transition,transition_inv=garderniveau(noeuds_label,map_edges,levels,times,indexsinv,niveau,sons,fathers)

compt=0
phylogen = {}
for x,y in map_edgesbis.iteritems():
	n_niv0,n_inter0,n_index0=renverser_index(transition_inv[x[0]],indexsinv)
	n_niv1,n_inter1,n_index1=renverser_index(transition_inv[x[1]],indexsinv)
	#print y


	
#print ' fathers'
#print fathersbis
#print 'sons'
#print sonsbis
try:
	CF_weight0=parameters.CF_weight0
except:
	CF_weight0=0.5
	
sortie = path_req + 'gexf/' + 'reseau_multilevel_temporel'+'_'+ dist_type +'_'+str(years_bins[0][0])+'-'+str(years_bins[-1][-1])+'_' + str(CF_weight0).replace('.','')+'.gexf'
#afficher_reseau(map_edgesbis,timesbis,levelsbis,noeuds_labelbis)

#auteur=7842
#sortie = path_req + 'gexf/' + 'reseau_multilevel_temporel_auteur_'+str(auteur)+'_'+ dist_type +'_'+str(years_bins[0][0])+'-'+str(years_bins[-1][-1])+'.gexf'
#intégrer information de l'auteur courant
#projection_aut2chp,projection_chp2aut = auteurs.load_projection(1)
#noeuds_labelbis,map_edgesbis,levelsbis,timesbis,attribut = garderniveau_aut(noeuds_label,map_edges,levels,times,indexsinv,niveau,projection_chp2aut,indexs,auteur)

#print sonsandfathersbis
	
gexf.gexf_builder_3d(noeuds_labelbis,map_edgesbis,sortie,levelsbis,timesbis,attribut,sonsbis,fathersbis)

dico_termes=fonctions.lexique()#on cree le dictionnaire des termes

try:
	fonctions_bdd.drop_table(name_bdd,'phylo')
	fonctions_bdd.drop_table(name_bdd,'cluster')
	fonctions_bdd.drop_table(name_bdd,'maps')
except:
	pass
fonctions_bdd.creer_table_phylo(name_bdd,'phylo')
fonctions_bdd.creer_table_cluster(name_bdd,'cluster')
fonctions_bdd.creer_table_map(name_bdd,'maps')
fonctions.ecrire_tables_cluster_phylo(noeuds_labelbis,map_edgesbis,sortie,levelsbis,timesbis,attribut,sonsbis,fathersbis,dico_termes,indexsinv,map_dessous,transition,sep_label)




