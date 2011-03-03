# -*- coding: utf-8 -*-
#!/usr/bin/python
import codecs
import unicodedata
import os
import treetaggerwrapper
import sys
import misc
import re
import parameters
import fonctions_bdd
name_bdd=parameters.name_bdd
language = parameters.language
#import letters

###############################
###############################
#UTF8 black magic##############
###############################
###############################


def specialutf8(str):		
	return str.replace(u'\u2019',"'").replace(u'\u2019',"'").replace(u'\xab','"').replace(u'\x92',"'").replace(u'\xbb','"').replace(u"\u2013","-").replace(u'\x99','').replace(u'\x96','').replace(u'\x93','"').replace(u'\x94','"').replace(u'\x9c',"oe").replace(u'\xb0',"o").replace(u'\u2026','...').replace(u'\u0153','oe').replace(u"\u2018","'").replace(u"\u00AB"," ").replace(u"\u00BB"," ").replace(u"\u2019","'").replace(u"\u201D",'"').replace(u"\u201C",'"').replace(u"\u2015",'-').replace(u"\u2016",'-').replace(u"\u20AC","euro").replace(u"\u2122","(tm)").replace(u"\u00C9","E").replace(u'\xc2\x99',"(tm)").replace("==========","").replace(u"\xe0","à")			
		
def remove_accents(str): #remove accents from a unicode thingy, dude
	nkfd_form=unicodedata.normalize('NFKD',unicode(str))
	tmp=u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
	return specialutf8(tmp)

###############################
###############################
#les stop-words################
###############################
###############################

	

def isNotStopWord(word):
#	print '\n' + word
	if 'PUN_' in word:
		return False
	if 'SEN_' in word:
		return False
	if 'KON_' in word:
		return False
	if '_' in word:
		word_base = word.split('_')[1]
	else:
		word_base=word
	if word_base not in stopWordsSet:
		return True
	else:
	#	print word_base
		return False
	
def notinterdit(language,tag):
	if language=='english':
		if tag in ['VE','VH','DT','RB','CC','IN','CC','UH','EX','LS','MD','RP','PP','PO','WP','PD','TO','IN','WP','WD','WR',':',',','.',';','CD','VB','SE',')','(','SY','#']:
			return False
		else:
			return True
	if language=='french':
		if tag in ['DE','KO','PR','PU','SE','KO','#',':',',','.',';']:
			return False
		else:
			return True

def notinterditfin(language,tag):
	if language=='english':
		if tag in ['VE','JJ','PR','DT','TO','IN','WD','VB','CC']:
			return False
		else:
			return True
	if language=='french':
		if tag in ['VE','PR','KO','DE']:
			return False
		else:
			return True

def notinterditall(tag):
#	if language=='english':
		if tag in [')','(','SE','PU',':',',',';']:
			return False
		else:
			return True
						
def atleast(tag):
	if language=='french':
		if tag in ['','NO','NA','AB']:
			return True
		else:
			return False
	if language=='english':
		#avec filtre
		if tag in ['','NN','NP']:
			return True
		else:
			return False
		#sans filtre
		#return True
		
def get_tags(wordv):
	tags=[]
	for word in wordv:
		tag=''
		if '_' in word:
			tag = word.split('_')[0]
		tags.append(tag)
	return tags


####Attention réglagle local ici.
special_bigramme = 0
def isNotStopWordForClique(word, language):	
	wordv=word.split(' ')
	if special_bigramme == 1:
		if len(wordv)==2:
			tags = get_tags(wordv)
			if language == 'french':
				if (tags[0] in ['NO','NA'] and tags[1] in ['AD','NA'])  or (tags[1] in ['NO','NA'] and tags[0] in ['AD','NA']):
					return True
				else:
					return False
			else:
				if tags[1] in ['NN','NA'] and tags[0] in ['JJ','NN']:
					#print word
					return True					
				else:
					return False
	else:
		if len(wordv)>1:#cette partie est dédiée aux n-lemmes n>=2
			tags = get_tags(wordv)
			tag_fin=tags[-1]
			if notinterditfin(language,tag_fin):
				tag_base=tags[0]
				if notinterdit(language,tag_base):#on supprime les ngrammes qui commencent par un mauvais tag
					if all(map(notinterditall,tags)):#on elimine les ensembles de tag qui ont des tags interdits
						if any(map(atleast,tags)):#cette dernière condition requiere la présence d'un nom 
							return True
		else:
			if len(word)>1:#on réduit maintenant aux 1-grammes. 
				if '_' in word:
					w = word.split('_')[0]
					if language == 'english':
						if w in ['NN','NP']:
							return True
					if language == 'french':
						if w in ['NO','NA']:
							return True						
				else:
					try:
						int(word)
						return False
					except:
						return True
			else:
				return False

