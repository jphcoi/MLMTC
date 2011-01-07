# -*- coding: utf-8 -*-
import os
from datetime import date
import sys,os
sys.path.append("./libraries")
import fonctions_lib
import sqlite3
server = "root@veilledynamique.com"

def vectoriser(chaine):
	chaine = chaine[1:-1]
	return map(int,chaine.split(','))
	
def load_param(fichier_name):
	fichier= open(fichier_name,'r')
	parametres = {}
	lines  = fichier.readlines()
	idx = 0
	for ligne in lines:
		idx = idx+1
		if len(ligne)>2:
			if idx<len(lines):
				ligne=ligne[:-1]
			lignev=ligne.split('=')
			nom_param = lignev[0].replace(' ','')
			val_param = lignev[1].replace(' ','')
			parametres[nom_param] = val_param
	return parametres
	
def connexion(name_bdd):
	connection = sqlite3.connect(name_bdd)
	cursor = connection.cursor()
	ex = connection.execute
	return connection,ex


def select_bdd_table_champ_simple(name_bdd,table,champ):
	connection,ex = connexion(name_bdd)
	sortie= ex("SELECT "  + champ +  "   from " +table ).fetchall()
	sortie_ok = []
	for sor in sortie:
		soso_v=[]
		for so in sor:
			if not type(so) == int:
				try:
					soso = so.encode('utf-8','replace')
					soso = soso.replace("popostrophe","'")
				except:
					soso=str(so)
			else:
				soso = so
			soso_v.append(soso)
		sortie_ok.append(soso_v)
	connection.commit()
	connection.close()	
	return sortie_ok
	
	
def build_total_window(dated,datef):
	total_window=[]
	for i in range(datef-dated+1):
		total_window.append(dated+i)
	return total_window

def build_years_bins(fenetre,dated,datef,overlap):
	total_window=build_total_window(dated,datef)
	total_window_pert = total_window[:]
	years_bins=[]
	year_bins=[]
	for i in range((datef-dated+1)/(fenetre)):
		window = total_window_pert[i*fenetre:(i+1)*fenetre+overlap]
		if (i+1)*fenetre+overlap<len(total_window_pert)+1:
			years_bins.append(window)
	for bins in years_bins:
		if len(bins)>0:
			year_bins.append(bins)
	years_bins_bis = []
	for intervalles in years_bins:
		interbis=[]
		for x in intervalles:
			interbis.append(x+datef-years_bins[-1][-1])
		years_bins_bis.append(interbis)
	return years_bins_bis
	
print "--- paremeters initialisation ..."

# 
# content_indexation='T'#Title
# # content_indexation='A'#  Abstract
# content_indexation='TA'#Title + Abstract 
# # content_indexation='TAKW'#Title + Abstract +Key Words
# #content_indexation='KW'#Key words
# #content_indexation='TA'#Title + Abstract 

argv = sys.argv
if len(argv)>1:#print argv
	parametres_file = '../parameters/' + sys.argv[1] + '.txt'
else:
	parametres_file='../parameters/toxico.txt'
print 'parameters files loaded from: ' + parametres_file

#default parameters:
sep = ' *** '
char_int = ['>','<','(',')','[',']','*','}','{','#','>','<','=','&','|']
continent=''

try:
	content_indexation=parameters.content_indexation
except:
	content_indexation='TA'
	
withrequete=0
lemmadictionary = 0




parametres = load_param(parametres_file)



print '\n'
print 'parametres: '+str(parametres)
print '\n'

for nom_param,val_param in parametres.iteritems():
	#print nom_param,val_param
	t=str(nom_param)+'='	
	if '[' in val_param and ']' in val_param:
		t = t + str(vectoriser(val_param))
	elif 'date' in val_param:
		date_str = val_param.replace('date(','').replace(')','')
		date_str_v = date_str.split(',')
		date_int = (int(date_str_v[0]),int(date_str_v[1]),int(date_str_v[2]))
		t = t + 'date' +str(date_int)
	elif '"' in val_param   or  "'" in val_param:
		t = t + '"' +str(val_param[1:-1])+ '"'
	else:
		if '.' in val_param:
			t = t + str(float(val_param))
		else:
			t = t + str(int(val_param))
	exec(t)
	



