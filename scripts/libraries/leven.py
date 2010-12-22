# -*- coding: utf-8 -*-
#!/usr/bin/python
import codecs
import unicodedata
import os
import sys

def levenshtein_distance(first, second):
    """Find the Levenshtein distance between two strings."""
    if len(first) > len(second):
        first, second = second, first
    if len(second) == 0:
        return 150
    first_length = len(first) + 1
    second_length = len(second) + 1
    distance_matrix = [[0] * second_length for x in range(first_length)]
    for i in range(first_length):
       distance_matrix[i][0] = i
    for j in range(second_length):
       distance_matrix[0][j]=j
    for i in xrange(1, first_length):
        for j in range(1, second_length):
            deletion = distance_matrix[i-1][j] + 1
            insertion = distance_matrix[i][j-1] + 1
            substitution = distance_matrix[i-1][j-1]
            if first[i-1] != second[j-1]:
                substitution += 1
            distance_matrix[i][j] = min(insertion, deletion, substitution)
    return distance_matrix[first_length-1][second_length-1]

def lire_fichier_classe(fichier_name):
	#on recupere les classes d'equivalence de formes passees
	unigrammes=[]
	deja_nouni_couple={}
	equivalences_leven={}
	try:
		levenclassesin=open(fichier_name,'r')
		classes_leven = levenclassesin.readlines()	
		for lignes in classes_leven:
			if len(lignes)>1:
				termes = lignes[:-1].split('\t')
				#print termes
				temp=equivalences_leven.get(termes[0],[])
				temp.append(termes[1])
				equivalences_leven[termes[0]]=temp
				temp=equivalences_leven.get(termes[1],[])
				temp.append(termes[0])
				equivalences_leven[termes[1]]=temp	
				if len(termes[0].split(' '))==1:
					temp=deja_nouni_couple.get(termes[0],[])
					if not termes[1] in temp:
						temp.append(termes[1])
					deja_nouni_couple[termes[0]]=temp
					temp=deja_nouni_couple.get(termes[1],[])
					if not termes[0] in temp:
						temp.append(termes[0])
					deja_nouni_couple[termes[1]]=temp
					unigrammes.append(termes[1])
					unigrammes.append(termes[0])
		levenclassesin.close()
	except:
		pass			
	return equivalences_leven,deja_nouni_couple,unigrammes


def check_include_more(x,y):
#étant donné deux ngrammes (non lemmatises) si l'une a plus de termes que l'autre, on verifie que ce n'est pas une inclusion
	n_x=x.count(' ')
	n_y=y.count(' ')
	if n_x!=n_y:
		if x in y or y in x:
			return True
		else:
			return False
	else:
		return False

def made_of_int(x):
	for c in x:
		if not c in['.','/']:
			try:
			 	if not str(int(c))==c:
					return False
			except:
				return False
				
def check_diff_int(x,y):
	n_x=x.count(' ')+1
	n_y=y.count(' ')+1
	if n_x==n_y:
		x_v=x.split(' ')
	 	y_v=y.split(' ')
		for i in range(n_x):
			L_x = list(x_v)
			L_y = list(y_v)
			rem_x = L_x.pop(i)
			rem_y = L_y.pop(i)
			if L_x==L_y:
				try:
					if not made_of_int(rem_x)==False and  not made_of_int(rem_y)==False:
						return True
				except:
					pass		
	else:
		return None

def recursive_eq(couple,equivalences_leven):
	classe_history = equivalences_leven[couple]
	for x in classe_history:
			new = equivalences_leven[x]
			for ne in new:
				ne_v=[]
				for j in classe_history:
					ne_v.append(ne)
				if not ne in classe_history and not ne==couple and not(map(check_include_more,ne_v,classe_history)):
					classe_history.append(ne)		
	return classe_history
	
def extension_uni(classe_history,deja_uni_couple,deja_uni,xl):
	classe_history.append(xl)
	#print "beign extension_uni"
	#print classe_history 
	for x in classe_history:#on itere sur tous les elements de la classe deja entres
		x_v = x.split(' ')
		for item in x_v:#on itere sur chaque terme des elements de la classe
			#print 'item'
			#print item
			if item in deja_uni:#on verifie si les termes ont des equivalents deja enregistres
				for item_cl in deja_uni_couple[item]:#on itere parmi tous les equivalents des termes
					prop = x.replace(item,item_cl)# on remplace un peu brutalement sur la chaine de caractere directement...
					#clno = 0
					#for cl_hi in classe_history:
					#	for cl_his in cl_hi.split(' '):
					#		if  prop == cl_his:
					#			clno=1
					#if clno ==0:
					prop_v=[]
					for j in classe_history:
						prop_v.append(prop)
					if not prop in classe_history and not(map(check_include_more,prop_v,classe_history)):
						classe_history.append(prop) 
	return classe_history
	
