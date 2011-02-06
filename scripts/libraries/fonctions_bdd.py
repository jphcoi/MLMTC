# -*- coding: utf-8 -*-
#!/usr/bin/python
import sqlite3
#from pysqlite2 import dbapi2 as sqlite
#from pysqlite2 import test
from datetime import datetime
import parseur

def connexion(name_bdd):
	connection = sqlite3.connect(name_bdd)
	cursor = connection.cursor()
	ex = connection.execute
	return connection,ex


###################################
#######creation des tables#########
###################################

def drop_table(name_bdd,name_table):
	connection,ex = connexion(name_bdd)
	ex('DROP TABLE '+name_table)
	connection.commit()
	connection.close()
	
def insert_select(name_bdd,name_table1,name_table2,requete):
	connection,ex = connexion(name_bdd)
	sql ="INSERT INTO " + name_table2 + " SELECT * FROM " + name_table1 + " WHERE " + requete
	ex(sql)
	connection.commit()
	connection.close()

def insert_select_substring(name_bdd,name_table1,name_table2,entree,champ):
	connection,ex = connexion(name_bdd)
	for x in entree:
		idx = x[0]
		n = x[1]
		requete = ' id = '+str(idx)
		sql ="UPDATE " + name_table2 + ' SET ' +champ  + "= (SELECT SUBSTR(" + champ + ",0," + str(n)+ ") FROM " + name_table1 + " WHERE " + requete  + ") WHERE " + requete
		print sql
		ex(sql)
	connection.commit()
	connection.close()


def creer_table_billets(name_bdd,name_table):
	connection,ex = connexion(name_bdd)
	try:
		ex('CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,title text, date datetime, permalink VARCHAR(1000), site VARCHAR(1500), auteur_id VARCHAR(300), categorie1 VARCHAR(200), categorie2 VARCHAR(200), categorie3 VARCHAR(200), categorie4 VARCHAR(200), categorie5 VARCHAR(200),content_lemmatise text, content text, href text, jours INTEGER, concepts text,identifiant_unique VARCHAR(2000) unique,requete VARCHAR(200))')
		print "    + table (billets) \"" +name_table+"\" creee"
	except:
		print "    * table (billets) \"" +name_table+"\" deja creee"
		pass
	connection.commit()
	connection.close()

def creer_table_auteurs(name_bdd,name_table):
	connection,ex = connexion(name_bdd)
	try:
#		print 'CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,auteurs VARCHAR(200) unique )'
		ex('CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,auteurs VARCHAR(200) unique)')
		print "    + table (auteurs) \"" +name_table+"\" creee"
	except:
		print "    * table (auteurs) \"" +name_table+"\" deja creee"
		pass
	connection.commit()
	connection.close()

def creer_table_term_neighbor(name_bdd,name_table):
	connection,ex = connexion(name_bdd)
	try:
#		print 'CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,term1 VARCHAR(10), term2 VARCHAR(10), distance text)'
		ex('CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,term1 VARCHAR(10), term2 VARCHAR(10), distances text, force_moy FLOAT, direction INTEGER )')
	except:
		print "    * table (term_neighbor) \"" +name_table+"\" deja creee"
		pass
	connection.commit()
	connection.close()
	
def creer_table_concepts(name_bdd,name_table):
	connection,ex = connexion(name_bdd)
	if 1:
		print 'CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,concepts VARCHAR(5000) unique,forme_principale VARCHAR(400) )'
		ex('CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,concepts VARCHAR(5000) unique,forme_principale VARCHAR(400) )')
		print "    + table (concepts) \"" +name_table+"\" creee"
	#except:
	#	print "    * table (concepts) \"" +name_table+"\" deja creee"
	#	pass
	connection.commit()
	connection.close()


def creer_table_sociosem(name_bdd,name_table):
	connection,ex = connexion(name_bdd)
	try:
#		print 'CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,auteurs VARCHAR(200) unique )'
		ex('CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,auteur INTEGER,concept INTEGER,jours INTEGER, id_b INTEGER,requete VARCHAR(200),identifiant_unique VARCHAR(20) unique )')
		print "      + table (sociosem) \"" +name_table+"\" creee"
	except:
		print "      * table (sociosem) \"" +name_table+"\" deja creee"
		pass
	connection.commit()
	connection.close()

