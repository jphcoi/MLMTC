import sys
fil = open("/Users/louiseduloquin/Desktop/decompte annuel.csv",'r')
#obtained via: select forme_principale,socsem.concept,count(socsem.concept),jours from socsem,concepts where jours>0 and concepts.id=socsem.concept group by socsem.concept,jours 
dico = {}
ans=[]
termes=[]
for ligne in fil.readlines():
	lignev= ligne.split(',')
	an = lignev[3]
	
	terme = lignev[0]#.replace('"','')
	if not terme in termes:
		termes.append(terme)
	compte = lignev[2]
	try:
		x= int(an)
		dico[(terme,x)]=compte
		ans.append(x)
		
	except:
		pass
filout = open("/Users/louiseduloquin/Desktop/decompteannuel.csv",'w')
debut = min(ans)
fin = max(ans)

filout.write(','+','.join(map(str,range(debut,fin)))+'\n')
for ter in termes:
	val=[]
	for an in range(debut,fin):
		val.append(dico.get((ter,an),'0'))
	filout.write(ter + ','.join(val)[1:]+'\n')
	