def pack_leven(fichier,fichier_out,language,user_interface,freqmin,Nb_rows = 0):
	print '\nreduction de la liste avec levenstein\n'
	fichier = open(fichier,'r')
	fichier_out = open(fichier_out,'w')
	fichierl = fichier.readlines()
	formes=[]
	lemmes=[]
	occ=[]
	old_cl=[]
	resultats=[]
	nlm=0
	deja_uni={}#dico des 1-grammes equivalents
	fichier_name = 'libraries/leven-classes_'+language+'o.txt'
	fichier_name_doute='libraries/leven-classes-doute_'+language+'o.txt'
	fichier_name_no = 'libraries/noleven-classes_'+language+'o.txt'
	equivalences_leven,deja_uni_couple,deja_uni = lire_fichier_classe(fichier_name)
	noequivalences_leven,deja_nouni_couple,deja_nouni = lire_fichier_classe(fichier_name_no)
	#if user_interface=='n':
	doute_levenclassesout=open(fichier_name_doute,'a')
	levenclassesout=open(fichier_name,'a')
	nolevenclassesout=open(fichier_name_no,'a')
	#print 'dans pack-leven'
	for ligne in fichierl:
		formes.append(ligne.split('\t')[1].lower())
		lemmes.append(ligne.split('\t')[0])
		occ.append(int(ligne.split('\t')[2][:-1]))
	colles=[]
	coldecol=[]
	
	#on trie formes et lemmes avant afin de limiter les calculs 
	vecteur = []
	for x,y,z in zip(formes,lemmes,occ):
		vecteur.append((x,y,z))
	vecteur.sort()
	formes=[]
	lemmes=[]
	occ= []
	for vect in vecteur:
		formes.append(vect[0])
		lemmes.append(vect[1])
		occ.append(vect[2])
	numero=-1
	for (x,xl) in zip(formes,lemmes):
		#print x, xl
		numero=numero+1
		equiv = []
		if xl not in colles:
			colles.append(xl)
			if (numero)%100==0:
				print '(#'+str(numero)+')'
			eq = []
			j=numero
			fin=0
			#on commence par alimenter les equivalences par celles qui ont été enregistrées dans le passé
			try:
				classe_history = recursive_eq(xl,equivalences_leven)
				#print classe_history
				# et on etend avec deja_uni 
			except:
				classe_history= []
			#print 'ici'
			#print classe_history
			#print deja_uni_couple
			#print deja_uni
			#print xl
			classe_history = extension_uni(classe_history,deja_uni_couple,deja_uni,xl)
			
			classe_history_sharp = []
			for machins in classe_history:
				if not machins in classe_history_sharp and not machins==xl:
					classe_history_sharp.append(machins)
			classe_history = classe_history_sharp
		
			
			#if 'corporate' in x.lower() and 'planning' in x.lower():
			#	print '\n'
			#	print xl,x,classe_history,numero
			#	print x[0:1].lower()
			#puis on regarde dans la nouvelle liste s'il y a de nouveaux candidats au poste.
			#print "classe_history"
			print classe_history
			for (y,yl) in zip(formes[numero+1:],lemmes[numero+1:]):
					j=j+1 
					first_x = x[0:1].lower()
					first_y = y[0:1].lower()
					if first_x == first_y:
						x_long= len(x)
						y_long= len(y)
						if x_long>y_long:
							diff_long = x_long-y_long
						else:
							diff_long = y_long-x_long

							
						if not yl in classe_history and diff_long<4:
												
							dist=levenshtein_distance(x.lower(),y.lower())
							if dist < 4 and float(dist) / len(y) < 0.14 :
								#print x,y
								if check_include_more(x,y)==False and not check_diff_int(x,y) == True:
									var='?'
									try:
										if yl in noequivalences_leven[xl]:
											var ='n'	
									except:
										pass
									try:
										if yl in equivalences_leven[xl]:
											var='y'
											equiv.append(j)
											colles.append(yl)	
									except:
										pass
									if var=='?':
										if user_interface == 'yy':
											var = raw_input('-> grouper "'+ str([x])  + '" ('+str([xl])+') dans la classe de "' + str([y]) + '" ('+str([yl])+') (y pour accepter, n pour refuser formellement):')
											if var == 'y':
												equiv.append(j)
												colles.append(yl)
												levenclassesout.write(xl+'\t'+yl+'\n')
												#on essaye d'en tirer des enseignements pour les plus petits n-grammes
												if len(xl.split(' '))>1:
													term_diff = list((set(xl.split(' '))|set(yl.split(' ')))-(set(xl.split(' '))&set(yl.split(' '))))
													ok=0
													if len(term_diff)==2 and not (term_diff[0],term_diff[1]) in deja_uni_couple:
														if term_diff[0] in equivalences_leven:
															if not term_diff[1] in equivalences_leven[term_diff[0]]:
																	ok=1
														else:
															ok=1
														if ok==1:	
															x_uni = term_diff[0].split('_')[-1]
															y_uni = term_diff[1].split('_')[-1]
															dist_uni=levenshtein_distance(x_uni,y_uni)
															#print (x_uni + ' * ' + y_uni)
															if (float(dist_uni)/len(x_uni)<0.3 and dist_uni < 4) or (x_uni in y_uni) or (y_uni in x_uni):
																var = raw_input('-> UNI grouper "'+ str([x_uni])  + '" ('+str([term_diff[0]])+') dans la classe de "' + str([y_uni]) + '" ('+str([term_diff[1]])+') (y pour accepter, n pour refuser formellement):')
																if var =='y':
																	levenclassesout.write(term_diff[0]+'\t'+term_diff[1]+'\n')
															
																	temp=deja_uni_couple.get(term_diff[0],[])
																	if not term_diff[1] in temp:
																		temp.append(term_diff[1])
																	deja_uni_couple[term_diff[0]]=temp
																	temp=deja_uni_couple.get(term_diff[1],[])
																	if not term_diff[0] in temp:
																		temp.append(term_diff[0])
																	deja_uni_couple[term_diff[1]]=temp
																	deja_uni.append(term_diff[0])
																	deja_uni.append(term_diff[1])
												else:#sinon, on redirige directement dans les uni-machins
													if len(xl.split(' '))==1 and len(yl.split(' '))==1:
														deja_uni.append(xl)
														deja_uni.append(yl)
														temp=deja_uni_couple.get(xl,[])
														if not yl in temp:
															temp.append(yl)
														deja_uni_couple[xl]=temp
														temp=deja_uni_couple.get(yl,[])
														if not xl in temp:
															temp.append(xl)
														deja_uni_couple[yl]=temp						
													
											else:
												nolevenclassesout.write(xl+'\t'+yl+'\n')	
										else:
											print 'suggestion de regroupement '+ xl,yl
											if (xl,yl) not in old_cl:
												old_cl.append((xl,yl))
												doute_levenclassesout.write(xl+'\t'+yl+'\n')
											
												if len(xl.split(' '))>1:
													term_diff = list((set(xl.split(' '))|set(yl.split(' ')))-(set(xl.split(' '))&set(yl.split(' '))))
													ok=0
													if len(term_diff)==2 and not (term_diff[0],term_diff[1]) in deja_uni_couple:
														if term_diff[0] in equivalences_leven:
															if not term_diff[1] in equivalences_leven[term_diff[0]]:
																	ok=1
														else:
															ok=1
														if ok==1:	
															x_uni = term_diff[0].split('_')[-1]
															y_uni = term_diff[1].split('_')[-1]
															dist_uni=levenshtein_distance(x_uni,y_uni)
															#print (x_uni + ' * ' + y_uni)
															if (float(dist_uni)/len(x_uni)<0.3 and dist_uni < 4) or (x_uni in y_uni) or (y_uni in x_uni):
																doute_levenclassesout.write(term_diff[0]+'\t'+term_diff[1]+'\n')
																														
											
					else:
						break
			chaine=xl
			occur = occ[numero]
			ensemble=[chaine]
			if len(equiv) + len(classe_history)>0:
				#chaine = str(lemmes[numero]) 
				
				for equ in equiv:
					chaine = chaine+'***'+lemmes[equ]
					ensemble.append(lemmes[equ])
					occur = occur + occ[equ]
				for classe_passe in classe_history:
					chaine = chaine+'***'+classe_passe
					ensemble.append(classe_passe)
					#print ensemble
					try:
						idx_past = lemmes.index(classe_passe_l)
						occur=occur +occ[idx_past]
						colles.append(classe_passe)
					except:
						pass			
			ens_set=set(ensemble)
			#si classe dans un autre ordre on arrête tous
			if not ens_set in coldecol:
				coldecol.append(ens_set)
				if occur> freqmin:
					nlm = nlm + 1
				 	if Nb_rows>0:
						resultats.append(chaine + '\t' + formes[numero] +'\t' + str(occur) +'\t' + str(float(occur)/float(Nb_rows)*100.).replace('.',',') +  '\n')
					else:
						resultats.append(chaine + '\t' + formes[numero] +'\t' + str(occur) +  '\n')
					#fichier_out.write(chaine + '\t' + formes[numero] +'\t' + str(occur) +  '\n')
	result_ensembles=[]
	resultats_propres=[]
	print str(len(resultats)) + ' nlemmes quasi-finaux'
	for resultat in resultats:
		nlem_cl = set(resultat.split('\t')[0].split('***'))
		clause=1
		for result_ens in result_ensembles:
			if nlem_cl <= result_ens:
				clause=0
			if result_ens <= nlem_cl:
				idx = result_ensembles.index(result_ens)
				del result_ensembles[idx]
				del resultats_propres[idx]
		if clause==1:
			result_ensembles.append(nlem_cl)
			resultats_propres.append(resultat)
	for res in 	resultats_propres:
		fichier_out.write(res)
	fichier_out.close()
	fichier.close()
	print str(len(resultats_propres)) + ' nlemmes finaux'

		
