datef = 2010
dated = 1991
fenetre = 2
overlap = 0
def build_total_window(dated,datef):
	total_window=[]
	for i in range(datef-dated+1):
		total_window.append(dated+i)
	return total_window

def build_years_bins(fenetre,dated,datef,overlap):
	total_window=build_total_window(dated,datef)
	print 'total_window'
	print total_window
	
	annee_min=-int((datef-dated+1)/(fenetre))*(fenetre-overlap)
	
	total_window_pert = total_window[:]
	print 'total_window_pert'
	print total_window_pert
	years_bins=[]
	year_bins=[]
	for i in range((datef-dated+1)/(fenetre)):
		print i
		window = total_window_pert[i*fenetre-overlap:(i+1)*fenetre]
		print window
		years_bins.append(window)
	for bins in years_bins:
		if len(bins)>0:
			year_bins.append(bins)
	return year_bins
		
years_bins = build_years_bins(fenetre,dated,datef,overlap)
print years_bins