def creer_table_soc(name_bdd,name_table):
	connection,ex = connexion(name_bdd)
	try:
#		print 'CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,auteurs VARCHAR(200) unique )'
		ex('CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,auteur1 INTEGER,auteur2 INTEGER,jours INTEGER,id_b INTEGER,requete VARCHAR(200),identifiant_unique VARCHAR(20) unique)')
		print "      + table (soc) \"" +name_table+"\" creee"
	except:
		print "      * table (soc) \"" +name_table+"\" deja creee"
		pass
	connection.commit()
	connection.close()

def creer_table_sem(name_bdd,name_table):
	connection,ex = connexion(name_bdd)
	try:
#		print 'CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,auteurs VARCHAR(200) unique )'
		ex('CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,concept1 INTEGER,concept2 INTEGER,jours INTEGER,id_b INTEGER,requete VARCHAR(200),identifiant_unique VARCHAR(20) unique)')
		print "      + table (sem) \"" +name_table+"\" creee"
	except:
		print "      * table (sem) \"" +name_table+"\" deja creee"
		pass
	connection.commit()
	connection.close()

def creer_table_sem_periode_valuee(name_bdd,name_table):
	connection,ex = connexion(name_bdd)
	try:
#		print 'CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,auteurs VARCHAR(200) unique )'
		ex('CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,concept1 INTEGER,concept2 INTEGER,periode INTEGER,cooccurrences INTEGER,distance0 float,distance1 float)')
		print "      + table (sem_weighted) \"" +name_table+"\" creee"
	except:
		print "      * table (sem_weighted) \"" +name_table+"\" deja creee"
		pass
	connection.commit()
	connection.close()



def creer_table_concept2billets(name_bdd,name_table):
	connection,ex = connexion(name_bdd)
	try:
#		print 'CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,auteurs VARCHAR(200) unique )'
		ex('CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,concept INTEGER,id_b INTEGER,jours INTEGER,requete VARCHAR(200),identifiant_unique VARCHAR(20) unique)')
		print "      + table (concept2billets) \"" +name_table+"\" creee"
	except:
		print "      * table (concept2billets) \"" +name_table+"\" deja creee"
		pass
	connection.commit()
	connection.close()


def creer_table_cluster(name_bdd,name_table):
	connection,ex = connexion(name_bdd)
	try:
		#print 'CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,id_cluster_univ INTEGER ,id_cluster INTEGER,label_1 INTEGER,label_2 INTEGER,label VARCHAR(300),attribut VARCHAR(300),level INTEGER, periode VARCHAR(50),concept INT, pseudo VARCHAR(10), cluster_size INT, density VARCHAR(10), nb_fathers INT, nb_sons INT, lettre VARCHAR(3), identifiant_unique VARCHAR(20))'
		ex('CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,id_cluster_univ INTEGER ,id_cluster INTEGER,label_1 INTEGER,label_2 INTEGER,label VARCHAR(300),attribut VARCHAR(300),level INTEGER,periode VARCHAR(50),concept INT, pseudo VARCHAR(10), cluster_size INT, density VARCHAR(10), nb_fathers INT, nb_sons INT, lettre VARCHAR(3), identifiant_unique VARCHAR(20))')
		print "      + table  \"" +name_table+"\" creee"
	except:
		print "      * table \"" +name_table+"\" deja creee"
		pass
	connection.commit()
	connection.close()

def creer_table_phylo(name_bdd,name_table):
	connection,ex = connexion(name_bdd)
	try:
		#print 'CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,id_cluster_1 INTEGER,periode_1 VARCHAR(50),id_cluster_1_univ INTEGER,id_cluster_2 INTEGER,periode_2 VARCHAR(50),id_cluster_2_univ INTEGER,strength VARCHAR(10))'
		ex('CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,id_cluster_1 INTEGER,periode_1 VARCHAR(50),id_cluster_1_univ INTEGER,id_cluster_2 INTEGER,periode_2 VARCHAR(50),id_cluster_2_univ INTEGER,strength VARCHAR(10))')
		print "      + table  \"" +name_table+"\" creee"
	except:
		print "      * table \"" +name_table+"\" deja creee"
		pass
	connection.commit()
	connection.close()

