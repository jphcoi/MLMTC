#!/usr/bin/python
# -*- coding: utf-8 -*- 
import os
import sys
sys.path.append("../scripts/libraries")
sys.path.append("../scripts")

print "export_maps v0.1 (20100220)"
print "--------------------------------\n"

import fonctions_bdd
import parameters
import os
import sys
import math
import gexf
import fonctions
import maps_union
from operator import itemgetter

path_req = parameters.path_req
years_bins = parameters.years_bins
name_bdd = parameters.name_bdd
path_req=parameters.path_req
timelimit='1'
CFinder_CL=parameters.CFinder_CL
dist_type=parameters.dist_type
sep_label = ' --- '

def lire_dictionnaire_transition(niveau):
	transition = {}
	for inter in range(len(years_bins)):
		# on recupere le dictionnaire de transition d'un niveau vers l'autre
		fichier = path_req + 'lexique'  +'/' + 'lexique_' + 'niv_' + str(niveau) + '_' + dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt'
		file = open(fichier,'r')
		for ligne in file.readlines():
			lignev = ligne.split('\t')
			chp = int(lignev[0])
			items = lignev[1][:-1].split(' ')
			itemint = []
			for item in items:
				itemint.append(int(item))
			transition[(inter,chp)]=itemint
	return transition


	
#on lance d'abord CFinder pour l'ensemble de nos réseaux avec les paramètres ci-dessus
def list2string(l_v):
	l_v = map(str,l_v)
	return '+'.join(l_v)

def Cfinderexport_name(niveau,inter,degmax):
	return path_req + 'CFINDER/'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'_dmax_'+str(degmax)+'_w_'+list2string(CF_weight_v[:niveau])+'_kmin_'+list2string(kmin_v[:niveau])+'_tmin_'+list2string(taillemin_v[:niveau])+'_taillemax_'+list2string(taillemax_v[:niveau])+'_niv_'+str(niveau)

def read_reseau(niveau,inter):
	fichier=path_req  + 'reseau/'+'reseauCF_'+'niv_'+str(niveau)+'_'+dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.txt'
	reseau = {}
	file_ = open(fichier,'r')
	for ligne in file_.readlines():
		ligne_v = ligne.split('\t')
		ori = int(ligne_v[0])
		des = int(ligne_v[1])
		poi = float(ligne_v[2][:-1])
		temp = reseau.get(ori,{})
		temp[des] = poi
		reseau[ori] = temp
	return reseau
	
def seuiller(res,degmax):
	res_seuil = {}
	for terme in res:
		l = res[terme].items()
		l.sort(key=itemgetter(1),reverse=True)
		res_seuil[terme]=l[:degmax] 
	return res_seuil

def write_reseau(res_seuil,niveau,inter):
	fichier_out=path_req  + 'reseau/'+'reseauCF_'+'niv_'+str(niveau)+'_'+dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'_degmax_'+str(degmax)+'.txt'
	fichier_out_ = open(fichier_out,'w')
	for terme in res_seuil:
		for x in res_seuil[terme]:
			fichier_out_.write(str(terme)+'\t'+str(x[0])+'\t'+str(x[1])+'\n')
	return fichier_out
		
def seuil_degmax(niveau,degmax,inter):
	res = read_reseau(niveau,inter)
	res_seuil = seuiller(res,degmax)
	fichier_out = write_reseau(res_seuil,niveau,inter)
	return fichier_out
	
def CFinder_launch(niveau,dico_termes,degmax,CF_weight):
	for inter in range(len(years_bins)):
		if degmax>0:
			fichier = seuil_degmax(niveau,degmax,inter)	
		else:
			fichier=path_req  + 'reseau/'+'reseauCF_'+'niv_'+str(niveau)+'_'+dist_type+'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'_degmax_'+str(degmax)+'.txt'
		sortie = Cfinderexport_name(niveau,inter,degmax)
		command_sys = CFinder_CL + " -i "+ fichier +' -t ' +str(timelimit)+" -D -o " + sortie + " -w " + str(CF_weight)
		print command_sys
		try:
			os.system(command_sys)
		except:
			'----------------------------------detection de communautés déjà calculée pour ces paramètres et ces données'


