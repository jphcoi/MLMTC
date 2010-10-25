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
path_req = parameters.path_req
years_bins = parameters.years_bins
name_bdd = parameters.name_bdd
path_req=parameters.path_req
dist_type=parameters.dist_type
sep_label = ' --- '

# ce script génère un gexf qui fusionne l'ensemble des niveaux.
#on recupere d'abord l'ensemble des noeuds à tous les niveaux:
def union_map(niv_max,seuil_net_champ):
	print seuil_net_champ
	for inter  in range(len(years_bins)):
		noeuds={}
		multi_level_edges={}
		map_edges={}
		level={}
		indexs={}
		index=0
		print " temps : "+str(inter)
		if 1:
			for niveau in range(niv_max):
				niveau=niveau+1
				fichier_leg=open(path_req + 'legendes'  +'/' + 'legendes' + 'niv_' + str(niveau) + '_' + dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt','r')
				lignes= fichier_leg.readlines()
				for ligne in lignes:
					index = index +1
					lignev=ligne[:-1].split('\t')
					indexs[str(niveau)+'_'+str(lignev[0])]=index
					noeuds[index] = lignev[1]
					level[index] = str(niveau)
			for niveau in range(niv_max):
				niveau=niveau+1
				fichier_lex=open(path_req + 'lexique'  +'/' + 'lexique_one_step_' + 'niv_' + str(niveau) + '_' + dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt','r')
				fichier_res=open(path_req +'reseau' + '/'+ 'reseauCF_'+'niv_'+str(niveau)+'_'+dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt','r')
	
				lignes_res= fichier_res.readlines()
				for ligne in lignes_res:
					lignev=ligne[:-1].split('\t')
				#	print 'ici'
				#	print lignev
				#	print float(lignev[2])
					if float(lignev[2])>seuil_net_champ:
						map_edges[(indexs[str(niveau)+'_'+lignev[0]],indexs[str(niveau)+'_'+lignev[1]])]=str(lignev[2])
				lignes_lex= fichier_lex.readlines()
				print fichier_lex
				if niveau>1:
					for ligne in lignes_lex:
						lignev=ligne[:-1].split('\t')
						for dessous in lignev[1].split(' '):
							map_edges[(indexs[str(niveau)+'_'+str(lignev[0])],indexs[str(niveau-1)+'_'+str(dessous)])]='1'
							map_edges[(indexs[str(niveau-1)+'_'+str(dessous)],indexs[str(niveau)+'_'+str(lignev[0])])]='1'
		#except:
		#	pass
		#print map_edges			
		sortie = path_req + 'gexf/' + 'reseau_multilevel_champ'+'_'+ dist_type +'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.gexf'
		gexf.gexf_builder(noeuds,map_edges,sortie,level)
	
