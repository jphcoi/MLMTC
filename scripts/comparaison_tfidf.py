#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import timedelta
from datetime import date
import sys
sys.path.append("./libraries")

print "database_builder v0.2 (20091102)"
print "--------------------------------\n"

import parameters
import fonctions_bdd
import parseur
import text_processing
import codecs 
import parameters
import math
###################################
#######0.quelques parametres#######
###################################

name_bdd = parameters.name_bdd
freqmin = parameters.freqmin
name_data = parameters.name_data 
requete = parameters.requete
name_data_real = parameters.name_data_real
path_req = parameters.path_req
years=parameters.years_bins_no_overlap

def lire_pretrie(fichier,colonne):
	file = open(fichier,'r')
	dico_pre_trie={}
	for line in file.readlines():
		line = line[:-1].replace('"','')
		linev = line.split('\t')
		nlemme = linev[0]
		valeur = linev[colonne].replace('\n','').replace('\r','')
		if nlemme not in dico_pre_trie:
			dico_pre_trie[nlemme]=valeur
	return dico_pre_trie

def lire_nlemme_freq(fichier):
	file = open(fichier,'r')
	sortie ={}
	maj ={}
	for line in file.readlines():
		linev = line.split('\t')
		if 'year' in fichier:
			sortie[linev[0]] = linev[2:]
		else:		
			freq=linev[2].replace(',','.')
			sortie[linev[0]]=float(freq[:-1]) * 100
			freq_aut=linev[3].replace(',','.')
			sortie[linev[0]]=(float(freq[:-1]) * 100,float(freq_aut[:-1]) * 100)
		maj[linev[0]]=linev[1]
	return sortie,maj


def find_sub(dico_pre_trie,elem):
	elem_s = set(elem.split('***'))
	sortie=''
	for el in dico_pre_trie:
		el_s = set(el.split('***'))
		if el_s <= elem_s or elem_s <=el_s:
			#print str(el_s) + '\t' + str(elem_s)
			if dico_pre_trie[el]=='x' or dico_pre_trie[el]=='w' or dico_pre_trie[el]=='u':
				 sortie= dico_pre_trie[el]
			break
	return sortie
			

filename_req = 	file_freq_exact =  path_req + requete + '_' +  'frequences_exactes.csv'
filename_req_year =  path_req +requete + '_' + str(freqmin)+'_' + str(min(years[0])) + '_' +str(max(years[-1]))+ '_' + '_' +  'frequences_exactes_totalyears.csv'

filename_pre_trie = path_req + 'concepts_pre_tries.csv' #fichier d'entree trie (rajouter _trie a la fin de la sortie standard)
filename_xhi2 = path_req + 'conceptsxhi2.csv'


try:
	print 'on importe le fichier de termes pretries original' + filename_pre_trie
	dico_pre_trie = lire_pretrie(filename_pre_trie,2)
except:
	print 'pas de fichier de concepts pre-tries ' +filename_pre_trie
	dico_pre_trie ={}

try:
	print 'on importe le fichier des scores de xhi2 ' + filename_xhi2
	dico_xhi2 = lire_pretrie(filename_xhi2,4)
except:
	print 'pas de fichier de scores de xhi2 ' +filename_xhi2
	dico_xhi2 ={}


#filename_bruit = "sorties/divers/divers_0_liste_n-grammes_freq.txt"
#
#########de facon tout a fait exceptionnelle:
#filename_bruit="sorties/RTGI/RTGI_5_liste_n-grammes_freq_divers.txt"
filename_bruit = 	file_freq_exact =  path_req + requete + '_' +  'frequences_exactes_bruit.csv'

print "on recupere la liste du fichier: "+ filename_req
try:
	ngrammes,maj_req = lire_nlemme_freq(filename_req)
except:
	ngrammes,maj_req = lire_nlemme_freq(filename_req_year)
print "on la compare a la liste du fichier: "+ filename_bruit
try:
	ngrammes_bruit,maj_bruit = lire_nlemme_freq(filename_bruit)
	compar = 1
except:
	compar = 0
	print 'pas de fichier de bruit de fond'

