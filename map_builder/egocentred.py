#!/usr/bin/env python
# encoding: utf-8

import parameters
path_req = parameters.path_req
treetagger_dir =parameters.treetagger_dir
years_bins = parameters.years_bins
dist_type=parameters.dist_type

import sys
import os

namef=path_req +'reseau/'+ 'reseauCF_'+dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt'


def get_auteurs(namef):
	filer  = open(namef,'r')
	auteurs  = {}
	for ligne in filer.readlines():
		if '"' in ligne:
			lignev =ligne[:-2].split(' ')
			auteurs[int(lignev[0])]=str(lignev[1].replace('"',''))
	return auteurs
		

def get_arcs(namef):
	fromv = []
	tov = []
	poidsv=[]
	filer  = open(namef,'r')
	for ligne in filer.readlines():
		if not '"' in ligne:
			ligne =  ligne[:-2]
			try:
				lignev=ligne.split(' ')
				noeud1 = int(lignev[0])
				noeud2 = int(lignev[1])
				poids = int(lignev[2])
				fromv.append(noeud1)
				tov.append(noeud2)
				poidsv.append(poids)
			except:
				pass
	return fromv,tov,poidsv
				 
		
fromv,tov,poidsv=  get_arcs(namef)
auteurs = get_auteurs(namef)
	
	
def	ecrire_ego(nom,auteurs,from_a,to_a,poids_a,voisins):

	file = open("sorties/ego/"+nom+".net",'w')
	file.write('*Vertices '+str(len(voisins))+'\r\n')
	for vois in voisins:
		file.write(str(voisins.index(vois)+1)+ ' "'+ auteurs[vois]+'"\r\n')
	file.write('*Arcs\r\n')
	for x,y,z in zip( from_a,to_a,poids_a):
		file.write(str(voisins.index(x)+1) + ' '+ str(voisins.index(y)+1) + ' '+ str(z) + '\r\n')


def ego_out(auteurs,fromv,tov,poidsv):	
	for auteur in auteurs:
		nom = auteurs[auteur]
		print nom
		voisins=[]
		from_a=[]
		to_a=[]
		poids_a=[]
		for voisins_from, voisins_to, poids in zip(fromv,tov,poidsv):
			if auteur == voisins_from or auteur == voisins_to:
				if not voisins_from in voisins:
					voisins.append(voisins_from)
				if not voisins_to in voisins:
					voisins.append(voisins_to)
		for voisins_from, voisins_to, poids in zip(fromv,tov,poidsv):
			clause=0
			if auteur == voisins_from or auteur == voisins_to:
				clause= 1
			else:
				if voisins_from in voisins and voisins_to in voisins:
					clause=1
			if clause==1:
				from_a.append(voisins_from)
				to_a.append(voisins_to)
				poids_a.append(poids)
	#	print from_a
		ecrire_ego(nom,auteurs,from_a,to_a,poids_a,voisins)
		print len(voisins)