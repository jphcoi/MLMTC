#!/usr/bin/env python
# encoding: utf-8
"""
parseur.py

Created by Jean philippe cointet  on 2010-08-11.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

import codecs
import os
import sys
import time
from datetime import timedelta
from datetime import date
import parameters
from xml.dom.minidom import parse
import xml.parsers.expat
import datetime
import calendar
import getopt
import copy, re
import BeautifulSoup
# 
# def convert(html):
# 	return BeautifulSoup(html,convertEntities=BeautifulSoup.HTML_ENTITIES,markupMassage=hexentityMassage).contents[0].string


content_indexation=parameters.content_indexation
try:
	Kws=parameters.Kws
except:
	Kws=[]


#maladie le 7 août 2010 à l’âge de 80 ans
def specialutf8(str):		
	return str.replace(u"’","'").replace(u'\xe2\x80\x99',"'").replace(u'\xe2\x80\x9d','"').replace(u'0xe2','\'').replace(u'\u2019',"'").replace(u'\u2019',"'").replace(u'\xab','"').replace(u'\x92',"'").replace(u'\xbb','"').replace(u"\u2013","-").replace(u'\x99','').replace(u'\x96','').replace(u'\x93','"').replace(u'\x94','"').replace(u'\x9c',"oe").replace(u'\xb0',"o").replace(u'\u2026','...').replace(u'\u0153','oe').replace(u"\u2018","'").replace(u"\u00AB"," ").replace(u"\u00BB"," ").replace(u"\u2019","'").replace(u"\u201D",'"').replace(u"\u201C",'"').replace(u"\u2015",'-').replace(u"\u2016",'-').replace(u"\u20AC","euro").replace(u"\u2122","(tm)").replace(u"\u00C9","E").replace(u'\xc2\x99',"(tm)").replace("==========","")#.replace(u'\xbf',"û").replace(u'xe0','à')

def insider(Kws,content):
	if len(Kws)==0:
		clause=1 
	else:
		clause=0
		for kw in Kws:
			kw_v =kw.split(' AND ')
			cl=0
			for k in kw_v:
			 	if k.lower() in content.lower():		
					cl = cl+1
			if cl == len(kw_v):
				clause=1
				break
	return clause 

#written by Telmo Menezes
class XML2DB:
    
    def __init__(self, indir, dbpath, continent, community, territory):
        self.indir = indir
        self.dbpath = dbpath
        self.continent = continent
        self.community = community
        self.territory = territory
        self.blogcount = 0
        self.importcount = 0
        self.articles = []
        self.importcount = 0
	
    def datestr2timestamp(self, str):
        clean_str = str[:19] + 'GMT'
        tzhours = 0
        tzminutes = 0
        if len(str) > 20:
            tzhours = int(str[19:22])
            tzminutes = int(str[23:25])
            if tzhours < 0:
                tzminutes = -tzminutes
        dt = datetime.datetime.strptime(clean_str, '%Y-%m-%dT%H:%M:%S%Z')
        dt -= datetime.timedelta(hours=tzhours, minutes=tzminutes)
        ts= calendar.timegm(dt.timetuple())

        return ts


    def accept_blog(self, continent, community, territory):
        if (len(self.continent) > 0) and (continent != self.continent):
            return False
        if (len(self.community) > 0) and (community != self.community):
            return False
        if (len(self.territory) > 0) and (territory != self.territory):
            return False
        return True

    def process_post(self, dom):
        date = ''
        permalink = u''
        title = u''
        author = u''
        content = u''
        editorial_links = None
        comments_links = None
        misc_links = None
        links_list=[]
        for e1 in dom.childNodes:
            if e1.tagName == 'date':
                datet = ''.join(t.nodeValue for t in e1.childNodes if t.nodeType == t.TEXT_NODE)
            #elif e1.tagName == 'permalink':
            elif e1.tagName == 'canon_url':
                permalink = u''.join(t.nodeValue for t in e1.childNodes if t.nodeType == t.TEXT_NODE)
            elif e1.tagName == 'title':
                title = u''.join(t.nodeValue for t in e1.childNodes if t.nodeType == t.TEXT_NODE)
                #print title
            elif e1.tagName == 'author':
                author = u''.join(t.nodeValue for t in e1.childNodes if t.nodeType == t.TEXT_NODE)
            elif e1.tagName == 'plain_content':
                content = u''.join(t.nodeValue for t in e1.childNodes if t.nodeType == t.TEXT_NODE)
            elif e1.tagName == 'links':
                links = e1
                if links is not None:
      	            for e2 in links.childNodes:
    	                if e2.tagName == 'link':
                            targ_postid = -1
                            targ_blogid = -1
                            link_type = 0
                            site = e2.getAttribute('site')
                            canon_url = e2.getAttribute('canon_url')
                            url = e2.getAttribute('url')
                            type = e2.getAttribute('type')
                            if type == 'editorial':
                                link_type = 1
                                links_list.append(site.replace('http://','')[:-1])
                            #elif type == 'comment':
                             #   link_type = 2
 	                        #print "link_type:"
                            #print site +'\t' + canon_url+'\t' + url+'\t' + str(link_type)
                            
                # links=[]
                #                 for t in e1.childNodes:
                #                     link = t.toxml()
                #                     link = link.split('canon_url=')[1]
                #                     links.append(link.split('"')[1].replace('http://','')[:-1])
                #                 if len(links)>0:
                #                     editorial_links = u'***'.join(link for link in links)
                #             elif e1.tagName == 'comments_links':
                #                 comments_links = e1
                #             elif e1.tagName == 'misc_links':
                #                 misc_links = e1
        #ts = self.datestr2timestamp(date)
        if len(links_list)>0:
            editorial_links = u'***'.join(link for link in links_list)
        else:
            editorial_links=u''
        return  datet, permalink, specialutf8(title), author, specialutf8(content),editorial_links
        #self.insert_post(blogid, ts, permalink, title, author, content)

    def process_xml(self, dom):
        nb_posts=0
        articles=[]
        for e1 in dom.childNodes:
            if e1.tagName == 'site':
                url = e1.getAttribute('url')
                continent = e1.getAttribute('continent')
                community = e1.getAttribute('community')
                territory = e1.getAttribute('territory')
                self.blogcount += 1
                if self.accept_blog(continent, community, territory):
                    self.importcount += 1
                    #blogid = self.insert_blog(url, continent, community, territory)
                    for e2 in e1.childNodes:
                        try:
                            if e2.tagName == 'posts':
                                for e3 in e2.childNodes:
                                    if e3.tagName == 'post':
                                        nb_posts = nb_posts+1
                                        datet, permalink, title, author, content,editorial_links= self.process_post(e3)                                        
                                        if insider(Kws,title + ' '  + content)>0:
                                            articles.append([title,datet,permalink,url,continent,community,territory,title+ '***' + content,author,editorial_links])
										
                        except:
                            pass
        return articles,nb_posts

    def process_dir(self, dir):
        """
        Recursively traverse directory tree and process files
        """
        articles=[]
        print('Entering directory %s.' % dir)
        for item in [f for f in os.listdir(dir)]:
            fullpath = os.path.join(dir, item)
            if os.path.isdir(fullpath):
                self.process_dir(fullpath, cycle)
            elif item[-4:] == '.xml':
                try:
                    dom = parse(fullpath)
                    articles_blog,nb_posts = self.process_xml(dom)
                    articles=articles + articles_blog
                    dom.unlink()
                    print('Imported xml file: %s number %d, [%d / %d]' % (fullpath, self.blogcount, len(articles_blog),nb_posts))
                except xml.parsers.expat.ExpatError:
                    print('Error importing xml file: %s' % fullpath)
        return articles
			

    def run(self):
        #self.conn = sqlite3.connect(self.dbpath)
        articles = self.process_dir(self.indir)
       # print articles
        return articles
        #self.conn.close()


#renvoie le contenu non-HTML d'un contenu brut HTML "cont", i.e. expurge des balises
def cleancontent(cont):
	newcont=""
	balise=0
	for i in range(len(cont)):
		if cont[i]=="<": balise=1
		if balise==0: newcont+=cont[i]
		if cont[i]==">": balise=0
	return newcont


#renvoie les references HREF d'un contenu brut HTML "cont", i.e. <a href=...>
def detecthref(cont):
	i=0
	anchorcont=""
	while i<len(cont):
		if cont[i]=="<":
			if i+1<len(cont):
				if cont[i+1]=="a": #anchor
					hrefstart=0
					i+=1
					mode=0
					okhref=0
					oldanchorcont=anchorcont
					while (i<len(cont) and cont[i]!=">"):
						#si on tombe sur un separateur, on incremente hrefstart, qui doit valoir 1 pour qu'on considere qu'on soit sur une href
						if (cont[i]==" " and mode==0): hrefstart+=1
						if (cont[i]=='"' and mode==1): hrefstart+=1
						if (cont[i]=="'" and mode==2): hrefstart+=1
						if hrefstart==1: anchorcont+=cont[i]
						#print anchorcont[-6:]
						#detection du separateur: mode 0: espace, mode 1: guillemet, mode 2: apostrophe
						if anchorcont[-5:]=="href=": okhref=1
						if anchorcont[-6:]=='href=h': mode=0
						if anchorcont[-6:]=='href="': mode=1
						if anchorcont[-6:]=="href='": mode=2
						i+=1
					anchorcont+=" *** "
					#si en fait ce n'etait pas une href, on annule:
					if (okhref==0): anchorcont=oldanchorcont 
		i+=1
	return anchorcont.replace(' href="'," ").replace(" href='"," ").replace(" href="," ")



###############################
###############################
#traitement date###############
###############################
###############################


def date_billet_parser(datee):
	datee = str(datee)
	if ' ' in datee:
		datev = datee.split(' ')
	else:
		if '-' in datee:
			datev = [datee,'']
		else:
			datev=[datee]

	if len(datev) >1:
		
		daate = datev[0]
		datev = daate.split('-') #a commenter dans le cas du xml seulemnt
		if len(str(datev[2]))>3:
			#doctissimo, annee et jour inverse
			y  = datev[2]
			datev[2]=datev[0]
			#bug sur date...
			datev[2]=15
			
			datev[0]=y
		date_billet = date(int(datev[0]),int(datev[1]),int(datev[2]))
	else:
		#date_billet =date(int(datev[0]),1,1)
		date_billet=datee
	return date_billet

def jour_entre(date_billet,date_depart):
	if len(str(date_billet))<4:
		return str(date_billet)
	else:
		try:
			if parameters.temps_grain!='years':
				delta= abs(date_billet - date_depart)
				return delta.days +1
		except:
			if "201" in str(date_depart):
				delta = abs(date_billet - date_depart)
				return delta.days +1
			else:
				return str(date_billet)[0:4]

	
###############################
###############################
#lecture des billets###########
###############################
###############################

def lecture_content(bdd_filename,date_depart):
 
	contenu=[]
	datebillet=[]
	auteurbillet=[]
	bdd_file=codecs.open(bdd_filename,"r","utf8")
	contenubillet = ''
	nbillet=0
	clause=0
	for ligne in bdd_file:
		if ligne[:7]=="website":	   
			auteur_billet = (ligne[9:-1])
			#if (date_depart)==0:
			#	date_depart = date_billet
			#jour = jour_entre(date_billet,date_depart)
		if ligne[:4]=="date":
			date_billet = date_billet_parser(ligne[6:])
			if (date_depart)==0:
				date_depart = date_billet
			jour = jour_entre(date_billet,date_depart)
		if ligne[:7]=='content':
			clause = 1
			ligne = ligne[8:]
		if ligne[:5]=='title':
			if len(contenubillet)>0:
				contenu.append(contenubillet)
				datebillet.append(jour)
				auteurbillet.append(auteur_billet)
				contenubillet=''
				clause = 0
				nbillet+=1
		if clause == 1:
			contenubillet = contenubillet + ligne
	bdd_file.close()
	return contenu,datebillet,auteurbillet
	print "--- database file closed, "+str(nbillet)+" posts processed with their date."
	
	
def lire_dico(dico_index_file):
	concepts = []
	fileo = open(dico_index_file,'r')
	lignes=fileo.readlines()
	for ligne in lignes:
		if '\t' in ligne:
			lignev  = ligne.split('\t')
			concept = lignev[0]
		else:
			concept = ligne[:-1]
			concept=concept.replace('\r','')
		concepts.append(concept)
	return concepts






###############################
###############################
#lecture integrale des billets#
###############################
###############################
#banner: Ctrl Shift B
#commentaire: pomme+ shift + slash
def get_field_raw(champs,line,dico,lines,i):
	if line[:2] in champs:
		valeur = line[3:]
		while lines[i+1][:2]=='  ':
			i=i+1
			valeur = valeur + lines[i][3:]			
		if line[:2]=='ID':
			valeur = valeur.lower()
		dico[line[:2]]=valeur
	return dico

def get_field_precise(champ,dico,sep):
	try:
		valeur= dico[champ][:-1].replace('\n',sep)
	except:
		valeur=''		
	return valeur
	
def process_field(champs_liste,dico_article,sep):
	#champs_liste=['TI','DT','ID','AB','CR','DI','AU','PY','CT','DE','ER','UT']
	
	infos = map(get_field_precise,['TI','PY','DI','AU','CT','ID','DE','AB','CR','UT'],[dico_article,dico_article,dico_article,dico_article,dico_article,dico_article,dico_article,dico_article,dico_article,dico_article],[sep,sep,sep,sep,sep,sep,sep,sep,sep,sep])
																														#champs_name = "(title,date,permalink,site,categorie1,categorie2,categorie3,content,href,requete,identifiant_unique)"#on n'enregistre pas le html bru	
	#on aggrege tous les champs contenus (TITRE  + MOTS CLES ID + MOTS CLES DE + ABSTRACT) 	
	#infos[7]=infos[0]+' . '+infos[5]+' . '+infos[6]+' . '+infos[7]
	#on aggrege tous les champs contenus (TITRE + ABSTRACT)
	if content_indexation == 'TA':
		infos[7]=infos[0]+' . '+infos[7]
	if content_indexation == 'A':
		infos[7]=' . '+infos[7]
	if content_indexation == 'T':
		infos[7]=' . '+infos[0]
	if content_indexation == 'TAKW':
		infos[7]=infos[0]+' . '+infos[5]+' . '+infos[6]+' . '+infos[7]
	if content_indexation == 'TAKWA':
		infos[7]=infos[0]+' . '+' . '+infos[6]+' . '+infos[7]

	if content_indexation == 'KW':
		infos[7]=infos[5]+' . '+infos[6]

	
		
	#on ne prend que le titre
	#infos[7]=infos[0]
	infos[7]=infos[7].replace(sep,' ')
	infos[2]=infos[2]+sep+infos[0]
	infos[3]=infos[3].lower()
	infos[6]=infos[9].lower()
	#on remet les DOI à leur place (CR)
	infos[8]=infos[8].replace('DOI *** ','DOI ')
	infos[8]=infos[4]#.replace('DOI *** ','DOI ')
	infos.pop() 
	return infos
	




def extract_champs_lfl(filename,sep,continent=''):
	articles=[]
	articles=XML2DB(filename, 'telmo.db', continent, '', '').run()
	print "---",len(articles),"posts processed."
	return articles

def isiparse(filename,sep):
	file=codecs.open(filename,"r","utf8")
	lines = file.readlines()
	dico_article = {}
	#champs_liste=['TI','DT','ID','AB','CR','DI','AU','PY','JI','DE','ER','UT']
	#on remplace le champ JI par le champ CT
	champs_liste=['TI','DT','ID','AB','CR','DI','AU','PY','CT','DE','ER','UT']
	i=-1
	articles=[]
	nb_article=0
	for line in lines:
		i=i+1
		dico_article = get_field_raw(champs_liste,line, dico_article,lines,i)
		if dico_article.has_key('ER'):
			nb_article +=1
			if nb_article%100==0:
				print nb_article
			categ3,categ2='',''
			infos= process_field(champs_liste,dico_article,sep)
			articles.append(infos)#sans le html brut
			dico_article={}
	file.close()
	print "---",len(articles),"posts processed."
	return articles


def extract_champs_isy(dir,sep):
	articles=[]
	print "    - répertoire d'articles: \""+dir+"\"..."
	articles = []
	for item in [f for f in os.listdir(dir)]:
		print "année : " +str(item)
		for item2 in [f for f in os.listdir(dir + '/' +item)]:
			if item2[0] != '.':
				fichier = dir +  '/' +item+'/' +item2
				print fichier
				articles_file=isiparse(fichier,sep)
				articles=articles +articles_file
	return articles

def extract_champs_isi(filename,sep):
	articles=[]
	print "    - fichier d'articles: \""+filename+"\"..."
	file=codecs.open(filename,"r","utf8")
	lines = file.readlines()
#	categ1,categ2,categ3,permalink,contentanchor = '','','','',''
	dico_article = {}
	#champs_liste=['TI','DT','ID','AB','CR','DI','AU','PY','JI','DE','ER','UT']
	#on remplace le champ JI par le champ CT
	champs_liste=['TI','DT','ID','AB','CR','DI','AU','PY','CT','DE','ER','UT']
	# TI Extraction of Bio-oils from Microalgae
	# DT Article
	# ID ACCELERATED SOLVENT-EXTRACTION; SUBCRITICAL WATER EXTRACTION; MICROBIAL
	# AB A wide variety of terrestrial biomass feed stocks have been identified
	# CR *DION, 2007, 210 DION
	#    BRUNECKY R, 2009, BIOTECHNOL BIOENG, V102, P1537, DOI 10.1002/bit.22211
	#    ALLARD B, 2000, PHYTOCHEMISTRY, V54, P369
	# DI 10.1080/15422110903327919
	# AU Cooney, M
	#    Young, G
	#    Nagle, N
	# PY 2009
	# JI Sep. Purif. Rev.
	# DE Microalgae; oil substitute; biofuel; biomass
	# ER
	i=-1
	nb_article=0
	for line in lines:
		i=i+1
		dico_article = get_field_raw(champs_liste,line, dico_article,lines,i)
		if dico_article.has_key('ER'):
			nb_article +=1
			if nb_article%100==0:
				print nb_article
			categ3,categ2='',''
			infos= process_field(champs_liste,dico_article,sep)
			#if dico_article['DT'][:-1] == 'Article':
			articles.append(infos)#sans le html brut
			dico_article={}
	file.close()
	print "---",len(articles),"posts processed."
	return articles

def extract_champs_medline(filename,sep):
	
	articles=[]
	print "    - fichier d'articles: \""+filename+"\"..."
	file=codecs.open(filename,"r","utf8")
	lines = file.readlines()
	i=0
	categ1,categ2,categ3,permalink,contentanchor = '','','','',''
	clause_titre=0
	clause_content=0
	date='oxic'
	for line in lines:
		i+=1
		if line[:4] == 'PMID':
			i= i+ 1#;# print i
			permalink = line[6:-1]
			title,date,website,contentclean = "",'','',''
		if line[:2] == "DP":
			date = line.split()[2]
			date= date[:4]
		if line[:2] == "TI":
			clause_titre=1
		if clause_titre==1:
			if line[0:2] == "  " or line[:2] == "TI":
				try:
					title  += str(line[6:-1]) + ' '
				except:
					print 'enc_err ' +str(i)
					pass
			else:
				clause_titre=0
				contentclean = title + ' *** '
		if line[:2] == "AB":
			clause_content=1
		if clause_content==1:
			if line[0:2] == "  " or line[:2] == "AB":
				try:
					contentclean  += str(line[6:-1]) + ' '
				except:
					print 'enc_err ' +str(i)
					pass
			else:
				clause_content=0
		if line[:2] == "AU":
			website = website + sep + line[6:-1]
		if line[:2] == "\n":
			if date == 'utat' or date == 'ood' or date =='hemi'or date =='egul'  or date == 'ourn' or date == 'oxic' : 
				pass
			else:
				if len(date)==4:
					h=str(int(date))
					if len(website)>1:
						website = website[5:]
					if insider(Kws,title + ' '  + contentclean)>0:
						articles.append([title,date,permalink,website,categ1,categ2,categ3,contentclean,contentanchor])#sans le html brut

		#print articles
	file.close()

	print "---",len(articles),"posts processed."
#	print "    - such as: ",posts[0]
	return articles

def extract_champs_fet(filename):
	articles=[]
	print "    - fichier d'articles: \""+filename+"\"..."
	file=codecs.open(filename,"r","utf8")
	lines = file.readlines()
	i=0
	categ1,categ2,categ3,permalink,contentanchor = '','','','',''
	clause_titre=0
	clause_content=0
	for line in lines:
		#if line[:4] == 'PMID':
		#	i= i+ 1; print i
		#	permalink = line[6:-1]
		linev= line.split("\",\"")
		title,date,website,contentclean = "",'1','',''
		permalink = linev[0]+'_'+linev[1]
		title = linev[2]
		contentclean = linev[4]
		website = title
		articles.append([title,date,permalink,website,categ1,categ2,categ3,contentclean,contentanchor])#sans le html brut
	file.close()
	print "---",len(articles),"posts processed."
	return articles

def utf_weird(content):
	#return content.replace(u'\xc3','').replace(u'\xa8',u'è').replace(u'\xa9',u'é').replace(u'\xa0',u'à').replace(u'\xe9',u'é').replace(u'\xe8',u'è').replace(u'\xaa',u'ê').replace(u'\xa7',u'ç').replace(u'\\u200b',u'').replace(u'\xc3\xa9',u'é').replace(u'\xb4',u'ô').replace(u'xe2',u"'").replace(u'\xef\xac',u"fi").replace(u'\xba',u'ï').replace(u'\xae',u'î').replace(u'\xb9',u'ù')
	return content.replace(u'\xC2\xA1',u'¡').replace(u'\xC2\xA2',u'¢').replace(u'\xC2\xA3',u'£').replace(u'\xC2\xA4',u'¤').replace(u'\xC2\xA5',u'¥').replace(u'\xC2\xA6',u'¦').replace(u'\xC2\xA7',u'§').replace(u'\xC2\xA8',u'¨').replace(u'\xC2\xA9',u'©').replace(u'\xC2\xAA',u'ª').replace(u'\xC2\xAB',u'«').replace(u'\xC2\xAC',u'¬').replace(u'\xC2\xAD',u'­').replace(u'\xC2\xAE',u'®').replace(u'\xC2\xAF',u'¯').replace(u'\xC2\xB0',u'°').replace(u'\xC2\xB1',u'±').replace(u'\xC2\xB2',u'²').replace(u'\xC2\xB3',u'³').replace(u'\xC2\xB4',u'´').replace(u'\xC2\xB5',u'µ').replace(u'\xC2\xB6',u'¶').replace(u'\xC2\xB7',u'·').replace(u'\xC2\xB8',u'¸').replace(u'\xC2\xB9',u'¹').replace(u'\xC2\xBA',u'º').replace(u'\xC2\xBB',u'»').replace(u'\xC2\xBC',u'¼').replace(u'\xC2\xBD',u'½').replace(u'\xC2\xBE',u'¾').replace(u'\xC2\xBF',u'¿').replace(u'\xC3\x80',u'À').replace(u'\xC3\x81',u'Á').replace(u'\xC3\x82',u'Â').replace(u'\xC3\x83',u'Ã').replace(u'\xC3\x84',u'Ä').replace(u'\xC3\x85',u'Å').replace(u'\xC3\x86',u'Æ').replace(u'\xC3\x87',u'Ç').replace(u'\xC3\x88',u'È').replace(u'\xC3\x89',u'É').replace(u'\xC3\x8A',u'Ê').replace(u'\xC3\x8B',u'Ë').replace(u'\xC3\x8C',u'Ì').replace(u'\xC3\x8D',u'Í').replace(u'\xC3\x8E',u'Î').replace(u'\xC3\x8F',u'Ï').replace(u'\xC3\x90',u'Ð').replace(u'\xC3\x91',u'Ñ').replace(u'\xC3\x92',u'Ò').replace(u'\xC3\x93',u'Ó').replace(u'\xC3\x94',u'Ô').replace(u'\xC3\x95',u'Õ').replace(u'\xC3\x96',u'Ö').replace(u'\xC3\x97',u'×').replace(u'\xC3\x98',u'Ø').replace(u'\xC3\x99',u'Ù').replace(u'\xC3\x9A',u'Ú').replace(u'\xC3\x9B',u'Û').replace(u'\xC3\x9C',u'Ü').replace(u'\xC3\x9D',u'Ý').replace(u'\xC3\x9E',u'Þ').replace(u'\xC3\x9F',u'ß').replace(u'\xC3\xA0',u'à').replace(u'\xC3\xA1',u'á').replace(u'\xC3\xA2',u'â').replace(u'\xC3\xA3',u'ã').replace(u'\xC3\xA4',u'ä').replace(u'\xC3\xA5',u'å').replace(u'\xC3\xA6',u'æ').replace(u'\xC3\xA7',u'ç').replace(u'\xC3\xA8',u'è').replace(u'\xC3\xA9',u'é').replace(u'\xC3\xAA',u'ê').replace(u'\xC3\xAB',u'ë').replace(u'\xC3\xAC',u'ì').replace(u'\xC3\xAD',u'í').replace(u'\xC3\xAE',u'î').replace(u'\xC3\xAF',u'ï').replace(u'\xC3\xB0',u'ð').replace(u'\xC3\xB1',u'ñ').replace(u'\xC3\xB2',u'ò').replace(u'\xC3\xB3',u'ó').replace(u'\xC3\xB4',u'ô').replace(u'\xC3\xB5',u'õ').replace(u'\xC3\xB6',u'ö').replace(u'\xC3\xB7',u'÷').replace(u'\xC3\xB8',u'ø').replace(u'\xC3\xB9',u'ù').replace(u'\xC3\xBA',u'ú').replace(u'\xC3\xBB',u'û').replace(u'\xC3\xBC',u'ü').replace(u'\xC3\xBD',u'ý').replace(u'\xC3\xBE',u'þ').replace(u'\xC3\xBF',u'ÿ').replace(u'\xE2\x80\x93',u'--').replace(u'\xE2\x80\x94',u'--').replace(u'\xE2\x80\x98',u'`').replace(u'\xE2\x80\x99',u'\'').replace(u'\xE2\x80\x9C',u"``").replace(u'\xE2\x80\x9D',u"''").replace(u'\xE2\x80\xA6',u'...')
   
def extract_champs_doc(filename):
	#extraction d'un export doctissimo
	articles=[]
	print "    - fichier d'articles: \""+filename+"\"..."
	file=codecs.open(filename,"r","utf8")
	lines = file.readlines()
	i=0
	categ1,categ2,categ3,permalink,contentanchor = '','','','',''
	clause_titre=0
	clause_content=0
	idx = 2
	line = ''
	clause=0
	for lin in lines:
		if lin[:len(str(idx))+2] == '"'+str(idx)+'"':
			clause = 1
		else:
			line = line + lin
		if clause==1:
			line= line.replace("\\n",' ').replace("\n",' ')
			idx = idx+1
			linev= line.split('", "')
			#print linev
			linev[0] = linev[0][1:]
			linev[-1] = linev[-1][:-1]
			
			categ1 = utf_weird(linev[6])
			#rôle du doctinaute
			categ2 = utf_weird(linev[2])
			#nom liste de discussion
			
			title,date,website,contentclean = '',linev[7][:-1],linev[5],linev[9]
			permalink = linev[1]
			contentclean = title +' ; ' +contentclean
			#print unicode(contentclean)
			#contentclean=(contentclean.encode('utf-8','replace'))
			#title=title.encode('utf-8','replace')
			contentclean = utf_weird(contentclean)
			title= str(idx)
			website=utf_weird(website)
			
			#print [contentclean]
			# title=title.replace('’','')
			# 		contentclean=contentclean.replace('’','')
			# 		title=title.replace('“','"')
			# 		contentclean=contentclean.replace('“','"')
			# 		title=title.replace('”','"')
			# 		contentclean=contentclean.replace('”','"')
			# 		title=title.replace('–','-')
			# 		contentclean=contentclean.replace('–','-')
			# 		title=title.replace('/','-')
			# 		contentclean=contentclean.replace('/','-')
			# 		title=title.replace('‘',"'")
			# 		contentclean=contentclean.replace('‘',"'")
			# 		title=title.replace('…',"...")
			# 		contentclean=contentclean.replace('…',"...")
			contentanchor = linev[-1]
			if len(contentanchor)>1:
				contentanchor = "http://forum.doctissimo.fr/" +contentanchor  
			articles.append([title,date,permalink,website,categ1,categ2,categ3,contentclean,website,contentanchor])#sans le html brut
			clause= 0
			line = lin
	file.close()
	print "---",len(articles),"posts processed."
	return articles




def extract_champs_csv(filename):
	articles=[]
	print "    - fichier d'articles: \""+filename+"\"..."
	file=codecs.open(filename,"r","utf8")
	lines = file.readlines()
	i=0
	categ1,categ2,categ3,permalink,contentanchor = '','','','',''
	clause_titre=0
	clause_content=0
	for line in lines[1:]:
		linev= line.split("\t")
		title,date,website,contentclean = "",'1','',''
		permalink = linev[0]
		date = linev[1]
		title = linev[2]
		contentclean = title +' ; ' +linev[3]
		website = linev[4][:-1]
		website=website.encode('utf-8','replace')
		contentclean=contentclean.encode('utf-8','replace')
		title=title.encode('utf-8','replace')
		title=title.replace('’','')
		contentclean=contentclean.replace('’','')
		title=title.replace('“','"')
		contentclean=contentclean.replace('“','"')
		title=title.replace('”','"')
		contentclean=contentclean.replace('”','"')
		title=title.replace('–','-')
		contentclean=contentclean.replace('–','-')
		title=title.replace('/','-')
		contentclean=contentclean.replace('/','-')
		title=title.replace('‘',"'")
		contentclean=contentclean.replace('‘',"'")
		title=title.replace('…',"...")
		contentclean=contentclean.replace('…',"...")
		
		
		articles.append([title,date,permalink,website,categ1,categ2,categ3,contentclean,contentanchor])#sans le html brut
	file.close()
	print "---",len(articles),"posts processed."
	return articles

def extract_champs_html(filename):	
	posts=[]
	print "    - fichier de posts: \""+filename+"\"..."
#	file = open(filename,"r")
	file=codecs.open(filename,"r","utf8")
	line = file.readline()
	newpost=0
	while line != "":
		if (not (len(posts))%50) and (len(posts)>0):
			print "     [#"+str(len(posts)) +"]"
		
		if newpost==0:
			sline = line.split()
			if len(sline)>0:
				if (sline[0]=="<div><b>title:"):
					newpost=1
		if newpost==1:
			#print "--- new post"
			title=file.readline()[12:-14]			
			#print title.encode('utf-8','replace')
			if verbose>0:
				 print "      - post title:",title
			current = file.readline()
			while not "date" in current:
				current = file.readline()
			date=file.readline()[12:-14]
			#print "    - date:",date
			file.readline()
			file.readline() #lf : IGNORED
			file.readline()
			file.readline() #accuracy : IGNORED
			file.readline()
			permalink=file.readline()[12:-14]
			if verbose>2: print "    - permalink:",permalink
			file.readline()
			website=file.readline()[12:-14]
			if verbose>2: print "    - website:",website
			file.readline()
			author=file.readline()[12:-14]
			if verbose>2: print "    - author:",author
			file.readline()
			file.readline() #query: IGNORED
			cur_ligne = file.readline()
			while not "categori" in cur_ligne:
				cur_ligne = file.readline()
			category=file.readline()[12:-14]
			if verbose>2: print "    - category:",category
			categs = category.split('>')
			#now is the content itself
			finished=0
			content=""
			while finished == 0:
				contentline=file.readline()
				if contentline=="": 
					finished=1
					line=""
				scontentline=contentline.split()
				if len(scontentline)>0: 
					if scontentline[0]=="<div><b>title:": finished=1
				if finished==0: content+=contentline
			content=content.replace("\n"," ").replace("\r"," ").replace("<b>content: </b>       ","").replace("      <div>","")
			categ1 = categs[0].replace(' ','')
			categ2 = categs[1].replace(' ','')
			categ3 = categs[2].replace(' ','')
			if verbose>1: print "    - content:",content
			contentclean=specialutf8(cleancontent(content.replace("</span>"," ").replace("</hr>"," ").replace("</li>"," ").replace("</a>"," ").replace("</br>"," ").replace("</div>"," ").replace("</p>"," ").replace("<hr />"," ").replace("</h1>"," ").replace("</h3>"," ").replace("</h4>"," ").replace("</h5>"," ").replace("</img>"," ")))
			title= specialutf8(title)
			if verbose>1: print "    - clean content:",contentclean
			contentanchor=detecthref(content)			
			if verbose>1: print "    - anchor content:",contentanchor
			title =title.encode('utf-8','replace')
			content =content.encode('utf-8','replace')
			contentclean =contentclean.encode('utf-8','replace')
			date=date.encode('utf-8','replace')
			permalink = permalink.encode('utf-8','replace')
			categ1=categ1.encode('utf-8','replace')
			categ2=categ2.encode('utf-8','replace')
			categ3=categ3.encode('utf-8','replace')
			contentanchor =contentanchor.encode('utf-8','replace')
			#posts.append([title,date,permalink,website,categ1,categ2,categ3,content,contentclean,contentanchor])#avec le html brut
			posts.append([title,date,permalink,website,categ1,categ2,categ3,contentclean,contentanchor])#sans le html brut
			newpost = 0
		else: 
			line = file.readline()
	file.close()

	print "---",len(posts),"posts processed."
#	print "    - such as: ",posts[0]
	return posts



def extract_champs_xml(filename):	
	posts=[]
	print "    - fichier de posts: \""+filename+"\"..."
	file=open(filename,"r")
	line = file.readline()
	newpost=0
	while "</posts>" not in line:
		if (not (len(posts))%50) and (len(posts)>0):
			print "     [#"+str(len(posts)) +"]"
			
		if newpost==0:
			sline = line.split()
			if len(sline)>0:
				if (sline[0]=="<post>"):
					newpost=1
				else:
					line = file.readline()			
					
		if newpost==1:
			current = file.readline()
			while not "date" in current:
				current = file.readline()
			date=current[8:16]
			date = date[:4] + '-' + date[4:6] + '-' + date[6:] + ' '
			
			file.readline()
			current = file.readline()
			categ1 = current[10:-8]
			
			current = file.readline()
			categ2 = current[10:-8]
			
			current = file.readline()
			categ3 = current[10:-8]
			
			file.readline()
			file.readline()
			file.readline()
			file.readline()
			current= file.readline()
			permalink  = unicode(current[13:-13],'utf-8')
			file.readline()
			current= file.readline()
			website = unicode(current[8:-8],'utf-8')
			finished=0
			content=''
			title = ''
			while finished == 0:
				contentline=file.readline()
				scontentline=contentline.split('>')
				if len(scontentline)>0: 
					if scontentline[0]=="  <title": 
						finished=1
						u=unicode(contentline[9:-9],'utf-8')
						title = u.encode("latin-1")
						content = title + ' . ' + content.encode('utf-8') 
				#		print "title "+ title
				if finished==0: content+=unicode(contentline,'utf-8')
			
			content = content.decode('utf-8','replace')
			#title = title.decode('utf-8','replace')
			content=content.replace("\n"," ").replace("\r"," ").replace("<b>content: </b>       ","").replace("      <div>","")
			print "title " + title
			if verbose>1: print "    - content:",content
			contentclean=specialutf8(cleancontent(content.replace("</span>"," ").replace("</hr>"," ").replace("</li>"," ").replace("</a>"," ").replace("</br>"," ").replace("</div>"," ").replace("</p>"," ").replace("<hr />"," ").replace("</h1>"," ").replace("</h3>"," ").replace("</h4>"," ").replace("</h5>"," ").replace("</img>"," ")))
			#title= specialutf8(title)
			if verbose>1: print "    - clean content:",contentclean
			contentanchor=detecthref(content)			
			if verbose>1: print "    - anchor content:",contentanchor
#			title =title.encode('utf-8','replace')
			content =content.encode('utf-8','replace')
			contentclean =contentclean.encode('utf-8','replace')
			date=date.encode('utf-8','replace')
			permalink = permalink.encode('utf-8','replace')
			categ1=categ1.encode('utf-8','replace')
			categ2=categ2.encode('utf-8','replace')
			categ3=categ3.encode('utf-8','replace')
			contentanchor =contentanchor.encode('utf-8','replace')
			#posts.append([title,date,permalink,website,categ1,categ2,categ3,content,contentclean,contentanchor])#avec le html brut
			posts.append([title,date,permalink,website,categ1,categ2,categ3,contentclean,contentanchor])#sans le html brut
			newpost = 0
			line = current
		else: 
			line = file.readline()			
	file.close()

	print "---",len(posts),"posts processed."
#	print "    - such as: ",posts[0]
	return posts
	

def extract_champs_txt(filename):	
	posts=[]
	print "    - post file \""+filename+"\"..."
	file=codecs.open(filename,"r","utf8")
	line = " "
	newpost=0
	while not line =='':
		if not (len(posts))%50:
			print "     [#"+str(len(posts)) +"]"
		if newpost==0:
			line = file.readline()
			sline = line.split()
			if len(sline)>0:
				if (sline[0]=="title:"):
					newpost=1
			
		if newpost==1:
			title=line[7:-1]
			if verbose>0:
				 print "      - post title:",title
			cur_ligne = ''
			while not "date" in cur_ligne:
				cur_ligne = file.readline()
			date=cur_ligne[6:-1]
			if verbose>0:
				print "    - date:",date
			#file.readline()
			file.readline() #lf : IGNORED
			#file.readline()
			file.readline() #accuracy : IGNORED
			#file.readline()
			
			permalink=file.readline()[11:-1]
			if verbose>2: print "    - permalink:",permalink
			#file.readline()
			website=file.readline()[9:-1]
			if verbose>2: print "    - website:",website
			#file.readline()
			author=file.readline()[8:-1]
			if verbose>2: print "    - author:",author
			#file.readline()
			file.readline() #query: IGNORED
			#file.readline()
			cur_ligne = ''
			while not "categorie" in cur_ligne:
				cur_ligne = file.readline()
				#print cur_ligne
			category=cur_ligne[12:]
			if verbose>2: print "    - category:",category
			categs = category.split('>')
			#now is the content itself
			finished=0
			content=""
			while finished == 0:
				contentline=file.readline()
				if"========" in contentline:
					finished=1
				scontentline=contentline.split()
				if len(scontentline)>0: 
					if scontentline[0]=="title:": finished=1
				if finished==0: content+=contentline
			content=content.replace("\n"," ").replace("\r"," ").replace("content:","")
			categ1 = categs[0].replace(' ','')
			categ2 = categs[1].replace(' ','')
			categ3 = categs[2].replace(' ','')

			if verbose>1: print "    - content:",content
			contentclean=cleancontent(content.replace("</span>"," ").replace("</hr>"," ").replace("</li>"," ").replace("</a>"," ").replace("</br>"," ").replace("</div>"," ").replace("</p>"," ").replace("<hr />"," ").replace("</h1>"," ").replace("</h3>"," ").replace("</h4>"," ").replace("</h5>"," ").replace("</img>"," "))
			if verbose>1: print "    - clean content:",contentclean
			contentanchor=detecthref(content)			
			if verbose>1: print "    - anchor content:",contentanchor
			contentclean =contentclean.encode('utf-8','replace')
			title =title.encode('utf-8','replace')
			content =content.encode('utf-8','replace')
			date=date.encode('utf-8','replace')
			permalink = permalink.encode('utf-8','replace')
			categ1=categ1.encode('utf-8','replace')
			categ2=categ2.encode('utf-8','replace')
			categ3=categ3.encode('utf-8','replace')
			contentanchor =contentanchor.encode('utf-8','replace')
			#posts.append([title,date,permalink,website,categ1,categ2,categ3,content,contentclean,contentanchor])#avec le html brut
			posts.append([title,date,permalink,website,categ1,categ2,categ3,contentclean,contentanchor])#sans le html brut			
			newpost = 0
	file.close()

	print "---",len(posts),"posts processed."
#	print "    - such as: ",posts[0]
	return posts

def extract_champs_rss(rss_url,sep):
	#web importer
	import feedparser
	from BeautifulSoup import BeautifulSoup
	hexentityMassage = copy.copy(BeautifulSoup.MARKUP_MASSAGE)
	hexentityMassage = [(re.compile('&#x([^;]+);'), lambda m: '&#%d' % int(m.group(1), 16))]
	
	liste_flux = open(rss_url,'r')
	posts=[]
	for flux in liste_flux.readlines():
		if len(flux)>1:
			rss_url=flux[:-1]
	
			feed = feedparser.parse( rss_url )
			taille_flux=len(feed[ "items" ])

			print rss_url + ', ' + str(taille_flux) + ' ' +'billets references dans le flux.'
			for i in range(taille_flux):
				e= feed.entries[i]
				try:
					content= e.content[0].value
					contentclean=repr(convert(content))
				except:
					content= e.description
					contentclean = content
				#print content
				#feed["items"][i]['content'][0]['value']
				#content=content.replace("\n"," ").replace("\r"," ").replace("<b>content: </b>       ","").replace("      <div>","")
				#contentclean=repr(convert(specialutf8(cleancontent(content.replace("</span>"," ").replace("</hr>"," ").replace("</li>"," ").replace("</a>"," ").replace("</br>"," ").replace("</div>"," ").replace("</p>"," ").replace("<hr />"," ").replace("</h1>"," ").replace("</h3>"," ").replace("</h4>"," ").replace("</h5>"," ").replace("</img>"," ")))))
				
#				maladie le 7 août 2010 à l’'âge de 80 ans
				
				contentclean=specialutf8(contentclean)
				title =  e.title
				
				encoding = feed.encoding
				day = e.updated_parsed.tm_yday 
				try:
					permalink = e.links[0].href
				except:
					permaling = ''
				contentclean=specialutf8(cleancontent(content))
				href = ''
				#unicode(title) +'***'+ unicode(
				posts.append([unicode(title),str(day),permalink,rss_url,'','','',contentclean,'rss_url',href])
	return posts 
	
	
def extraire_donnees(name_data,sep):
	if ".txt" == name_data[-4:]:#export au format .txt
		champs = extract_champs_txt(name_data)
	if ".xml" == name_data[-4:]:#export au format .xml
		champs = extract_champs_xml(name_data)
	if ".html" == name_data[-5:]:#export au format .html
		champs = extract_champs_html(name_data)
	if ".med" == name_data[-4:]:#export au format .medline
		champs = extract_champs_medline(name_data,sep)
	if ".fet" == name_data[-4:]:#export au format .fet
		champs = extract_champs_fet(name_data)
	if ".isi" == name_data[-4:]:#export au format .isi wos
		champs = extract_champs_isi(name_data,sep)
	if ".csv" == name_data[-4:]:#export au format .csv andrei, projet jobs.
		champs = extract_champs_csv(name_data)
	if ".lfl" == name_data[-4:]:#export au format .lfl: linkfluence type III ou IV
		try:
			continent = parameters.continent
		except:
			continent =''
		champs = extract_champs_lfl(name_data,sep,continent)
	if ".rss" == name_data[-4:]:#export au format .lfl: linkfluence type III ou IV
		champs = extract_champs_rss(name_data,sep)
	if ".isy" == name_data[-4:]:#export au format .lfl: linkfluence type III ou IV
		champs = extract_champs_isy(name_data,sep)

	if ".doc" == name_data[-4:]:#export au format .doc: export doctissimo
		champs = extract_champs_doc(name_data)

	return champs


#--------------------------------------------------------
#--------------------------------------------------------
#----- INITIALISATION DE LA BIBLIOTHEQUE parseur.py -----
#--------------------------------------------------------
#--------------------------------------------------------


#print "--- initialisation de \"parseur.py\"..."
verbose=0
if verbose>0:
	display="post title"
	if verbose>1:
		display+=", content, clean content, anchor content"
	if verbose>2:
		display+=", permalink, website, author, category"
	print "--- verbose level:",verbose,"\n    - displaying:",display
#print "    - \"parseur.py\" initialise.\n"

