#!/usr/bin/env python
# encoding: utf-8
"""
tubes_layout.py

Created by Jean-Philippe Cointet on 2010-10-05.
"""
import sys
sys.path.append("../scripts/libraries")
sys.path.append("../scripts")
import parameters
import fonctions_lib
years_bins = parameters.years_bins
name_bdd = parameters.name_bdd
name_data_real=parameters.name_data_real
from class_def import *
import fonctions 
resolution_niveau = 2
seuil_netermes=  0.4
resolution_continuite = 7
proj_thres=0.3
param_txt = name_data_real+'_res_niv_' + str(resolution_niveau) + '_seuil_netermes_' + str(seuil_netermes) +'_res_cont_'+str(resolution_continuite) +'_proj_thres_'+str(proj_thres)

try:
	tubes = fonctions.dumpingout(param_txt+'tubes')
	dyn_net_zoom = fonctions.dumpingout(param_txt+'dyn_net_zoom')
	res_intertemp_zoom = fonctions.dumpingout(param_txt+'res_intertemp_zoom')
	
except:
	import multi_tubes
	tubes,dyn_net_zoom,res_intertemp_zoom=multi_tubes.get_tubes(resolution_niveau,seuil_netermes,resolution_continuite	,proj_thres)
	
	
#tubes[seuil_intertemp][zoo] = liste de tubes

import multi_tubes
inter_temp_liste = tubes.keys()
zoom_niveau = tubes[inter_temp_liste[0]].keys()

#visualisation des données:
for seuil_inter,tubes_inter in tubes.iteritems():
	print 'seuil_inter: ' + str(seuil_inter)
	for zoo,tube_liste in tubes_inter.iteritems():
		nets = dyn_net_zoom[zoo]
		print 'zoo ' + str(zoo)
		for tube1 in tube_liste:
			for ch1 in tube1.liste_champs:
				for tube2 in tube_liste:
				#on cherche les distances entre éléments de tubes, juste pour vérif:
					for ch2 in tube2.liste_champs:
						if ch1.periode==ch2.periode:
							net = nets[ch1.periode]
							#print net
							#print '\t' + str((ch1,ch2))
							#print  '\n\t' + str(ch1.periode)
							#print  '\t' + str(Liste_termes.afficher_liste_termes(ch1.label))
							#print  '\t' + Champ.print_elements(ch1)
							distances  = net.champs_dist
							for couple in distances.keys():
								if (ch1,ch2)==couple:
									pass
									#print ' force ' + str(distances[couple]) + ' entre ' + str(ch1) + ' et ' +str(ch2)

def unique(liste):
	liste_u=[]
	for x in liste:
		if not x in liste_u:
			liste_u.append(x)
	return liste_u

def get_first(couple):
	return couple[0]

def get_second(couple):
	return couple[1]

def dict_init(keys):
	dicti={}
	for key in keys:
		dicti[key]=[]
	return dicti
	
def create_tube_linear(liste_champs):
	inters = unique(map(Champ.get_periode,liste_champs))
	annees = range(years_bins[inters[0]][0],years_bins[inters[-1]][-1]+1)
	tube_epaisseur= dict_init(annees)
	for champ in liste_champs:
		notices = champ.poids
		annees=years_bins[Champ.get_periode(champ)]
		epais = dict_init(annees)
		for notice in notices:
			epais[notice[1]]=epais[notice[1]]+[notice[0]]
		tube_epaisseur=fonctions_lib.merge(tube_epaisseur,epais,lambda x,y:unique(x+y))
	return tube_epaisseur

def create_tube(liste_champs):
	inters = unique(map(Champ.get_periode,liste_champs))
	annees = range(years_bins[inters[0]][0],years_bins[inters[-1]][-1]+1)
	tube_epaisseur= dict_init(annees)
	for champ in liste_champs:
		notices = champ.poids
		annees=years_bins[Champ.get_periode(champ)]
		epais = dict_init(annees)
	#	print notices
		for notice in notices:
			annee =notice[1] 
			notice_annee = notice[0]
			epais[annee]=epais[annee]+[notice_annee]
		tube_epaisseur=fonctions_lib.merge(tube_epaisseur,epais,lambda x,y:unique(x+y))
	return tube_epaisseur


	
def tranforme_points(tube_epaisseur,poid_total):
	points=[]
	annees= tube_epaisseur.keys()
	annees.sort()
	for an in annees:
		points.append((an,poid_total))
	annees.reverse()
	for an in annees:
		points.append((an,len(tube_epaisseur[an])+poid_total))
	points.append(points[0])
	return points


import svgfig
from svgfig import *
		
def create_svg(liste_points):
	window = svgfig.window(years_bins[0][0], years_bins[-1][-1], 0, 1000,width=100,height=100)
	#def window(xmin, xmax, ymin, ymax, x=0, y=0, width=100, height=100, xlogbase=None, ylogbase=None, minusInfinity=-1000, flipx=False, flipy=True):
	graph = svgfig.SVG("g", id="Tubes")
	labels = svgfig.SVG("g", id="Labels")
	for points in liste_points:
		poly = svgfig.Poly(points, "smooth", stroke="#eeeeee",  stroke_width="0.2",fill='#cccccc')##fill=self.rgb2hex(self.colors[layer])
		graph.append(poly.SVG(window))
		graph.append(poly.SVG(window))	
	graph.save("svg/tmp.svg")



#print res_intertemp_zoom

#on fait un test pour un seuil intertemporel nul et pour un niveau de zoom fixé à 0
tube_fin = tubes[inter_temp_liste[2]]
tube_fin_liste=tube_fin[0]
liste_points=[]
poid_total=0

for tube in tube_fin_liste[:]:
	liste_champs= tube.liste_champs
	#print liste_champs
	
	inters = map(Champ.get_periode,liste_champs)
	if not len(list(set(inters))) == len(inters):
	#	print liste_champs
	#	for ch in liste_champs:
	#		print ch.periode
	#	print 'branching occuring'
		tube_epaisseur =  create_tube(liste_champs)
		points = tranforme_points(tube_epaisseur,poid_total)
		#print points
		delta = max(map(get_second,points))
		liste_points.append(points)
		#print poid_total
		poid_total= delta+1
	else:
		if len(inters)>0:	
			#print inters
			#print 'no branching occuring'
			tube_epaisseur =  create_tube_linear(liste_champs)
			#print tube_epaisseur
			#print tranforme_points(tube_epaisseur,poid_total)
			points = tranforme_points(tube_epaisseur,poid_total)
			#print points
			delta = max(map(get_second,points))
			#liste_points.append(points)
			#print poid_total
			poid_total= delta+1
#for x in 	liste_points:
#	print x
create_svg(liste_points[:])
 
print tubes
print dyn_net_zoom
print res_intertemp_zoom