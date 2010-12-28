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
from operator import itemgetter
import operator
import parameters
import fonctions_bdd
import parseur
import fonctions_lib
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
	



def unique(lis):
	lisunique=[]
	for x in lis:
		if not x in lisunique:
			lisunique.append(x)
	return lisunique
	
def convert_clique_txt_2_list(clique_txt):
	if not str(clique_txt)=='None' and not len(str(clique_txt))<3:
		clique = clique_txt[1:-1].split(', ')
		return unique(list(map(int,clique)))
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

def rajouter_dico_simple_dico(muti2d,couple,cont,valeur):
	if couple in muti2d:
		temp = muti2d[couple]
		if cont in temp:
			print 'probleme'
		else:
			temp[cont] = valeur
		muti2d[couple] = temp
	else:
		temp ={}
		temp[cont] = valeur
		muti2d[couple] = temp
	return muti2d
	
def convert_muti3d_muti2d(muti):
	muti2d={}
	#on construit également la transposée
	#muti2d_trans={}
	for cles,valeur in muti.iteritems():
		terme = cles[0]
		cont = cles[1]
		inter = cles[2]
		couple  = (terme,inter)
		couple_trans = (cont,inter)
		muti2d = rajouter_dico_simple_dico(muti2d,couple,cont,valeur)
	#	muti2d_trans = rajouter_dico_simple_dico(muti2d_trans,couple_trans,terme,valeur)
	return muti2d#,muti2d_trans

def convert_dist_mat3d_dist2d(dist_mat):
	dist2d={}
	dist2d_trans={}
	#on construit également la transposée
	#muti2d_trans={}
	for cles,valeur in dist_mat.iteritems():
		terme1 = cles[0]
		terme2 = cles[1]
		inter = cles[2]
		couple  = (terme1,terme2)
		couple_trans  = (terme2,terme1)
		dist2d = rajouter_dico_simple_dico(dist2d,couple,inter,valeur)
		dist2d_trans = rajouter_dico_simple_dico(dist2d_trans,couple_trans,inter,valeur)
	return dist2d,dist2d_trans#,muti2d_trans


	
def build_precision(muti):
	precision={}
	precisionold={}
	voisinages_pos={}
	voisinages={}
	muti_pos = {}
	for x, y in muti.iteritems():
		if y>0:
			muti_pos[x]=y
			temp=voisinages_pos.get((x[0],x[2]),[])
			temp.append(x[1])
			voisinages_pos[(x[0],x[2])]=temp
	print "voisinages_pos ecrite"
	muti=muti_pos
	compt=0
	N=len(voisinages_pos.keys())
	muti2d = convert_muti3d_muti2d(muti)
	print 'matrice d information mutuelle 2d calculée'
	for element1,contextes in voisinages_pos.iteritems():
		terme1 = element1[0]
		inter = int(element1[1])
		compt+=1
		if not compt%100:
			print '(#'+str(compt)+" sur "+str(N) +")"
		MI_terme1 = muti2d[(terme1,inter)]
		denom = sum(MI_terme1.values())
		for cont,val in MI_terme1.iteritems():
			if cont != terme1:
				MI_terme2 = muti2d[(cont,inter)]
				somme_min =  fonctions_lib.merge0(MI_terme1, MI_terme2, lambda x,y: min(x,y))
				precision[(cont,terme1,inter)] = sum(somme_min.values())/denom
				
	print 'matrice de precision calculée'
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
		

		
dico_termes=fonctions.build_dico()
#print dico_termes	
print years_bins
name_date = str(years_bins[0][0]) + '_' + str(years_bins[0][-1]) + '_'+ str(years_bins[1][0])+ '_'+str(years_bins[-1][-1])

def add_zeros(dyn,years_bins):
	dyna = []
	for y in range(len(years_bins)):
		dyna.append("%.3f" %dyn.get(y,0.))
	return dyna


name_date = str(years_bins[0][0]) + '_' +str(years_bins[-1][-1])

#construction des voisinages dynamiques:

#on crée la table des voisins
try:
	fonctions_bdd.drop_table(name_bdd,'termneighbour')
except:
	pass
fonctions_bdd.creer_table_term_neighbor(name_bdd,'termneighbour')
#on importe les données si ce n'est pas déjà fait
try:
	
	dist_2d=fonctions.dumpingout('dist_2d'+name_date)
	dist_2d_trans=fonctions.dumpingout('dist_2d_trans'+name_date)
	print 'on charge dist_2d_trans deja calculé'
	
except:
	print 'on calcule dist_2d_trans pour les dates indiquées'
	try:
		contenu[0]==1
	except:
		contenu = fonctions_bdd.select_bdd_table(name_bdd,'billets','concepts_id,jours,id',requete)
		print "contenu importé"
	print "on construit la variable avec tous les jours"
	#on va plutôt calculer les distances par période, c'est moins long!!!
	#sinon ci dessous version au jour le jour
	# years_bins_jour = range(years_bins[0][0],years_bins[-1][-1]+1)
	# 	years_bins=[]
	# 	for x in years_bins_jour:
	# 		years_bins.append([x])
	# 	print years_bins
	p_cooccurrences = build_cooc_matrix(contenu,years_bins)
	print "matrice de cooccurrence sur tous les jours construite"
	dist_mat = distance(dist_type,p_cooccurrences)
	print "matrice de distance construite"
	dist_2d,dist_2d_trans = convert_dist_mat3d_dist2d(dist_mat)
	fonctions.dumpingin(dist_2d,'dist_2d'+name_date)
	fonctions.dumpingin(dist_2d_trans,'dist_2d_trans'+name_date)


def turn1d_moy(dict_couple):
	dict_mono_dict={}
	for couple,valeurs in dict_couple.iteritems():
		x=couple[0]
		y=couple[1]
		if x in dict_mono_dict:
			temp = dict_mono_dict[x]
		else:
			temp = {}
		temp[y]=moy = float(sum(valeurs.values())/n)
		dict_mono_dict[x]=temp
	return 	dict_mono_dict

n=len(years_bins)
dist_1d = turn1d_moy(dist_2d)
dist_1d_trans = turn1d_moy(dist_2d_trans)

def export_nfirst(dist_2d,dist_1d,direction,nfirst):
	dist_2d_vector = []
	for x,vois_forcemoy in dist_1d.iteritems():
		vois_forcemoy_sorted = sorted(vois_forcemoy.iteritems(), key=operator.itemgetter(1),reverse=True)
		for voisin_force in vois_forcemoy_sorted[:nfirst]:
			voisin = voisin_force[0]
			force =voisin_force[1]
			dist_2d_vector.append((x,voisin,','.join(map(str,add_zeros(dist_2d[(x,voisin)],years_bins))),str("%.3f" %(force)),direction))
	return dist_2d_vector
	
thres = 50
dist_2d_vector=export_nfirst(dist_2d,dist_1d,'1',thres)
fonctions_bdd.remplir_table(name_bdd,'termneighbour',dist_2d_vector,"(term1,term2, distances,force_moy,direction)")

dist_2d_vector_trans=export_nfirst(dist_2d_trans,dist_1d_trans,'0',thres)
fonctions_bdd.remplir_table(name_bdd,'termneighbour',dist_2d_vector_trans,"(term1,term2,distances,force_moy,direction)")
#fonctions.ecrire_reseau(dist_mat,years_bins,dist_type,seuil,1,dedoubler(dico_termes,years_bins))		 