def creer_table_map(name_bdd,name_table):
	connection,ex = connexion(name_bdd)
	try:
		#print 'CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,id_cluster_1 INTEGER,periode_1 VARCHAR(50),id_cluster_1_univ INTEGER,id_cluster_2 INTEGER,periode_2 VARCHAR(50),id_cluster_2_univ INTEGER,strength VARCHAR(10))'
		ex('CREATE TABLE '+ name_table +' (id INTEGER PRIMARY KEY,id_cluster_1 INTEGER,periode_1 VARCHAR(50),id_cluster_1_univ INTEGER,id_cluster_2 INTEGER,periode_2 VARCHAR(50),id_cluster_2_univ INTEGER,strength VARCHAR(10))')
		print "      + table  \"" +name_table+"\" creee"
	except:
		print "      * table \"" +name_table+"\" deja creee"
		pass
	connection.commit()
	connection.close()

###################################
#######opération sur  tables#######
###################################

def add_column(name_bdd,name_table,name_col,col_type):
	connection,ex = connexion(name_bdd)
	ex('ALTER TABLE '+ name_table + ' ADD ' + name_col + ' ' + col_type )
	print "    - colonne \"" + name_col +"\" creee dans la table " +name_table
	connection.commit()
	connection.close()
	
def renommer_table(name_bdd,table1,table2):
	connection,ex = connexion(name_bdd)
	ex('ALTER table '+table1+' RENAME TO ' +table2)
	connection.commit()
	connection.close()

def detruire_table(name_bdd,table):
	connection,ex = connexion(name_bdd)
	ex('DROP table '+table)
	connection.commit()
	connection.close()

def select_bdd_table_champ(name_bdd,table,champ,champ2,b_id):
	connection,ex = connexion(name_bdd)
#	print "SELECT "  + champ +  "   from " +table +" WHERE "+ champ2 +" = \'" +str(b_id)+ "\'" 	
	sortie= ex("SELECT "  + champ +  "   from " +table +" WHERE "+ champ2 +" = \'" +str(b_id)+ "\'" ).fetchall()
	connection.commit()
	connection.close()
	return sortie[0][0]

def select_bdd_table_champ_complet(name_bdd,table,champ,champ2,b_id):
	connection,ex = connexion(name_bdd)
#	print "SELECT "  + champ +  "   from " +table +" WHERE "+ champ2 +" = \'" +str(b_id)+ "\'" 	
	print "SELECT "  + champ +  "   from " +table +" WHERE "+ champ2 +" = \'" +str(b_id)+ "\'" 
	sortie= ex("SELECT "  + champ +  "   from " +table +" WHERE "+ champ2 +" = \'" +str(b_id)+ "\'" ).fetchall()
	connection.commit()
	connection.close()
	return sortie


def select_bdd_table_champ(name_bdd,table,champ,champ2,b_id):
	connection,ex = connexion(name_bdd)
#	print "SELECT "  + champ +  "   from " +table +" WHERE "+ champ2 +" = \'" +str(b_id)+ "\'" 	
	sortie= ex("SELECT "  + champ +  "   from " +table +" WHERE "+ champ2 +" = \'" +str(b_id)+ "\'" ).fetchall()
	connection.commit()
	connection.close()
	return sortie[0][0]
	
def select_bdd_table_champ_complet(name_bdd,table,champ):
	connection,ex = connexion(name_bdd)
#	print "SELECT "  + champ +  "   from " +table +" WHERE "+ champ2 +" = \'" +str(b_id)+ "\'" 	
	sortie= ex("SELECT "  + champ +  "   from " +table  ).fetchall()
	connection.commit()
	connection.close()
	return sortie
	
