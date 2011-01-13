# -*- coding: utf-8 -*-
#!/usr/bin/python

###############################
###############################
#tri des dictionnaires#########
###############################
###############################
from text_processing import *
import fonctions_bdd
import text_processing
import parameters
import leven
from operator import itemgetter
char_int=parameters.char_int

def interdit_char(word):
	for x in char_int:
		if x in word:
			return False
	return True

def isList(obj):
   """isList(obj) -> Returns true if obj is a Python list.

      This function does not return true if the object supplied
      is a UserList object.
   """
   return type(obj)==types.ListType


def sortedDictValues1(adict):
    items = adict.items()
    items.sort()
    return [value for key, value in items]


def sortfunc(x,y):
	return cmp(x[1],y[1])
	

def lire_dico(dico_index_file):
	concepts = []
	fileo = codecs.open(dico_index_file,'r','utf-8')
	lignes=fileo.readlines()
	for ligne in lignes:
		#print ligne
		if '\t' in ligne:
			lignev  = ligne.split('\t')
			concept = lignev[0]
		else:
			concept = ligne[:-1]
			concept=concept.replace('\r','')
		if not concept in concepts:
			concepts.append(concept)
	return concepts


def lire_dico_classes(dico_index_file,language):
	coldecol=[]
	#on contrôle qu'il n'y a pas de differences entre les equivalences du fichier à indexer et le fichier d'equivalence de la langue courante
	#lancer deux fois potentiellement.
	fichier_name = 'libraries/leven-classes_'+language+'o.txt'
	equivalences_leven,x,y = leven.lire_fichier_classe(fichier_name)
	equivalences_leven_file =open(fichier_name,'a')
	concepts = []
	nngrammes=[]
	fileo = codecs.open(dico_index_file,'r','utf-8')
	print dico_index_file
	lignes=fileo.readlines()
	for ligne in lignes:
		if '\t' in ligne:
			lignev  = ligne.split('\t')
			concept = lignev[0]
		else:
			concept = ligne[:-1]
			concept=concept.replace('\r','')
		concept_cl=concept.encode('utf-8','replace')
		concept_cl_v=concept_cl.split('***')
		concept_cl_0=concept_cl_v[0]
		classe_0=equivalences_leven.get(concept_cl_0,'ailleyapaslemot')
		#si une nouvelle correspondance est proposée on complète le fichier de correspondance.
		if len(concept_cl_v)>1:
			for concept in concept_cl_v[1:]:
				if not concept in classe_0: 	
					equivalences_leven_file.write(concept_cl_0 + '\t' + concept +'\n')
					print concept_cl_0 + '\t' + concept +'\n'
					print "<- on rajoute le terme " + concept + " dans la classe de " + concept_cl_0 + ' dans le fichier de correspondance'
		for concept in concept_cl_v:
			try:
				equivalences_leven_c = equivalences_leven[concept]
				for c in equivalences_leven_c:
					if not c in concept_cl_v:
						concept_cl_v.append(c)	
						print "-> on rajoute le terme " + c + " dans la classe de " + concept					
			except:
				pass				
		concept_corr = '***'.join(concept_cl_v)
		if not concept_corr in concepts:
			ens_set=set(concept_corr)
			if not ens_set in coldecol:
				coldecol.append(ens_set)
				concepts.append(concept_corr)
	#print concepts
	equivalences_leven_file.close()
	fileo.close()
	return concepts


def add_n(dico):
	ngrammes_dict={}
	for ngr in dico:
		n=ngr.count(' ')+1
		ngrammes_dict[ngr]=(n,dico[ngr])
	items = ngrammes_dict.items()
	items = [(v, k) for (k, v) in items]
	items.sort() 
	#items.reverse()		
	items = [(k, v) for (v, k) in items]
	return items
	
def redondance_cleaner(dico):
	items = add_n(dico)
	ii=-1	
	for element in items:
	#	print element
		ii +=1
		nb_occ=element[1][1]
		n=element[1][0]
		nlemme = element[0]
		if n>1 and nb_occ>0:
			jj = -1
			for elem in items[:ii]:
				jj+=1
				if elem[1][0] == n-1:#a debattre
					if elem[0] in nlemme:
						#print elem[0]
						#nlemmev = nlemme.split(' ')
						#if elem[0] in nlemmev:
							d_uple = items[jj][1]
							d_uple = (d_uple[0],d_uple[1]-nb_occ)
							items[jj] = (items[jj][0],d_uple)
						#	print 'on modifie '+ str(items[jj])
	dico_final ={}
	for elem in items:
		dico_final[elem[0]] = elem[1][1]
	return dico_final

		


