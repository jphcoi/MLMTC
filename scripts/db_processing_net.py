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
###################################
#######3.Indexer les billets#######
###################################

#on crée la table concepts
#marche une fois sur deux, zarbo, peut-etre unique?...
try: 
	fonctions_bdd.detruire_table(name_bdd,'concepts')
	print "on detruit la table concept"
except: 
	print "pas de tabe  concept"

print "    + creation de la table \"concepts\" (qui fait office de dictionnaire)..."
fonctions_bdd.creer_table_concepts(name_bdd,'concepts')

# on indexe a partir de la liste des ngrammes tries

filename = path_req + requete + '_' + str(freqmin) + '_' + 'liste_n-grammes_freq_comparatif'  +'_trie' + '.csv' #fichier d'entree trie (rajouter _trie a la fin de la sortie standard)
#print filename
if os.path.isfile(filename) == 1:
	print '--- on indexe a partir du fichier \"' + filename+"\""
else:
	filename = path_req + 'concepts.csv' #fichier d'entree trie (rajouter _trie a la fin de la sortie standard)
	if not os.path.isfile(filename) == 1:
		filename_leven_redond =  path_req + requete + '_' + str(freqmin) + '_' + 'liste_n-grammes_freq_divers_leven_noredond.csv'
		filename = filename_leven_redond
		
		
print '--- on indexe a partir du fichier \"' + filename+"\""
#on lit le fichier des n-grammes a indexer
ngrammes = misc.lire_dico_classes(filename,language)
#pour plus de sûreté
ngrammes = misc.lire_dico_classes(filename,language)
#pour plus de sûreté
ngrammes = misc.lire_dico_classes(filename,language)


#affichage de la liste des 10 premiers concepts
print "--- les 10 premiers concepts (sur " +str(len(ngrammes))+") : "
for gra in ngrammes[:10]:
	try:
		print "    ",str([gra])
	except:
		print "encodage error"

if len(ngrammes)>1000:
	print "vous avez "+str(len(ngrammes)) + ' concepts, au-delà de 2000 concepts, le script peut devenir tres long'
	if user_interface =='y':
		var = raw_input('reduire la liste avant de lancer l\'indexation ? (y pour arreter, tout autre touche pour continuer)')
	else:
		var = 'n'
	if var=='y':
		exit()
###################################
#####indexation des billets########
###################################

def extension(x,y):
	x.extend(y)
	return list(set(x))
	
#il faut découper ici car ça prend trop de RAM
Nb_rows = fonctions_bdd.count_rows(name_bdd,'billets')
Nb_auteurs = fonctions_bdd.count_rows(name_bdd,'auteurs')
size_seq = 1000
nb_sequences = Nb_rows/size_seq
billets_id=[]
ngramme_billets_fit=[]
ngrammes_auteurs_fit={}
formes={}

#for x in range(nb_sequences+1):
for x in range(nb_sequences+1):
	lim_d = str(size_seq*x)
	if x<nb_sequences:
		duration = str(size_seq)
	else:
		duration = str(size_seq)
		#duration = str(Nb_rows - size_seq*x)
	#on extrait les champs contenus lemmatises et id de la table
	contenu = fonctions_bdd.select_bdd_table_limite(name_bdd,'billets','id,content_lemmatise,content,auteur_id',requete,lim_d+','+duration)
	#on indexe chaque billet et on recupere un triplet qui donne: la liste des ngrammes pour chaque billet, la liste des index des ngrammes pour chaque billet, et l'id des billets - ce script permet egalement de calculer les formes des n-lemmes.
	include=1 #le parametre include permet d'activer ou non l'overlap de lemmes dans le comptage: si 1, les nicolas sarkozy ne forment pas de sarkozy 
	ngramme_billets_fit_x,billets_id_x,formes_x,ngrammes_auteurs_fit_x = text_processing.indexer_billet(contenu,ngrammes,maxTermLength,include)
	billets_id = billets_id + billets_id_x
	ngramme_billets_fit = ngramme_billets_fit + ngramme_billets_fit_x
	formes=fonctions_lib.merge(formes, formes_x, lambda x,y: fonctions_lib.merge(x,y,lambda x,y:x+y))
	ngrammes_auteurs_fit=fonctions_lib.merge(ngrammes_auteurs_fit,ngrammes_auteurs_fit_x,lambda x,y : extension(x,y))
	print "    + billets numéros "+ str(int(lim_d)+1)+ " à "+  str(int(lim_d)+int(duration)) +" indexés (sur "+ str(Nb_rows) +")"
	
	
