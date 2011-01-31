#!/Library/Frameworks/Python.framework/Versions/2.6/bin/python
# -*- coding: utf-8 -*-
#script pour creer la liste des n-grammes avec leur frequence respectives

print "db_processing v0.2 (ccr) (20091102)"
print "-----------------------------------\n"

import parameters
import sys
import fonctions_bdd
import parseur
import os
import glob
import codecs
import unicodedata
import text_processing
import leven 
import misc 
from datetime import timedelta
from datetime import date
import treetaggerwrapper
import fonctions_lib
import math
import fusion_years
import multiprocessing

print "--- initialisations terminees...\n"
###################################
#######0.quelques parametres#######
##################################

maxTermLength = parameters.maxTermLength
name_bdd = parameters.name_bdd
freqmin = parameters.freqmin
name_data = parameters.name_data 
requete = parameters.requete
#requete = "jean"
name_data_real = parameters.name_data_real
lemmadictionary = parameters.lemmadictionary# si nul, on  calcule ou recalcule  le dico de lemmes sur la requete consideree sinon on ne calcule pas
treetagger_dir =parameters.treetagger_dir
path_req = parameters.path_req
language = parameters.language
ng_filter=parameters.ng_filter
top=parameters.top
sample=parameters.sample
user_interface=parameters.user_interface
###################################
#######1.fonctions utiles##########
###################################

#fonction d'affichage, champ par champ
#champs_name = ["title","date","permalink","site","categorie1","categorie2","categorie3","content_html","content","href","requete","identifiant_unique"]
#for cha in champs_name[6:8]: 
#	fonctions_bdd.afficher_bdd_table(name_bdd,name_table,cha,requete)


###################################
#######2.Analyse contenu###########
###################################

lemmatisation=1#on active/desactive la phase de lemmatisation des billets brutes
#!!!!!!!!utiliser lemmadictionary=1 si dictionnaire des lemmes deja calculé pour eviter de refaire une passe inutile
lemmadictionary=0
Nb_rows = fonctions_bdd.count_rows(name_bdd,'billets')

name_export_pkl=requete + '_dico_'+str(sample)+'_'+str(Nb_rows) + '_year'
name_export_lemme_pkl = requete + '_lemme_'+str(sample)+'_'+str(Nb_rows) 

#on recupere d'abord toutes les années en base
years=parameters.years_bins_no_overlap






def do_calculation(year):
		print str(year) + ' being processed '
		#il faut découper ici car ça prend trop de RAM
		if sample<Nb_rows:
			size_seq = sample
			nb_sequences=0
		else:
			size_seq = 10000
			nb_sequences = Nb_rows/size_seq
		dictionnaire_gramme = {}#initialisation du dictionnaire de lemmes
		billetprocessed_after_requete=0 #counts the number of processed posts
		for x in range(nb_sequences+1):
			dictionnaire_gramme_x={}
		#	billetprocessed_after_requete=1+billetprocessed_after_requete
			lim_d = str(size_seq*x)
			if x<nb_sequences:
				duration = str(size_seq)
			else:
				duration = str(min(Nb_rows - size_seq*x,sample))
			where = " jours IN ('" + "','".join(list(map(str,year))) + "') "
			where=''
			for ii,ystr in enumerate(list(map(str,year))):
				if ii>0:
					where = where + ' or '
				where = where + ' jours = ' +"'"+ ystr+"'"
			#print where
			contenu = fonctions_bdd.select_bdd_table_where_limite(name_bdd,'billets','content_lemmatise',sample,requete,where,lim_d+','+duration,Nb_rows)
			Nb_rows=len(contenu)
			for billetlemm in contenu:
				billetprocessed_after_requete=1+billetprocessed_after_requete
				if not billetprocessed_after_requete%500 or billetprocessed_after_requete == Nb_rows : 
					print '---------'+str(billetprocessed_after_requete)+ ' traités (export ngrammes sur '+str(Nb_rows)+ ' billets)'
				billet_lemmatise =  billetlemm[0]
				dictionnaire_gramme_x = text_processing.ngramme_build(billet_lemmatise.split(),maxTermLength,dictionnaire_gramme_x,language,'absolu')
			dictionnaire_gramme=fonctions_lib.merge(dictionnaire_gramme, dictionnaire_gramme_x, lambda x,y:x+y)
		return dictionnaire_gramme
			
			
			
			