def count_rows(name_bdd,table):
	connection,ex = connexion(name_bdd)
	sortie= ex("SELECT COUNT(*)  from " +table).fetchall()
	#print '\n' + "comptage de l evolution du nombre de " +champ_nom + " "+ str(champ_val) + " de la table " + table +  " dans la bdd " +name_bdd +'\n'
	connection.close()	
	return sortie[0][0]

def count_champ(name_bdd,table,champ_nom,champ_val):
	connection,ex = connexion(name_bdd)
#	print "SELECT jours,COUNT(*)  from " +table +" WHERE " +champ_nom+ " = " +str(champ_val) +" GROUP BY " +' jours '	
	sortie= ex("SELECT jours,COUNT(*)  from " +table +" WHERE " +champ_nom+ " = " +str(champ_val) +" GROUP BY " +' jours ').fetchall()
	print '\n' + "comptage de l evolution du nombre de " +champ_nom + " "+ str(champ_val) + " de la table " + table +  " dans la bdd " +name_bdd +'\n'
	connection.close()	
	return sortie



def count_rows_where(name_bdd,table,where):
	connection,ex = connexion(name_bdd)
	print "SELECT COUNT(*)  from " +table + ' ' + where
	
	sortie= ex("SELECT COUNT(*)  from " +table + ' ' + where).fetchall()
	#print '\n' + "comptage de l evolution du nombre de " +champ_nom + " "+ str(champ_val) + " de la table " + table +  " dans la bdd " +name_bdd +'\n'
	connection.close()
	return sortie[0][0]

def count(name_bdd,table):
	connection,ex = connexion(name_bdd)
	sortie= ex("SELECT jours,COUNT(*)  from " +table +" GROUP BY " +' jours ').fetchall()
	print '\n' + "comptage de l evolution du nombre de  champs  de la table " + table +  " dans la bdd " +name_bdd +'\n'
	connection.close()	
	return sortie

def delete_field(name_bdd,table,id_b):
	connection,ex = connexion(name_bdd)
	ex("DELETE from " +table +" WHERE id=\'" + str(id_b)+"\'")
	connection.commit()
	connection.close()	

	
def select_bdd_table_champ_simple(name_bdd,table,champ, where = ' where 1'):
	print name_bdd
	if not 'where' in where:
		where = "where " + where 
	connection,ex = connexion(name_bdd)
	sortie= ex("SELECT "  + champ +  "   from " +table + ' '  + where ).fetchall()
	#print "       - selection du/des champ(s) \"" + champ + "\" de la table \"" + table + "\" dans la BDD " +name_bdd
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
			#print soso
	connection.commit()
	connection.close()	
	return sortie_ok
	


def filtre_requete_base(filename_req):
	file = codecs.open(filename_req,'r','utf-8')
	terme1 = u'santé'
	terme2 =u'environnement'
	commandesql = " (content LIKE '% "+ terme1.encode('utf-8') + "%' AND content LIKE '% "+ terme2.encode('utf-8') + "%') " 
	for line in file.readlines():
		line = line.encode('utf-8')[:-1]
		machin = line.replace("\'","popostrophe")
		commandesql = commandesql  + ' OR ' + "content LIKE  '% " + machin +" %' "
	print "                  requete reduite "  + commandesql 
	return commandesql




def select_bdd_table_where_limite(name_bdd,table,champ,sample,requete,where,limit,Nb_rows):
	connection,ex = connexion(name_bdd)
#	print "SELECT "  + champ +  "   from " +table +" ORDER by RAND()  LIMIT "+str(sample) +" WHERE " + "requete = \'" +requete+ "\' AND " + str(where)  + ' LIMIT '+str(limit)
	if sample<Nb_rows:
		sortie= ex("SELECT "  + champ +  "   from " +table  + " WHERE " + str(where)  +" ORDER by RANDOM()   LIMIT "+str(sample)).fetchall()
	else:
		sortie= ex("SELECT "  + champ +  "   from " +table  +" WHERE " + str(where)  +"   LIMIT "+str(limit)).fetchall()
	#print "       - selection du/des champ(s) " + champ + " de la table " + table +  " dans la bdd " +name_bdd + " avec la requete " +requete
	sortie_ok = []
