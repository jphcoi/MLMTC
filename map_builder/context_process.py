#!/usr/bin/python
# -*- coding: utf-8 -*-
#recupere les liens des trois reseaux pour exporter les reseaux au format texte
import sys
import math
import gexf
from copy import deepcopy
sys.path.append("../scripts/libraries")
sys.path.append("../scripts")

print "context_process.py (20091102)"
print "--------------------------------\n"

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
import multiprocessing
import time
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
user_interface=parameters.user_interface
seuil=0.2
seuil=0
###################################
#######export #####################
###################################
	

def verif_sym(dictionnaire_temp, sym=0):
	print 'on contrôle la matrice symétrique'
	for x,y in dictionnaire_temp.iteritems():
		if not (x[1],x[0],x[2]) in  dictionnaire_temp:
			print 'ouillllllle'
		else:
			if sym>0:
				if not dictionnaire_temp[(x[1],x[0],x[2])] == y:
					print 'passym'
	print 'fin du contrôle'

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

# def build_voisins(contenu,years_bin):
# 	#now: contenu = liste de [concepts_id,jours,id_billet]
# 	voisins={}
# 	#voisins[terme,intervalle] = array(termes co-présents)
# 	for y_b in range(len(years_bins)):
# 		for ter in dico_termes:
# 			voisins[(ter,y_b)]=[]
# 	for cont in contenu:
# 		for intervalle,y_b in enumerate(years_bins):
# 			if cont[1] in y_b:
# 				clique = convert_clique_txt_2_list(cont[0])
# 				for idx, con_1 in enumerate(clique):
# 					for con_2 in clique[idx:]:						
# 						if not con_1==con_2:
# 							temp = voisins[(con_1,intervalle)]
# 							temp.append(con_2)
# 							voisins[(con_1,intervalle)]=temp
# 
# 							temp = voisins[(con_2,intervalle)]
# 							temp.append(con_1)
# 							voisins[(con_2,intervalle)]=temp
# 						else:
# 							temp = voisins[(con_1,intervalle)]
# 							temp.append(con_1)
# 							voisins[(con_1,intervalle)]=temp
# 	return voisins 


# 	
# def build_cooc(voisins,nb_billets):
# 	p_cooccurrences={}
# 	#p_cooccurrences[terme1,terme2,intervalle] = proba du terme
# 	compt=0
# 	waiting_time = len(voisins)
# 	for x,y in voisins.iteritems():
# 		compt+=1
# 		if not compt%100:
# 			print '(#'+str(compt)+' sur '+str(waiting_time)+")"
# 		
# 		N = nb_billets[x[1]]
# 		terme1 = x[0]
# 		inter = x[1]
# 		voisinage = set(y)
# 		dict_temp={}
# 		for terme2 in voisinage:
# 			dict_temp[terme2] = 0
# 		for terme2 in y:
# 			dict_temp[terme2] = dict_temp[terme2]  + 1
# 				
# 		for terme2 in voisinage:
# 			#more than one cooccurrence:
# 			if dict_temp[terme2]>=parameters.seuil_cooccurrences:
# 				p_cooccurrences[(int(terme1),int(terme2),int(inter))] = float(dict_temp[terme2]) / float(N)
# 	print 'matrice temporelle de cooccurrence ecrite'
# 	return p_cooccurrences
# 
# 
# 
# 
# 
# 
# # 
# 
# def build_cooc_matrix(contenu, years_bin):
# 	#before: 	contenu = List de [concept1,concept2,jours,id_b]
# 	#now: 		contenu = liste de [concepts_id,jours,id_billet]
# 	nb_billets = build_nbbillet(contenu,years_bin)
# 	print "variable nombre de billets construite"
# 	voisins = build_voisins(contenu,years_bin)
# 	print "variable voisins construite"
# 	p_cooccurrences=build_cooc(voisins,nb_billets)
# 	return p_cooccurrences
# 	
	
