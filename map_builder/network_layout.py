#!/usr/bin/python
# -*- coding: utf-8 -*- 
# needs mayavi2
# run with ipython -wthread
import networkx as nx

import numpy as np
try:
	import matplotlib.pyplot as plt
except:
	pass
import pyparsing
import sqlite3
import random
import math
from copy import deepcopy
import jsonpickle
import parameters
path_req=parameters.path_req

#import layout


class Tube:
	pass

class Edge:
	pass
	
def renormalisation(vpos,periodes):
	xmax,xmin,largeur = {},{},{}
	for inter in periodes:
		xmax[inter] = 0.
		xmin[inter] = 1.
	
	for x in vpos.values():
		xmax[x[1]] = max(x[0],xmax[x[1]])
		xmin[x[1]] = min(x[0],xmin[x[1]])

	for inter in periodes:
		largeur[inter] = xmax[inter]-xmin[inter]
	vpos_norm = {}
	for u,x in vpos.iteritems():
		x[0]=(x[0] - xmin[x[1]] )/largeur[x[1]]
		vpos_norm[u]=x
	return vpos_norm

def renormalisation_globale(vpos):
	#on rajoute une fonction pour empêcher un noeud de partir a perpete
	xmax,xmin,largeur =0.,1.,0.
	for x in vpos.values():
		xmax = max(x[0],xmax)
		xmin = min(x[0],xmin)
	largeur = xmax-xmin
	vpos_norm = {}
	for u,x in vpos.iteritems():
		x[0]=(x[0] - xmin )/largeur
		vpos_norm[u]=x
	solong=0.2	
	nb_voisins_min=2
	for u,x1 in vpos_norm.iteritems():
		voisins=0
		for v,x2 in vpos_norm.iteritems():
			if x2[1] == x1[1] and u!=v:
				if abs(x2[0]-x1[0]) <solong: 
					voisins += 1#dist_min = min(dist_min,abs(x2[0]-x1[0]))
		
		if voisins < nb_voisins_min:
			print '*************ca derive*************'
			if x1[0]<0.5:
				vpos_norm[u][0] += solong
			else:
				vpos_norm[u][0] -= solong
	return vpos_norm

def crosscount(edge1,edge2,vpos):
  # Convert the number list into a dictionary of person:(x,y) 
#	loc=dict([(people[i],(v[i*2],v[i*2+1])) for i in range(0,len(people))]) 
#	total=0 
	# Loop through every pair of links 
#	for i in range(len(links)): 
#		for j in range(i+1,len(links)): 
# Get the locations 
	#print edge1
	u1 = edge1[0]
	v1 = edge1[1]
	u2 = edge2[0]
	v2 = edge2[1]
	(x1,y1),(x2,y2)=vpos[u1],vpos[v1]
	(x3,y3),(x4,y4)=vpos[u2],vpos[v2]
	den=(y4-y3)*(x2-x1)-(x4-x3)*(y2-y1)

	if abs(den)>0:
		ua=((x4-x3)*(y1-y3)-(y4-y3)*(x1-x3))/den 
		ub=((x2-x1)*(y1-y3)-(y2-y1)*(x1-x3))/den
	# 	# If the fraction is between 0 and 1 for both lines 
	# 	# then they cross each other 
		if ua>0 and ua<1 and ub>0 and ub<1: 
			return 1 
		else:
			return 0
	else:
		return 0
	# (x1,y1),(x2,y2)=pos[links[i][0]],loc[links[i][1]] 
	# (x3,y3),(x4,y4)=loc[links[j][0]],loc[links[j][1]] 
	# den=(y4-y3)*(x2-x1)-(x4-x3)*(y2-y1) 
	# # den==0 if the lines are parallel 
	# if den==0:
	# 	# Otherwise ua and ub are the fraction of the 
	# 	# line where they cross 
	# 	ua=((x4-x3)*(y1-y3)-(y4-y3)*(x1-x3))/den 
	# 	ub=((x2-x1)*(y1-y3)-(y2-y1)*(x1-x3))/den
	# 	# If the fraction is between 0 and 1 for both lines 
	# 	# then they cross each other 
	# 	if ua>0 and ua<1 and ub>0 and ub<1: 
	# 		total+=1 