#	print "---------nombre de billets traités " + str(len(sortie))
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
			#print soso
	connection.commit()
	connection.close()	
	return sortie_ok
		
			
def select_bdd_table(name_bdd,table,champ,requete=''):
	connection,ex = connexion(name_bdd)
	sortie= ex("SELECT "  + champ +  "   from " +table ).fetchall()
	#print "       - selection du/des champ(s) " + champ + " de la table " + table +  " dans la bdd " +name_bdd + " avec la requete " +requete
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

def select_bdd_table_limite(name_bdd,table,champ,requete,limit):
	connection,ex = connexion(name_bdd)
	sortie= ex("SELECT "  + champ +  "   from " +table + ' LIMIT '+str(limit) ).fetchall()
	#print "SELECT "  + champ +  "   from " +table +" WHERE requete = \'" +requete+ "\'"+ ' LIMIT '+str(limit)
	#print "SELECT "  + champ +  "   from " +table +" WHERE requete = \'" +requete+ "\'"+ ' LIMIT '+str(limit) 
	#print "       - selection du/des champ(s) " + champ + " de la table " + table +  " dans la bdd " +name_bdd + " avec la requete " +requete
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
			#print soso
	connection.commit()
	connection.close()	
	return sortie_ok


def select_bdd_table_limit(name_bdd,table,champ,requete,limit):
	connection,ex = connexion(name_bdd)
	sortie= ex("SELECT "  + champ +  "   from " +table + " LIMIT " + str(limit) ).fetchall()
	#print "       - selection du/des champ(s) " + champ + " de la table " + table +  " dans la bdd " +name_bdd + " avec la requete " +requete
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
			#print soso
	connection.commit()
	connection.close()	
	return sortie_ok


def afficher_bdd_table(name_bdd,table, champ,requete):
	sortie = select_bdd_table(name_bdd,table,champ,requete)
	print sortie
	


def remplir_table_billets_lfl(name_bdd,name_table,champs_liste,champs_name,requete):
	connection, ex = connexion(name_bdd)
#	champs_name = "(title,date,permalink,site,categorie1,categorie2,categorie3,content,href,requete,identifiant_unique)"#on n'enregistre pas le html brut
#title,datet,permalink,url,continent,community,territory,content,author
	for champ in champs_liste:
		champ[8]=requete
		id_unique=champ[0]+'_'+champ[3]
		champ.append(id_unique)
		ex("INSERT OR IGNORE INTO billets (title, date,permalink,site,categorie1,categorie2,categorie3,content,requete,href,identifiant_unique) VALUES (?,?,?,?,?,?,?,?,?,?,?)", champ)
	connection.commit()
	connection.close()
	print "    + table \"" + name_table+"\" remplie"


def remplir_table_billets_propre(name_bdd,name_table,champs_liste,champs_name,requete):
	connection, ex = connexion(name_bdd)
	for champ in champs_liste:
		champ.append(champ[2])
		#title,date,permalink,website,categ1,categ2,categ3,contentclean,contentanchor
		ex("INSERT OR IGNORE INTO billets (title, date,permalink,site,categorie1,categorie2,categorie3,content,requete,identifiant_unique) VALUES (?,?,?,?,?,?,?,?,?,?)", champ)
	connection.commit()
	connection.close()
	print "    + table \"" + name_table+"\" remplie"

def remplir_table_billets_propre4(name_bdd,name_table,champs_liste,champs_name,requete):
	connection, ex = connexion(name_bdd)
	for champ in champs_liste:
		champ.append(champ[2])
		#title,date,permalink,website,categ1,categ2,categ3,contentclean,contentanchor
		ex("INSERT OR IGNORE INTO billets (title, date,permalink,site,categorie1,categorie2,categorie3,categorie4,content,requete,identifiant_unique) VALUES (?,?,?,?,?,?,?,?,?,?,?)", champ)
	connection.commit()
	connection.close()
	print "    + table \"" + name_table+"\" remplie"


def remplir_table_billets(name_bdd,name_table,champs_liste,champs_name,requete):
	connection, ex = connexion(name_bdd)