#muti[(terme1,terme2,intervalle)]=MI(t1,t2,t)
def build_mutual_information(cooccurrences,nb_cooc,cooccurrences_somme):
	muti={}
	for couple,cooc in cooccurrences.iteritems():
		(terme1,terme2)=couple
		if cooc>parameters.seuil_cooccurrences:
			muti_val=math.log10( cooc * nb_cooc /float((cooccurrences_somme[terme1]*cooccurrences_somme[terme2])))
			muti.setdefault(terme1,{})
			muti.setdefault(terme2,{})
			muti[terme1].setdefault(terme2,muti_val)
			muti[terme2].setdefault(terme1,muti_val)
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
	#	couple_trans = (cont,inter)
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
	# for x,y in muti.iteritems():
	# 	if y>0:
	# 		muti_pos[x]=y
	# 		temp=voisinages_pos.get((x[0],x[2]),[])
	# 		temp.append(x[1])
	# 		voisinages_pos[(x[0],x[2])]=temp
	# print "voisinages_pos ecrite"
	# muti=muti_pos
	# compt=0
	# N=len(voisinages_pos.keys())
	# muti2d = convert_muti3d_muti2d(muti)
	# print 'matrice d information mutuelle 2d calculée'
	#for element1,contextes in voisinages_pos.iteritems():
	compt=0
	N=len(muti.keys())
	for terme1,muti_terme1 in muti.iteritems():
		compt+=1
		if not compt%100:
			print '(#'+str(compt)+" sur "+str(N) +")"

		denom = sum(muti_terme1.values())
		for terme2 in muti_terme1.keys():#on itere donc sur les termes2 qui ont cooccuré au moins deux fois avec terme1
			muti_terme2 = muti[terme2]
			somme_min =  fonctions_lib.merge0(muti_terme1, muti_terme2, lambda x,y: min(x,y))
			precision[(terme1,terme2)] = sum(somme_min.values())/denom
		# 	
		# 	
		# terme1 = element1[0]
		# inter = int(element1[1])
		# MI_terme1 = muti2d[(terme1,inter)]
		# denom = sum(MI_terme1.values())
		# for cont,val in MI_terme1.iteritems():
		# 	if cont != terme1:
		# 		MI_terme2 = muti2d[(cont,inter)]
		# 		somme_min =  fonctions_lib.merge0(MI_terme1, MI_terme2, lambda x,y: min(x,y))
		# 		precision[(cont,terme1,inter)] = sum(somme_min.values())/denom
				
	print 'matrice de precision calculée'
	return precision





def build_chavabien(p_cooccurrences):
	dist_mat={}
	for element in p_cooccurrences:
		if element[0]!=element[1]:
			dist_mat[element] = math.pow(p_cooccurrences[element]/p_cooccurrences[element[0],element[0],element[2]],0.01)*p_cooccurrences[element]/p_cooccurrences[element[1],element[1],element[2]]
	return dist_mat


def distance(delta,cooccurrences,nb_cooc,cooccurrences_somme):
	if delta=='precision':
		muti = build_mutual_information(cooccurrences,nb_cooc,cooccurrences_somme)#muti est un dictionnaire dont les clés sont les termes et les valeurs des dictionnaires dont les clés sont d'autres termes et les valeurs des informations mutuelles.
		print 'matrice temporelle d information mutuelle ecrite'		
		dist_mat = build_precision(muti)
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
		
def remplir_colonne_distance_sem_weighted(dist_mat):
	print 'in remplir_colonne_distance_sem_weighted'
	contenu = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'sem_weighted','id,concept1,concept2,periode',' where 1 limit 10000')
	sem_weighted_triplet_id={}
	j=0
	N=len(contenu)
	print N
	for cont in contenu:
		j+=1
		if not j%1000:
			print j , N
		sem_weighted_triplet_id[(cont[1],cont[2],cont[3])]=cont[0]
	champs_liste=[]
	champs_name=[]
	j=0
	N  = len(dist_mat.keys())
	for x,y in dist_mat.iteritems():
		j+=1
		if not j%1000:
			print j , N
		#if x in sem_weighted_triplet_id:
		id_triplet = sem_weighted_triplet_id[x]
		champs_liste.append((id_triplet,y))
		champs_name.append('distance0')
		id_triplet = sem_weighted_triplet_id[(x[1],x[0],x[2])]
		champs_liste.append((id_triplet,y))
		champs_name.append('distance1')
		
		#else:
			# #c'est une distance entrante!
			# try:
			# 	x=(x[1],x[0],x[2])
			# 	id_triplet = sem_weighted_triplet_id[x]
			# 	champs_liste.append((id_triplet,y))
			# 	champs_name.append('distance1')
			# except:
			# 	#some distances may be under the threshold.
			# 	pass
	fonctions_bdd.update_multi_table(name_bdd,'sem_weighted',champs_name,champs_liste)
	print "remplit la colonne champ_name d'indice id - entree liste de doublon (id, valeur)"
		