try:
	print requete + '_' + str(freqmin) + str(sample)
	if user_interface =='y':
		var = raw_input('do you wish to force new indexation ? (y to reindex)')
	else:
		var='n'	
	if var =='y':
		dictionnaire_gramme=fonctions_lib.dumpingout(name_export_pkl+'jlkjjlkjlkjlkjlkjl',requete)
	print '\n\nOn importe le dictionnaire de n-grammes deja calcule\n\n'
	dictionnaire_gramme_year=fonctions_lib.dumpingout(name_export_pkl,requete)
	lemme_maj=fonctions_lib.dumpingout(name_export_lemme_pkl,requete)
		
except:
	if lemmatisation ==1:	
		#	on extrait le champ contenu de la table
		print "--- extraction des contenus des billets..."
		contenu = fonctions_bdd.select_bdd_table(name_bdd,'billets','id,content,content_lemmatise',requete)
		print "    - par exemple, contenu[0][1]=",contenu[0][1]
		print "+++ lemmatisation avec treetagger de tous les contenus..."
		#on construit la liste des n-grammes accompagnée de leur fréquence
		tagger = treetaggerwrapper.TreeTagger(TAGLANG=language,TAGDIR=treetagger_dir)
		billetprocessed=0
		billetnotprocessed=0
		billetcleans=[]
		billetorigs=[]
		for billets in contenu:			
			billetprocessed+=1
			billet_id = billets[0]
			billet = billets[1]
			billet = billet.replace('<b>','').replace('</b>','')
			billet_lem = billets[2]	
			if not billetprocessed%250 : 
				print "     [#"+str(billetprocessed) +"]"
			if str(billet_lem)=="None":
				
				billetclean,billetorig = text_processing.billets_cleaner(billet,tagger)# transforme le billet en une liste de termes lemmatises apres avoir detache les elements de ponctuation
				billetcleantxt = ' '.join(billetclean)
				billetorigtxt = ' '.join(billetorig)
				billetcleantxt = billetcleantxt.encode('utf-8','replace')
				billetorigtxt = billetorigtxt.encode('utf-8','replace')
				billetcleans.append((billet_id,billetcleantxt))
				billetorigs.append((billet_id,billetorigtxt))
			else:
				billetnotprocessed=billetnotprocessed+1			
			if not billetprocessed%2000 or  billetprocessed == len(contenu) : 
				print "\n--- finished processing post terms: " + str(billetprocessed) +" posts"
				fonctions_bdd.update_table(name_bdd,'billets',"content_lemmatise",billetcleans)
				fonctions_bdd.update_table(name_bdd,'billets',"content",billetorigs)
				billetcleans=[]
				billetorigs=[]
		if billetnotprocessed>0:
			print "\n--- " + str(billetprocessed) +" posts had been already processed"

	#on construit le dictionnaire de lemmes si inexistant (pas besoin de redonner le nom du dictionnaire si celui-ci a deja ete cree)
	dictionnaire_treetagged_name= path_req  + "Treetagger_lemmes.txt"  
	if lemmadictionary==0: 
		print "+++ creation du dictionnaire de lemmes \""+dictionnaire_treetagged_name+"\""
	else: 
		print "*** dictionnaire de lemmes non recree pour eviter une passe inutile"
	if lemmadictionary==0:
		contenu = fonctions_bdd.select_bdd_table(name_bdd,'billets','content,content_lemmatise',requete)
	else:
		contenu = ''
	occ_termes_lemmes=text_processing.lemmatisation(lemmadictionary,dictionnaire_treetagged_name,contenu,treetagger_dir)#cette fonction renvoie le dictionnaire termes/lemmes mais aussi un dictionnaire du nombre d'occurrences des couples (terme,lemme): occ
	#print occ_termes_lemmes
	dictionnaire_treetagged__formes_name = path_req  + "Treetagger_lemmes_formes.txt"  
	dictionnaire_treetagged__formemajoritaire_name = path_req  + "Treetagger_lemmes_formemajoritaire.txt"  
	print "+++ creation des fichiers de lemmes:\n       1. \""+dictionnaire_treetagged__formes_name+"\" (toutes les formes des lemmes)\n       2. \""+dictionnaire_treetagged__formemajoritaire_name+"\" (formes majoritaires)"
	lemme_maj = text_processing.extraire_forme_majoritaire(lemmadictionary,occ_termes_lemmes,dictionnaire_treetagged__formes_name,dictionnaire_treetagged__formemajoritaire_name)
	fonctions_lib.dumpingin(lemme_maj,name_export_lemme_pkl,requete)


	#where=0, on applique la requete resserree, where =1 on  ne l'applique pas. 
	where=1

	if where==0:
		filename = "requete_OR.csv"
		filename_req = path_req + filename
		print "+++ on essaie d'importer la requete depuis le fichier "+filename_req
		try:
			where = fonctions_bdd.filtre_requete_base(filename_req)
		except:
			where=1
	
	#decoupage annuel:
	#on recupere d'abord toutes les années en base
	dictionnaire_gramme_year={}
	pool_size = int(multiprocessing.cpu_count() * 2)
	pool = multiprocessing.Pool(processes=pool_size)
	pool_outputs = pool.map(do_calculation, years)
	for y,x in enumerate(pool_outputs):		
		dictionnaire_gramme_year[y]=x
	fonctions_lib.dumpingin(dictionnaire_gramme_year,name_export_pkl,requete)