def simple_ponctuation(str):
	return str.replace("...",".").replace('-', ' ').replace(':', ' ').replace('\'', ' ').replace('.', ' . ').replace(',', ' , ').replace(';', ' ; ').replace(':', ' : ').replace("'", " ").replace('"',' ').replace("\t"," ").replace("["," ").replace("]"," ").replace("\n"," ").replace("!"," ! ").replace("?"," ? ").replace("("," ( ").replace(")"," ) ").replace("*"," ").replace("/"," / ").replace("\\"," \\ ")

def remove_ponctuation(str):
	return str.replace(".","").replace(';', '').replace(':', '').replace(',', '').replace(':', '').replace(" ","").replace("!","").replace("?","").replace("(","").replace(")","").replace("/","").replace("\\","")


###############################
###############################
#le dictionnaire de lemmes#####
###############################
###############################
	
def lemmatisation(lemmadictionary,dictionary_filename,contenu,treetagger_dir):
	#par defaut, il n'y a pas de lemmatisation
	lemmadict={}
	occ={}
	#si on ne specifie pas un dictionnaire de lemmes alors on en recree un directement depuis python.
	if lemmadictionary==0: #and not os.path.isfile(dictionary_filename):
		print '    + building lemma dictionnary indeed.'
		compteur = 0
		for cont in contenu:
			texte_brut =  cont[0]
			texte_brut=texte_brut.replace('<b>','').replace('</b>','')
			texte_lemm = cont[1]
			compteur +=1
			if not compteur%250 or compteur==len(contenu) : 
				print "     [#"+str(compteur) +"]"
			clause=0
			for bout in zip(texte_brut.split(),texte_lemm.split()):
				orig = bout[0]
				dest = bout[1]
				if dest in occ:
					dico_dest = occ[dest]
					if orig in dico_dest:
						dico_dest[orig] = dico_dest[orig] + 1
					else:	
						dico_dest[orig] = 1
					occ[dest]  = dico_dest
				else:
					dico_dest = {}
					dico_dest[orig] = 1
					occ[dest] = dico_dest
	return  occ

def cmpval(x,y):
    if x[1]>y[1]:
        return -1
    elif x[1]==y[1]:
        return 0
    else:
        return 1

def extraire_forme_majoritaire(lemmadictionary,occ_termes_lemmes,dictionnaire_treetagged__formes_name,dictionnaire_treetagged__formemajoritaire_name):
	lemme_maj={}
	if lemmadictionary==0:
		file1 = codecs.open(dictionnaire_treetagged__formes_name,'w','utf-8')
		file2 = codecs.open(dictionnaire_treetagged__formemajoritaire_name,'w','utf-8')
		for lemme in occ_termes_lemmes:
			dico_lemme = occ_termes_lemmes[lemme]
			liste_dic_lemme = dico_lemme.items()
			liste_dic_lemme.sort(cmpval)
			new = liste_dic_lemme[0][0]
			new=new.decode('utf-8','replace')
			try:
				lemme =  lemme.decode('utf-8','replace')
			except:
				pass
			lemme_maj[lemme] = new
			file1.write(lemme +'\t')
			occurrences=0
			for fo in liste_dic_lemme:
				form = fo[0]
				form = form.decode('utf-8','replace')
				occurrences=occurrences+int(fo[1])
				file1.write( form + ' ('+ str(fo[1]) + ') ')
			file1.write("\n")
			file2.write(lemme +'\t'+new+'\t'+str(occurrences)+'\n')	
		file1.close()
		file2.close()
				
	else:
		try:
			lemmadict_file=codecs.open(dictionnaire_treetagged__formemajoritaire_name,"r","utf8")
		except:
			print "no dictionnary !"
			quit()
		print "--- opened lemma dictionary (UTF8) file \""+dictionnaire_treetagged__formemajoritaire_name+"\"..."

		for l in lemmadict_file:
			p=l.split("\t")
			orig=p[0]
			dest=(p[1].split("\n"))[0]	
			orig = orig#.encode('utf-8','replace')
			dest = dest#.decode('utf-8','replace')
			if orig not in lemme_maj:
				lemme_maj.setdefault(orig,dest)
		lemmadict_file.close()
		print "    -  lemma formes majoritaires: ("+str(len(lemme_maj.keys()))+" entries)."		
	return lemme_maj
		
	

	