def build_cooc_ok(contenu_occurrences):
	nb_cooc=0
	cooccurrences,cooccurrences_somme,occurrences={},{},{}
	compt=0
	N = len(contenu_occurrences.keys())
	i=0
	for id_abstract,cont in contenu_occurrences.iteritems():
		if type(cont) is str:
			clique = list(map(int,eval(cont)))
		else:	
			clique = list(map(int,unique(cont.keys())))
		i+=1
		if not i%100:
			print str(i) + ' (over ' +str(N)+ ')'
		for x in clique:
			occurrences[x] = occurrences.get(x,0) + 1
		if len(clique)>1:
			for idx, terme1 in enumerate(clique[:-1]):
				for terme2 in clique[idx+1:]:
					cooccurrences[(terme1,terme2)] = cooccurrences.get((terme1,terme2),0) + 1
					cooccurrences[(terme2,terme1)] = cooccurrences.get((terme2,terme1),0) + 1
					cooccurrences_somme[terme1] =  cooccurrences_somme.get(terme1,0) + 1
					cooccurrences_somme[terme2] =  cooccurrences_somme.get(terme2,0) + 1		
					nb_cooc = nb_cooc + 2
	return cooccurrences,nb_cooc,cooccurrences_somme,occurrences


def get_distance(inter):
	print 'nouvelle iteration ',inter
	years=years_bins[inter]
	print years
	where=' where jours in ('+ str(years)[1:-1] + ')'
	#lignes = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'billets','id,concepts_id',where)
	print 'ici1'
	print name_bdd
	print where
	lignes = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'billets','id,concepts_id',where)
	print 'ici2'
	
	contenu_occurrences={}
	for ligne in lignes:
		contenu_occurrences[ligne[0]]=ligne[1]
	print 'ici3'
	cooccurrences,nb_cooc,cooccurrences_somme,occurrences=build_cooc_ok(contenu_occurrences)#contenu_occurrences = dictionnaire: id,concepts_ids
# 	coocs = fonctions_bdd.select_bdd_table(name_bdd,'sem_weighted','concept1,concept2,periode,cooccurrences')
# 	contenu = fonctions_bdd.select_bdd_table(name_bdd,'billets','id,jours',requete)
# 	nb_billets = build_nbbillet(contenu,years_bins)

	print inter 
	print 'somme'

	dist_mat = distance(dist_type,cooccurrences,nb_cooc,cooccurrences_somme)

	# print sum(cooccurrences.values())
	# lienssem_weighted=[]
	# for x,y in cooccurrences.iteritems():
	# 	if y>=parameters.seuil_cooccurrences:
	# 		lienssem_weighted.append((x[0],x[1],inter,y))
	# for x,y in cooccurrences_somme.iteritems():
	# 	if y>=parameters.seuil_cooccurrences:
	# 		lienssem_weighted.append((x,x,inter,y))
	# 
	# fonctions_bdd.remplir_table(name_bdd,'sem_weighted',lienssem_weighted,"(concept1,concept2,periode,cooccurrences)")



	#INUTILE DE CALCULER p_cooc
	# for couple,cooc in cooccurrences.iteritems():
	# 	if int(cooc)>=parameters.seuil_cooccurrences:
	# 		terme1 = int(couple[0])
	# 		terme2 = int(couple[1])
	# 		p = float(cooc)/float(nb_cooc)
	# 		p_cooccurrences[(terme1,terme2,inter)] = p

	# for terme,cooc in cooccurrences_somme.iteritems():
	# 	if int(cooc)>=parameters.seuil_cooccurrences:
	# 		p = float(cooc)/float(nb_cooc)
	# 		p_cooccurrences[(int(terme),int(terme),inter)] = p

	#print "matrice de cooccurrence construite"


#	fonctions.ecrire_reseau(p_cooccurrences,years_bins,'',0,'cooc',dedoubler(dico_termes,years_bins))		 	

#INUTILE D'ECRIRE RESEAU CF de cooccurrences
#fonctions.ecrire_reseau_CF(p_cooccurrences,years_bins,'',0,'cooc')

#INUTILE DE CALCULER TOUTES LES DISTANCES A LA FOIS
#dist_mat = distance(dist_type,p_cooccurrences)

	print "matrice de distance construite"
#	fonctions.ecrire_reseau(dist_mat,years_bins,dist_type,seuil,1,dedoubler(dico_termes,years_bins))		 
	fonctions.ecrire_reseau_CF_inter(dist_mat,inter,dist_type,seuil,1)




dico_termes=fonctions.build_dico()
#print dico_termes	




print years_bins
if len(years_bins)>1:
	name_date = str(years_bins[0][0]) + '_' + str(years_bins[0][-1]) + '_'+ str(years_bins[1][0])+ '_'+str(years_bins[-1][-1])
else:
	name_date = str(years_bins[0][0]) + '_' + str(years_bins[0][-1]) + '_'+ str(years_bins[0][0])+ '_'+str(years_bins[-1][-1])
