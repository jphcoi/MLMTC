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
path_req = parameters.path_req
years_bins = parameters.years_bins
name_bdd = parameters.name_bdd
name_data_real=parameters.name_data_real
import numpy
from numpy.random import rand
from pylab import *

from class_def import *
import fonctions 
resolution_niveau = 10
seuil_netermes=  0.4
resolution_continuite = 2
proj_thres=0.3
param_txt = name_data_real+'_res_niv_' + str(resolution_niveau) + '_seuil_netermes_' + str(seuil_netermes) +'_res_cont_'+str(resolution_continuite) +'_proj_thres_'+str(proj_thres)

try:
	tubes = fonctions.dumpingout(param_txt+'tubessdqklsqkmlsdjslqdkjm')
	tubes = fonctions.dumpingout(param_txt+'tubes')
	dyn_net_zoom = fonctions.dumpingout(param_txt+'dyn_net_zoom')
	res_intertemp_zoom = fonctions.dumpingout(param_txt+'res_intertemp_zoom')
	
except:
	import multi_tubes
	tubes,dyn_net_zoom,res_intertemp_zoom=multi_tubes.get_tubes(resolution_niveau,seuil_netermes,resolution_continuite	,proj_thres)
	
print "*********cestbon********"	
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

def dict_init(keys,val=[]):
	dicti={}
	for key in keys:
		dicti[key]=val
	return dicti
	
def create_tube_linear(liste_champs):
	inters = unique(map(Champ.get_periode,liste_champs))
	#print inters
	annees = range(years_bins[inters[0]][0],years_bins[inters[-1]][-1]+1)
	tube_epaisseur = dict_init(annees)
	#print tube_epaisseur
	for champ in liste_champs:
		notices = champ.poids
		#print notices
		annees=years_bins[Champ.get_periode(champ)]
		epais = dict_init(annees)
		for notice in notices:
			epais[notice[1]]=epais[notice[1]]+[notice[0]]
		tube_epaisseur=fonctions_lib.merge(tube_epaisseur,epais,lambda x,y:unique(x+y))
	return tube_epaisseur

def print_l(dict):
	for x,y in dict.iteritems():
		print str(x)  + '\t' + str(len(y))

def create_tube(liste_champs):
	inters = unique(map(Champ.get_periode,liste_champs))
	annees = range(years_bins[min(inters)][0],years_bins[max(inters)][-1]+1)
	tube_epaisseur= dict_init(annees)

	for champ in liste_champs:
		notices = champ.poids
		annees=years_bins[Champ.get_periode(champ)]
		epais = dict_init(annees)
		for notice in notices:
			annee =notice[1] 
			notice_annee = notice[0]
			epais[annee]=epais[annee]+[notice_annee]
		tube_epaisseur=fonctions_lib.merge(tube_epaisseur,epais,lambda x,y:unique(x+y))
	return tube_epaisseur


	
def tranforme_points(tube_epaisseur,poid_total=0,type=''):
	points=[]
	annees= tube_epaisseur.keys()
	annees.sort()
	if type=='svg':
		for an in annees:
			points.append((an,poid_total))
		annees.reverse()
	for an in annees:
		points.append((an,len(tube_epaisseur[an])+poid_total))
	if type=='svg':
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
continuite=0
tube_fin = tubes[inter_temp_liste[continuite]]
print ' on regarde le seuil de continuite: ' +str(inter_temp_liste[continuite])

print tube_fin.keys()
#zoom_lev = 1
#print ' on regarde le niveau de zoom: ' +str(zoom_niveau[zoom_lev])
#tube_fin_liste=tube_fin[zoom_niveau[zoom_lev]]
for niv,tube_fin_liste in tube_fin.iteritems():
	niveau = zoom_niveau.index(niv)
	liste_points=[]
	poid_total=0
	label_tubes = []
	for tube in tube_fin_liste:
		liste_champs= tube.liste_champs
	
		#print liste_champs
		#print Tube.print_elements(tube)
		label_tube = Liste_termes.afficher_liste_termes(tube.label)
		label_tubes.append(label_tube)
		inters = map(Champ.get_periode,liste_champs)
		if not len(list(set(inters))) == len(inters):
		#	print liste_champs
		#	for ch in liste_champs:
		#		print ch.periode
		#	print 'branching occuring'
			tube_epaisseur =  create_tube(liste_champs)
			points = tranforme_points(tube_epaisseur,poid_total,'svg')
			#print points
			delta = max(map(get_second,points))
			liste_points.append(tranforme_points(tube_epaisseur))
			#print poid_total
			#poid_total= delta+1
		else:
			if len(inters)>0:	
				#print inters
				#print 'no branching occuring'
				tube_epaisseur =  create_tube_linear(liste_champs)
				#print tube_epaisseur
				#print tranforme_points(tube_epaisseur,poid_total)
				points = tranforme_points(tube_epaisseur,poid_total,'svg')
				liste_points.append(tranforme_points(tube_epaisseur))
			
				#print points
				delta = max(map(get_second,points))
				#liste_points.append(points)
				#print poid_total
				#poid_total= delta+1
	#for x in 	liste_points:
	#	print x

	# 
	# var years = [1850,1860,1870,1880,1900,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000];
	# 
	# var jobs = {
	# "Accountant / Auditor": {
	# men: [708,1805,1310,2295,11753,0,111209,181482,0,330352,425002,575667,661606,814842,866460],
	# women: [0,0,0,0,807,0,15746,14657,0,56117,112853,248441,452783,949683,1217596]
	# },
	# "Actor": {
	def to_dict(points):
		dic_points = {}
		for x in points:
			dic_points[x[0]]=int(x[1])
		return dic_points
		
	def create_js_bar(liste_points,label_tubes,niv):
		path_req_protovis = path_req + '/' + 'protovis'  + '/'
		if not os.path.isdir(path_req_protovis):
			os.makedirs(path_req_protovis)
		fichier = file(path_req_protovis+'jobs2-niv' +str(niv)+'.js','w')
		rge_y = range(years_bins[0][0], years_bins[-1][-1]+1)
		out = 'var years = ' + str(rge_y)+';'
		dict_0 = dict_init(rge_y,0)
		#print dict_0
		out = out + '\n'
		out = out + "var jobs = {" 
		for label,points in zip(label_tubes,liste_points):
			out = out + '\n"' + label[1:] + '"' + ': {'
			points_complets = fonctions_lib.merge(to_dict(points),dict_0,lambda x,y:x+y)
			points_ranges=[]
			for x in rge_y:
	 			points_ranges.append((points_complets[x]))
			out = out + '\nmen: '
			out = out + str(points_ranges)# + ',' + '\n'
			#print points_ranges
			#out = out + 'women: '		
			#out = out + str(points_ranges) + '\n'
			out = out + '},'
			#blank part to be blanked...
			# out = out + '\n"'  +label[1:4]+ '"' + ': {'
			# points_ranges=[]
			# for x in rge_y:
			#  			points_ranges.append(4)
			# print points_ranges
			# out = out + '\nmen: '
			# out = out + str(points_ranges)# + ',' + '\n'
			# out = out + '},'
		
		out = out[:-1]
		out = out + "\n};"
		fichier.write(out)
	#	print out	

	#print liste_points
	create_js_bar(liste_points,label_tubes,niveau)
	#create_html...
	#create_svg(liste_points[:])
 
# print tubes
# print dyn_net_zoom
# print res_intertemp_zoom