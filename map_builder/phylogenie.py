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
timelimit='1'

dist_type=parameters.dist_type
sep_label = ' --- '
seuil=0.0

# ce script génère un gexf qui fusionne l'ensemble des niveaux.
#on recupere d'abord l'ensemble des noeuds à tous les niveaux:

def add_sonsandfathers(sonsbis,fatherbis):
	sonsandfathersbis={}
	for x in sonsbis:
		if int(sonsbis[x])>0:
			if int(fathersbis[x])>0:
				sonsandfathersbis[x]=3
			else:
				sonsandfathersbis[x]=2
		else:
			if int(fathersbis[x])>0:
				sonsandfathersbis[x]=1
			else:
				sonsandfathersbis[x]=0
	return sonsandfathersbis


def phylogenie(niv_max):
	#simple fonction de recuperation des donnees et de mise au format
	map_corr={}
	map_corr_noeuds={}
	indexs={}
	indexsinv={}
	index=0
	times={}
	levels={}
	noeuds_label={}
	map_edges={}
	map_dessous={}
	for inter  in range(len(years_bins)):
		print " temps : "+str(inter)
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
				fichier_res=open(path_req +'reseau' + '/'+ 'reseauCF_'+'niv_'+str(niveau)+'_'+dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt','r')
			except:
				break
			
			lignes_res= fichier_res.readlines()
			print fichier_res
			#reseau à un niveau donné
			for ligne in lignes_res:
				lignev=ligne[:-1].split('\t')
				map_edges[(indexs[str(niveau)+'_'+lignev[0]+'_'+str(inter)],indexs[str(niveau)+'_'+lignev[1]+'_'+str(inter)])]=str(lignev[2])
				#print (str(niveau)+'_'+lignev[0]+'_'+str(inter),str(niveau)+'_'+lignev[1]+'_'+str(inter))
			fichier_lex=open(path_req + 'lexique'  +'/' + 'lexique_' + 'niv_' + str(niveau) + '_' + dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt','r')
			lignes_lex= fichier_lex.readlines()
			print fichier_lex
			#reseau inter-niveau ou plutôt description micro de chaque niveau
			if niveau>0:
				for ligne in lignes_lex:
					lignev=ligne[:-1].split('\t')
					element_dessous=[]
					for dessous in lignev[1].split(' '):
						#on recrupere la description micro du champ courant
						element_dessous.append(indexs[str(1)+'_'+str(dessous)+'_'+str(inter)])
				#	print element_dessous
					liens=[]
					for item1 in element_dessous:
						for item2 in element_dessous:
							try:
								if float(map_edges[item1,item2])>seuil:
									liens.append((item1,item2))
							except:
								pass
					#map_corr donne pour chaque communauté à un niveau n, la liste des liens entre ses éléments au niveau 1 sous forme d'index
					temp=map_corr.get((inter,niveau),[])
					temp.append(liens)
					map_corr[(inter,niveau)]=temp
					temp=map_corr_noeuds.get((inter,niveau),[])
					temp.append(indexs[str(niveau)+'_'+str(lignev[0])+'_'+str(inter)])
					map_corr_noeuds[(inter,niveau)]=temp
			
			#reseau inter-niveau d'un échellon à l'autre
			fichier_lex_os=open(path_req + 'lexique'  +'/' + 'lexique_one_step_' + 'niv_' + str(niveau) + '_' + dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt','r')
			lignes_lex_os= fichier_lex_os.readlines()
			print fichier_lex_os
			if niveau>1:
				for ligne in lignes_lex_os:
					lignev=ligne[:-1].split('\t')
					#print str(niveau)+'_'+str(lignev[0])+'_'+str(inter) + '->'
					for dessous in lignev[1].split(' '):
						#print '+++++++++'+str(niveau-1)+'_'+str(dessous)+'_'+str(inter)
						map_edges[(indexs[str(niveau)+'_'+str(lignev[0])+'_'+str(inter)],indexs[str(niveau-1)+'_'+str(dessous)+'_'+str(inter)])]='1.0001'
						map_edges[(indexs[str(niveau-1)+'_'+str(dessous)+'_'+str(inter)],indexs[str(niveau)+'_'+str(lignev[0])+'_'+str(inter)])]='1.0001'
						temp = map_dessous.get(indexs[str(niveau)+'_'+str(lignev[0])+'_'+str(inter)],[])
						temp.append(indexs[str(niveau-1)+'_'+str(dessous)+'_'+str(inter)])
						map_dessous[indexs[str(niveau)+'_'+str(lignev[0])+'_'+str(inter)]] = temp
			
	return map_corr,map_corr_noeuds,map_edges,noeuds_label,levels,times,indexsinv,indexs,map_dessous

def renverser_index(x,indexsinv):
	noeud = indexsinv[x]
	noeud_v = noeud.split('_')
	n_niv = noeud_v[0]
	n_inter = int(noeud_v[2])
	n_index=noeud_v[1] 
	return n_niv,n_inter,n_index
	
def overlap (x,y):
	union_x = x|y
	inter_x = x&y
	if len(union_x)>0:
		return float(len(inter_x))/len(union_x)
	else:
		return 0

def compare(liens,noms,liens_past,map_edges,seuil):
	#se servir de map_edges pour vérifier si le lien entre clusters antérieurs existaient effectivement ou non
	mapping={}
	keymax=[]
	for x in liens_past:
		compteur=0
		mapping[liens_past.index(x)] = overlap(set(x),set(liens))
	#mapping decrit ici l'overlap en nombre de liens entre clusters passes et futurs.
	keymax =  (max(mapping, key=mapping.get))
	valmax = mapping[keymax]
	keymax=[keymax]
	#puis on fait une deuxième passe pour chercher des couples de clusters éventuels.
	for ante1  in mapping:
		if mapping[ante1]>0:
			for ante2 in mapping:
				if ante2 > ante1 and mapping[ante2]>0 :					
					liens1=set(liens_past[ante1])
					liens2=set(liens_past[ante2])
					liens_union  = liens1 | liens2
					diff=[]
					score= overlap(liens_union,set(liens))		
					if score>valmax:
						valmax  = score
						keymax = [ante1,ante2]	
	if valmax >seuil:
		return keymax,valmax
	else:
		return [],0
	
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


	
def intertemporel(map_corr,map_corr_noeuds,map_edges,seuil_intertemp):
	#map_corr donne pour chaque communauté à un niveau n, la liste des liens entre ses éléments au niveau 1 (n-1?) sous forme d'index	
	intertemp={}	
	#on souhaite produire les liens inter-temporels,
	#map_edges y a tout ( ? ... )
	k=0
	j=0
	for x,noeuds in map_corr_noeuds.iteritems():
		inter = int(x[0])
		print 'inter'+str(inter)
		niveau =x[1]
		if int(inter)>0:
			liens = map_corr[x]
			index_retro = reindex(liens,map_corr_noeuds,inter)
			liens = reindex_retro(liens,index_retro)
			
			print "niveau : " + str(niveau) + ' intervalle: '+str(inter)
			for noeud in noeuds:
				valmax=0
				try:
				#	print liens_actuels
					liens_actuels = liens[noeuds.index(noeud)]
					keymax,valmax = compare(liens_actuels,map_corr_noeuds[(int(inter)-1,niveau)],map_corr[(int(inter)-1,niveau)],map_edges,seuil_intertemp)
					tmax = int(inter)-1
					if valmax>0:
						j=j+1
						#print str(j) + ' valide'
					liens_temp=liens
					if valmax==0:
					 	i=1
					 	while valmax==0  and inter-i>-2 and i<1:#i<5:#liens à longue distance temporelle
					 		
							tmax = inter-i-1 		
							index_retro = reindex(liens_temp,map_corr_noeuds,inter-i)
					 		liens_temp = reindex_retro(liens_temp,index_retro)
					 		liens_actuels = liens_temp[noeuds.index(noeud)]
					 		#print '****************************************'
					 		keymax,valmax = compare(liens_actuels,map_corr_noeuds[(inter-i-1,niveau)],map_corr[(inter-i-1,niveau)],map_edges,seuil_intertemp)
					 		
					 		#if valmax>0:
					 		#	print 'oooooooooo'
					
							i=i+1
							
				except:
					keymax,valmax=[],0
				if len(keymax)>0:
					intertemp[noeud]=[]
					for keym in keymax:
						#valmax = valmax#on fixe la valeur des liens intertemp à 2 d'office!!!
						intertemp[noeud].append(((map_corr_noeuds[(tmax,niveau)])[keym],1.0001+20*valmax))
					#	print str(noeud) + '\t'+str(((map_corr_noeuds[(inter-1,niveau)])[keym],20*valmax))
						k=k+1
					#	print k
						#intertemp donne les antecendents des champs directement sous leur forme labellisee
				if niveau==1:
					intertemp[noeud]=[(map_corr_noeuds[(int(inter)-1,1)][noeuds.index(noeud)],0.1)]

#on retropropage egalement 
		retro=0
		if retro==1:
			if int(inter)<len(years_bins)-1:
				liens = map_corr[x]
				index_futur = reindexf(liens,map_corr_noeuds,inter)
				liens = reindex_retro(liens,index_futur)
				print "futur: niveau : " + str(niveau) + ' intervalle: '+str(inter)
				for noeud in noeuds:
					liens_actuels = liens[noeuds.index(noeud)]
					try:
						keymax,valmax = compare(liens_actuels,map_corr_noeuds[(int(inter)+1,niveau)],map_corr[(int(inter)+1,niveau)],map_edges,seuil_intertemp)
					except:
						keymax,valmax=[],0
					if len(keymax)>0:
						intertemp[noeud]=[]
						for keym in keymax:
							valmax = valmax#on fixe la valeur des liens intertemp à 2 d'office!!!
							intertemp[noeud].append(((map_corr_noeuds[(inter+1,niveau)])[keym],20*valmax))
							#print str(noeud) + '\t'+str(((map_corr_noeuds[(inter+1,niveau)])[keym],20*valmax))
							#intertemp donne les antecendents des champs directement sous leur forme labellisee
					if niveau==1:
						intertemp[noeud]=[(map_corr_noeuds[(int(inter)+1,1)][noeuds.index(noeud)],0.1)]
 				

	return intertemp


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


def invert_dict(d):
    return dict([(v, k) for k, v in d.iteritems()])

def get_label_annees(inter):
	annees = years_bins[inter]
	annee_d=str(annees[0])
	annee_f=str(annees[-1])
	return annee_d + ' '+annee_f

def ecrire_tables_cluster_phylo(nodes,edges,sortie,level,time,attribut,sonsbis,fathersbis,dico_termes,indexs_inv,map_dessous,transition):
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








nivmax= 3
map_corr,map_corr_noeuds,map_edges,noeuds_label,levels,times,indexsinv,indexs,map_dessous=phylogenie(nivmax)
seuil_intertemp=0.03
intertemp = intertemporel(map_corr,map_corr_noeuds,map_edges,seuil_intertemp)

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


#maintenant on regroupe les champs dans la phylogénie complète incluant les liens inter-clusters en faisant varier un seuil.
#on recherche simplement les composantes connexes du graphe.
#ps limite à 0.30 à l'origine sur les liens inter-clusters à régler dans les paramètres de CFpipe.py: seuil_net_champ_v
def comp_connexes(liens,noeuds_labelbis,seuil):
	comp = {}
	noeuds=[]
	noeuds_attribues = []
	#les noeuds sont numerotes de 1 à nbre_noeuds
	for x in range(len(noeuds_labelbis)):
		noeuds.append(x+1)
	#on regroupe les noeuds lies
	for x,y in liens.iteritems():
		#print x
		if float(y)>seuil:
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
	for x in noeuds:
		if not x in noeuds_attribues:
			comp[len(comp)+1] = [x]
	comp_simple={}
	#comp_simple=[]
	nb_comp=0
	for x,y in comp.iteritems():
		if len(y)>0:
			nb_comp=nb_comp+1
			y.sort()
			comp_simple[nb_comp] = y
	return comp_simple	
	







composantes_seuil = {}
nb_tranche=10
tranche = 1./float(nb_tranche)
for decoup in range(nb_tranche+1):
	seuil= decoup*tranche
	comp= comp_connexes(map_edgesbis,noeuds_labelbis,seuil)
	composantes_seuil[seuil] = comp
	print comp

print '\n'
hierarchie = {}
for decoup in range(nb_tranche):
	seuil= (decoup+1)*tranche
	seuil_avt = (decoup)*tranche
	composa =  composantes_seuil[seuil]
	composa_avt=composantes_seuil[seuil_avt]
	for x,y in composa.iteritems():
		for x_a,y_a in composa_avt.iteritems():
			if set(y)|set(y_a)==set(y_a):
				hierarchie[(x,decoup+1)] = (x_a,decoup)
print hierarchie
				
		

	
#print ' fathers'
#print fathersbis
#print 'sons'
#print sonsbis
sortie = path_req + 'gexf/' + 'reseau_multilevel_temporel'+'_'+ dist_type +'_'+str(years_bins[0][0])+'-'+str(years_bins[-1][-1])+'.gexf'
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
ecrire_tables_cluster_phylo(noeuds_labelbis,map_edgesbis,sortie,levelsbis,timesbis,attribut,sonsbis,fathersbis,dico_termes,indexsinv,map_dessous,transition)





#EN OPTION
#deprecated
# def ecrire_clusterfile(map_corr,intertemp,indexs,indexsinv):
# #deprecated
# 	niveau=2
# 	try:
# 		os.mkdir(path_req+'site')
# 	except:
# 		pass
# 	fichier_cluster=open(path_req + 'site'  +'/' + 'ExportClusterDetails.txt','w')
# 	fichier_phylo=open(path_req + 'site'  +'/' + 'ExportPhyloDetails.txt','w')
# 	fichier_cluster.write("Years;Cluster Id;Cluster generic legend;Cluster specific legend;Terms id;Pseudo-Inclusion;Cluster Size;Density;Number of fathers;Number of sons\n")
# 	sons={}
# 	fathers={}
# 	phylo_champs_var=[]
# 	for x,y in intertemp.iteritems():
# 		n_niv,n_inter,n_index=renverser_index(x,indexsinv)
# 		if n_niv=='2':
# 			avants=[]
# 			for passe in y:
# 				avant_niv,avant_inter,avant_index = renverser_index(passe[0],indexsinv)
# 				avants.append(avant_index)
# 
# 			fichier_phylo.write(str(years_bins[n_inter][0])+' '+str(years_bins[n_inter][-1])+' '+n_index+' '+str(years_bins[avant_inter][0])+' '+str(years_bins[avant_inter][-1])+' '+' '.join(avants)+'\n')
# 			for av in avants:
# 				phylo_champs_var.append([n_index,str(years_bins[n_inter][0])+' '+str(years_bins[n_inter][-1]),av,str(years_bins[avant_inter][0])+' '+str(years_bins[avant_inter][-1])])
# 
# 			if (n_index,n_inter) in fathers:
# 				fathers[(n_index,n_inter)]=fathers[(n_index,n_inter)]+len(avants)
# 			else:
# 				fathers[(n_index,n_inter)]=len(avants)
# 			for av in avants:
# 				if (av,avant_inter) in sons:
# 					sons[(av,avant_inter)]=sons[(av,avant_inter)]+1
# 				else:
# 					sons[(av,avant_inter)]=1
# 	print str(len(sons))+" filiations:"
# 	print sons
# 	print fathers
# 	variables_cluster=[]
# 	compte_cluster=0
# 	for inter  in range(len(years_bins)):
# 		print inter
# 		fichier_lex=open(path_req + 'lexique'  +'/' + 'lexique_' + 'niv_' + str(niveau) + '_' + dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt','r')
# 		lignes_lex= fichier_lex.readlines()
# 		#print fichier_lex
# 		fichier_legende_id=open(path_req + 'legendes'  +'/' + 'legendes_id_' + 'niv_' + str(niveau) + '_' + dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt','r')
# 		lignes_leg= fichier_legende_id.readlines()
# 		#print fichier_legende_id
# 
# 		#reseau inter-niveau ou plutôt description micro de chaque niveau
# 		for ligne,ligne_leg in zip(lignes_lex,lignes_leg):
# 			lignev=ligne[:-1].split('\t')
# 			ligne_leg_v=ligne_leg[:-1].split('\t')
# 			element_dessous=[]
# 			label_leg=[]
# 			for dessous in lignev[1].split(' '):
# 				#on recrupere la description micro du champ courant
# 				element_dessous.append(str(dessous))
# 			for legendes in ligne_leg_v[1].split(' '):
# 				label_leg.append(str(legendes))
# 			try:
# 				fat=str(fathers[(lignev[0],inter)])
# 			except:
# 				fat='0'
# 			try:
# 				son=str(sons[(lignev[0],inter)])
# 			except:
# 				son='0'
# 			fichier_cluster.write(str(years_bins[inter][0])+' '+str(years_bins[inter][-1])+';'+lignev[0]+';'+label_leg[0]+';'+label_leg[1]+';'+' '.join(element_dessous)+';0;0;0;'+fat+';'+son+'\n')
# 			#variable_cluster
# 			for concepts in element_dessous:
# 				compte_cluster=compte_cluster+1
# 				print [compte_cluster,label_leg[0],label_leg[1],str(years_bins[inter][0])+' '+str(years_bins[inter][-1]),concepts,int(fat),int(son),str(compte_cluster)+'_'+str(years_bins[inter][0])+' '+str(years_bins[inter][-1])]
# 				variables_cluster.append([int(lignev[0]),label_leg[0],label_leg[1],str(years_bins[inter][0])+' '+str(years_bins[inter][-1]),concepts,int(fat),int(son),str(lignev[0])+'_'+str(years_bins[inter][0])+' '+str(years_bins[inter][-1])])
# 			#(id INTEGER PRIMARY KEY,id_cluster INTEGER,label_1 INTEGER,label_2 INTEGER,periode VARCHAR(50),concept INT, pseudo FLOAT, cluster_size INT, density FLOAT, nb_fathers INT, nb_sons INT, lettre VARCHAR (3), identifiant_unique VARCHAR(20)
# 
# 


#ecrire_clusterfile(map_corr,intertemp,indexs,indexsinv)