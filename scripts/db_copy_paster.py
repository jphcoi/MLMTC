#!/usr/bin/env python
# encoding: utf-8
"""
db_copy_paster.py
Created by Jean philippe cointet  on 2011-01-11.
"""
try:
	import feedparser
except:
	pass
from datetime import timedelta
from datetime import date
import sys,os
sys.path.append("libraries")

print "DB_copy_paster v1.0 (20100831)"
print "--------------------------------\n"

import parameters
import fonctions_bdd
import parseur
import text_processing
import shutil
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
user_interface=parameters.user_interface
print "--- initialisations terminees...\n"
print "+++ processing raw database \""+name_data+"\" into SQL database file \""+name_bdd+"\""

sep  = ' *** '
##############################################################
#######1.importation des billets d'une base extérieure########
##############################################################


#a modifier en fonction de l'endroit où on se trouve:
name_bdd_new = '.'.join(name_bdd.split('.')[:-2]) + '_new.' + '.'.join(name_bdd.split('.')[-2:])
print name_bdd
print name_bdd_new
champs_name = "(title,date,permalink,site,categorie1,categorie2,categorie3,content,href,requete,identifiant_unique)"#on n'enregistre pas le html brut
billet_new = fonctions_bdd.select_bdd_table_champ_simple(name_bdd_new,'billets',champs_name[1:-1])
champs=billet_new
fonctions_bdd.remplir_table(name_bdd,'billets',champs,champs_name)

###################################
#######2.calcul des infos annexes##
###################################



#creation de la table auteurs
try:
	fonctions_bdd.detruire_table(name_bdd,'auteurs')
except:
	pass
print "    + creation de la table auteurs..."
fonctions_bdd.creer_table_auteurs(name_bdd,'auteurs')

print "    - remplissage de la table auteurs..."
sortie = fonctions_bdd.select_bdd_table(name_bdd,'billets','site',requete)
sites = set()
for sor in sortie:
	names =sor[0].split(sep)
	for nom in names:
		sites.add(text_processing.nettoyer_url(nom))
sites=list(sites)
#print sites
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
	names =sit[1].split(sep)
	id_aut=[]
	for nom in names:
		sit_name = text_processing.nettoyer_url(nom)
		id_aut.append(dic_auteurs[sit_name.replace("popostrophe","'")])
	auteur_index.append([id_b,id_aut])

print "    - mise a jour de la table billets avec les noms des sites nettoyes obtenus via la table auteurs..."
print "         (auteur_id = # du site dans la table auteurs)"
fonctions_bdd.update_table(name_bdd,'billets','auteur_id',auteur_index)

#transforme la date en nombre de jours depuis date_depart	
fonctions_bdd.remplir_jours(name_bdd,'billets',requete,date_depart)
#commenter si format par annee

print "\n+++ base de donnees \""+name_bdd+"\" creee."