def billets_cleaner(billet,tagger):
	"billet en texte en entree et en sortie billet en liste mais les termes sont remplaces par leurs  lemmes et la ponctuation dans la phrase a disparue"
	billetclean=[]
	billetorig=[]
	compteur = 0
	tags = tagger.TagText(billet.decode('utf-8',"replace"))
	for line in tags:
		ps=line.split()
		if len(ps)>2:
			orig,dest,forme=ps[0],ps[2].lower(),ps[1]
			if (dest!="<unknown>" and dest!="@card@"):
				dest2  = forme[:2] + '_' + dest
				billetclean.append(dest2)
				billetorig.append(orig)
			else:
				billetclean.append(orig.lower())
				billetorig.append(orig.lower())
	return [' ']+billetclean+[' '],[' ']+billetorig+[' ']


def tag2(word):
	words = word.split(' ')
	word=''
	for w in words:
		wv=w.split('_')
		if len(wv)>1:
			word = word+' '+wv[0][:2]+'_'+''.join(wv[1:])
		else:
			word = word+' '+w
	word = word[1:]
	return word

def ngramme_build(billet,maxTermLength,dictionnaire_gramme,language,freq_type):
	dejavu=[]
	for termLengthMinusOne in range(maxTermLength): # minusOne because range(maxTermLength)= [0,...,maxTermLength - 1]
		for i in range(len(billet) - termLengthMinusOne): 
			if i == 0 :
				wordWindow = billet[:termLengthMinusOne + 1]
			else :
				wordWindow.append(billet[i + termLengthMinusOne])
				wordWindow.pop(0)
 			term = ' '.join(wordWindow)
			if all(map(isNotStopWord,wordWindow)) and not term in stopnWordsSet:
				term=tag2(term)
				if not str(term)=='None':
					if isNotStopWordForClique(term,language)==True:#False not in map(isNotStopWordForClique,wordWindow): # set(wordWindow) ^ stopWordsSet != set([]) no stop word in term	
						if not term in dejavu:
							#on ne compte qu'une occurrence par billet
							#finalement selon le moment il peut être plus prudent de compter l'ensemble des occurrenes notamment pour calculer les poupées russes, il y a donc deux façon de requêter  ngramme_build
							if freq_type == 'billet':
								dejavu.append(term)
							#if freq_type == 'absolu':
							#	pass
							if not dictionnaire_gramme.has_key(term):
								dictionnaire_gramme[term] = 1
							else:
								dictionnaire_gramme[term] = dictionnaire_gramme[term] + 1
	return dictionnaire_gramme

def	ngramme_find(billet_lemmatise,dictionnaire_gramme,concept_list):

	for x in concept_list:
		term= ' '+x + ' '
		if term in ' ' + billet_lemmatise +' ':
			term = term[1:-1]
			if not dictionnaire_gramme.has_key(term):
				dictionnaire_gramme[term] = 1
			else:
				dictionnaire_gramme[term] = dictionnaire_gramme[term] + 1
	return dictionnaire_gramme
	
def nettoyer_url(author):
	if "http://" in author:
		author = author[:-1]
		author = author.replace('http://','')
		author= author.replace('www.','')
	author = author.replace("'",'popostrophe')
	return author
	

def nospace(chaine):
	"enleve les espaces au debut et a la fin"
	if len(chaine)>0:
		while chaine[0] == ' ' and len(chaine)>3:
			chaine = chaine[1:]
		while chaine[-1] == ' 'and len(chaine)>3:
			chaine = chaine[:-1]	
		return chaine
	
