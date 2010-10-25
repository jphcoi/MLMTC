#!/usr/bin/env python
# encoding: utf-8
"""
class_def.py

Created by Jean philippe cointet  on 2010-10-05.
"""
import sys
class Generali(object):
	"""Class Terme"""
	def __init__(self):
		pass
	def __eq__(self, other) : 
		return self.__dict__ == other.__dict__
	
class Terme(Generali):
	"""Class Terme"""
	def __init__(self,index,label):
		"""Method docstring."""
		self.index = index
		self.label=label
	def __str__(self):
		"""Method docstring."""
		return "Terme: index({0}), label({1})".format(self.index, self.label)
	def get_label(self):
		return self.label
	def get_index(self):
		return self.index
	
class Dictionnaire_Terme(Generali):
	"""Class Dictionnaire de Terme"""
	def __init__(self,liste_termes):
		"""Method docstring."""
		print 'importation du dictionnaire des termes'
		self.liste_termes = liste_termes
	def __str__(self):
		"""Method docstring."""
		return "Liste de Termes longueur: {0}".format(str(len(self.liste_termes))) 	

	
class Liste_termes(Generali):
	"""Class Liste de Terme"""
	def __init__(self,liste_termes):
		self.liste_termes = liste_termes
	def afficher_liste_termes(self):
		chaine =''
		for x in self.liste_termes:
			chaine = chaine + ' ' + str(x.label) + ';' 
		return chaine[:-1]
	def concatener_liste_termes(liste_liste_termes):
		liste_termes_concatenes=[]
		for liste_termes in liste_liste_termes:
			for ter in liste_termes.liste_termes:
				liste_termes_concatenes.append(ter)
		return Liste_termes(liste_termes_concatenes)


# def addnfields(fields_liste,idx,inter):
# 	index=idx
# 	periode = fields_liste[0].periode
# 	fields_liste_liste_termes=[]
# 	nivel = [] 
# 	for field in fields_liste:
# 		fields_liste_liste_termes.append(field.termes)
# 		for niv in field.niveau:
# 			nivel.append(niv)
# 	termes = Liste_termes.concatener_liste_termes(fields_liste_liste_termes)
# 	termes_ids =  map(Terme.get_index,termes.liste_termes)
# 	return construire_champ(termes_ids,index,inter,nivel)
# 	
# 		
		 
			
class Champ(Generali):
	"""Class Champ."""
	def __init__(self,index,periode,niveau,label,termes,poids):
		"""Method docstring."""
		self.index = index
		self.periode=periode
		#niveau denombre le nombre de clusters sous-jacents
		self.niveau=niveau
		self.label=label
		self.termes=termes
		self.poids = poids
	def get_label(self):
		return self.label
	def get_periode(self):
		return self.periode
	def __str__(self):
		"""Method docstring."""
		return "Champ: niveau({0}), periode({1}), label({2},index({3}))".format(self.niveau, self.periode, map(Terme.get_label,self.label.liste_termes),self.index)
	def print_elements(self):
		"""Method docstring."""
		chaine  = '\n\t* champ de la periode ' + str(self.periode)+ ' de poids: ' + str(len(self.poids))+ ' dont les elements sont: '
		chaine =  chaine+self.termes.afficher_liste_termes()
		chaine = chaine + ' et le label: ' + Liste_termes.afficher_liste_termes(self.label)
		return chaine		
		
class Tube(Generali):
	def __init__(self,liste_champs,label):
		"""Method docstring."""
		self.liste_champs = liste_champs
		self.label=label
	def print_elements(self):
		"""Method docstring."""
		chaine  = '\nTube de label: '+ Liste_termes.afficher_liste_termes(self.label) +' dont les ' + str(len(self.liste_champs))+ ' champ(s) est (sont): '
		return chaine  +', '.join(map(Champ.print_elements,self.liste_champs))
		
class Tube_layout(Generali):
	def __init__(self,tube):
		"""Method docstring."""
		self.tube = tube
		self.position=position
		self.epaisseur = epaisseur
	def get_position(self):
		return self.position
	
class Network(Generali):
	"""Class Network, il peut être composé de champs ou de termes"""
	def __init__(self,champs_liste,champs_dist):
		"""Method docstring."""
		self.champs_liste = champs_liste
		self.champs_dist = champs_dist
	def __str__(self):
		"""Method docstring."""
		return "Network: nombre de champs({0}), nombre de liens({1})".format(len(self.champs_liste), len(self.champs_dist))
	def afficher_champs(self):
		for champ in self.champs_liste:
			champ.print_label()