#	champs_name = "(title,date,permalink,site,categorie1,categorie2,categorie3,content_html,content,href,requete,identifiant_unique)"#on enregistre le html brut
	champs_name = "(title,date,permalink,site,categorie1,categorie2,categorie3,content,href,requete,identifiant_unique)"#on n'enregistre pas le html brut
	
	#verif des doublons
	#champs : ['TI','PY','DI','AU','CT','ID','DE','AB','CR','UT']
	#isi_un=[]
	#auteur_source_annee_titre=[]

	for champ in champs_liste: 
		# if not champ[-1] in isi_un:
		# 		isi_un.append(champ[6])
		# 	auteur_source_annee_titre_val = champ[3] + '_' + champ[4] + '_' +champ[1] + '_' + champ[0]
		# 	if  not auteur_source_annee_titre_val in auteur_source_annee_titre:
		# 		auteur_source_annee_titre.append(auteur_source_annee_titre_val)
		# 	else:
		# 		print auteur_source_annee_titre_val
		try:
			champ_sql = ''
			for ch in champ:
				chaine=(ch.replace("'","popostrophe"))
				chaine = str(chaine)
				champ_sql = champ_sql + '\'' +chaine +   '\'' + ','
			champ_sql = champ_sql +     '\'' +requete +   '\'' 
			if ".isi" in name_bdd or ".isy" in name_bdd :
				#version isi pour éliminer les doublons à partir de la liste des identifiants isi: isi:a1996ur12500023
				champ_sql = champ_sql + ','+    '\'' +champ[6] +   '\'' 
			else:
				if not '.db' in name_bdd:
					champ_sql = champ_sql + ','+    '\'' +champ[1].replace("'","popostrophe")+'_'+champ[2].replace("'","popostrophe") +'_'+ requete  +   '\'' 
				else:
					champ_sql = champ_sql + ','+    '\'' +champ[2].replace("'","popostrophe") +   '\'' 
			values = " VALUES (" +str(champ_sql) + ')'
			commandesql = "INSERT OR IGNORE INTO billets " + champs_name + values
			ex(commandesql)
			#print commandesql
			#print 'youpi'
			
		except:
			#print champ
			print "il y a un  probleme d'encodage pour remplir la table billets"
	connection.commit()
#	print str(len(isi_un)) + ' numeros isi uniques'
#	print str(len(auteur_source_annee_titre)) + ' auteur_source_annee_titre dans la base '

	connection.close()
	print "    + table \"" + name_table+"\" remplie"
	
	#ex("INSERT OR IGNORE INTO billets (title, permalink, content) VALUES (?,?,?)", (champ[1],champ[-1],champ[-2]))


# def remplir_table_billets(name_bdd,name_table,champs_liste,champs_name,f):
# 	connection, ex = connexion(name_bdd)
# #	champs_name = "(title,date,permalink,site,categorie1,categorie2,categorie3,content,href,requete,identifiant_unique)"#on n'enregistre pas le html brut
# #title,datet,permalink,url,continent,community,territory,content,author
# 	for champ in champs_liste:
# 		champ[8]=requete
# 		id_unique=champ[0]+'_'+champ[3]
# 		champ.append(id_unique)
# 		ex("INSERT OR IGNORE INTO billets (title, date,permalink,site,categorie1,categorie2,categorie3, content,requete,href,identifiant_unique) VALUES (?,?,?,?,?,?,?,?,?,?,?)", champ)
# 	connection.commit()
# 	connection.close()
# 	print "    + table \"" + name_table+"\" remplie"


	
def isList(obj):
   """isList(obj) -> Returns true if obj is a Python list.

      This function does not return true if the object supplied
      is a UserList object.
   """
   return type(obj)==type([1,2])

def istuple(obj):
   """isList(obj) -> Returns true if obj is a Python list.

      This function does not return true if the object supplied
      is a UserList object.
   """
   return type(obj)==type((1,2))


def remplir_table(name_bdd,name_table,champs_liste,champs_name):
	connection, ex = connexion(name_bdd)
