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
		fichier_CF=open(path_req +'reseau' + '/'+ 'reseauCF_'+'niv_'+str(niveau)+'_'+dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt','w')
		for x,y in dist_mat.iteritems():
			if x[2]==inter:
#				print str(x[0])+ '\t' + str(x[1]) + '\t' + str(y) + '\n'
				if float(dist_mat[x])>seuil:
					fichier.write(legende_noeuds[(inter,x[0])].replace(' ','_') + '\t' + legende_noeuds[(inter,x[1])].replace(' ','_') + '\t' + str(y) + '\n')
					fichier_CF.write(str(x[0])+ '\t' + str(x[1]) + '\t' + str(y) + '\n')
#					print 'out'
		print '------- fichier: reseau_' +str('reseauCF_'+dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt')+ ' ecrit dans le repertoire: '+path_req + 'reseau/'


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

def calcul_distance(champ1,champ2,dist_mat,inter1,type_distance):
	dist = 0.
	inter1= int(inter1)
	if len(champ1)>0 and len(champ2)>0:
		for terme1 in champ1:
			terme1=int(terme1)
			dist1=[]
			for terme2 in champ2:
				terme2=int(terme2)
				if terme1==terme2:
					dist1.append(1)
				else:
					dist1.append(float(dist_mat.get((terme1,terme2,inter1),0)))
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
	output = open('../../inout/pkl/'+requete+'/'+datastr+'.pkl', 'wb')
	# Pickle dictionary using protocol 0.
	pickle.dump(data, output)
	output.close()


def dumpingout(datastr):
	pkl_file = open('../../inout/pkl/'+requete+'/'+datastr+'.pkl', 'rb')
	data = pickle.load(pkl_file)
	return data

