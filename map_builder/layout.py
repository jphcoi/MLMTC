"""
******
Layout
******

Node positioning algorithms for graph drawing.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nDan Schult(dschult@colgate.edu)"""
#    Copyright (C) 2004-2009 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['circular_layout',
           'random_layout',
           'shell_layout',
           'spring_layout',
           'spectral_layout',
           'fruchterman_reingold_layout']

import networkx as nx


def _rescale_layout(pos,scale=1):
    # rescale to (0,pscale) in all axes

    # shift origin to (0,0)
    lim=0 # max coordinate for all axes
    for i in range(pos.shape[1]):
        pos[:,i]-=pos[:,i].min()
        lim=max(pos[:,i].max(),lim)
    # rescale to (0,scale) in all directions, preserves aspect
    for i in range(pos.shape[1]):
        pos[:,i]*=scale/lim
    return pos



def fruchterman_reingold_layout(G,vert_pos,dim=2,
                                pos=None,
                                fixed=None,
                                iterations=50,
                                weighted=True,scale=1):
    """Position nodes using Fruchterman-Reingold force-directed algorithm. 

    Parameters
    ----------
    G : NetworkX graph 

    dim : int 
       Dimension of layout

    pos : dict
       Initial positions for nodes as a dictionary with node as keys
       and values as a list or tuple.  

    fixed : list
      Nodes to keep fixed at initial position.


    iterations : int
       Number of iterations of spring-force relaxation 

    weighted : boolean
        If True, use edge weights in layout 

    scale : float
        Scale factor for positions 

    Returns
    -------
    dict : 
       A dictionary of positions keyed by node

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> pos=nx.spring_layout(G)

    # The same using longer function name
    >>> pos=nx.fruchterman_reingold_layout(G)
    
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError("fruchterman_reingold_layout() requires numpy: http://scipy.org/ ")
    if fixed is not None:
        nfixed=dict(list(zip(G,list(range(len(G))))))
        fixed=np.asarray([nfixed[v] for v in fixed])

    if pos is not None:
        pos_arr=np.asarray(np.random.random((len(G),dim)))
        for n,i in zip(G,list(range(len(G)))):
            if n in pos:
                pos_arr[i]=np.asarray(pos[n])
    else:
        pos_arr=None

    if len(G)==0:
        return {}
    if len(G)==1:
        return {G.nodes()[0]:(1,)*dim}

    try:
        # Sparse matrix 
        if len(G) < 500:  # sparse solver for large graphs
            raise ValueError
        A=nx.to_scipy_sparse_matrix(G)
        pos=_sparse_fruchterman_reingold(A,vert_pos,
                                         pos=pos_arr,
                                         fixed=fixed,
                                         dim=dim,
                                         iterations=iterations,
                                         weighted=weighted)
    except:
        A=nx.to_numpy_matrix(G)
        pos=_fruchterman_reingold(A,vert_pos,
                                  pos=pos_arr,
                                  fixed=fixed,
                                  dim=dim,
                                  iterations=iterations,
                                  weighted=weighted)
    if fixed is None:
        pos=_rescale_layout(pos,scale=scale)
    return dict(list(zip(G,pos)))
	#return pos





spring_layout=fruchterman_reingold_layout


def _fruchterman_reingold(A,vert_pos,dim=2,
                          pos=None,
                          fixed=None,
                          iterations=50,
                          weighted=True):
    # Position nodes in adjacency matrix A using Fruchterman-Reingold  
    # Entry point for NetworkX graph is fruchterman_reingold_layout()
    try:
        import numpy as np
    except ImportError:
        raise ImportError("_fruchterman_reingold() requires numpy: http://scipy.org/ ")

    try:
        nnodes,_=A.shape
    except AttributeError:
        raise nx.NetworkXError(
            "fruchterman_reingold() takes an adjacency matrix as input")
    
    A=np.asarray(A) # make sure we have an array instead of a matrix
    if not weighted: # use 0/1 adjacency instead of weights
        A=np.where(A==0,A,A/A)

    if pos==None:
        # random initial positions
        pos=np.asarray(np.random.random((nnodes,dim)),dtype=A.dtype)
        #print pos
        pos2 = []
        for x,y in zip(pos,vert_pos.values()):
            pos2.append([x[0],y])
        pos = np.asarray(pos2,dtype=A.dtype)
        #print pos
    else:
        # make sure positions are of same type as matrix
        pos=pos.astype(A.dtype)

    # optimal distance between nodes
    k=np.sqrt(1.0/nnodes) 
    # the initial "temperature"  is about .1 of domain area (=1x1)
    # this is the largest step allowed in the dynamics.
    t=0.1
    # simple cooling scheme.
    # linearly step down by dt on each iteration so last iteration is size dt.
    dt=t/float(iterations+1) 
    #print pos.shape
    delta = np.zeros((pos.shape[0],pos.shape[0],pos.shape[1]),dtype=A.dtype)
    # the inscrutable (but fast) version
    # this is still O(V^2)
    # could use multilevel methods to speed this up significantly
    for iteration in range(iterations):
        # matrix of difference between points
        for i in range(pos.shape[1]-1):
            #print i,pos[:,i,None],pos[:,i]
            delta[:,:,i]= pos[:,i,None]-pos[:,i]
        # distance between points
        distance=np.sqrt((delta**2).sum(axis=-1))
        #print distance
        # enforce minimum distance of 0.02
        min_dist = 0.01
        distance=np.where(distance<0.01,0.01,distance)
        # displacement "force"
        displacement=np.transpose(np.transpose(delta)*\
                                  (k*k/distance**2-A*distance/k))\
                                  .sum(axis=1)
        # update positions            
        length=np.sqrt((displacement**2).sum(axis=1))
        length=np.where(length<0.01,0.1,length)
        delta_pos=np.transpose(np.transpose(displacement)*t/length)
        if fixed is not None:
            # don't change positions of fixed nodes
            delta_pos[fixed]=0.0
        pos+=delta_pos
        # cool temperature
        t-=dt

    return pos

