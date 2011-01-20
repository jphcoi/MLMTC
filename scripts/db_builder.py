#!/usr/bin/env python
# encoding: utf-8
"""
db_builder.py

Created by Jean philippe cointet  on 2010-08-11.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""
try:
	import feedparser
except:
	pass
from datetime import timedelta
from datetime import date
import sys,os
sys.path.append("libraries")

print "database_builder v1.0 (20100831)"
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
###################################
#######1.creation de la bdd########
###################################

#on detruit eventuellement la table correspondante


if user_interface =='y':
	var = raw_input('You may erase existing table billets, are you sure you want to proceed ? (type n if you want to stop, any other key to go on): ')
else:
	var='y'
if var=='n':
	exit()
else:
	if user_interface =='y':
		var2 = raw_input('do you want to add data to existing database or start a new project (type y to create a new database) any other key to add new content to existing database)')
	else:
		var2 = 'y'
	if var2 == 'y':
		print 'suppression de la base de données ' + name_data_real
		try:
			#fonctions_bdd.detruire_table(name_bdd,'billets')
			pkl_files= '/'.join(path_req.split('/')[:-3]) + '/pkl/'+requete
			shutil.rmtree(pkl_files)
			os.remove(name_bdd)	
		except:
			pass
		#on cree la table billet dans la bdd base.db
		print 'creation de la base de données ' + name_data_real
		fonctions_bdd.creer_table_billets(name_bdd,'billets')
		
	else:
		pass


#on parse d'abord le fichier de donnees de depart
champs = parseur.extraire_donnees(name_data,sep)
print champs
print len(champs)
print "    - liste de liste de champs \"champs\" mise a jour."
print "      - par exemple, champs[0] = ",champs[0]
#on remplit la bdd avec les infos extraites

champs_name = "(title,date,permalink,site,categorie1,categorie2,categorie3,content,href,requete,identifiant_unique)"#on n'enregistre pas le html brut
if  name_data[-4:] in [".lfl",'.rss','.doc']:#export au format .lfl: linkfluence type III ou IV
	fonctions_bdd.remplir_table_billets_lfl(name_bdd,'billets',champs,champs_name,requete)
else:
	#title, date,permalink,site,categorie1,categorie2,categorie3,content,requete,href,identifiant_unique
	fonctions_bdd.remplir_table_billets(name_bdd,'billets',champs,champs_name,requete)
###################################
#######2.calcul des infos annexes##
###################################
#fonction d'ajout d'une colonne.
#fonctions_bdd.add_column(name_bdd,name_table,"jours",'INTEGER')



#creation de la table auteurs
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