# 
# def repulsion(vpos,G,epaisseur_0,gamma = 0.004):
# 	vital_area = 0.01
# 	alpha = 0.001
# 	numero = 0
# 	disp_v = []
# 	moyenne_v=[]
# 	for v in G:
# 		for u in G:
# 			numero =numero +1
# 			if vpos[u][1] == vpos[v][1] and u!=v:# and (vpos[v][1]==5 or  vpos[v][1]==2):
# 				x_u = vpos[u][0]
# 				x_v = vpos[v][0]
# 				x_moy = (x_u+x_v)/2.
# 				e_u = epaisseur_0[u]
# 				e_v = epaisseur_0[v]
# 				if x_v == x_u:
# 					vpos[v][0] = vpos[v][0] + 0.000001
# 					vpos[u][0] = vpos[u][0] - 0.000001
# 					delta_x_0 = 0.000002
# 				else:
# 					delta_x_0= x_v - x_u
# 				
# 				epaisseur_uv=(e_v+e_u)*gamma
# 				if x_u<x_v:
# 					ordre = 1 # u puis v					
# 				else:
# 					ordre = 0 # v puis u
# 					delta_x_0=-delta_x_0
# 				delta_x = delta_x_0-epaisseur_uv 
# 
# 				if delta_x<vital_area:
# 					
# 					#disp_x = min(0.002,alpha/(math.fabs(delta_x))**2)
# 					disp_x = (math.fabs(delta_x) + vital_area)/2
# 					disp_x = vital_area
# 					#disp_x = vital_area*2
# 					disp_v.append(disp_x)
# 					moyenne_v.append(x_moy)
# 					print delta_x,delta_x_0, epaisseur_uv, disp_x
# 					#if numero <300:
# 					#	print delta_x_0,delta_x,disp_x,math.fabs(delta_x)					
# 					
# 	mem = 1	
# 	for disp_x,x_moy in zip(disp_v,moyenne_v):
# 		print x_moy,disp_x
#  	vpos2=deepcopy(vpos)
# 	for w in G:
# 		for disp_x,x_moy in zip(disp_v,moyenne_v):
# 			if 1: #vpos[w][1]==5 or  vpos[w][1]==2:
# 				distance = abs(x_moy-vpos[w][0])
# 				deplacement=alpha*disp_x / math.pow(max(vital_area,distance),2.)
# 				if vpos[w][0]<x_moy:
# 					vpos2[w][0] = vpos2[w][0] - deplacement
# #					print "deplacement" + str(deplacement)
# 				elif vpos[w][0]>x_moy:
# 					vpos2[w][0] = vpos2[w][0] + deplacement
# 				else:
# 					print 'brisqkslqmlksqmlkqds'
# 		#vpos = renormalisation_globale(vpos)
# 	return vpos2

def mean(numberList):
    floatNums = [float(x) for x in numberList]
    return sum(floatNums) / len(numberList)


def repu(G,vpos,v,epaisseur_0,displacement_max):
	vital_area = 0.008
	alpha = 0.000003
	gamma = 0.0004
	max_e=0
	for u in G:
		if vpos[u][1] == vpos[v][1] and u!=v:
			x_u = vpos[u][0]
			x_v = vpos[v][0]
			if abs(x_u-x_v)<0.2:
				x_moy = (x_u+x_v)/2.
				e_u = epaisseur_0[u]
				e_v = epaisseur_0[v]
				if x_v == x_u:
					vpos[v][0] = vpos[v][0] + 0.000001
					vpos[u][0] = vpos[u][0] - 0.000001
					delta_x_0 = 0.000002
				else:
					delta_x_0= x_v - x_u
				epaisseur_uv=(e_v+e_u)*gamma
				#max_e = max(e_v * gamma,max_e)
				if x_u<x_v:
					ordre = 1 # u puis v				    	
				else:
					ordre = 0 # v puis u
					delta_x_0=-delta_x_0
				delta_x = delta_x_0-epaisseur_uv
				if delta_x<0:
					deplacement = vital_area-delta_x
				else:
					deplacement=alpha / math.pow(max(vital_area,delta_x),2.)*displacement_max
				#if delta_x<0:
				#	deplacement= vital_area + epaisseur_uv/2
				if vpos[u][0]<x_moy:
					vpos[u][0] = vpos[u][0] - deplacement
					#print "deplacement" + str(deplacement)
				elif vpos[u][0]>x_moy:
					vpos[u][0] = vpos[u][0] + deplacement
				#print 'repulsion de ' + str(deplacement)
	#print max_e
	return vpos
	
	