#	champs_name = "(title,date,permalink,site,categorie1,categorie2,categorie3,content_html,content,href,requete,identifiant_unique)"#,content,href,concepts)
	for champ in champs_liste: 
		champ_sql = ''
	#	print champ
		if isList(champ) or istuple(champ):
			for chaine in champ:
				if not type(chaine)==type(5):
					if "\'" in chaine:
						chaine=(chaine.replace("\'","popostrophe"))
					chaine = str(chaine)					
				else:
					chaine = str(chaine)
				champ_sql = champ_sql + '\'' +chaine +   '\'' + ','
		else:
			chaine=(champ.replace("\'","popostrophe"))
			chaine = str(chaine)
			champ_sql = champ_sql + '\'' +chaine +   '\'' + ','
		values = " VALUES (" +str(champ_sql[:-1]) + ')'
		commandesql = "INSERT OR IGNORE INTO  " +name_table +' '+ champs_name + values
		ex(commandesql)
	connection.commit()
	connection.close()
	print "      + table " + name_table+" remplie"



def remplir_table_propre(name_bdd,name_table,champs_liste,champs_name):
	connection, ex = connexion(name_bdd)
	insert_cols = ", ".join (champs_name)
	insert_qmarks = ", ".join ("?" for _ in champs_liste[0])
	
	for champ in champs_liste:
		sql = "INSERT OR IGNORE  INTO  "+ name_table +  " (%s) VALUES (%s)" % ( insert_cols,insert_qmarks)
		ex(sql,champ)
	connection.commit()
	connection.close()
	print "    + table \"" + name_table+"\" remplie"

#		ex("INSERT OR IGNORE INTO billets (title, date,permalink,site,categorie1,categorie2,categorie3,categorie4,content,requete,identifiant_unique) VALUES (?,?,?,?,?,?,?,?,?,?,?)", champ)


def update_multi_table(name_bdd,name_table,champs_name,champs_liste):
	"remplit la colonne champ_name d'indice id - entree liste de doublon (id, valeur)"
	connection, ex = connexion(name_bdd)
	for champ,champ_name in zip(champs_liste,champs_name): 
		champ_id  = str(champ[0])
		champ_value =str(champ[1])
		values = " SET " + champ_name +   ' = '+ champ_value 
		commandesql = "UPDATE   " + name_table +' '+ values+" WHERE id=" + champ_id
		#print commandesql
		ex(commandesql)
	connection.commit()
	connection.close()
	#print "table "+name_table+" remplie avec les champs "  + champs_name
	

def update_table(name_bdd,name_table,champs_name,champs_liste):
	"remplit la colonne champ_name d'indice id - entree liste de doublon (id, valeur)"
	connection, ex = connexion(name_bdd)
	for champ in champs_liste: 
		champ_id  = str(champ[0])
		champ_value =str(champ[1])
		champ_sql = champ_value.replace("'","popostrophe")#eliminer les quotes simples pour inserer dans la table sql
		values = " SET " + champs_name +   '= \''+champ_sql +'\''
		commandesql = "UPDATE   " + name_table +' '+ values+" WHERE id=" + champ_id
		ex(commandesql)
	connection.commit()
	connection.close()
	#print "table "+name_table+" remplie avec les champs "  + champs_name
	
def remplir_jours(name_bdd,name_table,requete,date_depart):
	print "    - calcul de la colonne \"jours\" dans la table \""+name_table+"\"..."
	sortie = select_bdd_table(name_bdd,name_table,'id,date',requete)
	nb_jourv=[]
	for dates in sortie:

		date_b = str(dates[1])
		if 'T' in date_b:
			date_b = date_b.split('T')[0]
		#conforme a la mise en forme de telmo
		date_billet=parseur.date_billet_parser(date_b)
		#attention prendre une date départ en 2010 si on veut indexer par jour!!!
		nb_jour= parseur.jour_entre(date_billet,date_depart)
		nb_jourv.append((dates[0],nb_jour))

	#on rajoute les champs ainsi construits dans la table
	#print nb_jourv
	update_table(name_bdd,name_table,'jours',nb_jourv)
	print '    - colonne \"jours\" completee dans la table \"' + name_table+"\""

