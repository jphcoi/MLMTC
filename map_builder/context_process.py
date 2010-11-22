#!/usr/bin/python
# -*- coding: utf-8 -*-
#recupere les liens des trois reseaux pour exporter les reseaux au format texte
import sys
import math
import gexf
from copy import deepcopy
sys.path.append("../scripts/libraries")
sys.path.append("../scripts")

print "export_networks v0.2 (20091102)"
print "--------------------------------\n"

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
import fonctions

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
seuil=0.2
###################################
#######export #####################
###################################

def build_dico():
	lesidstermes = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'concepts','id')
	lestermes = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'concepts','forme_principale')
	dico_termes ={}
	for x,y in zip(lesidstermes,lestermes):
		dico_termes[x[0]]=y[0]
	print 'dictionnaire des termes écrit, taille: '+str(len(dico_termes))
	return dico_termes	
	


def init_dictionnary_list(taille,val):
	dico={}
	for x in range(taille):
		dico[x]=val
	return dico
		
#billets décrit les concepts utilisé chaque annee
#billet[annee]=array(id des billets publies)
#termes=array(id des termes présents)
def build_nbbillet(contenu,years_bin):
	#now: 		contenu = liste de [concepts_id,jours,id_billet]
	nb_billets = init_dictionnary_list(len(years_bins),0)
	for cont in contenu:
		jour = cont[1]
		for idx, val in enumerate(years_bins):
			if jour in val:
				nb_billets[idx]=nb_billets[idx]+1
	return nb_billets
	



def convert_clique_txt_2_list(clique_txt):
	if not str(clique_txt)=='None' and not len(str(clique_txt))<3:
		clique = clique_txt[1:-1].split(', ')
		return map(int,clique)
	else:
		return []

def build_voisins(contenu,years_bin):
	#now: 		contenu = liste de [concepts_id,jours,id_billet]
	voisins={}
	#voisins[terme,intervalle] = array(termes co-présents)
	for y_b in range(len(years_bins)):
		for ter in dico_termes:
			voisins[(ter,y_b)]=[]
	for cont in contenu:
		intervalle=-1
		for y_b in years_bins:
			intervalle+=1
			if cont[1] in y_b:
				clique = convert_clique_txt_2_list(cont[0])
				for idx, con_1 in enumerate(clique):
					for con_2 in clique[idx:]:						
						if not con_1==con_2:
							temp = voisins[(con_1,intervalle)]
							temp.append(con_2)
							voisins[(con_1,intervalle)]=temp

							temp = voisins[(con_2,intervalle)]
							temp.append(con_1)
							voisins[(con_2,intervalle)]=temp
						else:
							temp = voisins[(con_2,intervalle)]
							temp.append(con_1)
							voisins[(con_1,intervalle)]=temp
	return voisins 


	
def build_cooc(voisins,nb_billets):
	p_cooccurrences={}
	#p_cooccurrences[terme1,terme2,intervalle] = proba du terme
	compt=0
	waiting_time = len(voisins)
	for x,y in voisins.iteritems():
		compt+=1
		if not compt%100:
			print '(#'+str(compt)+' sur '+str(waiting_time)+")"
		
		N = nb_billets[x[1]]
		terme1 = x[0]
		inter = x[1]
		voisinage = set(y)
		dict_temp={}
		for terme2 in voisinage:
			dict_temp[terme2] = 0
		for terme2 in y:
			dict_temp[terme2] = dict_temp[terme2]  + 1
		for terme2 in voisinage:
			p_cooccurrences[(terme1,terme2,inter)] = float(dict_temp[terme2]) / N
	print 'matrice temporelle de cooccurrence ecrite'
	return p_cooccurrences




def build_cooc_matrix(contenu, years_bin):
	#before: 	contenu = List de [concept1,concept2,jours,id_b]
	#now: 		contenu = liste de [concepts_id,jours,id_billet]
	nb_billets = build_nbbillet(contenu,years_bin)
	print "variable nombre de billets construite"
	voisins = build_voisins(contenu,years_bin)
	print "variable voisins construite"
	p_cooccurrences=build_cooc(voisins,nb_billets)
	return p_cooccurrences
	
	
#muti[(terme1,terme2,intervalle)]=MI(t1,t2,t)
def build_mutual_information(p_cooccurrences):
	muti={}
	for x,y in p_cooccurrences.iteritems():
		muti[x]=math.log10( y/float((p_cooccurrences[(x[0],x[0],x[2])]*p_cooccurrences[(x[1],x[1],x[2])])))
		#print str(p_cooccurrences[(x[0],x[0],x[2])])+'\t'+ str(p_cooccurrences[(x[1],x[1],x[2])])+'\t'+str(y)
		#print str(muti[x])
	return muti
	
def initialiser_zeros(dico_termes):
	num={}
	for x in dico_termes:
		num[x]=0
	return num
	