file_sortie = path_req + requete  + '_' + str(freqmin) + '_' + 'liste_n-grammes_freq_comparatif.csv'
file=codecs.open(file_sortie,"w",'utf-8')
file.write('n-lemme' + '\t' + 'forme principale' + '\t'+"tri"+ '\t'+"n" + '\t' + 'frequence d\'occurrence corpus (%) ' + requete  + '\t'+"frequence d\'occurrence bruit  (%)" +  '\t'+"ratio" +  '\t'+"tf.idf" + '\t'+ 'frequence d\'occurrence corpus_aut (%) ' + requete  + '\t'+"frequence d\'occurrence bruit_aut  (%)" +  '\t'+"ratio_aut" +  '\t'+"tf.idf_aut" +  '\t'+"score xhi2" +'\n')
for elem in ngrammes:
	#if elem in ngrammes_bruit:
	#else:
	#	freq_base = 0
	#pretrie = 	dico_pre_trie.get(elem,'')
	pretrie = find_sub(dico_pre_trie,elem)
	#print pretrie
	xhi2 = 	dico_xhi2.get(elem,'')
	if compar==1:
		freq_base = ngrammes_bruit.get(elem,(0,0))
		#print elem
		#print freq_base
		if not freq_base[0]==0:
		#file.write(elem.decode("utf-8","replace") + '\t' +maj_req[elem].decode("utf-8","replace") +  '\t'+pretrie +'\t' +str(maj_req[elem].count(' ')+1) +'\t'+str(ngrammes[elem][0]).replace('.',','))# + '\t'+str(freq_base[0]).replace('.',',')+ '\t'+str(float(ngrammes[elem][0])/float(freq_base[0])).replace('.',',') + '\t'+str(float(ngrammes[elem][0])*math.log10(float(ngrammes[elem][0])/float(freq_base[0]))).replace('.',',') +'\t'+str(ngrammes[elem][1]).replace('.',',') + '\t'+str(freq_base[1]).replace('.',','))
			file.write(elem.decode("utf-8","replace") + '\t' +maj_req[elem].decode("utf-8","replace") +  '\t'+pretrie +'\t' +str(maj_req[elem].count(' ')+1) +'\t'+str(ngrammes[elem][0]).replace('.',',') + '\t'+str(freq_base[0]).replace('.',',')+ '\t'+str(float(ngrammes[elem][0])/float(freq_base[0])).replace('.',',') + '\t'+str(float(ngrammes[elem][0])*math.log10(float(ngrammes[elem][0])/float(freq_base[0]))).replace('.',',') +'\t'+str(ngrammes[elem][1]).replace('.',',') + '\t'+str(freq_base[1]).replace('.',',')+ '\t'+str(float(ngrammes[elem][1])/float(freq_base[1])).replace('.',',') + '\t'+str(float(ngrammes[elem][1])*math.log10(float(ngrammes[elem][1])/float(freq_base[1]))).replace('.',',') + '\t' + xhi2+ '\n')
		else:
			print 'pas de ' + elem + '\n'
			file.write(elem.decode("utf-8","replace") + '\t' +maj_req[elem].decode("utf-8","replace") +  '\t'+pretrie +'\t' +str(maj_req[elem].count(' ')+1) +'\t'+str(ngrammes[elem][0]).replace('.',',') + '\t'+ '\t'+'\t'+'\t'+str(ngrammes[elem][1]).replace('.',',') + '\t'+ '\t'+ '\t'+ '\t' + xhi2+ '\n')
	if compar==0:
		try:
			file.write(elem.decode("utf-8","replace") + '\t' +maj_req[elem].decode("utf-8","replace") +  '\t'+pretrie +'\t' +str(maj_req[elem].count(' ')+1) +'\t'+str(ngrammes[elem][0]).replace('.',',') + '\t'+ '\t'+'\t'+'\t'+str(ngrammes[elem][1]).replace('.',',') + '\t'+ '\t'+ '\t'+ '\t' + xhi2+ '\n')
		except:
			#year
			file.write(elem.decode("utf-8","replace") + '\t' +maj_req[elem].decode("utf-8","replace") +  '\t'+pretrie +'\t' +str(maj_req[elem].count(' ')+1) +'\t'+ngramme[elem] + '\t'+ '\n')
			
print "fichier "+file_sortie+ 'produit'