def parse_dir_comm(pathk):
	commk=[]
	filek = open(pathk+'/directed_communities','r')
	for ligne in filek.readlines():
		if ligne[0]=='#' or len(ligne)<2:
			pass
		else:
			commk.append(ligne[:-1].split(':')[1].split(' ')[1:-1])
	return commk

def parser_CFinder(niveau):
	communities={}
	for inter in range(len(years_bins)):

		rep = Cfinderexport_name(niveau,inter,degmax)
		for repk in os.listdir(rep):
			if repk[0]=='k':
				k = int(repk.split('=')[-1])
				pathk = rep + '/' + repk
				commk = parse_dir_comm(pathk)
				communities[(inter,k)]=commk
	return communities

def tri_comm(communities,taillemin, taillemax, kmin):
	champs={}
	card_champs_pot ={}
	card_taillemin={}
	card_taillemax={}
	card_kmin={}
	card_chpsok={}
	chaine = []
	for x,y in communities.iteritems():
		candidats=[]
		inter = x[0]
		if not inter in card_taillemin:
			card_taillemin[inter] = 0  
		if not inter in card_taillemax:
			card_taillemax[inter] = 0  
		if not inter in card_kmin:
			card_kmin[inter] = 0  
		if not inter in card_chpsok:
			card_chpsok[inter] = 0  
		if not inter in card_champs_pot:
			card_champs_pot[inter] = 0  
				
		for candidat in y:
			card_champs_pot[inter]=card_champs_pot[inter]+1
			if len(candidat)>=taillemin and len(candidat)<=taillemax and int(x[1])>=kmin:
				candidats.append(candidat)
				card_chpsok[inter]=card_chpsok[inter]+1
			else:
				if int(x[1])<kmin:
					card_kmin[inter] = card_kmin[inter]+1
				else:
					if len(candidat)<taillemin:
						card_taillemin[inter] = card_taillemin[inter]+1
					if len(candidat)>taillemax:
						card_taillemax[inter] = card_taillemax[inter] +1
				
		if len(candidats)>0:
			champs[x]=candidats
	for inter in card_kmin:
		chaine.append('***'  + " periode: " + str(inter))
		chaine.append('*** sur '  + str(card_champs_pot[inter]) +' cluster(s) potentiel(s) ')
		chaine.append('*** sur '  + str(card_chpsok[inter]) +' cluster(s) selectionne(s) avant overlap ')
		chaine.append('*** ôté(s) de '  + str(card_kmin[inter]) +' cluster(s) exclu(s) car de k inférieur à ' + str(kmin))
		chaine.append('*** ôté(s) de '  + str(card_taillemin[inter]) +' cluster(s) exclu(s) car de taille inférieure à  ' + str(taillemin))
		chaine.append('*** ôté(s) de '  + str(card_taillemax[inter]) +' cluster(s) exclu(s) car de taille supérieure à  ' + str(taillemax))
		chaine.append('\n')
	
	return champs,chaine

def inside(liste_de_liste,liste):
	resultat = 0
	if  len(liste_de_liste)>0:
		for x in liste_de_liste:
			clause=0
			for item in liste:
				if  item in x:
					clause=clause + 1
			if clause==len(liste):
				resultat = 1
	return resultat
					
def flat_comm(champs_k,years_bins):
	champs={}
	for inter in range(len(years_bins)):
		candidats_inter=[]
		for x,y in champs_k.iteritems():
			if x[0]==inter:
				for z in y:
					clausein=0
					if inside(candidats_inter,z)==0:#on gere l'overlap ici
						clausein=1
					if clausein==1:
						clauseout=1
						out=[]
						for deja in candidats_inter:
							if inside([z],deja)==1:
								clauseout=0
								out.append(deja)
						candidats_inter.append(z)
						if clauseout==0:
							for ou in out:
								candidats_inter.remove(ou)
		champs[inter]=candidats_inter
	return champs
	

