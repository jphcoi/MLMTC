from hcluster import pdist, linkage, dendrogram,centroid,weighted
import numpy
from numpy.random import rand
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

X = rand(5,2)
print X

X[0:3,:] *= 50
print X
Y = pdist(X)
print Y
Z = weighted(Y)
print Z
hh = dendrogram(Z)
print hh 



plt.show()
