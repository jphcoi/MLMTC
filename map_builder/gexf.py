# -*- coding: utf-8 -*-
import datetime
import tenjin
from tenjin.helpers import *   # or escape, to_str
engine = tenjin.Engine()

def gexf_builder(nodes,edges,sortie,level):
	gexf = {
            'description' : "",
            'creators'    : ["jp"],
            'type'        : 'static'
			}

	gexf.update({
                    'date' : "%s"%datetime.datetime.now().strftime("%Y-%m-%d"),
		            'attrnodes'   : { 'category' : 'string',},
		            'attredges'   : { 'cooc' : 'integer' },
                    'nodes' : nodes,
                    'level' : level,
                    'edges' : edges})


	# renders gexf
	result = engine.render('gexf.template.xml',gexf)

	f = open(sortie,"w+")
#	print '++++++++++++++++gexf: fichier '+sortie + ' ecrit '
	f.write(result)

def gexf_builder_3d(nodes,edges,sortie,level,time,attribut,sonsbis,fathersbis):
	
	gexf = {
            'description' : "",
            'creators'    : ["jp"],
            'type'        : 'static'

			}

	gexf.update({
                    'date' : "%s"%datetime.datetime.now().strftime("%Y-%m-%d"),
		            'attrnodes'   : { 'niveau' : 'string','temps':'string','url':'string','sonsbis':'string','fathersbis':'string'},
		            'attredges'   : { 'temps' : 'string' },
                    'nodes' : nodes,
                    'level' : level,
					'time' : time,
					'attribut' : attribut,
					'sonsbis' : sonsbis,
					'fathersbis' : fathersbis,
                    'edges' : edges})

	# renders gexf
	result = engine.render('gexf.template3d.xml',gexf)

	f = open(sortie,"w+")
	print '++++++++++++++++gexf: fichier '+sortie + ' ecrit '
	f.write(result)