def afficher_champ(liste_indices_termes,dico_termes,dico_transition,inter):
	chaine= ''

	for x in liste_indices_termes:	
		for trans in dico_transition[(inter,int(x))]:
			chaine = chaine + ' - ' + dico_termes[int(trans)] 
	chaine=chaine[2:]
	print  '### '+ chaine
	
def afficher_tous_champs(champs,scores,nb_label,sep_label,dico_termes,dico_transition):
	for inter,y in (champs.iteritems()):
		if len(y)>0:
			scoresinter=scores[inter]
			print '\n'
			print '**************************************************'
			print 'intervalle '+ str(inter) + ' : '  + str(len(y)) + ' champs:'
			print '**************************************************'
			print '\n'
			for c in y:
				label=''
				for j in range(nb_label):				
					label =  label + sep_label + dico_termes[(scoresinter[y.index(c)])[j]]
				label = label[len(sep_label):]
				print '\n' + label
				afficher_champ(c,dico_termes,dico_transition,inter)

def score_compute(type_score,champ_terme,dist_mat,terme,inter):
	score_computed = 0.
	if type_score=='combine':
		for voisin in champ_terme:
			din,dout=0,0
			if terme==voisin:
				din,dout=1,1
			else:
				try:
					din=float(dist_mat[(terme,voisin,inter)])
					dout=float(dist_mat[(voisin,terme,inter)])
				except:
					pass
			try:
				score_computed = score_computed +  float(din*dout)/(din+dout)
			except:
				pass
	score_computed = score_computed / (len(champ_terme)-1)
#	print 	str(terme) + '\t' + str(score_computed)
	return score_computed
	
def label_champs(champs0,nb_label,dico_transition,dico_termes,dist_mat,type_score):
	scores = {}
	termes = {}
	D={}	
	for inter,champs in champs0.iteritems():
		for champ in champs:
			D[inter] = D.get(inter,0)+1
			#D, c'est simplement pour chaque période le nombre de champs
			for item in champ:
				temp = termes.get(inter,[])
				temp.extend(dico_transition[(inter,int(item))])
				termes[inter]=temp
				#termes, c'est pour chaque périoden un vecteur qui aggrège tous les termes qui occurrent eventuellement n fois
	for inter,champs in champs0.iteritems():
		for champ in champs:			
			score=[]
			champ_terme =[]
			for item in champ:
				champ_terme.extend(dico_transition[(inter,int(item))]) 
				#champ_terme=vecteur de tous les termes compris dans champ
			nb_termes_chp = len(champ_terme)
			for terme in champ_terme:
				doc_total = termes[inter].count(terme)
				doc_champ = champ_terme.count(terme)
				ratio = (float(doc_champ)/nb_termes_chp) / (float(doc_total)/len(termes[inter]))
				#le ratio c'est la proportion  du terme dans le champ normalisee par sa proportion dans tous les champs 
				#et là on calcule le score a proprement parler:
				meilleur_voisin = score_compute(type_score,champ_terme,dist_mat,terme,inter)
				ponderation = math.log10(ratio)
				score.append(meilleur_voisin*ponderation)
			scoretrie = score[:]
			scoretrie.sort()
			scomax=[]
			j=0
			label_int_old='-1219129'
			i=-1
			while len(scomax)<nb_label:
				i=i+1
				if champ_terme[int(score.index(scoretrie[-i-1]))] != label_int_old:
					scomax.append(champ_terme[int(score.index(scoretrie[-i-1]))])
					label_int_old = champ_terme[int(score.index(scoretrie[-i-1]))]
					champ_terme.remove(champ_terme[int(score.index(scoretrie[-i-1]))])
					score.remove((scoretrie[-i-1]))
					scoretrie.remove((scoretrie[-i-1]))
					i=i-1
			temp = scores.get(inter,[])
			temp.append(scomax)
			scores[inter] = temp
	return scores		
		
				

def labellize(champ1,inter,scores,champs,nb_label,dico_termes,sep_label):

	label = ''
	label_id=[]
	scoresinter=scores[inter]
	for j in range(nb_label):
		label =  label + sep_label + dico_termes[(scoresinter[champ1])[j]]		
		label_id.append(str((scoresinter[champ1])[j]))
	label = label[5:]
	return label,label_id