def build_precision(muti):
	precision={}
	voisinages_pos={}
	voisinages={}
	dico_t={}
	for x, y in muti.iteritems():
		if y>0:
			temp=voisinages_pos.get((x[0],x[2]),[])
			temp.append(x[1])
			voisinages_pos[(x[0],x[2])]=temp
		temp = dico_t.get(x[2],[])
		if not x[0] in temp:
			temp.append(x[0])
		dico_t[x[2]] = temp
	print "voisinages_pos ecrite"
	
	compt=0
	for element1,contextes in voisinages_pos.iteritems():
		terme1 = element1[0]
		inter = int(element1[1])
		compt+=1
		if not compt%100:
			print '(#'+str(compt)+")"
		denom=0
		num=initialiser_zeros(dico_t[inter])
		for contexte in contextes:
			MI = muti[(terme1,contexte,inter)]
			#print MI
			denom = denom + MI
			for terme2 in contextes:#dico_t[inter]:#contextes:#dico_t[inter]:#soit on compare par rapport à tous les neuds/ soit uniquement parmi les contextes positifs
				if not terme2==terme1:
					try:
						if muti[(terme2,contexte,inter)]>0:
							num[terme2]=num[terme2]+ min(MI,muti[(terme2,contexte,inter)])
					except:
						pass

		for terme2 in contextes:#dico_t[inter]:#contextes:#dico_t[inter]:#soit on compare par rapport à tous les neuds/ soit uniquement parmi les contextes positifs
			try:
				precision[(terme2,terme1,inter)]=float(num[terme2])/denom
			except:
				pass
	return precision





def build_chavabien(p_cooccurrences):
	dist_mat={}
	for element in p_cooccurrences:
		if element[0]!=element[1]:
			dist_mat[element] = math.pow(p_cooccurrences[element]/p_cooccurrences[element[0],element[0],element[2]],0.01)*p_cooccurrences[element]/p_cooccurrences[element[1],element[1],element[2]]
	return dist_mat


def distance(delta,p_cooccurrences):
	if delta=='precision':
		muti = build_mutual_information(p_cooccurrences)
	#	print muti
		print 'matrice temporelle d information mutuelle ecrite'
		dist_mat = build_precision(muti)
		for x,y in dist_mat.iteritems():
			terme1 = x[0]
			terme2 = x[1]
			temps  = x[2]
		print 'matrice de distance de precision ecrite'
	if delta=='cooc':
		dist_mat = build_chavabien(p_cooccurrences)
		print 'matrice de distance de precision ecrite'
	return dist_mat


def lire_dist_mat_file(fichier_CF):
	dist_mat_temp={}
	file=open(fichier_CF,'r')
	for line in file.readlines():
		linev = line.split('\t')
		dist_mat_temp[(linev[0],linev[1])]=linev[2][:-1]
	return dist_mat_temp

def dedoubler(dico_termes,years_bins):
	dico_termes_temp={}
	for inter in range(len(years_bins)):
		for x,y in dico_termes.iteritems():
			dico_termes_temp[(inter,x)]=y
	return dico_termes_temp

def compare_dictionnaire(dist_mat_temp_old,dist_mat_temp):
		commun = 0
		total_old = len(dist_mat_temp_old)
		total_new = len(dist_mat_temp)
		for x in dist_mat_temp_old:
			if x in dist_mat_temp:
				commun += 1
		return commun, total_old, total_new
		

		
dico_termes=build_dico()
#print dico_termes	
name_date = str(years_bins[0][0]) + '_' + str(years_bins[0][-1]) + '_'+ str(years_bins[1][0])+ '_'+str(years_bins[-1][-1])
try:# si on a deja calcule le reseau de proximit
	try:
		p_cooccurrences = fonctions.dumpingout('p_cooccurrences'+name_date)
		dist_mat = fonctions.dumpingout('dist_mat'+name_date)
	except:
		p_cooccurrences={}
		dist_mat={}
		for inter in range(len(years_bins)):
			print inter
			fichier_CF=path_req +'reseau/'+'reseauCF_niv_1_'+dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt'
			fichier_cooc=path_req +'reseau/'+'reseauCF_niv_cooc__'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt'
			fichier_gexf = path_req + 'gexf/' + 'reseau_champ_0_'+'_' + dist_type +'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.gexf'		
			if inter>0:
				dist_mat_temp_old = deepcopy(dist_mat_temp)
			dist_mat_temp = lire_dist_mat_file(fichier_CF)
			p_cooccurrences_temp=lire_dist_mat_file(fichier_cooc)
			for x,y in dist_mat_temp.iteritems():
				dist_mat[(int(x[0]),int(x[1]),int(inter))]=y
			for x,y in p_cooccurrences_temp.iteritems():
				p_cooccurrences[(int(x[0]),int(x[1]),int(inter))]=y
			try:
				os.mkdir(path_req +'gexf')
			except:
				pass
			level={}
			for x in dico_termes:
				level[x]=1
			gexf.gexf_builder(dico_termes,dist_mat_temp,fichier_gexf,level)
			print 'cest fini ou presque'
		fonctions.ecrire_dico(dico_termes,dico_termes,dico_termes,1)
		
		fonctions.dumpingin(p_cooccurrences,'p_cooccurrences'+name_date)
		fonctions.dumpingin(dist_mat,'dist_mat'+name_date)
		
		
except:# sinon on recalcule du début
	#contenu = fonctions_bdd.select_bdd_table(name_bdd,'sem','concept1,concept2,jours,id_b',requete)
	contenu = fonctions_bdd.select_bdd_table(name_bdd,'billets','concepts_id,jours,id',requete)
	print "contenu importé"
	p_cooccurrences = build_cooc_matrix(contenu,years_bins)
	print "matrice de cooccurrence construite"
	fonctions.ecrire_reseau(p_cooccurrences,years_bins,'',0,'cooc',dedoubler(dico_termes,years_bins))		 	
	dist_mat = distance(dist_type,p_cooccurrences)
	print "matrice de distance construite"
	fonctions.ecrire_reseau(dist_mat,years_bins,dist_type,seuil,1,dedoubler(dico_termes,years_bins))		 
	pass
	
print 'matrice de cooccurrences et de distance en mémoire'