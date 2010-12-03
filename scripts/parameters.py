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
	#annee_min=-int((datef-dated+1)/(fenetre))*(fenetre-overlap)
	total_window_pert = total_window[:]
	years_bins=[]
	year_bins=[]
	for i in range((datef-dated+1)/(fenetre)):
		window = total_window_pert[i*fenetre-overlap:(i+1)*fenetre]
		years_bins.append(window)
	for bins in years_bins:
		if len(bins)>0:
			year_bins.append(bins)
	#print year_bins
	return year_bins
	
print "--- initialisation de \"parameters.py\"..."

# 
# content_indexation='T'#Title
# # content_indexation='A'#  Abstract
# content_indexation='TA'#Title + Abstract 
# # content_indexation='TAKW'#Title + Abstract +Key Words
# #content_indexation='KW'#Key words
# #content_indexation='TA'#Title + Abstract 
# 
# 
# 
# 
# 
# 
# 
# 
# name_data,language,date_depart,freqmin,ng_filter,top,sample =  "../data/nature/nature-abstract.med",'english',date(1970,1,1),2,[1,1.5,2,2,2],5000,5000
# withrequete=0
# dated = 1970
# datef = 2009
# fenetre = 5
# overlap = 5
# years_bins = build_years_bins(fenetre,dated,datef,overlap)
# 
# 
# 
# name_data,language,date_depart,freqmin,ng_filter,top,sample =  "../data/export_MESR_20100722_light.lfl",'french',date(2010,1,1),2,[1,2,3,0,0],400,300
# maxTermLength=5
# #years_bins = [[1980], [2000], [2009]]
# datef = 500
# dated = 1
# fenetre = 500
# overlap = 0
# years_bins = build_years_bins(fenetre,dated,datef,overlap)
# 
# name_data,language,date_depart,freqmin,ng_filter,top,sample =  "../data/toxico/toxico.isi",'english',date(1970,1,1),10,[1,2,3,3,3],100,100
# dated = 1990
# datef = 2010
# fenetre = 4
# overlap = 5


################################################
################################################
################################################
################################################
################################################

argv = sys.argv
if len(argv)>1:#print argv
	parametres_file = '../parameters/' + sys.argv[1] + '.txt'
else:
	parametres_file='../parameters/job.txt'
print parametres_file


# parametres_file='../parameters/job.txt'
# parametres_file='../parameters/toxico.txt'
# parametres_file='../parameters/param.txt'
# 
# #parametres_file='../parameters/docilite.txt'
# parametres_file='../parameters/test.txt'
# parametres_file='../parameters/docti.txt'
# parametres_file='../parameters/MESR.txt'
# parametres_file='../parameters/MESR-light.txt'

################################################
################################################
################################################
################################################
################################################

print os.getcwd()
parametres = load_param(parametres_file)
print '\n'
print 'parametres: '+str(parametres)
print '\n'

#default parameters:
content_indexation='TA'
withrequete=0
lemmadictionary = 0
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
		t = t + str(int(val_param))
	exec(t)
	
years_bins = build_years_bins(fenetre,dated,datef,overlap)
################################################




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
if name_data[-4:] in ['.lfl','.rss'] :
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




try:
	if name_data[-4:] in ['.lfl','.rss']:
		jours = select_bdd_table_champ_simple(name_bdd,'billets','jours')
		dated = min(jours)
		#print 'dated'
		#print dated
		dated[0] =  7 * (int(dated[0]) / 7)  + 11 #c'est le jour du 1er janvier 2010 qui dicte cela
		#print datearr
		datef = max(jours)
		#print datef
		years_bins = build_years_bins(fenetre,int(dated[0]),int(datef[0]),overlap)
except:
	pass


#print "    - on traitera les donnees du fichier \""+ name_data_real+"\""
#print "    - parametres: " + "\n      - name_bdd: \"" +name_bdd  + "\"\n      - name_data: \""+name_data+  "\"\n      - name_data_real: \"" + name_data_real +"\"\n      - maxTermLength: "+ str(maxTermLength)  +"\n      - requete: \"" + requete + "\"\n      - freqmin: " + str(freqmin)#requete = "environnement"
#if lemmadictionary == 1:
#	print "      + sans calculer le dictionnaire des lemmes"
#else:
#	print "      + en calculant le dictionnaire des lemmes"




sep = ' *** '
char_int = ['>','<','(',')','[',']','*','}','{','#','>','<','=','&','|']
if nofigure==1:
	for i in range(10):
		char_int.append(str(i))
#print char_int

print "    - \"parameters.py\" initialise.\n"
#for name in dir():
	#print name 
	#exec("print "+name)