#!/usr/bin/python
# -*- coding: utf-8 -*-

print "db_processing_net v0.2 (ccr) (20091102)"
print "---------------------------------------\n"

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
from datetime import timedelta
from datetime import date
import parameters
import fonctions_lib
###################################
#######0.quelques parametres#######
###################################

maxTermLength = parameters.maxTermLength
name_bdd = parameters.name_bdd
freqmin = parameters.freqmin
name_data = parameters.name_data 
requete = parameters.requete
user_interface=parameters.user_interface
name_data_real = parameters.name_data_real
#lemmadictionnary = parameters.lemmadictionary# si nul, on  calcule ou recalcule  le dico de lemmes sur la requete consideree sinon on ne calcule pas
path_req = parameters.path_req
sep = parameters.sep
build_link_tables=parameters.build_link_tables
language = parameters.language
maxTermLength = parameters.maxTermLength

###################################
#######3.Indexer les billets#######
###################################

# # on indexe a partir de la liste des ngrammes tries
# 
# filename = path_req + requete + '_' + str(freqmin) + '_' + 'liste_n-grammes_freq_comparatif'  +'_trie' + '.csv' #fichier d'entree trie (rajouter _trie a la fin de la sortie standard)
# #print filename
# if os.path.isfile(filename) == 1:
# 	print '--- on indexe a partir du fichier \"' + filename+"\""
# else:
# 	filename = path_req + 'concepts.csv' #fichier d'entree trie (rajouter _trie a la fin de la sortie standard)
# 	if not os.path.isfile(filename) == 1:
# 		filename_leven_redond =  path_req + requete + '_' + str(freqmin) + '_' + 'liste_n-grammes_freq_divers_leven_noredond.csv'
# 		filename = filename_leven_redond
		
		
# print '--- on indexe a partir du fichier \"' + filename+"\""
# #on lit le fichier des n-grammes a indexer
# ngrammes = misc.lire_dico_classes(filename,language)
# #pour plus de sûreté
# ngrammes = misc.lire_dico_classes(filename,language)
# #pour plus de sûreté
# ngrammes = misc.lire_dico_classes(filename,language)


# #affichage de la liste des 10 premiers concepts
# print "--- les 10 premiers concepts (sur " +str(len(ngrammes))+") : "
# for gra in ngrammes[:10]:
# 	try:
# 		print "    ",str([gra])
# 	except:
# 		print "encodage error"
# 
# if len(ngrammes)>1000:
# 	print "vous avez "+str(len(ngrammes)) + ' concepts, au-delà de 2000 concepts, le script peut devenir tres long'
# 	if user_interface =='y':
# 		var = raw_input('reduire la liste avant de lancer l\'indexation ? (y pour arreter, tout autre touche pour continuer)')
# 	else:
# 		var = 'n'
# 	if var=='y':
# 		exit()
###################################
#####indexation des billets########
###################################

def extension(x,y):
	x.extend(y)
	return list(set(x))
	

