#!/usr/bin/python
# -*- coding: utf-8 -*-
#recupere les liens des trois reseaux pour exporter les reseaux au format texte
import sys
sys.path.append("./libraries")

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
from datetime import timedelta
from datetime import date
###################################
#######0.quelques parametres#######
###################################

maxTermLength = parameters.maxTermLength
name_bdd = parameters.name_bdd
freqmin = parameters.freqmin
name_data = parameters.name_data 
requete = parameters.requete
#requete = "jean"
name_data_real = parameters.name_data_real
#lemmadictionnary = parameters.lemmadictionary# si nul, on  calcule ou recalcule  le dico de lemmes sur la requete consideree sinon on ne calcule pas
path_req = parameters.path_req
treetagger_dir =parameters.treetagger_dir

###################################
#######export #####################
###################################




#reseau social
contenu = fonctions_bdd.select_bdd_table(name_bdd,'soc','auteur1,auteur2,jours',requete)
file_net_name = path_req + "social_net.txt"
misc.extraire_reseaux(contenu,file_net_name)
print "=> reseau social exporte fichier: " + file_net_name

#reseau semantique
contenu = fonctions_bdd.select_bdd_table(name_bdd,'sem','concept1,concept2,jours,id_b',requete)
file_net_name = path_req + "sem_net" + '.txt' 
misc.extraire_reseaux(contenu,file_net_name)
print "=> reseau semantique exporte fichier: " + file_net_name

file_net_name = path_req + "sem_net" + "_pondere.txt"
misc.extraire_reseaux_pondere(contenu,file_net_name,name_bdd)
print "=> reseau semantique pondere exporte fichier: " + file_net_name

#reseau socio-semantique
contenu = fonctions_bdd.select_bdd_table(name_bdd,'socsem','auteur,concept,jours',requete)
file_net_name = path_req + "soc-sem_net.txt"
misc.extraire_reseaux(contenu,file_net_name)
print "=> reseau socio-semantique exporte fichier: " + file_net_name

#liste des concepts
contenu = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'concepts','id,concepts')
contenu2 = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'concepts','id,forme_principale')
file_concepts_name = path_req + "liste_concepts.txt"
file_concepts=open(file_concepts_name,'w')
file_concepts_name2 = path_req + "concepts_forme_principale.txt"
file_concepts2=open(file_concepts_name2,'w')
for con in contenu:
	file_concepts.write(str(con[0]) + '\t'  + str(con[1]) + '\n')
print "=> liste des concepts ecrite dans le fichier " +file_concepts_name	
for con in contenu2:
	file_concepts2.write(str(con[0]) + '\t'  + str(con[1]) + '\n')
print "=> liste des formes principales ecrite dans le fichier " +file_concepts_name	

#liste des auteurs
contenu = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'auteurs','id,auteurs')
file_auteurs_name = path_req + "auteurs.txt"
file_auteurs=open(file_auteurs_name,'w')
for con in contenu:
	file_auteurs.write(str(con[0]) + '\t'  + str(con[1]) + '\n')	
print "=> liste des auteurs ecrite dans le fichier " +file_auteurs_name

#evolution du nombre de billets
contenu= fonctions_bdd.count(name_bdd,'billets')
file_nb_billets_name=path_req + "nb_billets.txt"
file_nb_billets=open(file_nb_billets_name,'w')
for con in contenu:
	file_nb_billets.write(str(con[0]) + '\t'  + str(con[1]) + '\n')	
print "=> evolution du nombre de billets ecrit dans le fichier " +file_nb_billets_name