def pack_rendondance_exact(fichier,fichier_out,maxTermLength,freqmin,language,ng_filter,user_interface):
	print 'reduction de la liste en intégrant les redondances\n'
	russe = {}	
	russe_inv = {}	
	fichier = open(fichier,'r')
	fichier_out = open(fichier_out,'w')
	fichierl = fichier.readlines()
	formes=[]
	lemmes=[]
	ns=[]
	occ=[]
	for ligne in fichierl[1:]:
		formes.append(ligne.split('\t')[1])
		lemmes.append(ligne.split('\t')[0])
		occ.append(int(ligne.split('\t')[3]))	
		ns.append(len(ligne.split('\t')[1].split(' ')))
	colles=[]
	vecteur = []
	for w,x,y,z in zip(formes, lemmes , occ, ns):
		vecteur.append((z,w,x,y))
	vecteur.sort() 
	#vecteur.reverse()

	formes=[]
	lemmes=[]
	ns=[]
	occ=[]
	for vect in vecteur:
		ns.append(vect[0])
		formes.append(vect[1])
		lemmes.append(vect[2])
		occ.append(vect[3])	
	numero0=-1
	#on recalcule des pseudo-occurrences avec les inclusions de nlemmes
	for x in lemmes:

		numero0=numero0+1
		if numero0+1%100==0:
			print '(#'+str(numero0-1)+')'
		equiv = []
		n_x = ns[numero0]
		russe[numero0]=[]
		#print 'on evalue ' + x + ' occ: '+str(occ[numero0]) + ', n=' + str(n_x)
		if n_x >0:
			numero=numero0	
			for y in lemmes[numero0+1:]:
				numero=numero+1
				n_y = ns[numero]
				if n_y>n_x:

					if x in y and set(x.split(' ')) <= set(y.split(' ')): #and pour faire attention à falsiform(ibility.)
						#print '-> on rencontre ' + y
						temp = russe[numero0]
						temp.append(numero)
						russe[numero0]=temp
				
						temp_inv = russe_inv.get(numero,[])
						temp_inv.append(numero0)
						russe_inv[numero]=temp_inv
	# a ce stade on a integralement reconstruit les enchassements.
	# maintenant on calcule les véritables fréquences de chaque lemmes
	
	#on copie occ original
	occbis=[]
	for x in occ:
		occbis.append(x)
	
	#on range russe_inv dans l'ordre inverse des n-lemmes.
	vecteurs=[]
	for x,y in russe_inv.iteritems():
		taille = ns[x]
		vecteurs.append((taille,x,y))
	vecteurs.sort()
	vecteurs.reverse()
	for x in vecteurs:
		occ_x=occbis[x[1]]
		print 'lemme: '+ lemmes[x[1]]  + '\t' + str(occbis[x[1]])
		
		for sub_cl in x[2]:
			print '                ' + lemmes[sub_cl] + '\t' + str(occbis[sub_cl]) +' - '  + str(occbis[x[1]]) +' = '+str(occbis[sub_cl] - occbis[x[1]])
			#on retire trop ici, si nmax = 4, US food and drug (5) / food and drug administration (5) font perdre chacun 5 à food and drug.
			occbis[sub_cl] = occbis[sub_cl] - occbis[x[1]]		
	numero0=-1	
	nb_elimine = 0	
	sizelemmes=len(lemmes)
	for x in lemmes:
		numero0 = numero0+1
		if numero0+1%100==0:
			print '(##'+str(numero0)+' / '+ str(sizelemmes)+')'
		if occbis[numero0]*ng_filter[ns[numero0]-1]>=freqmin:
			#print "on conserve " + lemmes[numero0]   + '('+ str(occbis[numero0]) + ')'
			fichier_out.write(str(lemmes[numero0]) + '\t' + str(formes[numero0]) +'\t' + str(occbis[numero0]) +  '\n')
		else:
			print "on elimine car trop peu frequent " + lemmes[numero0]   + '('+ str(occbis[numero0]) + ')'
			nb_elimine = nb_elimine +1
			for x in russe[numero0]:
				print '    -> au profit de '+  lemmes[x] + '('+ str(occbis[x]) + ')'
	fichier_out.close()
	fichier.close()
	print str(nb_elimine) + ' termes elimines'
	print str(sizelemmes-nb_elimine) + ' lemmes restants '