def freq_tri(dictionnaire_gramme,freqmin,top,language,ng_filter):
	print "-------- tri du dictionnaire"
	dico_final={}
	dico_final_norm={}
	di_gr = dictionnaire_gramme.keys()
	n=len(di_gr)
	nb_gr=0
	for gramme in di_gr:
		nb_gr=nb_gr+1
		if not nb_gr%10000 or nb_gr==n:
			print '+ '+str(nb_gr) +" ngrammes triés sur " +str(n) + " au total" 
		
		if  interdit_char(gramme) ==  True:
			n_gramme = len(gramme.split())
			if n_gramme>0:
				if float(ng_filter[n_gramme-1])>0:
					if  dictionnaire_gramme[gramme] > float(freqmin)/float(ng_filter[n_gramme-1]):#**(1/(float(n_gramme))): # Modules en fonction de la taille du terme
						dico_final[gramme] = dictionnaire_gramme[gramme]
						dico_final_norm[gramme] = dictionnaire_gramme[gramme]*float(ng_filter[n_gramme-1])
	l = dico_final_norm.items()
	l.sort(key=itemgetter(1),reverse=True)
	dico_final_top={}
	for x in l[:top]:
		dico_final_top[x[0]]=dico_final[x[0]]
	print "--- created reduced n-gram list"
	return dico_final_top

def transforme_forme_majoritaire(n_lemme,lemme_maj):
	n_lemmev=n_lemme.split(' ')
	forme_majoritaire=[]
	for partie in n_lemmev:
		partie = partie.decode('utf-8','replace')
		if partie in lemme_maj:
			forme_majoritaire.append((lemme_maj[partie]).encode('utf-8','replace'))
		else:
			forme_majoritaire.append(partie)#.encode('utf-8','replace'))
	return forme_majoritaire



	
def ecrire_liste_lemmes_freq(dico,billetprocessed,filename,lemme_maj,freqmin,ng_filter):
	sortie = codecs.open(filename,'w')
	ligne= 'ngramme lemmatise' + '\t'+'forme principale'+'\t'+'selection (x ok, w out)'+'\t'+ 'nombre d\'occurrences'+'\t'+'nombre d\'occ normalise'+'\t'+'frequence'+'\n'
	sortie.write(ligne)
	
	for dic in dico:
		occ=str(dico[dic])
		if int(occ)>0:
			forme_majoritaire = transforme_forme_majoritaire(dic,lemme_maj)
			forme_maj=''
			try:
				forme_maj = ' '.join(forme_majoritaire)
			except:
				forme_maj = str(forme_majoritaire)
			freq = float(dico[dic])/float(billetprocessed)
			n_gramme = len(dic.split())
			occ_norm = str(int(occ)*(ng_filter[n_gramme-1]))
			try:
				ligne= dic + '\t'+str(forme_maj)+'\t'+'\t'+ occ+'\t'+str(occ_norm).replace('.',',')+'\t'+(str(freq).replace('.',','))+'\n'
				sortie.write(ligne)
			except:
				print 'ratage encodage'
	print "\n--- fichier comportant la liste des n-grammes lemmatises et leur frequence cree: \n     \"" +filename+"\""
		

def add_cooc(cooc,clique,date_b):
	j=-1
	for concept1 in clique:
		j += 1
		for concept2 in clique[j:]:
			if cooc.has_key((concept1,concept2,date_b)):
				cooc[(concept1,concept2,date_b)] = cooc[(concept1,concept2,date_b)]+1
			else:
				cooc[(concept1,concept2,date_b)] = 1
	return cooc
	
	
def ecrire_liste(dico_idx,dico_index_file):
	"une liste et un nom de fichier en entree, ecrit simplement la liste dans un fichier"
	filel = open(dico_index_file,'w')
	for ligne in dico_idx:
		filel.write(ligne+'\n')
		
def calcul_cooc(billets_clean,date_billet,dic_index,dico_index_file,dico_final):
	cooc={}
	if dic_index == 1:
		dico_idx = lire_dico(dico_index_file)
	else:
		dico_idx = dico_final.keys()
	ecrire_liste(dico_idx,dico_index_file)
	
	billetprocessed=0
	for billet, date_b in zip(billets_clean,date_billet):
		billetprocessed+=1
		if not billetprocessed%250 : 
			print "     [#"+str(billetprocessed) +"]"
		j = 0
		clique=set([])
		for concept in dico_idx:
			j += 1
			for termes in billet:
				if termes==concept:
					clique.add(j)
		cooc = add_cooc(cooc,list(clique),date_b)
	return cooc