#dist_mat_temp[(linev[0],linev[1])]=linev[2][:-1]
def gexf_champ(years_bins,scores,champs,nb_label,dico_termes,sep_label,dist_type,distance_champ,niveau,seuil_net_champ):
	legende_noeuds={}
	legende_noeuds_id={}
	for inter in range(len(years_bins)):
		try:
			os.mkdir(path_req + 'gexf')
		except:
			pass
		nodes_chp = {}
		level={}
		
		
		dist_mat_chp_temp = {}
		#on met d'abord des labels à tous les champs
		for x,leschamps in champs.iteritems():
			if inter==x:
				for champ1 in leschamps:
					if not leschamps.index(champ1) in nodes_chp:
						etiquette,etiquette_id=labellize(leschamps.index(champ1),inter,scores,champs,nb_label,dico_termes,sep_label)
						nodes_chp[leschamps.index(champ1)] = etiquette
						level[leschamps.index(champ1)]=niveau
						legende_noeuds[(inter,leschamps.index(champ1))]=etiquette
						legende_noeuds_id[(inter,leschamps.index(champ1))]=etiquette_id
		
		for x,dist in distance_champ.iteritems():
			if inter==x[2]:
				
				champ1 = x[0]
				champ2 = x[1]

				if not champ1 in nodes_chp:
					etiquette,etiquette_id=labellize(champ1,inter,scores,champs,nb_label,dico_termes,sep_label)
					nodes_chp[champ1] = etiquette
					level[champ1]=niveau
					legende_noeuds[(inter,champ1)]=etiquette
					legende_noeuds_id[(inter,champ1)]=etiquette_id
					
				if not champ2 in nodes_chp:
					etiquette,etiquette_id=labellize(champ2,inter,scores,champs,nb_label,dico_termes,sep_label)
					nodes_chp[champ2] = etiquette
					legende_noeuds[(inter,champ2)]=etiquette
					legende_noeuds_id[(inter,champ2)]=etiquette_id
				if dist>seuil_net_champ and champ1!=champ2:
					dist_mat_chp_temp[(champ1,champ2)]=dist
		sortie = path_req + 'gexf/' + 'reseau_champ'+'_' +str(niveau)+'_'+ dist_type +'_'+str(years_bins[inter][0])+'-'+str(years_bins[inter][-1])+'.gexf'
		
		for x in nodes_chp:
			level[x]=niveau
		
		gexf.gexf_builder(nodes_chp,dist_mat_chp_temp,sortie,level)	
	return legende_noeuds,legende_noeuds_id	

def restrict(dist_mat,inter,CF_weight):
	voisins_inter={}
	for (x,y) in dist_mat.iteritems():
		if x[2]==inter:
			ori = x[0]
			des = x[1]
			stre = y
			if stre>CF_weight:
				temp = voisins_inter.get(ori,[])
				temp.append((des,stre))
				voisins_inter[ori]=temp			
	return voisins_inter

def	aggreger(voisins,champs,seuil_aggregation):
	deja = []
	aggregation = {}
	for ch in champs:
		deja = deja + ch
	poids={}
	for terme,voisins_liste in voisins.iteritems():
		for voisin in voisins_liste:
			vois = voisin[0]
			stre = voisin[1]
			poids_vois = poids.get(vois,0.)
			poids[vois] = poids_vois+float(stre)
	for terme,voisins_liste in voisins.iteritems():
		if not str(terme) in deja:
			score_terme = {}
			score_terme_total=0.
			for voisin in voisins_liste:
				vois = voisin[0]
				stre  = voisin[1]
				for ch in champs:
					if str(vois) in ch:
						temp = score_terme.get(champs.index(ch),0.)
						score_terme[champs.index(ch)] = temp+float(stre)/poids[vois]
				score_terme_total=score_terme_total+float(stre)/poids[vois]
			score_terme_norm={}
			for x,y in score_terme.iteritems():
				score_terme_norm[x]=float(y)/float(score_terme_total)#/float(len(champs[x]))*10.
		#	print score_terme_norm
			for x,y in score_terme_norm.iteritems():
				comm =[]
				if y>seuil_aggregation:
					comm.append(x)
				if len(comm)>0:
					aggregation[terme]=comm
	return aggregation