dictionnaire_treetagged__formes_name = path_req  + "Treetagger_n-lemmes_formes.txt"  
dictionnaire_treetagged__formemajoritaire_name = path_req  + "Treetagger_n-lemmes_formemajoritaire.txt"
text_processing.extraire_forme_majoritaire(0,formes,dictionnaire_treetagged__formes_name,dictionnaire_treetagged__formemajoritaire_name)

N  = float(len(ngramme_billets_fit))
print "    +" + str(N) + " billets indexés"


## on alimente la table concepts avec la liste des concepts trie et leur forme principale
file_concepts=codecs.open(dictionnaire_treetagged__formemajoritaire_name,'r','utf-8')
liste_concepts=[]
correspondance_lemme_forme={}
for ligne in file_concepts.readlines():
	lignev = ligne.split('\t')
	liste_concepts.append((lignev[0].encode('utf-8','replace'),lignev[1].encode('utf-8','replace')))
	correspondance_lemme_forme[lignev[0].encode('utf-8','replace')]=lignev[1].encode('utf-8','replace')
print "&&&",len(liste_concepts),"concepts now."
##si necessaire on recree la table concepts


#on remplit la table concept
#print liste_concepts
fonctions_bdd.remplir_table(name_bdd,'concepts',liste_concepts,"(concepts,forme_principale)")



contenu = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'concepts','id,concepts')
liste_concepts_dico={}
for con in contenu:
	liste_concepts_dico[con[1]]=con[0]



#on construit la liste des index des concepts dans l'ordre 
ngrammes_fit_index=[]

#on calcule nos stats à l'échelle des auteurs aussi, freq = nombre de blogs parlant d'un terme 
dictionnaire_frequence_exact_auteur={}
dictionnaire_frequence_exact={}
for terme in liste_concepts:
	dictionnaire_frequence_exact[terme[0]]=0
	dictionnaire_frequence_exact_auteur[terme[0]]=0
	
for clique in ngramme_billets_fit:
	clique_index=[]
	for terme in set(clique):
		clique_index.append(liste_concepts_dico[terme])
		dictionnaire_frequence_exact[terme]=dictionnaire_frequence_exact[terme]+1
	ngrammes_fit_index.append(clique_index)
print "    + liste des index des concepts creee"


for aut,clique in ngrammes_auteurs_fit.iteritems():
	for terme in set(clique):
		dictionnaire_frequence_exact_auteur[terme]=dictionnaire_frequence_exact_auteur[terme]+1
print "    + liste des index des concepts creee"

file_freq_exact =  path_req + requete + '_' +  'frequences_exactes.csv'
fichier_out =file(file_freq_exact,'w')
def format(value):
    return "%.9f" % value

for x in dictionnaire_frequence_exact:	
#	print str(x) + '\t' + str(correspondance_lemme_forme[x]) +'\t' + (str(format(float(dictionnaire_frequence_exact[x])/N))).replace('.',',') +'\t' + (str(format(float(dictionnaire_frequence_exact_auteur[x])/float(Nb_auteurs)))).replace('.',',')+  '\n'
	fichier_out.write(str(x) + '\t' + str(correspondance_lemme_forme[x]) +'\t' + (str(format(float(dictionnaire_frequence_exact[x])/N))).replace('.',',') +'\t' + (str(format(float(dictionnaire_frequence_exact_auteur[x])/float(Nb_auteurs)))).replace('.',',')+  '\n')
print "    + frequences exactes calculees   "+ file_freq_exact


#on alimente nos tables avec ces resultats
#on inscrit d'abord la liste des concepts indexes dans la table billet.
ngramme_billets_fit_txt =[]
for b_id,ngra in zip(billets_id,ngramme_billets_fit):
	ngratxt = ';'.join(ngra)
	ngramme_billets_fit_txt.append((b_id,ngratxt))
#et on remplit la table des billets avec la liste des concepts histoire d'en garder une trace
fonctions_bdd.update_table(name_bdd,'billets','concepts',ngramme_billets_fit_txt)