def	ecrire_cooc(cooc,bdd_filename_real,dico_index_file):
	name = dico_index_file+'_' +bdd_filename_real +'.txt'
	print name
	filel = open( name,'w')
	for co in cooc:
		print co
		print "valeur"
		
		print cooc[co]
		filel.write(str(co[0])+"\t"+str(co[1])+"\t"+str(co[2])+"\t"+str(cooc[co])+"\n")
	print "cooccurrences file " + name + " written"
	


def searchforconcept(billets_clean,date_billet,auteur_billet,author_liste,maxTermLength,liste_concepts):
	author_profil={}

	for con,dat,aut in zip(billets_clean,date_billet,auteur_billet):
		if aut in author_liste:
			autid = author_liste.index(aut)+1
			dictionnaire_gramme={}
			dictionnaire_gramme = ngramme_build(con,maxTermLength,dictionnaire_gramme)
			#print dictionnaire_gramme
			for element in dictionnaire_gramme:
				j = 0
				for concept in liste_concepts:
					j +=1 
					if element==concept:

						if author_profil.has_key((autid,j,dat)):
							author_profil[(autid,j,dat)] = author_profil[(autid,j,dat)]+1
						else:
							author_profil[(autid,j,dat)] = 1
	return author_profil


def searchforlinks(contenu,date_billet,auteur_billet,author_liste):
	social_net={}
	for con,dat,aut in zip(contenu,date_billet,auteur_billet):
		#print dat
		#print aut
		if aut in author_liste:
			autid = author_liste.index(aut)+1
			#print "autid " + str(autid)
			for bout in con.split(' '):
				
				if "http" == bout[:4]:
					print bout
					j = 0
					for acteur in author_liste:
						j += 1
						if acteur in bout:
							print  "mapping " + acteur + '\t' + bout
							if social_net.has_key((autid,j,dat)):
								social_net[(autid,j,dat)] = social_net[(autid,j,dat)]+1
							else:
								social_net[(autid,j,dat)] = 1
	return social_net	


def build_semantic_nets(billets_id,ngramme_billets_fit,name_bdd,requete,sep):
	"construit les reseaux sociosemantique et semantique a partir de la liste des ngrammes associes a chaque index de billet"
	lienssocsem = []
	lienssem = []
	for b_id,ngra in zip(billets_id,ngramme_billets_fit):
		auteur_ids = fonctions_bdd.select_bdd_table_champ(name_bdd,'billets','auteur_id','id',b_id)
		#auteur = text_processing.nettoyer_url((auteur))
		jours = fonctions_bdd.select_bdd_table_champ(name_bdd,'billets','jours','id',b_id)
		#names =auteur.split(sep)
		#auteur_ids=[]
		#for nom in names:
		#	auteur_ids.append(fonctions_bdd.select_bdd_table_champ(name_bdd,'auteurs','id','auteurs',nom))
		auteur_ids = auteur_ids[1:-1].split(', ')
		concept_ids = []
		for gra in ngra:
			concept_id = gra
			for auteur_id in auteur_ids: 
				lienssocsem.append([auteur_id,concept_id,jours,b_id,requete,str(b_id)+'_' + str(auteur_id) + '_' + str(concept_id)])
			concept_ids.append(concept_id)
		if len(concept_ids)>0:
			concept_ids.sort()
			ccid = -1
			for con1 in concept_ids:
				ccid +=1
				for con2 in concept_ids[ccid:]:
					lienssem.append([con1,con2,jours,b_id,requete,str(b_id)+'_' + str(con1) + '_' + str(con2)])
	return lienssocsem,lienssem
	