def extension(champs,dist_mat,years_bins,CF_weight,seuil_aggregation):
#	print years_bins
	champs_ext={}
	for inter in range(len(years_bins)):
		champs_inter=champs[inter]
		voisins_inter = restrict(dist_mat,inter,CF_weight)
		aggregation = aggreger(voisins_inter,champs_inter,seuil_aggregation)
		champs_bonus={}
		for x,y in aggregation.iteritems():
			for y0 in y:
				temp = champs_bonus.get(y0,[])
				temp.append(x)
				champs_bonus[y0]=temp
		champs_inter_new=[]
		for ch in champs_inter:
			if champs_inter.index(ch) in champs_bonus:
				plus=map(str,champs_bonus[champs_inter.index(ch)])
			else:
				plus=[]
			ch_ext = ch + plus
			champs_inter_new.append(ch_ext)
		champs_ext[inter]=champs_inter_new
	#print '\n'+str(len(champs_bonus))+ ' élément rapportés \n'
	return champs_ext

def edges_list(distance_champ):
	edges = {}
	for x,y in distance_champ.iteritems():
		ori = x[0]
		t = x[2]
		dest = x[1]
		if (ori,t) in edges:
			temp = edges[(ori,t)]
			temp[dest]= y
			edges[(ori,t)]=temp
		else:
			dico = {}
			dico[dest]=y
			edges[(ori,t)]=dico
	return edges



def edges_list_reverse(edges):
	distance_champ = {}
	for x,y in edges.iteritems():
		ori = x[0]
		t = x[1]
		for z in y:
			dest = z[0]
			poid = z[1]
			distance_champ[(ori,dest,t)]=poid
	return distance_champ
	
dico_termes=fonctions.lexique()#on cree le dictionnaire des termes
import context_process
dist_mat = context_process.dist_mat#on recupere la matrice de distance entre termes
#p_cooccurrences=context_process.p_cooccurrences#on recupere la matrice de cooccurrences entre termes
fini=1
niveau=0
CF_weight_v = [0.5,0.2,0.5,0.5,0.5]
try:
	CF_weight_v[0]=parameters.CF_weight0
except:
	pass
	
seuil_net_champ_v = [0.,0.,0.,0.,0.]
taillemin_v=[3,3,3,3,3,3]
taillemax_v=[30,25,25,25,25,25]
kmin_v = [5,5,5,5,5,5]
kmin_v = [3,3,3,3,3,3]
kmin_v = [4,4,4,4,4,4]