print "    - recuperation des ids des concepts dans la table \"concepts\" (index SQL) pour reinjecter dans la table \"billets\"..."
concepts = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'concepts','id,concepts')
dic_concepts ={}
for con in concepts:
	dic_concepts[con[1]] = con[0]
concepts_billets = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'billets','id,concepts')

concepts_index=[]
for cons in concepts_billets:
	id_b= cons[0]
	if len(cons[1])>0:
		names =cons[1].split(";")
		id_conc=[]
		for nom in names:
			conc_name = nom
			id_conc.append(dic_concepts[conc_name.replace("popostrophe","'")])
	else:
		id_conc=[]
	concepts_index.append([id_b,id_conc])

print "    - mise a jour de la table billets avec les index des cocncepts obtenus via la table concepts..."
print "         (concept_id = # du site dans la table auteurs)"
try:
	fonctions_bdd.add_column(name_bdd,'billets','concepts_id','VARCHAR(1500)')
except:
	pass
fonctions_bdd.update_table(name_bdd,'billets','concepts_id',concepts_index)



try:
	fonctions_bdd.drop_table(name_bdd,'concept2billets')
except:
	pass
fonctions_bdd.creer_table_concept2billets(name_bdd,'concept2billets')

con2bill = []
for couple in concepts_index:
	id_b = couple[0]
	for con in couple[1]:
		con2bill.append([con,id_b,requete,str(con)+'_'+str(id_b)])



fonctions_bdd.remplir_table(name_bdd,'concept2billets',con2bill,"(concept,id_b,requete,identifiant_unique)")






#on alimente ensuite la table socsem liant les index des acteurs aux index des concepts ainsi qu'au jour du lien



if build_link_tables=='y':

	print "    + creation des tables relationnelles socsem, sem, soc..."
	recreer_table_nets=1
	if recreer_table_nets ==1:
		try: fonctions_bdd.detruire_table(name_bdd,'socsem')
		except: pass
		try: fonctions_bdd.detruire_table(name_bdd,'sem')
		except: pass
		fonctions_bdd.creer_table_sociosem(name_bdd,'socsem')
		fonctions_bdd.creer_table_sem(name_bdd,'sem')
	

	# on construit les reseaux sociosemantique et semantique a partir de la liste des ngrammes associes a chaque index de billet

	def decoupe_segment(taille_total,taille_segment):
		decoupe = (taille_total/taille_segment)
		vec=[]
		for x in range(decoupe):
			vac = []
			for j in range(taille_segment):
				vac.append(j+x*taille_segment)
			vec.append(vac)
		vac= []
		for j in range(taille_total-decoupe*taille_segment):
			vac.append(j+decoupe*taille_segment)
		if len(vac)>0:
			vec.append(vac)
		return vec
	
	ll = len(billets_id)
	vecteurs=decoupe_segment(ll,1000)
	for x in vecteurs:
		print 'on traite les billets: ' + str(x[0])+ ' a ' + str(x[-1]) +' (sur ' + str(ll) +' billets)'
		lienssocsem,lienssem = misc.build_semantic_nets(billets_id[x[0]:x[-1]],ngrammes_fit_index[x[0]:x[-1]],name_bdd,requete,sep)
		##on remplit la table socsem
		fonctions_bdd.remplir_table(name_bdd,'socsem',lienssocsem,"(auteur,concept,jours,id_b,requete,identifiant_unique)")
		# ##on remplit la table sem
		fonctions_bdd.remplir_table(name_bdd,'sem',lienssem,"(concept1,concept2,jours,id_b,requete,identifiant_unique)")
	print "\n--- finished inserting data in tables socsem & sem."
	

###################################
####construction des liens#########
###################################

#on alimente enfin la table soc liant les index des acteurs entre eux ainsi qu'au jour du lien
try: 
	fonctions_bdd.detruire_table(name_bdd,'soc')
except: 
	pass
fonctions_bdd.creer_table_soc(name_bdd,'soc')
lienssoc = misc.build_social_net(requete,name_bdd,sep,name_data)
fonctions_bdd.remplir_table(name_bdd,'soc',lienssoc,"(auteur1,auteur2,jours,id_b,requete,identifiant_unique)")
print "\n--- finished inserting data in table soc."