def move_edge(edge,vpos,epaisseur_0,G,syn_coeff,dia_coeff,displacement_max,beta,disp_vect,i):
	u = edge[0]
	v = edge[1]
	x_u = vpos[u][0]
	x_v = vpos[v][0]
	e_u = epaisseur_0[u]
	e_v = epaisseur_0[v]
	
	#attraction							
	stre = G[v][u]['weight']
	type_lien  = G[v][u]['key']#0 synchrone
	if type_lien==1:
		#stre=stre*math.sqrt(rect)
		stre = dia_coeff/(syn_coeff+dia_coeff)*stre
	else:
		#stre=stre/math.sqrt(rect)				
		stre = syn_coeff/(syn_coeff+dia_coeff)*stre
	if x_u<x_v:
		ordre = 1
		delta_x_0= x_v - x_u
	else:
		ordre = 0
		delta_x_0= x_u - x_v
	#delta_x_0 = min(delta_x_0,1-delta_x_0)#espace cyclique
	disp_x = min(delta_x_0,displacement_max*beta*stre*math.fabs(delta_x_0))

	temp = disp_vect[i]
	#if disp_x != 0.:
	temp.append(abs(disp_x))
	disp_vect[i] = temp

	#on prend en compte l'inertie des noeuds
	degu = G.degree(u, weighted=True)
	degv = G.degree(v, weighted=True)
	coeffu = degv/(degu+degv)
	coeffv = degu/(degu+degv)
	if ordre==0:
		
		vpos[u][0]=vpos[u][0]-disp_x * coeffu
		vpos[v][0]=vpos[v][0]+disp_x * coeffv
	else:
		vpos[u][0]=vpos[u][0]+disp_x * coeffu
		vpos[v][0]=vpos[v][0]-disp_x * coeffv
	
	#repulsion								
	vpos = repu(G,vpos,v,epaisseur_0,displacement_max)
	return vpos,disp_vect	
	
		
def spring_layout_1d(G, periodes,epaisseur,iterations=20, dim=2, node_pos=None):
	epaisseur_0={}
	for u,e in epaisseur.iteritems():
		epaisseur_0[u] =np.power(epaisseur[u],1)

	"""Spring force model layout"""
	beta = 1. #coefficient d'attraction
	gamma = 0.0008 # evitement overlap
	vpos=node_pos
	disp_vect={}
	displacement_max_v = [float(iterations-x)/float(iterations) for x in range(iterations)]

	#first round considering only synchronous links
	print 'consider first synchronous links'
	for i in range(0,iterations):
		print "iteration:" + str(i) +'/'+str(iterations)
		dia_coeff=0.
		syn_coeff=10.
		disp_vect[i]=[]
		#colding_speed = 0.5
		#displacement_max = np.power(20/(float(i+1)),colding_speed)
		displacement_max=displacement_max_v[i]
		print "disp_max:" +str(displacement_max)
		edges_list = [e for e in G.edges_iter()]
		for edge in edges_list:
			vpos,disp_vect=move_edge(edge,vpos,epaisseur_0,G,syn_coeff,dia_coeff,displacement_max,beta,disp_vect,i)
		vpos = renormalisation_globale(vpos)
		print 'deplacement total: '+ str(sum(disp_vect[i]))   + '\tdeplacement moyen: ' + str(mean(disp_vect[i])) + '\tdeplacements positifs moyens: ' + str(mean([x for x in disp_vect[i] if x>0]))
	
	print 'and add then asyncrhonous connections.'	
	iterations=iterations*2
	for i in range(0,iterations):
		print "iteration:" + str(i) +'/'+str(iterations)
		dia_coeff=40.
		syn_coeff=20.
		disp_vect[i]=[]
		#colding_speed = 0.5
		#displacement_max = np.power(20/(float(i+1)),colding_speed)
		displacement_max=displacement_max_v[i/2]
		print "disp_max:" +str(displacement_max)
		edges_list = [e for e in G.edges_iter()]
		for edge in edges_list:
			vpos,disp_vect=move_edge(edge,vpos,epaisseur_0,G,syn_coeff,dia_coeff,displacement_max,beta,disp_vect,i)
		vpos = renormalisation_globale(vpos)
		print 'deplacement total: '+ str(sum(disp_vect[i]))   + '\tdeplacement moyen: ' + str(mean(disp_vect[i])) + '\tdeplacements positifs moyens: ' + str(mean([x for x in disp_vect[i] if x>0]))
	
	return vpos



	

