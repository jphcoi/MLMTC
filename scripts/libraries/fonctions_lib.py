#!/usr/bin/env python
# encoding: utf-8
"""
fonctions_lib.py

Created by Jean philippe cointet on 2010-08-06.
"""

import sys
import os
import codecs
import pickle

def lire_fichier(filename):
	liste=[]
	file = codecs.open(filename,'r','utf-8')
	for ligne in file.readlines():
		if len(ligne)>1:
			liste.append(ligne[:-1])
	print str(len(liste)) + ' élements dans le fichier'
	return liste
	


def merge(d1, d2, merge=lambda x,y:y):
    """
    Merges two dictionaries, non-destructively, combining 
    values on duplicate keys as defined by the optional merge
    function.  The default behavior replaces the values in d1
    with corresponding values in d2.  (There is no other generally
    applicable merge strategy, but often you'll have homogeneous 
    types in your dicts, so specifying a merge technique can be 
    valuable.)

    Examples:

    >>> d1
    {'a': 1, 'c': 3, 'b': 2}
    >>> merge(d1, d1)
    {'a': 1, 'c': 3, 'b': 2}
    >>> merge(d1, d1, lambda x,y: x+y)
    {'a': 2, 'c': 6, 'b': 4}

    """
    result = dict(d1)
    for k,v in d2.iteritems():
        if k in result:
            result[k] = merge(result[k], v)
        else:
            result[k] = v
    return result

def merge_prod(d1, d2, merge=lambda x,y:y):
    """
    Merges two dictionaries, non-destructively, combining 
    values on duplicate keys as defined by the optional merge
    function.  The default behavior replaces the values in d1
    with corresponding values in d2.  (There is no other generally
    applicable merge strategy, but often you'll have homogeneous 
    types in your dicts, so specifying a merge technique can be 
    valuable.)

    Examples:

    >>> d1
    {'a': 1, 'c': 3, 'b': 2}
    >>> merge(d1, d1)
    {'a': 1, 'c': 3, 'b': 2}
    >>> merge(d1, d1, lambda x,y: x+y)
    {'a': 2, 'c': 6, 'b': 4}

    """
    result = {}
    for k,v in d2.iteritems():
        if k in d1:
            result[k] = merge(d1[k], v)
    return result

def dumpingin(data,datastr,requete):
	try:
		os.mkdir('../../inout/pkl/'+requete)
		print '../../inout/pkl/'+requete  + ' créé '
	except:
		pass
	output = open('../../inout/pkl/'+requete+'/'+datastr+'.pkl', 'wb')
	# Pickle dictionary using protocol 0.
	pickle.dump(data, output)
	output.close()


def dumpingout(datastr,requete):
	pkl_file = open('../../inout/pkl/'+requete+'/'+datastr+'.pkl', 'rb')
	data = pickle.load(pkl_file)
	return data
