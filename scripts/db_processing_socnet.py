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