def plot_graph(liens_totaux_syn,liens_totaux_dia,clusters):
	
	#on initialise le graphe
	G=nx.Graph()

	nb_iterations=40
	forces,edge_colors=[],[]
	
	
	
	for lien in liens_totaux_syn:
		G.add_edge(int(lien[0]), int(lien[1]), weight = float(lien[2]),key = 0)
		G.add_edge(int(lien[1]), int(lien[0]), weight = float(lien[2]),key = 0)
		forces.append(4.5*float(lien[2]))
		forces.append(4.5*float(lien[2]))

	for lien in liens_totaux_dia:
		G.add_edge(int(lien[0]), int(lien[1]), weight =  float(lien[2]),key = 1)
		G.add_edge(int(lien[1]), int(lien[0]), weight =  float(lien[2]),key = 1)
		forces.append(4.5*float(lien[2]))
		forces.append(4.5*float(lien[2]))
	vpos=nx.random_layout(G, dim=2)

	print vpos
	epaisseur = {}
	periodes=[]
	vert_pos={}
	labels={}

	for k,row in clusters.iteritems():
		periode=int(row['periode'])
		labels[k] = k
		vpos[k][1]=periode
		if not periode in periodes:
			periodes.append(periode)
		try:
			epaisseur[k] = 4+int(4 * float(row['epaisseur']))
		except:
			epaisseur[k] = 4
		vert_pos[k] = periode
	#normalisation des épaisseurs:
	epaisseur_norm={}
	width_total = sum(epaisseur.values())
	for k,width in epaisseur.iteritems():
		epaisseur_norm[k] = float(width) / width_total * 1000.
	epaisseur=epaisseur_norm
	print 'order'
	#print G.order()
	vpos_0 = deepcopy(vpos)

	print "computing graph layout"	
	#print vpos

	#pos = layout.spring_layout(G,vert_pos,dim=2,pos=None,fixed=None,iterations=500,weighted=True,scale=1)
	pos = spring_layout_1d(G,periodes,epaisseur,iterations=nb_iterations,dim=2,node_pos=vpos_0)
	epaisseur_0={}
	for u,e in epaisseur.iteritems():
		epaisseur_0[u] =np.power(epaisseur[u],1)

	for x in G.edges(data=True):
		if x[2]['key']==0:
			G.remove_edge(*x[:2])
	forces_plot=[]
	for x in forces:
		forces_plot.append(x*1.4)
#	nx.draw_networkx_edges(G,pos,None,width=forces_plot)
#	nx.draw_networkx_nodes(G,pos,None,epaisseur.values())
	
	#nx.draw_networkx_labels(G,pos,labels,font_size=12,font_color='blue')
	print 'labels added'
#	i = random.randint(1,10)
#	plt.savefig(path_req + str(i) + '.png')
	return G,epaisseur_0,pos


def get_pos(liens_totaux_syn,liens_totaux_dia,clusters):
	G,epaisseur_0,pos=plot_graph(liens_totaux_syn,liens_totaux_dia,clusters)
	return pos

def plot_graph_json(liens_totaux_syn,liens_totaux_dia,clusters,label_edges):
	print clusters
	G,epaisseur,pos = plot_graph(liens_totaux_syn,liens_totaux_dia,clusters)
	steps = 0

	r = {}
	r["meta"] = {}
	r["nodes"] = []
	r["edges"] = []


	r["meta"]["tubes_count"] = len(pos)
	
	for n in pos:
		c = Tube()

		c.i = n
		c.x = float(pos[n][0])
		c.y = float(pos[n][1])
		c.width = int(epaisseur[n])
		try:
			print clusters[n]['label_node']
		except:
			print 'pas de label tube'
		c.label = clusters[n]['label_node']
		
		#c.contain= ? 
		#c.contained_by= ? 
		c.level = 0
		#steps = max(steps, c.y)

		r["nodes"].append(c)

	for edge,edge_label in zip(liens_totaux_dia,label_edges):
		#structure objet
		e= Edge()
		e.node_parent=edge[0]
		e.node_child=edge[1]
		if edge[2]>0.5:
			e.weak=1
		else:
			e.weak=0
		e.label= edge_label
		#e.node_label=?
		#e.weak=1/0
		r["edges"].append(e)
		#r["edges"].append( ( e[0], e[1]) )
	#	r["edges"].append( ( e[0], e[1] ) )

	#r["meta"]["steps"] = int(steps + 1)
	#r["meta"]["start"] = ?
	#r["meta"]["step"] = ?
	#r["meta"]["depth"] = ?
	print jsonpickle.encode(r)