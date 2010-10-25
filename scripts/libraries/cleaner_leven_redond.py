import codecs
for language in ['english','french']:
	for ause in ['no','']:
		filename =  ause + 'leven-classes_'+language+'.txt'
		filename_out =  ause + 'leven-classes_'+language+'o.txt'
		print '********************'
		print filename
		print '********************'
		
		file = codecs.open(filename,'r','utf-8')
		file_o = codecs.open(filename_out,'w','utf-8')
		
		remplacement = []
		for ligne in file.readlines():
			lignev = ligne[:-1].split('\t')
			try:
				fro = '_'.join(lignev[0].split('_')[1:])
				to = '_'.join(lignev[1].split('_')[1:])
				remplacement.append(fro + '\t' + to)
			except:
				pass

		for x in remplacement:
			file_o.write(x+'\n')
			
