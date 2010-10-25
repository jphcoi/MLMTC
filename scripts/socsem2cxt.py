
def decoupe_segment(taille_total,taille_segment):
	decoupe = (taille_total/taille_segment)
	vec=[]
	for x in range(decoupe):
		vac = []
		for j in range(taille_segment):
			vac.append(j+x*taille_segment)
		vec.append(vac)
	vac= []
	for j in range(taille_total-decoupe*taille_segment):
		vac.append(j+decoupe*taille_segment)
	if len(vac)>0:
		vec.append(vac)
	return vec

print decoupe_segment(45,100)