def indexer_billet(contenu,ngrammes,maxTermLength,include):
	formes ={}#fournit le dictionnaire des formes majoritaires prises par les n-lemmes	
	billetprocessed=0
	billets_id=[]
	ngrammes_fit=[]
	ngrammes_fit_auteurs={}
	#ngrammes_fit_index=[]
	nn=[]
	nouveau_contenu=[]
	#on trie la liste des ngrammes du plus grand n au plus petit
	ngrammes_dict={}
	for ngr in ngrammes:
		n=ngr.count(' ')+1
		nn.append(n)
		ngrammes_dict[ngr]=n
	items = ngrammes_dict.items()
	items = [(v, k) for (k, v) in items]
	items.sort() 
	items.reverse()		
	items = [(k, v) for (v, k) in items]
	for billets in contenu:
		billetprocessed+=1
		#if not billetprocessed%250 : 
		#	print "     [#"+str(billetprocessed) +"]"
		billet_id = billets[0]
		billet_lemmatise=billets[1]
		billet_brut=billets[2]
		billet_brut = billet_brut.replace('<b>','').replace('</b>','')
		billet_auteur = billets[3]
		billet_auteur=billet_auteur[1:-1]
		billet_brutv = billet_brut.split()
		billet_brutv_copie = billet_brut.split()
		#version anciennce
		#billet_lemmatise=' '+billet_lemmatise+' '
		billet_lemmatise=' '+unicode(billet_lemmatise,'utf-8')+' '
		billets_id.append(billet_id)
		ngramme_fit=[]
		ngramme_fit_auteur=ngrammes_fit_auteurs.get(billet_auteur,[])
		#ngramme_fit_index=[]
		for ngraz in items:#zip(ngrammes,nn):
			for ngra in ngraz[0].split('***'):
				if len(ngra)>0:
					ngraz1_long = ngra.count(' ')+1
					#version anciennce
					#chaine=' '+str(ngra)+' ','utf-8'
					chaine=unicode(' '+str(ngra)+' ','utf-8')
					if chaine in billet_lemmatise:
						if not ngraz[0] in ngramme_fit:
							ngramme_fit.append(ngraz[0])
						dest = ngraz[0]
						idx = billet_lemmatise.find(chaine)
						clause_include_0 = 0
						while chaine in billet_lemmatise and clause_include_0 == 0:
							idx = billet_lemmatise.find(chaine)
						
							longueur = len(ngra)+1
							avant = billet_lemmatise[:idx]
							pas = len(avant.split())
					
							orig = billet_brutv[pas:pas+ngraz1_long]	
							orig_c = billet_brutv[pas:pas+ngraz1_long]
							orig = ' '.join(orig)
							#attention bug parfois!!!:
							try:
								orig_c[0]='<b>'+orig_c[0]
								orig_c[-1]= orig_c[-1]+'</b>'
							except:
								pass
							billet_brutv_copie = billet_brutv_copie[:pas] + orig_c +  billet_brutv_copie[pas+ngraz1_long:]
							if include==1:
								billet_lemmatise=billet_lemmatise[:idx] + ' '+ billet_lemmatise[idx+longueur:] 
								######AMELIORATION: Enlever les bouts plutôt que de les rajouter...
								billet_brutv=billet_brutv[:pas] + billet_brutv[pas+ngraz1_long:] 	
							if dest in formes:
								dico_dest = formes[dest]
								if orig in dico_dest:
									dico_dest[orig] = dico_dest[orig] + 1
								else:	
									dico_dest[orig] = 1
								formes[dest]=dico_dest
							else:
								dico_dest = {}
								dico_dest[orig] = 1
								formes[dest] = dico_dest
							if include == 0:
								clause_include_0 = 1
		#mise à jour du champ content
		nouveau_contenu.append((billet_id,' '.join(billet_brutv_copie)))
		ngrammes_fit.append(ngramme_fit)
		ngramme_fit_auteur.extend(ngramme_fit)
		ngramme_fit_auteur = list(set(ngramme_fit_auteur))
		ngrammes_fit_auteurs[billet_auteur]=ngramme_fit_auteur
		#billet_brutv_copie
	
	#fonctions_bdd.update_table(name_bdd,'billets','content',nouveau_contenu)	
	return ngrammes_fit,billets_id,formes,ngrammes_fit_auteurs
	
#--------------------------------------------------------
#--------------------------------------------------------
#- INITIALISATION DE LA BIBLIOTHEQUE text_processing.py -
#--------------------------------------------------------
#--------------------------------------------------------


def define_stop_words(language,name):
	stopWordsSet = set([])
	try:
		stopword_filename="libraries/"+name+'_'+language+'.txt'
		stopWordsFile = codecs.open(stopword_filename, 'r',encoding='utf8',errors="replace")
		nstopword=0
		for word in stopWordsFile.readlines():
			for w in word.split('***'):
				stopWordsSet.add(str(word.encode("utf8")).strip())
				#add without accent
				#stopWordsSet.add(remove_accents(word).strip())
				nstopword+=1
		stopWordsFile.close()
	except:
		pass
	return stopWordsSet
	stopWordsFile.close()
stopWordsSet = define_stop_words(language,"stop_words")
stopnWordsSet = define_stop_words(language,"stop_wordsn")
	
#print stopWordsSet
#print stopnWordsSet
