#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import timedelta
from datetime import date
import sys
import codecs
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


filename_req = path_req + "requete_OR.csv"
file = codecs.open(filename_req,'r','utf-8')
	
terme1 = u'santé'
terme2 =u'environnement'

connection, ex = fonctions_bdd.connexion(name_bdd)
commandesql = "SELECT id from billets WHERE (content LIKE '% "+ terme1.encode('utf-8') + " %' AND content LIKE '% "+ terme2.encode('utf-8') + "%') " 
for line in file.readlines():
	line = line.encode('utf-8')[:-1]
	machin = line.replace("\'","popostrophe")
	commandesql = commandesql  + ' OR ' + "content LIKE  '% " + machin +" %' "
print commandesql
	 
sortie = ex(commandesql).fetchall()
billet_id_ok=[]
for sor in sortie:
	billet_id_ok.append(int(sor[0]))
print billet_id_ok
connection.commit()
connection.close()

connection, ex = fonctions_bdd.connexion(name_bdd)
commandesql = "SELECT id from billets" 
sortie = ex(commandesql).fetchall()
for sor in sortie:
	if int(sor[0]) not in billet_id_ok:
		print int(sor[0])