if name_data[-4:] in ['.lfl','.med'] and withrequete == 1:
	try:
		Kws = fonctions_lib.lire_fichier(name_data+'.txt')
		#print  "    - on filtrera avec les mots cles de la requete (N= \""+ str(len(Kws))+"\")"
	except:
		pass
else:
	Kws = []

#	print  "    - on ne filtre pas "
#Kws = [u'santé',u'environnement']
#Kws = ['et']
#Kws=[]


treetagger_dir_jp='/Users/louiseduloquin/Desktop/treetagger/'
treetagger_dir_cam='/Users/camille/src/NLP/'
treetagger_dir_david='F:\Treetagger\TreeTagger'
treetagger_dir_andrei='C:/Users/andrei/Documents/Projects/Ifris/TreeTagger'

if "duloquin" in os.getcwd():
	treetagger_dir = treetagger_dir_jp
	CFinder_CL = "./CFinder_commandline_mac"
if "andrei" in os.getcwd():
	treetagger_dir = treetagger_dir_andrei
	CFinder_CL = "CFinder_commandline.exe"
if "camille" in os.getcwd():
	treetagger_dir = treetagger_dir_cam
	CFinder_CL = "./CFinder_commandline_mac"
if "F:" in os.getcwd():
	treetagger_dir = treetagger_dir_david
	CFinder_CL = "./CFinder_commandline.exe"
if "iscpif" in os.getcwd():
	treetagger_dir = "/iscpif/users/cointet/Bureau/treetagger"
	CFinder_CL = "./CFinder_commandline"
if "home/web/prod" in os.getcwd():
	treetagger_dir = "/iscpif/users/cointet/Bureau/treetagger"
	CFinder_CL = "./CFinder_commandline"
#print "    - path de TreeTagger: " + treetagger_dir



name_data_v = name_data.split('/')
requete = name_data_v[-2]
if name_data[-4:] in ['.lfl','.rss','.isy'] :
	requete = name_data_v[-1]
	if len(Kws)>0:
		requete = requete + continent + str(len(Kws))
	else:
		requete = requete + continent
name_data_real = (name_data_v[-1]).split('.')[0]
path_req = "../../inout/sorties2/" + requete + '/'
if not os.path.isdir(path_req):
	os.makedirs(path_req)
name_bdd = path_req + requete+ '.db'



#decoupage hebdomadaire
try:
	if name_data[-4:] in ['.lfl','.rss']:
		jours = select_bdd_table_champ_simple(name_bdd,'billets','jours')
		dated = min(jours)
		prop =  7 * (int(dated[0]) / 7)  + 4 #c'est le jour du 1er janvier 2010 qui dicte cela
		if prop>=dated[0]:
			dated[0] = prop
		else:
			dated[0]= prop + 7
		datef = max(jours)
		prop =  7 * (int(datef[0]) / 7)  + 3 #c'est le jour du 1er janvier 2010 qui dicte cela
		if prop<=datef[0]:
			datef[0] = prop
		else:
			datef[0]= prop - 7

		#print datef
		#years_bins = build_years_bins(fenetre,int(dated[0]),int(datef[0]),overlap)
		dated = int(dated[0])
		datef = int(datef[0])
except:
	pass



try:
	years_bins = build_years_bins(fenetre,dated,datef,overlap)
	years_bins_no_overlap = build_years_bins(fenetre,years_bins[0][0],years_bins[-1][-1],0)
	print years_bins
except:
	print 'years_bins non calculables pour le moment'
	
if requete=='biocomplex':#rajouter  periodes 1956-1979 et 1980-1989
	years_bins = [range(1957,1980),range(1975,1985),range(1981,1987)]+years_bins
	
#print years_bins_no_overlap

if nofigure==1:
	for i in range(10):
		char_int.append(str(i))
if nofigure==1:
	for i in range(10):
		char_int.append(str(i))

try:
	print seuil_cooccurrences
except:
	seuil_cooccurrences=2
try:
	print user_interface
except:
	user_interface='n'

print "    - \"parameters.py\" initialise.\n"