def build_social_net(requete,name_bdd,sep,name_data):
	lienssoc=[]
	auteurs = fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'auteurs','id,auteurs')
	dic_auteurs ={}
	for aut in auteurs:
		dic_auteurs[aut[1]] = aut[0]
			#auteur = fonctions_bdd.select_bdd_table_champ(name_bdd,'billets','site','id',b_id)
			#auteur = text_processing.nettoyer_url((auteur))
			#jours = fonctions_bdd.select_bdd_table_champ(name_bdd,'billets','jours','id',b_id)
		#	print auteur
			#names =auteur.split(" *%* ")
			#auteur_ids=[]
			#for nom in names:
			#	auteur_ids.append(fonctions_bdd.select_bdd_table_champ(name_bdd,'auteurs','id','auteurs',nom))
	
	if name_data[-4:] in ['.isi','.med'] :
		contenu = fonctions_bdd.select_bdd_table(name_bdd,'billets','id,auteur_id,jours',requete)
		for cont in contenu:
			b_id=cont[0]
			clique_auteurs = cont[1]
			participants=[]
			jours = cont[2]
			for participant in clique_auteurs.split(', '):
				participant=participant.replace('[','')
				participant=participant.replace(']','')
				participants.append(participant)
			for aut_1 in participants:
				for aut_2 in participants:
					if aut_1 != aut_2:
						lienssoc.append([aut_1,aut_2,jours,b_id,requete,str(b_id)+'_' + str(aut_1) + '_' + str(aut_2)])
						
						
	else:
		contenu = fonctions_bdd.select_bdd_table(name_bdd,'billets','id,href,jours,site',requete)
		for cont in contenu:
			b_id=cont[0]
			aut_id = cont[1]
			href_list = cont[1]
			jours = cont[2]
			site = cont[3]
			auteurs = text_processing.nettoyer_url(site)
			names =auteurs.split(sep)
			auteur_ids=[]
			for nom in names:
				auteur_ids.append(fonctions_bdd.select_bdd_table_champ(name_bdd,'auteurs','id','auteurs',nom))
			url_ids=[]
			if len(href_list)>0:
				hrefs = href_list.split("***")
				hrefs_propre=[]
				for hre in hrefs:
					if len(hre)>1:
						hrefs_propre.append(hre)
				hrefs = hrefs_propre
				hrefs  = map(text_processing.nospace,hrefs)
				
				for url in hrefs:
					#print str(url)
					urlok = url.decode('utf-8','replace')
					url = urlok.replace("popostrophe","'")
					for aut in dic_auteurs.keys():
						if aut in url:
							id_lien = dic_auteurs[aut]
							if not id_lien in url_ids: 	
								url_ids.append(id_lien)
								for aut_id in auteur_ids:
									if not id_lien ==aut_id:
										lienssoc.append([aut_id,id_lien,jours,b_id,requete,str(b_id)+'_' + str(aut_id) + '_' + str(id_lien)])
	return(lienssoc)

def extraire_reseaux(contenu,file_social_net_name):
	file_social_net = open(file_social_net_name,'w')
	net={}
	for lien in contenu:
		auteur1 = lien[0]
		auteur2 = lien[1]
		jour = lien[2]
		lien_soc = (auteur1,auteur2,jour)
		if not lien_soc in net:
			net[lien_soc] = 1
		else:
			net[lien_soc] = 1+net[lien_soc] 
	for link_date in net:
		file_social_net.write(str(link_date[0]) + '\t'+str(link_date[1]) + '\t' +str(link_date[2]) + '\t'+ str(net[link_date])+ '\n')

def extraire_reseaux_filtre(contenu,file_social_net_name,condition,name_bdd):
	#filtre sur la sélection...
	billets_index =  fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'socsem','id_b')
	billet_occ={}
	for bill_et in billets_index:
		bille=bill_et[0]
		if bille in billet_occ:
			billet_occ[bille]=billet_occ[bille]+1
		else:
			billet_occ[bille]=1
#	print billet_occ
	file_social_net = open(file_social_net_name,'w')
	net={}
	for lien in contenu:
		if billet_occ[lien[3]]<20:
			auteur1 = lien[0]
			auteur2 = lien[1]
			jour = lien[2]
			lien_soc = (auteur1,auteur2,jour)
			if not lien_soc in net:
				net[lien_soc] = 1
			else:
				net[lien_soc] = 1+net[lien_soc] 
		#else:
		#	print 'billet '+str(lien[3]) + ' occ ' + str(billet_occ[lien[3]]) + ' rejete'
	for link_date in net:
		file_social_net.write(str(link_date[0]) + '\t'+str(link_date[1]) + '\t' +str(link_date[2]) + '\t'+ str(net[link_date])+ '\n')

def extraire_reseaux_pondere(contenu,file_social_net_name,name_bdd):
	#filtre sur la sélection...
	billets_index =  fonctions_bdd.select_bdd_table_champ_simple(name_bdd,'socsem','id_b')
	billet_occ={}
	for bill_et in billets_index:
		bille=bill_et[0]
		if bille in billet_occ:
			billet_occ[bille]=billet_occ[bille]+1
		else:
			billet_occ[bille]=1
#	print billet_occ
	file_social_net = open(file_social_net_name,'w')
	net={}
	for lien in contenu:
		if 1:
			normalisation = billet_occ[lien[3]]
			auteur1 = lien[0]
			auteur2 = lien[1]
			jour = lien[2]
			lien_soc = (auteur1,auteur2,jour)
			if not lien_soc in net:
				net[lien_soc] = float(1) / float(normalisation)
			else:
				net[lien_soc] = float(1) / float(normalisation)+net[lien_soc] 
		#else:
		#	print 'billet '+str(lien[3]) + ' occ ' + str(billet_occ[lien[3]]) + ' rejete'
	for link_date in net:
		file_social_net.write(str(link_date[0]) + '\t'+str(link_date[1]) + '\t' +str(link_date[2]) + '\t'+ str(net[link_date])+ '\n')
	