def agency(targets,contenu):
	extraits=[]
	extraits_no=[]
	billetprocessed=0
	for billets in contenu:
		#contenu = fonctions_bdd.select_bdd_table_limite(name_bdd,'billets','id,content_lemmatise,content,jours,title,site,categorie1',requete,lim_d+','+duration)
		billetprocessed+=1
		an = billets[3]
		titre = billets[4]
		auteur = billets[5]
		categ1 = billets[6]
		billet_id = billets[0]
		billet_lemmatise=billets[1]
		billet_lemmatise_v = billet_lemmatise.split()
		billet_brut=billets[2]
		billet_brut = billet_brut.replace('<b>','').replace('</b>','')
		billet_brutv = billet_brut.split()
		billet_brutv_copie = billet_brut.split()
		billet_lemmatise=' '+unicode(billet_lemmatise,'utf-8')+' '
		billets_id.append(billet_id)
		#ngramme_fit_index=[]
		for termLengthMinusOne in range(maxTermLength): # minusOne because range(maxTermLength)= [0,...,maxTermLength - 1]
			for i in range(len(billet_lemmatise_v) - termLengthMinusOne): 
				if i == 0 :
					wordWindow = billet_lemmatise_v[:termLengthMinusOne + 1]
				else :
					wordWindow.append(billet_lemmatise_v[i + termLengthMinusOne])
					wordWindow.pop(0)
	 			term = ' '.join(wordWindow)
				for target in targets:
					for ngra in target.split('***'):		
						ngraz1_long = ngra.count(' ')+1
				 		if ngra ==term:
							#affiche l'environnement immédiat.
							#print billet_lemmatise_v[ i-1: i + termLengthMinusOne+2]
							#print billet_brutv[ i-1: i + termLengthMinusOne+2]
							#print billet_lemmatise_v[i:i+termLengthMinusOne+1]
							fin = i-1
							debut=i
							try:
								while  billet_lemmatise_v[fin][:3]!='SE_':
									fin=fin+1
								while	 billet_lemmatise_v[debut][:3]!='SE_':
									debut=debut-1
								type_after=billet_lemmatise_v[i+termLengthMinusOne+1][:3]
								terme_after=billet_brutv[i+termLengthMinusOne+1]
								if type_after=='VV_':
									phrase_v = billet_brutv[ debut+1: fin]
									phrase_v[i-debut-1] = '<b>'+phrase_v[i-debut-1]
									if billet_lemmatise_v[i+termLengthMinusOne+2][:3] == 'VV_':
										phrase_v[i + termLengthMinusOne+1-debut] = phrase_v[i + termLengthMinusOne+1-debut]+'</b>'
									elif billet_brutv[i+termLengthMinusOne+2][:3] == 'not' and billet_lemmatise_v[i+termLengthMinusOne+3][:3] == 'VV_' :
										phrase_v[i + termLengthMinusOne+1-debut+1] = phrase_v[i + termLengthMinusOne+1-debut+1]+'</b>'								
									else:
										phrase_v[i + termLengthMinusOne+1-debut-1] = phrase_v[i + termLengthMinusOne+1-debut-1]+'</b>'
									extrait =  ' '.join(phrase_v)	
									#print len(' '.join(phrase_v[:i-debut-1]))
									#print extrait
									infos=(billet_id,an,titre,auteur,categ1,extrait,billet_brut,len(' '.join(phrase_v[:i-debut-1])))
									if billet_lemmatise_v[i+termLengthMinusOne+2][:3] != 'IN_' and terme_after[-3:] != 'ing':
										extraits.append(infos)
									else:										
										extraits_no.append(infos)
							except:
								pass								
	return extraits,extraits_no			
#il faut découper ici car ça prend trop de RAM
def ecrire_phrases(phrase,fichier,fichier2):
	imax = 0
	for x in phrase:
		imax = max(imax,x[7])
	for x in phrase:
		blanc=''
		for i in range(imax-x[7]):
			blanc = blanc + ' '
		x=map(str,x)
		ext=blanc+x[5]
		ext = ext[imax-50:imax+70]
		print ext
		fichier.write(x[0]+'\t'+ext+'\t'+x[1]+'\t'+x[2]+'\t'+x[3]+'\t'+x[4]+'\t'+x[6]+'\n')
		fichier2.write(x[0]+'\t'+ext+'\t'+'\t'+x[1]+'\n')

Nb_rows = fonctions_bdd.count_rows(name_bdd,'billets')
size_seq = 1000
nb_sequences = Nb_rows/size_seq
billets_id=[]


target = ['NN_network***NP_network***NP_networks']
target = ['NN_gene***NP_gene***NN_genetics***genomic***genomics***NN_genome***genome']
target = ['NN_protein***protein***proteins']
#target = ['NN_phosphatase NN_gene']

agency_name=path_req + 'agency_'+str(target)+'.csv'
agency_name_out=path_req + 'agency_out_'+str(target)+'.csv'
agency_name2=path_req + 'agency_'+str(target)+'.txt'
agency_name_out2=path_req + 'agency_out_'+str(target)+'.txt'
file_oui = open(agency_name,'w')
file_no = open(agency_name_out,'w')
file_oui2 = open(agency_name2,'w')
file_no2 = open(agency_name_out2,'w')
phrases_ok,phrases_out=[],[]
for x in range(nb_sequences+1):
	lim_d = str(size_seq*x)
	duration = str(size_seq)
	#on extrait les champs contenus lemmatises et id de la table
	contenu = fonctions_bdd.select_bdd_table_limite(name_bdd,'billets','id,content_lemmatise,content,jours,title,site,categorie1',requete,lim_d+','+duration)
	include=1 #le parametre include permet d'activer ou non l'overlap de lemmes dans le comptage: si 1, les nicolas sarkozy ne forment pas de sarkozy 
	phrase_ok,phrase_out =  agency(target,contenu)
	phrases_ok=phrases_ok+phrase_ok
	phrases_out=phrases_out+phrase_out
ecrire_phrases(phrases_ok,file_oui,file_oui2)
ecrire_phrases(phrases_out,file_no,file_no2)