#decoupage par periode:
print dictionnaire_gramme_year.keys()
#puis on itere annee par annee
try: 
	os.mkdir(path_req +'years/')
except:
	pass
for y,year in enumerate(years):
	#on trie par fréquence et on exporte le lexique final avec les occurrences 
	print '\n'
	print year
	
	dico_final = misc.freq_tri(dictionnaire_gramme_year[y],freqmin,int(math.floor(top*1.1)),language,ng_filter)#on effectue le tri de notre dictionnaire
	filename = path_req +'years/'+ requete + '_' + str(freqmin) + '_' +str(year) + '_'+ 'liste_n-grammes_freq_divers.csv'
	filename_redond =  path_req +'years/'+ requete + '_' + str(freqmin) +str(year) + '_'+ 'liste_n-grammes_freq_divers_noredond.csv'
	filename_redond_leven =  path_req +'years/'+ requete + '_' + str(freqmin)+str(year) + '_' 'liste_n-grammes_freq_divers_leven_noredond.csv'
	misc.ecrire_liste_lemmes_freq(dico_final,Nb_rows,filename,lemme_maj,freqmin,ng_filter)#on ecrit la liste precedente dans un fichier filename
	print "\n+++"+str(len(dico_final))+" n-lemmes crees."
	#leven.pack_rendondance(filename,filename_redond,maxTermLength,freqmin,language,redondance_manuelle,ng_filter,user_interface)
	leven.pack_rendondance_exact(filename,filename_redond,maxTermLength,freqmin,language,ng_filter,user_interface)
	print "\n"
	Nb_rows = fonctions_bdd.count_rows_where(name_bdd,'billets'," where jours IN ('" + "','".join(list(map(str,year))) + "') ")
	print Nb_rows
	leven.pack_leven(filename_redond,filename_redond_leven,language,user_interface,freqmin,Nb_rows)

fusion_years.fusion('redond')