try:
	os.mkdir(path_req +'gexf')
except:
	pass
					
try:# si on a deja calcule le reseau de proximit
	if user_interface =='y':
		var = raw_input('do you wish to try to rebuild cooccurrence matrix  ? (y to rebuild)')
	else:
		var='n'	
		
	try:
		if var =='y':
			fonctions.dumpingout('klqsdjlmsqjdklqsmd')
		
		#p_cooccurrences = fonctions.dumpingout('p_cooccurrences'+name_date)
		print 'dist_mat loading...'
		#dist_mat = fonctions.dumpingout('dist_mat'+name_date)
		dist_mat = fonctions.dumpingout('dist_mat_10'+name_date)

	except:
		if var =='y':
			print 'on reconstruit'
			fonctions.dumpingout('klqsdjlmsqjdklqsmd')

		#p_cooccurrences={}
		dist_mat={}
		dist_mat_10={}
		print 'on construit la version pkl de dist_mat'
		for inter in range(len(years_bins)):
			fichier_CF=path_req +'reseau/'+'reseauCF_niv_1_'+dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt'
			#fichier_cooc=path_req +'reseau/'+'reseauCF_niv_cooc__'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt'
			fichier_gexf = path_req + 'gexf/' + 'reseau_champ_0_'+'_' + dist_type +'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.gexf'		

#			if inter>0:
#				dist_mat_temp_old = deepcopy(dist_mat_temp)
			dist_mat_temp = lire_dist_mat_file(fichier_CF)
			dist_mat_temp_res = {}
			for x,y in dist_mat_temp.iteritems():
				if not int(x[0]) in dist_mat_temp_res:
					dic = {}	
				else:
					dic = dist_mat_temp_res[int(x[0])]
				dic[int(x[1])]=float(y)
				dist_mat_temp_res[int(x[0])] = dic
			dist_mat_temp_res_10 = fonctions.seuiller(dist_mat_temp_res,10)
			print 'on construit maintenant dist_mat pour chaque periode ' + str(inter)
			for x,y in dist_mat_temp.iteritems():
				dist_mat[(int(x[0]),int(x[1]),int(inter))]=y
			for x,y in dist_mat_temp_res_10.iteritems():
				for u in y:
					dist_mat_10[(int(x),int(u[0]),int(inter))]=u[1]
			level={}
			for x in dico_termes:
				level[x]=1
			gexf.gexf_builder(dico_termes,dist_mat_temp,fichier_gexf,level)
			
		fonctions.ecrire_dico(dico_termes,dico_termes,dico_termes,1)
		print 'dicos ecrits'
		#fonctions.dumpingin(p_cooccurrences,'p_cooccurrences'+name_date)
		fonctions.dumpingin(dist_mat_10,'dist_mat_10'+name_date)
		print 'on a dumpé distmat_10: top 10 de chaque terme'
		fonctions.dumpingin(dist_mat,'dist_mat'+name_date)
		print 'on a dumpé distmat'
		
		try: 
			fonctions_bdd.detruire_table(name_bdd,'sem_weighted')
		except: pass
		#fonctions_bdd.creer_table_sem(name_bdd,'sem')
		fonctions_bdd.creer_table_sem_periode_valuee(name_bdd,'sem_weighted')
		lienssem_weighted=[]
		deja=[]
		for x,dist0 in dist_mat_10.iteritems():
			if not x in deja:
				deja.append((x[1],x[0],x[2]))
				deja.append(x)
				dist1 = dist_mat_10.get((x[1],x[0],x[2]),'')
				lienssem_weighted.append((x[0],x[1],x[2],dist0,dist1))
		starttime= time.time()
		
		fonctions_bdd.remplir_table_new(name_bdd,'sem_weighted',lienssem_weighted,"(concept1,concept2,periode,distance0,distance1)")
		
		print '\n\n\ncombien de temps:',time.time()-starttime
		
		#remplir_colonne_distance_sem_weighted(dist_mat)		
		#remplir_colonne_distance_sem_weighted(dist_mat_10)		
		#print 'on a enregistre la variable dist_mat' + name_date + ' en mémoire et remplit la table sem_weighted avec les distances positives.'
		
except:# sinon on recalcule du début
	print 'on calcule les données de départ'
	#p_cooccurrences  = {}
	pool_size = int(multiprocessing.cpu_count()*2)
	pool = multiprocessing.Pool(processes=pool_size)
	print years_bins
	inters= range(len(years_bins))
	pool.map(get_distance, inters)
	#for inter,years in enumerate(years_bins):

print 'matrice de cooccurrences et de distance en mémoire'
