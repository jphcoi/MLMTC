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

###################################
#######0.quelques parametres#######
###################################

date_depart = parameters.date_depart
maxTermLength = parameters.maxTermLength
name_bdd = parameters.name_bdd
freqmin = parameters.freqmin
requete = parameters.requete
name_data = parameters.name_data 
name_data_real = parameters.name_data_real
lemmadictionary = parameters.lemmadictionary# si nul, on  calcule ou recalcule  le dico de lemmes sur la requete consideree sinon on ne calcule pas
path_req = parameters.path_req

print "--- initialisations terminees...\n"
print "+++ processing raw database \""+name_data+"\" into SQL database file \""+name_bdd+"\""


###################################
#######1.creation de la bdd########
###################################




#on fait un clean sur les sources en enlevant toutes les sources qui appartiennent à la liste interdite.


try:
	fonctions_bdd.detruire_table(name_bdd,'auteurs')
except:
	pass

#creation de la table auteurs
print "    + creation de la table auteurs..."
fonctions_bdd.creer_table_auteurs(name_bdd,'auteurs')

file = open(path_req+'sources_interdites.txt')
sites_interdits=[]
for lignes in file.readlines():
	sites_interdits.append(lignes.split('\t')[0][:-1])
print "    - on charge la liste des sources inerdites..."

print "    - remplissage de la table auteurs..."
sortie = fonctions_bdd.select_bdd_table(name_bdd,'billets','site',requete)
sites = set()
for sor in sortie:
	names =sor[0].split(" *%* ")
	for nom in names:
		site_name=text_processing.nettoyer_url(nom)
		if site_name not in sites_interdits:
			sites.add(site_name)
			
sites=list(sites)
fonctions_bdd.remplir_table(name_bdd,'auteurs',sites,"(auteurs)")

print "    - recuperation des ids des auteurs dans la table \"auteurs\" (index SQL) pour reinjecter dans la table \"billets\"..."
auteurs = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'auteurs','id,auteurs')
dic_auteurs ={}
for aut in auteurs:
	dic_auteurs[aut[1]] = aut[0]
site_billets = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'billets','id,site')

auteur_index=[]
for sit in site_billets:
	id_b= sit[0]
	names =sit[1].split(" *%* ")
	for nom in names:
		sit_name = text_processing.nettoyer_url(nom)
		if sit_name in dic_auteurs:
			id_aut = dic_auteurs[sit_name]
			auteur_index.append([id_b,id_aut])
		else:
			fonctions_bdd.delete_field(name_bdd,'billets',id_b)
			
		

print "    - mise a jour de la table billets avec les noms des sites nettoyes obtenus via la table auteurs..."
print "         (auteur_id = # du site dans la table auteurs)"
fonctions_bdd.update_table(name_bdd,'billets','auteur_id',auteur_index)


print "\n+++ base de donnees \""+name_bdd+"\" creee."