nb_label_v = [2,3,4,5,6,7]
degmax=5
type_score='combine'
info={}
lenchampsfinal={}
text = ''
while fini==1:
	niveau=  niveau+1
	CF_weight=CF_weight_v[niveau-1]
	seuil_net_champ=seuil_net_champ_v[niveau-1]
	taillemin=taillemin_v[niveau-1]
	taillemax = taillemax_v[niveau-1]
	kmin = kmin_v[niveau-1]
	nb_label=nb_label_v[niveau-1]

	print "niveau = "+ str(niveau)
	
	dico_transition= lire_dictionnaire_transition(niveau)
	CFinder_launch(niveau,dico_termes,degmax,CF_weight)#on lance CFinder au besoin
	communities =parser_CFinder(niveau)#on récupère les données ainsi produites
	print " \n- niveau = "+ str(niveau)
	#print " \n- periode = "+ str(x)
	
	champs_k,chaine = tri_comm(communities,taillemin, taillemax, kmin)#on fait un tri sommaire en fonction de la taille et du kmin
	info[niveau]=chaine
	champs = flat_comm(champs_k,years_bins)#on enleve l'overlap et on remet tout ça dans un ordre agréable
	
	#extension
	seuil_aggregation=0.2
	if niveau==1:
		distance_champ=dist_mat
	champs = extension(champs,distance_champ,years_bins,CF_weight,seuil_aggregation)
	# on apparie en calculant un score liant chaque terme aux clusters: score(terme, champ)  = somme_{elements du cluster} [d(terme,elements du cluster)/(somme_{tous les termes} d(element du cluster, tous les termes))] / somme_{voisins du terme} d(terme,voisins)/poids_total_entrant(voisins)
	nb_champs  = 0
	nb_champs_min = 100000
	
	for x,y in champs.iteritems():
		print 'niveau: '+str(niveau)+ ',periode : '+str(x) + ', ' + str(len(y)) + ' champs'
		lenchampsfinal[(niveau,x)]=len(y)
		nb_champs_min=min(nb_champs_min,len(y))
	if nb_champs_min==0 or  len(champs)==0:
		print 'Attention: aucun champ au niveau ' + str(niveau)
		if niveau==1:
			print 'VEUILLEZ CHANGER VOS PARAMETRES DE CLUSTERISATION, AUCUN CLUSTER\n'
		fini=0
		
	
	if fini>0:
		noeuds_presents = []
		for x in dico_transition.values():
			for xx in x:
				if not xx in noeuds_presents:
					noeuds_presents.append(xx)
		couverture ='niveau ' + str(niveau) +' : '+ str(len(noeuds_presents)) + ' noeuds présents dans la reconstruction sur ' + str(len(dico_termes.keys()))			
		print couverture
		text = text + couverture + '\n'
		fonctions.ecrire_dico(champs,dico_transition,dico_termes,niveau+1)#ecrit le dictionaire de transition pour la prochaine etape
		scores = label_champs(champs,nb_label,dico_transition,dico_termes,dist_mat,type_score)#on calcule le label des champs		
		#afficher_tous_champs(champs,scores,nb_label,sep_label,dico_termes,dico_transition)#on affiche tout ça.		
		#type_distance='max','moy' ou 'min'
		type_distance='moy'
		distance_champ=fonctions.map_champs(champs,dist_mat,'moy')
		#print distance_champ
		distance_champ_edges_list=edges_list(distance_champ)
		#version des distances sans la limitation degmax.
		fonctions.ecrire_reseau_CF(distance_champ,years_bins,dist_type,seuil_net_champ,niveau+1)		 
		
		#print '\n'
		#print distance_champ_edges_list
		distance_champ_edges_list_seuil=seuiller(distance_champ_edges_list,degmax)
		#print '\n'
		#print distance_champ_edges_list_seuil
		distance_champ = edges_list_reverse(distance_champ_edges_list_seuil)
		#print '\n'
		#print distance_champ
		legende_noeuds,legende_noeuds_id=gexf_champ(years_bins,scores,champs,nb_label,dico_termes,sep_label,dist_type,distance_champ,niveau,seuil_net_champ)
		fonctions.dumpingin(champs,'champs_'+str(niveau))
		fonctions.dumpingin(distance_champ,'distance_champ_'+str(niveau))	
		fonctions.ecrire_legende(champs,legende_noeuds,legende_noeuds_id,niveau+1,years_bins)
		fonctions.ecrire_reseau(distance_champ,years_bins,dist_type,seuil_net_champ,niveau+1,legende_noeuds)				
print "niveau vide!"



maps_union.union_map(2,seuil_net_champ)
#print lenchampsfinal.keys()
logfile = open(Cfinderexport_name(0,0,degmax),'a')
for x,y in info.iteritems():
	text= text + '\n'
	text = text+ 'niveau: '+str(x) + '\n'
	inter=-1
	for ligne in y:
		if '*** periode: ' in ligne:
			ligne_v = ligne.split('*** periode: ')
			inter = int(ligne_v[1])
			
		text=text+ ligne + '\n'
		if inter>-1:
			text=text+ '*** on a conserve ' + str(lenchampsfinal[(x,inter)])	+' champs sur...' + '\n'
			inter=-1
	print text
	logfile.write(text)	
