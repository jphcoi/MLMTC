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
import multi_tubes

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
resolution_continuite = 4
proj_thres=0.3
try:
	CF_weight0 = parameters.CF_weight0
except:
	CF_weight0=0.5
name_date = str(years_bins[0][0]) + '_' + str(years_bins[0][-1]) + '_'+ str(years_bins[1][0])+ '_'+str(years_bins[-1][-1])
param_txt = name_data_real+'_res_niv_' + str(resolution_niveau) + '_seuil_netermes_' + str(seuil_netermes) +'_res_cont_'+str(resolution_continuite) +'_proj_thres_'+str(proj_thres) +name_date  + str(CF_weight0)
print param_txt

try:
	#recalculer les tubes, alors lancer ligne suivante:
	#tubes = fonctions.dumpingout(param_txt+'tubessdqklsqkmlsdjslqdkjm')
	tubes = fonctions.dumpingout(param_txt+'tubes')
	#res_intertemp_zoom = fonctions.dumpingout(param_txt+'res_intertemp_zoom')
	#pas utile
	#dyn_net_zoom = fonctions.dumpingout(param_txt+'dyn_net_zoom')
	print 'bravo'
except:
	tubes,dyn_net_zoom,res_intertemp_zoom=multi_tubes.get_tubes(resolution_niveau,seuil_netermes,resolution_continuite,proj_thres)
	
	print "des tubes précédemments calculés ont été importés" 
#tubes[seuil_intertemp][zoo] = liste de tubes

inter_temp_liste = tubes.keys()
zoom_niveau_v = tubes[inter_temp_liste[0]]
#zoom_continuite = multi_tubes.build_zoom_log(resolution_continuite)

zoom_niveau=zoom_niveau_v.keys()

#visualisation des données:
visu=0
if visu==1:
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
								distances  = net.champs_dist
								for couple in distances.keys():
									if (ch1,ch2)==couple:
										pass

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
	
def print_l(dict):
	for x,y in dict.iteritems():
		print str(x)  + '\t' + str(len(y))

def find_tube_epaisseur(liste_champs):
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
		#version dans laquelle on ne compte qu'une fois les notice multiples
		#tube_epaisseur=fonctions_lib.merge(tube_epaisseur,epais,lambda x,y:unique(x+y))
		#version dans laquelle on compte n fois les notice multiples
		tube_epaisseur=fonctions_lib.merge(tube_epaisseur,epais,lambda x,y:(x+y))
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


def to_dict(points):
	dic_points = {}
	for x in points:
		dic_points[x[0]]=int(x[1])
	return dic_points
		
def create_js_bar(liste_points,label_tubes,niv,fichier):
	rge_y = range(years_bins[0][0], years_bins[-1][-1]+1)
	dict_0 = dict_init(rge_y,0)
	out =''
	for label,points in zip(label_tubes,liste_points):
		out = out + '\n"' + str(niv) + '*'  + label[1:] + '"' + ': {'
		points_complets = fonctions_lib.merge(to_dict(points),dict_0,lambda x,y:x+y)
		points_ranges=[]
		for x in rge_y:
 			points_ranges.append((points_complets[x]))
		out = out + '\n' + str(niv) + ':'
		out = out + str(points_ranges)# + ',' + '\n'
		out = out + '},'	
	fichier.write(out)


def export_jobs(continuite_test):
	tube_fin = tubes[inter_temp_liste[continuite_test]]
	print ' on regarde le seuil de continuite: ' +str(inter_temp_liste[continuite_test])
	inter_temp_liste_ord = inter_temp_liste
	inter_temp_liste_ord.sort()
	
	path_req_protovis = path_req + '/' + 'protovis'  + '/'
	if not os.path.isdir(path_req_protovis):
		os.makedirs(path_req_protovis)
	fichier = file(path_req_protovis+'jobs' +str(inter_temp_liste_ord.index(inter_temp_liste[continuite_test]))  +'.js','w')
	rge_y = range(years_bins[0][0], years_bins[-1][-1]+1)
	out = 'var years = ' + str(rge_y)+';'
	out = out + "var jobs = {" 
	fichier.write(out)

	for niv,tube_fin_liste in tube_fin.iteritems():
		niveau = zoom_niveau.index(niv)
		niv_ok = int(niv*resolution_niveau)
		print str(niv),str(niveau),str(niv_ok)
		liste_points=[]
		poid_total=0
		label_tubes = []
	
		for tube in tube_fin_liste:
			liste_champs= tube.liste_champs
			label_tube = Liste_termes.afficher_liste_termes(tube.label)
			label_tubes.append(label_tube)
			inters = map(Champ.get_periode,liste_champs)
			if 1:
				tube_epaisseur =  find_tube_epaisseur(liste_champs)
				points = tranforme_points(tube_epaisseur,poid_total,'svg')
				#print points
				delta = max(map(get_second,points))
				liste_points.append(tranforme_points(tube_epaisseur))	
		create_js_bar(liste_points,label_tubes,niv_ok,fichier)
	fichier.write("\n};")
 
	# print tubes
	# print dyn_net_zoom
	# print res_intertemp_zoom
	
for continuite_test in range(resolution_continuite):
	print continuite_test
	export_jobs(continuite_test)