import random
import numpy as np
import pandas as pd
import scanpy as sc
# import scanpy as sc # not in use, can be removed
import scanpy.external as sce
# import scvelo as scv # not in use, can be removed
#import ringity as rng
# import seaborn as sns # not in use, can be removed
import scipy.stats as ss
import matplotlib.pyplot as plt
# import gudhi as gd
# import torch
import plotly.express as px
import ringity as rng

from scipy.spatial import distance

# for building the boundary matrices
from scipy import sparse
from scipy.sparse import coo_matrix,diags

from sklearn.datasets import make_circles
from ripser import ripser
from persim import plot_diagrams

from tqdm import tqdm

from plotly.subplots import make_subplots
import plotly.graph_objects as go



#### ---- CIRCULAR COORDINATE FUNCTIONS ---- ####

def mod_p_cocycle(vals, p):
    """
    Given a cocycle, replace each value by its congruence class closest to zero mod p.

    Parameters
    ----------
    vals : np.array
        The cocycle to be modified. 
    p : int
        The modulus.

    Returns
    -------
    vals: np.array
        The modified cocycle.
    
    """
    vals = vals % p
    vals[vals > p/2] = vals[vals > p/2] - p
    return vals




# turn ripser type cocycle into a vectorized cochain
def vectorize(cocycle, simplices):

    """ 
    function to vectorize a cocycle

    Parameters
    ----------
        cocycle: np.array
            cocycle in the form of a list of [i,j,val] where i,j are the vertices
            and val is the value of the cocycle on the edge between i and j
    
    Returns
    -------
        cocycle_vec: np.array
            a cochain vectorized over the edges of the simplicial complex which agrees with the indexing in simplices
    """


    for k in range(len(cocycle)):
        [i,j,val] = cocycle[k,:]
        
        # correct orientation

        if i > j:
            i,j = j,i
            val = -val
            cocycle[k,:] = [i,j,val]

    # vectorize cocycle
    cocycle_vec = np.zeros(len(simplices[1]))
    for k in range(cocycle.shape[0]):

        [i,j,val] = cocycle[k,:]

        # check if edge is in simplices[1], if so, add value to vector
        # this is because we may need to restrict the cocycle to a subcomplex
        if frozenset([i,j]) in simplices[1].keys():
            cocycle_vec[simplices[1][frozenset([i,j])]] = val
    
    return cocycle_vec




# create ripser type cochain from a vectorized cochain
def devectorize(projection, simplices):
    
        """ 
        function to devectorize a cocycle
    
        Parameters
        ----------
            projection: np.array
                vectorized cocycle
        
        Returns
        -------
            cocycle: np.array
                cocycle in the form of a list of [i,j,val] where i,j are the vertices
                and val is the value of the cocycle on the edge between i and j
        """
    
        c = np.zeros((len(simplices[1]),3))
        for k in range(len(simplices[1])):
            [i,j] = np.sort(list(list(simplices[1])[k]))
            c[k,:] = [i,j,projection[k]]

        
        return c




# extract the simplices from the simplex tree
def extract_simplices(simplex_tree):
    """Extract simplices from a gudhi simplex tree.

    Parameters
    ----------
    simplex_tree: gudhi simplex tree

    Returns
    -------
    simplices: List of dictionaries, one per dimension d. The size of the dictionary
        is the number of d-simplices. The dictionary's keys are sets (of size d
        + 1) of the 0-simplices that constitute the d-simplices. The
        dictionary's values are the indexes of the simplices in the boundary
        and Laplacian matrices.
    """
    
    simplices = [dict() for _ in range(simplex_tree.dimension()+1)]
    for simplex, _ in simplex_tree.get_skeleton(simplex_tree.dimension()):
        k = len(simplex)
        simplices[k-1][frozenset(simplex)] = len(simplices[k-1])
    return simplices




# Build the boundary operators
def build_boundaries(simplices):
    """Build unweighted boundary operators from a list of simplices.

    Parameters
    ----------
    simplices: list of dictionaries
        List of dictionaries, one per dimension d. The size of the dictionary
        is the number of d-simplices. The dictionary's keys are sets (of size d
        + 1) of the 0-simplices that constitute the d-simplices. The
        dictionary's values are the indexes of the simplices in the boundary
        and Laplacian matrices.

    Returns
    -------
    boundaries: list of sparse matrices
       List of boundary operators, one per dimension: i-th boundary is in i-th position
    """
    boundaries = list()
    for d in range(1, len(simplices)):
        idx_simplices, idx_faces, values = [], [], []
        for simplex, idx_simplex in simplices[d].items():
            for i, left_out in enumerate(np.sort(list(simplex))):
                idx_simplices.append(idx_simplex)
                values.append((-1)**i)
                face = simplex.difference({left_out})
                idx_faces.append(simplices[d-1][face])
        assert len(values) == (d+1) * len(simplices[d])
        boundary = coo_matrix((values, (idx_faces, idx_simplices)),
                                     dtype=np.float32,
                                     shape=(len(simplices[d-1]), len(simplices[d])))
        
        
        boundaries.append(boundary)


    return boundaries




# a function that inputs data matrix, cocycle and threshold and outputs the circular coordinates
def circular_coordinates(data, cocycle, thresh, p = 3):
        
        """ 
        function to calculate the circular coordinates of a persistence diagram
        
        Parameters
        ----------
            data: np.array
                matrix of data
            cocycle: np.array
                cocycle in the form of a list of [i,j,val] where i,j are the vertices (output of ripser with do_cycles = True)
            thresh: float
                threshold for the persistence diagram, should be between birth and death time of the interval to which to cocycle belongs
            p: int
                prime number for the field
        
        Returns
        -------
            coordinates: np.array
                circular coordinates of the persistence diagram
        """
        
        # put cocycle values in the right congruence class mod p
        cocycle[:,2] = mod_p_cocycle(cocycle[:,2], 3)

        # build a simplex tree
        Rips_complex_sample = gd.RipsComplex(points = data, max_edge_length=thresh)
        st = Rips_complex_sample.create_simplex_tree(max_dimension=2)
        
        # extract simplices
        simplices = extract_simplices(st)

        # build the boundary matrices and laplacian
        boundaries = build_boundaries(simplices)
        laplacian = boundaries[0].T @ boundaries[0] + boundaries[1] @ boundaries[1].T
        
        # vectorize cocycle
        cocycle_vec = vectorize(cocycle, simplices)
        
        # calculate the 0 eigenvectors of the laplacian
        eigvals, eigvecs = sparse.linalg.eigsh(laplacian, k=1, which='SM')
        
        # calculate the projection
        projection = eigvecs[:,0].T @ cocycle_vec * eigvecs[:,0]
        for k in range(1,eigvecs.shape[1]):
             projection = projection + eigvecs[:,k].T @ cocycle_vec * eigvecs[:,k]
        
        # calculate the coordinates
        coordinates = np.linalg.lstsq(boundaries[0].T.toarray(), cocycle_vec - projection, rcond=None)[0] % 1
        
        return coordinates




# Import some plotting functions from the Ripser documentation examples

def drawLineColored(X, C):
    for i in range(X.shape[0]-1):
        plt.plot(X[i:i+2, 0], X[i:i+2, 1], c=C[i, :])

def plotCocycle2D(D, X, cocycle, thresh):
    """
    Given a 2D point cloud X, display a cocycle projected
    onto edges under a given threshold "thresh"
    """
    #Plot all edges under the threshold
    N = X.shape[0]
    t = np.linspace(0, 1, 10)
    c = plt.get_cmap('Greys')
    C = c(np.array(np.round(np.linspace(0, 255, len(t))), dtype=np.int32))
    C = C[:, 0:3]

    for i in range(N):
        for j in range(N):
            if D[i, j] <= thresh:
                Y = np.zeros((len(t), 2))
                Y[:, 0] = X[i, 0] + t*(X[j, 0] - X[i, 0])
                Y[:, 1] = X[i, 1] + t*(X[j, 1] - X[i, 1])
                drawLineColored(Y, C)
    #Plot cocycle projected to edges under the chosen threshold
    for k in range(cocycle.shape[0]):
        [i, j, val] = cocycle[k, :]

        i, j = int(i), int(j)
        
        if D[i, j] <= thresh:
            [i, j] = [min(i, j), max(i, j)]
            a = 0.5*(X[i, :] + X[j, :])
            plt.text(a[0], a[1], '%g'%val, color='b')
    #Plot vertex labels
    for i in range(N):
        plt.text(X[i, 0], X[i, 1], '%i'%i, color='r')
    plt.axis('equal')


### --- WEIGHTED CIRCULAR COORDINATES (Modified version from Paik et al. 2023) ---


def weighted_circular_coordinate(data, distance_matrix=False, ripser_result=False, prime=3, cocycle_n=None, eps=None,
                                 weight_ft: callable = None, return_aux=False):
    if not ripser_result:
        ripser_result = ripser(data, distance_matrix=distance_matrix, coeff=prime, do_cocycles=True)
    else:
        ripser_result = data

    dist_mat = ripser_result['dperm2all']
    n_vert = len(dist_mat)

    argsort_eps = np.argsort(np.diff(ripser_result['dgms'][1], 1)[:, 0])[::-1]
    if cocycle_n is None:
        cocycle_n = argsort_eps[0]
    else:
        cocycle_n = argsort_eps[cocycle_n]

    if eps is None:
        birth, death = ripser_result['dgms'][1][cocycle_n]
        eps = (birth + death) / 2

    # Delta
    edges = np.asarray((dist_mat <= eps).nonzero()).T
    n_edges = len(edges)
    I = np.c_[np.arange(n_edges), np.arange(n_edges)]
    I = I.flatten()
    J = edges.flatten()
    V = np.c_[-1 * np.ones(n_edges), np.ones(n_edges)]
    V = V.flatten()
    delta = sparse.coo_matrix((V, (I, J)), shape=(n_edges, n_vert))

    # Cocycle
    cocycle = ripser_result["cocycles"][1][cocycle_n]
    val = cocycle[:, 2]
    val[val > (prime - 1) / 2] -= prime
    Y = sparse.coo_matrix((val, (cocycle[:, 0], cocycle[:, 1])), shape=(n_vert, n_vert))
    Y = Y - Y.T
    cocycle = np.asarray(Y[edges[:, 0], edges[:, 1]])[0]

    # Minimize
    if weight_ft is None:
        mini = sparse.linalg.lsqr(delta, cocycle)[0]
    else:
        new_delta, new_cocycle = weight_ft(delta, cocycle, dist_mat, edges)
        mini = sparse.linalg.lsqr(new_delta, new_cocycle)[0]

    if return_aux:
        return new_delta, mini, new_cocycle, edges
    else:
        return np.mod(mini, 1.0)


def weight_ft_0(k, t=None, alpha = 0.2):
    def _weight_ft(delta, cocycle, dist_mat, edges):
        nonlocal t
        if t is None:
            tmp = dist_mat[edges[:, 0], edges[:, 1]]
            t = alpha * np.mean(tmp[tmp != 0])
            print(t)
        G = np.exp(-(dist_mat ** 2) / (4 * t))
        G = G / ((4 * np.pi * t) ** (k / 2))
        P = np.mean(G, axis=0)
        P_inv = np.diag(1 / P)
        W = G @ P_inv
        D = np.sum(W, axis=1)
        L_w = P_inv @ (np.diag(D * P) - G) @ P_inv
        metric_weight = -L_w[edges[:, 0], edges[:, 1]]
        metric_weight = np.maximum(metric_weight, 0)  # for safety
        sqrt_weight = np.sqrt(metric_weight)

        new_delta = delta.multiply(sqrt_weight[:, None])
        new_cocycle = sqrt_weight * cocycle

        return new_delta, new_cocycle

    return _weight_ft


def weight_ft_with_degree_meta(ft: callable):
    # ft(degree1: ndarray, degree2: ndarray) -> c
    def _weight_ft(delta, cocycle, dist_mat, edges):
        degrees = np.asarray(np.abs(delta).sum(0))[0] / 2
        degrees = degrees[edges]
        weights = ft(degrees[:, 0], degrees[:, 1])
        new_cocycle = weights * cocycle
        new_delta = delta.multiply(weights[:, None])

        return new_delta, new_cocycle

    return _weight_ft 




# turn the above into a function
def elbow(eigvals):
    plt.plot(np.abs(eigvals[::2]), 'o')
    plt.xticks(np.arange(len(eigvals))[::2])
    plt.title('Modulus of Complex Eigenvalues')
    plt.show()

# a function for turning a path into a chain
def edges_to_chain(edges,data):
    """  
    A function for turning a path into a chain

    Parameters
    ----------
    edges: numpy array
        An array of shape (m,2) representing a collection of edges and their start and end indices

    data: numpy array
        An array of shape (d,n) representing a collection of n points in R^n

    Returns
    -------
    chain : numpy array
        A chain in R^n, represented as a numpy array of shape (m,2,n), where m is the number of edges and n is the dimension of the space.
        The middle index corresponds to start and endpoints of the edges in the chain.
    """

    r = edges.shape[0]

    n = data.shape[1]
    
    
    chain = torch.zeros((r,2,n))

    chain[:,1,:] = torch.tensor(data[edges[:,1],:])
    chain[:,0,:] = torch.tensor(data[edges[:,0],:])

    return chain

# chain projection
def chain_projection(chain,i,j):

    projector = torch.zeros(chain.shape[2], 2)
    projector[i,0] = 1
    projector[j,1] = 1

    return torch.matmul(chain,projector)

def ij_integral(edges, data, cocycle, angular, i, j):
    
    projection = chain_projection(edges_to_chain(edges,data),i,j)
    integral = gen_CDM(angular, projection)

    return torch.tensor(cocycle).float().reshape(1,-1) @ integral

def edge_filtering(cocycle, edges, filter_perc):
    """
    This function takes in a cocycle and edges and returns a subset of the cocycle and edges
    that only includes the top filter_perc of edges by absolute value of cocycle.
    
    Parameters
    ----------
    cocycle: np.array
        The cocycle to be subsetted
    edges: np.array
        The edges to be subsetted
    filter_perc: float
        The percentage of edges to be included in the subset
        
    Returns
    -------
    cocycle_subset: np.array
        The subsetted cocycle
    edges_subset: np.array
        The subsetted edges
    """
    
    # find the top filter_perc of edges by absolute value of cocycle
    top_edges = np.argsort(np.abs(cocycle))[-int(filter_perc*len(cocycle)):]
    top_edges = np.sort(top_edges)

    # subset the cocycle and edges to only include the top edges
    cocycle_subset = cocycle[top_edges]
    edges_subset = edges[top_edges]

    return cocycle_subset, edges_subset


def angular_integral(edges, data, cocycle, filter_perc = None):

    if filter_perc is not None:
        cocycle, edges = edge_filtering(cocycle, edges, filter_perc)

    n = data.shape[1]
    integrals = torch.zeros(n,n)

    angular = torch.nn.Sequential(torch.nn.Linear(2, 2, bias=False))
    angular[-1].weight.data = torch.tensor([[0, 1], [-1, 0]], dtype=torch.float)

    for i in range(n):
        for j in range(i+1,n):
            integrals[i,j] = ij_integral(edges, data, cocycle, angular, i, j)
            integrals[j,i] = -integrals[i,j]

    return integrals.detach().numpy()

def rotational_plot(integrals, data):
    # compute the eigenvalues and eigenvectors of the integrals
    eigvals, eigvecs = np.linalg.eig(integrals)

    # take the real and complex part of the first eigenvector
    re = eigvecs[:,0].real
    im = eigvecs[:,0].imag

    # project the data onto the real and imaginary parts of the first eigenvector
    proj_re = data @ re
    proj_im = data @ im

    # plot the nonzero edges as lines between points on projected data
    #for edge in nonzero_edges:
    #  plt.plot(proj_re[edge],proj_im[edge],color='red')
        


    # plot the data projected onto the real and imaginary parts of the first eigenvector
    plt.scatter(proj_re,proj_im)
    plt.title("Projection onto Principle Leadlag Eigenvector")
    plt.show()

    return  eigvals, eigvecs


def phase_rotate(adata, theta):

    # make sure theta between 0 and 1
    assert -1 <= theta <= 1, "Theta must be between -1 and 1"

    # exp(2*pi*i*theta)
    exp = np.exp(2*np.pi*1j*theta)

    adata.var['gene_phase'] =  ( adata.var['gene_phase'] + 2 * np.pi * theta ) % (2 * np.pi)

    # rotate the lead-lag eigenvector
    adata.varm['leadlag_pcs'][:,0] = exp * adata.varm['leadlag_pcs'][:,0] 

    return adata

def reparametrize(adata, theta, plot = False):

    adata.obs['coords'] = (adata.obs['coords'] + theta) % 1

    if 'gene_phase' in adata.var:
        # make sure theta between 0 and 1
        assert -1 <= theta <= 1, "Theta must be between -1 and 1"

        # exp(2*pi*i*theta)
        exp = np.exp(2*np.pi*1j*theta)

        adata.var['gene_phase'] =  ( adata.var['gene_phase'] + 2 * np.pi * theta ) % (2 * np.pi)

        # rotate the lead-lag eigenvector
        adata.varm['leadlag_pcs'][:,0] = exp * adata.varm['leadlag_pcs'][:,0] 

        if plot:
            phase_plot(adata, topk=10)
            plot_2d(adata, c = 'coords', mode = 'll')




        return adata

def align(adata):

    # Compute target values
    target = np.cos(adata.obs['coords'] * 2 * np.pi).values

    # Get top genes and subset the data
    genes = get_top_genes(adata, k=20)
    subset = adata[:, genes]
    X = subset.X

    # If X is a sparse matrix, convert it to a dense array
    if hasattr(X, "toarray"):
        X = X.toarray()


    # Ensure X is at least 2D (if it's a scalar or 1D, reshape it)
    X = np.atleast_2d(X)

    # Normalize the columns of X using keepdims so the result is broadcastable
    norms = np.linalg.norm(X, axis=0, keepdims=True)
    # Avoid division by zero by setting zero norms to 1
    norms[norms == 0] = 1
    X = X / norms

    # Normalize the target vector
    target_norm = np.linalg.norm(target)
    if target_norm == 0:
        target_norm = 1
    target = target / target_norm

    # Calculate correlations between each gene (column) and target
    scores = X.T @ target

    # Find the gene with the highest correlation
    argmax = np.argmax(scores)
    starting_gene = subset.var_names[argmax]
    print("Estimated starting gene:", starting_gene)

    # Get phase correction from the gene's data
    phase_correction = subset.var['gene_phase'][starting_gene]
    print("Phase correction:", phase_correction, "rad")

    # Apply phase rotation
    phase_rotate(adata, -phase_correction / (2 * np.pi))

    return adata


def maxmin(dist, k):
    L = []
    rand_int = np.random.randint(0, dist.shape[0], 1)[0]
    L.append(rand_int)
    for i in range(k-1):
        mins = np.min(dist[L,:], axis = 0)
        L.append(np.argmax(mins))
    return L

def maxmin_subsampling_optimized(point_cloud, num_samples):
    """
    Perform MaxMin subsampling on a point cloud with optimized performance.

    Parameters:
    point_cloud (np.ndarray): An array of shape (N, D) representing the point cloud, 
                              where N is the number of points and D is the dimension of the space.
    num_samples (int): The number of points to subsample.

    Returns:
    np.ndarray: An array of shape (num_samples, D) containing the subsampled points.
    """
    # Step 1: Initialize
    N, D = point_cloud.shape
    subsampled_indices = np.zeros(num_samples, dtype=int)
    
    # Randomly choose the first point
    subsampled_indices[0] = np.random.randint(0, N)
    
    # Initialize min distances to a large value
    min_distances = np.full(N, np.inf)
    
    for i in range(1, num_samples):
        # Update the minimum distances with the distance from the latest added point
        last_added_point = point_cloud[subsampled_indices[i-1]]
        distances = np.linalg.norm(point_cloud - last_added_point, axis=1)
        min_distances = np.minimum(min_distances, distances)
        
        # Choose the point that has the maximum of these minimum distances
        subsampled_indices[i] = np.argmax(min_distances)
    
    return subsampled_indices

def maxmin_sample(adata, comp = None, k = 2**10):


    if comp != None:
        L = maxmin_subsampling_optimized(adata.obsm['X_pca'][:,comp], k)
    else:
        L = maxmin_subsampling_optimized(adata.X, k)
    
    return adata[L]


from sklearn.neighbors import KernelDensity


def extend_coordinates(adata_main, adata_sub, key='coords', comp=0, sigma=0.2):
    """
    Extend a circle-valued function defined on a subset of cells (contained in a smaller AnnData object)
    to all cells in a main AnnData object using a heat kernel affinity computed on a lead-lag projection.
    
    In adata_sub, the function values are stored in adata_sub.obs[key] (assumed to be in [0,1)), 
    and are scaled by 2π to convert them into radians. These values are then mapped onto adata_main
    by matching cell names. The lead-lag projection is stored in adata_main.varm['leadlag_pcs'], and 
    its real and imaginary parts for component `comp` are used to create a 2D embedding.
    
    A Gaussian kernel (heat kernel) is computed on the 2D coordinates to determine an affinity between
    cells. For each cell in adata_main, a weighted circular mean (using the unit circle representation)
    of the known function values is computed and then normalized back to the [0, 1) range.
    
    Parameters:
    -----------
    adata_main : AnnData
        The main AnnData object for which you want to extend the function.
    adata_sub : AnnData
        The smaller AnnData object that contains the function values in adata_sub.obs[key].
    key : str, default 'coords'
        The key in adata_sub.obs that stores the function values (assumed to be in [0,1)).
    comp : int, default 0
        The index of the lead-lag eigenvector to use. The eigenvectors are stored as pairs:
        column 2*comp is the real part and column 2*comp+1 is the imaginary part.
    sigma : float, default 0.2
        The bandwidth parameter for the Gaussian kernel.
    
    Returns:
    --------
    adata_main : AnnData
        A copy of the main AnnData object with the extended function added to adata_main.obs["f_extended"].
    """
    # Create a copy of the main AnnData object
    adata_main = adata_main.copy()
    
    # Compute sub_coords from the subset adata: scale the 'key' values by 2π to convert [0,1) to radians.
    sub_coords = adata_sub.obs[key] * (2 * np.pi)
    # Convert the series to a dictionary (keys are cell names in adata_sub.obs_names)
    sub_coords_dict = sub_coords.to_dict()
    
    # For each cell in adata_main, assign the corresponding value if present, otherwise NaN.
    coords = [sub_coords_dict.get(cell, np.nan) for cell in adata_main.obs_names]
    adata_main.obs["f"] = coords  # these are the function values in radians (if defined)
    
    # Retrieve the lead-lag principal components from adata_main.varm.
    eigvecs = adata_main.varm['leadlag_pcs']
    # For the chosen component, take the real and imaginary parts.
    re = eigvecs[:, 2 * comp].real
    im = eigvecs[:, 2 * comp].imag
    
    # Project the main data (adata_main.X) onto these components.
    proj_re = adata_main.X @ re
    proj_im = adata_main.X @ im
    # Store the 2D projection (lead-lag embedding) in adata_main.obsm.
    adata_main.obsm['X_LL'] = np.vstack((proj_re, proj_im)).T
    
    # Identify cells with defined function values.
    mask = ~adata_main.obs["f"].isna()
    f_known = adata_main.obs["f"].values[mask]  # angles in radians
    
    # Get the 2D embedding for all cells and for cells with known function values.
    X_all = adata_main.obsm['X_LL']
    X_known = X_all[mask]
    
    # Fit the Gaussian kernel density estimator on the known cells.
    kde = KernelDensity(kernel='gaussian', bandwidth=sigma).fit(X_known)
    
    # Compute pairwise squared Euclidean distances from every cell to each known cell.
    D2 = np.sum((X_all[:, np.newaxis, :] - X_known[np.newaxis, :, :])**2, axis=2)
    
    # Compute the Gaussian (heat) kernel weights.
    weights = np.exp(-D2 / (2 * sigma**2))  # shape: (n_cells, n_known)
    
    # For circle-valued data, convert the known angles to complex numbers on the unit circle.
    weighted_complex = np.sum(weights * np.exp(1j * f_known), axis=1) / np.sum(weights, axis=1)
    f_extended = np.angle(weighted_complex)  # get the weighted circular mean (in radians)
    
    # Normalize the angles to the interval [0, 1)
    f_extended = (f_extended % (2 * np.pi)) / (2 * np.pi)
    
    # Store the extended function in the main AnnData object's .obs.
    adata_main.obs["coords"] = f_extended
    
    print("Extended function computed for all cells.")
    return adata_main

# Example usage:
# adata_ext = extend_circle_function_from_subadata(lum_full_andro, andro, key='coords', comp=0, sigma=0.2)

def filter_cells_by_density(adata, n_pcs=3, bandwidth=0.5, lower_percentile=10, upper_percentile=90):
    """
    Filters cells in an AnnData object based on the density of their PCA coordinates.

    Parameters:
    -----------
    adata : AnnData
        The annotated data matrix.
    n_pcs : int, optional (default: 3)
        Number of principal components to consider for density estimation.
    bandwidth : float, optional (default: 0.5)
        Bandwidth parameter for the Gaussian kernel in KDE.
    lower_percentile : float, optional (default: 10)
        Lower percentile threshold to filter out cells with the lowest density.
    upper_percentile : float, optional (default: 90)
        Upper percentile threshold to filter out cells with the highest density.

    Returns:
    --------
    AnnData
        Filtered AnnData object containing only cells within the specified density range.
    """
    # Check if PCA has been computed; if not, compute it
    if 'X_pca' not in adata.obsm:
        sc.tl.pca(adata)
    
    # Extract the first `n_pcs` PCA coordinates
    X = adata.obsm['X_pca'][:, :n_pcs]

    # Fit a Kernel Density Estimator using a Gaussian kernel
    kde = KernelDensity(kernel='gaussian', bandwidth=bandwidth)
    kde.fit(X)

    # Evaluate the density at each data point
    log_density = kde.score_samples(X)
    density = np.exp(log_density)

    # Add density values to the AnnData object
    adata.obs['density'] = density

    # Determine the density thresholds
    lower_threshold = np.percentile(density, lower_percentile)
    upper_threshold = np.percentile(density, upper_percentile)

    # Create a boolean mask for cells with density within the specified range
    keep_idx = (density > lower_threshold) & (density < upper_threshold)

    # Filter the AnnData object to retain only cells within the specified density range
    adata_filtered = adata[keep_idx].copy()

    return adata_filtered

def circular_contribution_plot(eigvec, labels = None, scale = 1):
    

    # plot the entries of eigenvector 0 on the complex plane with size the modulus of the entry
    plt.scatter(eigvec.real, eigvec.imag, s = np.abs(eigvec)*200)
    

    # label the points with the index
    for i in range(len(eigvec.real)):
                # position of the point
        v = [eigvec[i].real, eigvec[i].imag]

        v =  v / np.linalg.norm(v)

        # add a random scaling factor to the vector
        v = v * (1 + np.random.rand()*0.5)

        # scale the vector by 0.7
        v = v * 0.6
        

        if labels == None:
            plt.text(eigvec[i].real, eigvec[i].imag, str(i), fontsize = 10)

            # draw a line from the point to the text
            plt.plot([eigvec[i].real, v[0]], [eigvec[i].imag, v[1]], alpha = 0.3, colo = 'black')
        else:

            # plot the text, colored by the angle of eigvecs[i,0] and with the label labels[i], at position v
            plt.text(v[0], v[1], labels[i], fontsize = 10)

            # draw a line from the point to the text
            plt.plot([eigvec[i].real, v[0]], [eigvec[i].imag, v[1]], alpha = 0.3, color = 'black')

    # plot some labelled level sets of the function x^2 + y^2
    x = np.linspace(-1,1,100)
    y = np.linspace(-1,1,100)
    X, Y = np.meshgrid(x,y)
    Z = X**2 + Y**2

    # plot the level sets with a low opacity and a labelling
    plt.contourf(X,Y,Z,levels=np.linspace(0,1,10)**2, alpha=0.2)

    # make the plot square
    plt.gca().set_aspect('equal', adjustable='box')

    # make lines radiating from the origin with a label of their angle
    for i in range(0,360,30):
        plt.plot([0,np.cos(i*np.pi/180)],[0,np.sin(i*np.pi/180)],'k', alpha=0.2)
        plt.text(1.15*np.cos(i*np.pi/180),1.05*np.sin(i*np.pi/180),str(i)+str('°'))


    # plot a black boundary around the circle
    plt.plot(np.cos(np.linspace(0,2*np.pi,100)), np.sin(np.linspace(0,2*np.pi,100)), 'k')
    

    # remove the axes
    plt.axis('off')

    # make the plot bigger
    plt.gcf().set_size_inches(scale * 10, scale * 10)

    plt.show() 

def circular_contribution_plot_old(eigvecs, labels = None, scale = 1):
    

    # plot the entries of eigenvector 0 on the complex plane with size the modulus of the entry
    plt.scatter(eigvecs[:,0].real, eigvecs[:,0].imag, s = np.abs(eigvecs[:,0])*200, c = plt.cm.hsv((np.angle(eigvecs[:,0])+np.pi)/(2*np.pi)), cmap = 'hsv')
    

    # label the points with the index
    for i in range(len(eigvecs[:,0].real)):
                # position of the point
        v = [eigvecs[i,0].real, eigvecs[i,0].imag]

        v =  v / np.linalg.norm(v)

        # add a random scaling factor to the vector
        v = v * (1 + np.random.rand()*0.5)

        # scale the vector by 0.7
        v = v * 0.6
        

        if labels == None:
            plt.text(eigvecs[i,0].real, eigvecs[i,0].imag, str(i), fontsize = 10)

            # draw a line from the point to the text
            plt.plot([eigvecs[i,0].real, v[0]], [eigvecs[i,0].imag, v[1]], color = plt.cm.hsv((np.angle(eigvecs[i,0])/np.pi*180)/360), alpha = 0.3)
        else:

            # plot the text, colored by the angle of eigvecs[i,0] and with the label labels[i], at position v
            plt.text(v[0], v[1], labels[i], fontsize = 10)

            # draw a line from the point to the text
            plt.plot([eigvecs[i,0].real, v[0]], [eigvecs[i,0].imag, v[1]], color = plt.cm.hsv((np.angle(eigvecs[i,0])/np.pi*180)/360), alpha = 0.3)

    # plot some labelled level sets of the function x^2 + y^2
    x = np.linspace(-1,1,100)
    y = np.linspace(-1,1,100)
    X, Y = np.meshgrid(x,y)
    Z = X**2 + Y**2

    # plot the level sets with a low opacity and a labelling
    plt.contourf(X,Y,Z,levels=np.linspace(0,1,10)**2, alpha=0.2)

    # make the plot square
    plt.gca().set_aspect('equal', adjustable='box')

    # make lines radiating from the origin with a label of their angle
    for i in range(0,360,30):
        plt.plot([0,np.cos(i*np.pi/180)],[0,np.sin(i*np.pi/180)],'k', alpha=0.2)
        plt.text(1.15*np.cos(i*np.pi/180),1.05*np.sin(i*np.pi/180),str(i)+str('°'))


    # plot a black boundary around the circle
    plt.plot(np.cos(np.linspace(0,2*np.pi,100)), np.sin(np.linspace(0,2*np.pi,100)), 'k')
    

    # remove the axes
    plt.axis('off')

    # make the plot bigger
    plt.gcf().set_size_inches(scale*10,scale*10)

    plt.show() 

# plot the lead-lag matrix
def plot_leadlag(integrals, genes, eig = None, order = False):
    """ 
    A function to plot the lead-lag matrix of a set of genes.

    Parameters
    ----------
    integrals : numpy array
        The lead-lag matrix of the genes.
    genes : list
        The list of genes.

    Returns
    -------
    None.
    """
    if order == True:
        # order the genes by their angle in the first eigenvector
        gene_order = np.argsort(np.angle(eig))

        # sort the rows and columns of integrals by gene_order
        integrals = integrals[gene_order,:]
        integrals = integrals[:,gene_order]

        # sort the genes by gene_order
        genes = np.array(genes)[gene_order]

    plt.imshow(-integrals, cmap = 'bwr', interpolation = 'nearest')
    plt.xticks(np.arange(len(genes)), genes, rotation = 90)
    plt.yticks(np.arange(len(genes)), genes)
    plt.colorbar()
    plt.show()

def plot_histogram(adata, c = None, bins = 7, sort = False, alpha = 0.8, histtype = 'barstacked', polar = True, scale = 1):

    fig = plt.figure(figsize=(10,5))
    ax = fig.add_subplot(1,2,1, polar=polar)  

    if c != None: 

        classes = adata.obs[c].unique()

                # sort times alphabetically
        if sort == True:
            classes = sorted(classes) 
        

        # check that c is categorical class in adata
        if c not in adata.obs:
            raise ValueError(f"{c} is not a valid class in adata.obs")
        
        for cl in classes:

            # subset adata by timepoint
            subset = adata[adata.obs[c] == cl]
            radians = subset.obs['coords'] * 2 * np.pi
            ax.hist(radians, bins=bins, density=True, alpha=alpha, histtype = histtype)
            ax.legend(classes)

            
    else: 
        radians = adata.obs['coords'] * 2 * np.pi
        ax.hist(radians, bins=bins, density=True, alpha=alpha, histtype = histtype)
        # label x axis
    
    plt.xlabel('Circular Coordinate')

    fig.set_size_inches(scale*10, scale*10)
    plt.show()

# a function for recentering around a harmonic
def harmonic_recenter(data, delta, mini, cocycle, edges, return_center = False):
    
    # calculate the barycenter of each edge
    barycenters = (data[edges[:,0]] + data[edges[:,1]])/2
    
    # calculate the harmonic
    harmonic = delta @ mini - cocycle
    
    # take the absolute value of the harmonic
    harmonic = np.abs(harmonic)
    
    # divide the harmonic by its norm
    harmonic = harmonic/np.sum(harmonic)
    
    # calculate the harmonic center
    harmonic_center = harmonic.T @ barycenters
    
    # subtract the harmonic center from the data
    data = data - harmonic_center

    if return_center == True:
        return data, harmonic_center
    
    else:
        return data

# turn the above into a function that removes the first eigenvector
def leadlag_denoise(X, eigvecs, eig_index = 0):
    """
    Removes the component of X in the direction of the eigenvector eig_index of eigvecs.
    
    Parameters
    ----------
    X : array
        The data matrix.
    eigvecs : array
        The eigenvectors of the rotational plot.
    eig_index : int
        The index of the eigenvector to remove.
        
    Returns
    -------
    X_no_eig : array
        The data matrix with the component in the direction of eig_index removed.
    """
    
    # collect the real and imaginary parts of the first eigenvector
    eig_real = np.real(eigvecs[:,eig_index])
    eig_imag = np.imag(eigvecs[:,eig_index])

    # normalize the eigenvector
    eig_real = eig_real / np.linalg.norm(eig_real)
    eig_imag = eig_imag / np.linalg.norm(eig_imag)

    # make a copy of X
    X_no_eig = X.copy()
    
    # remove component of X in direction of the eigenvectors
    X_no_eig = X - np.dot(X, eig_real)[:,np.newaxis] * eig_real - np.dot(X, eig_imag)[:,np.newaxis] * eig_imag


    return X_no_eig

## effective resistence
import numpy as np
from scipy.sparse import csr_matrix, diags, identity, issparse
from scipy.spatial.distance import cdist
from scipy.sparse.linalg import eigsh

def compute_knn_adjacency(X, num_neighbors=10):
    """
    Compute a binary symmetric k-nearest neighbor (kNN) adjacency matrix from a point cloud.
    
    Two points i and j are connected (i.e. A[i, j] = 1) if either j is among the 
    num_neighbors nearest neighbors of i or vice versa.
    
    Parameters:
        X (ndarray or sparse matrix): An n x d array where each row is a point in d-dimensional space.
        num_neighbors (int): Number of nearest neighbors to include for each point.
        
    Returns:
        A (ndarray): An n x n binary adjacency matrix.
    """
    # Convert X to dense if it is sparse.
    if issparse(X):
        X = X.toarray()
    
    n = X.shape[0]
    dists = cdist(X, X)  # Compute full pairwise Euclidean distances.
    A = np.zeros((n, n), dtype=int)
    
    # For each node, select the num_neighbors nearest neighbors (excluding itself).
    for i in range(n):
        neighbors = np.argsort(dists[i])[1:num_neighbors+1]
        A[i, neighbors] = 1

    # Make the graph symmetric (if either i or j is a neighbor, connect i and j).
    A = np.maximum(A, A.T)
    return A

def compute_effective_resistance_embedding(X, num_neighbors=10, k=10):
    """
    Compute the effective resistance embedding from a point cloud using a binary symmetric kNN graph.
    
    This function:
      1. Constructs the binary symmetric kNN adjacency matrix.
      2. Computes its degree vector and forms the symmetrically normalized Laplacian.
      3. Computes the first k+1 smallest eigenpairs (discarding the trivial eigenpair).
      4. Constructs the embedding using the scaling factors (scale = (1 - mu) / sqrt(mu)) and normalizing by 1/sqrt(degree).
    
    Parameters:
        X (ndarray or sparse matrix): An n x d point cloud.
        num_neighbors (int): Number of nearest neighbors for the kNN graph.
        k (int): Number of nontrivial eigen-components (embedding dimensions) to retain.
        
    Returns:
        e_eff (ndarray): An n x k effective resistance embedding. The squared Euclidean distances 
                         between rows correspond to the effective resistance between points.
    """
    # Build the binary symmetric kNN adjacency matrix.
    A_dense = compute_knn_adjacency(X, num_neighbors)
    n = A_dense.shape[0]
    
    # Convert the dense adjacency matrix to a sparse matrix.
    A_sparse = csr_matrix(A_dense)
    
    # Compute the degree vector: d_i = sum_j A[i,j]
    d = np.array(A_sparse.sum(axis=1)).ravel()
    d_inv_sqrt = 1.0 / np.sqrt(d)
    
    # Create the diagonal matrix D^(-1/2)
    D_inv_sqrt = diags(d_inv_sqrt)
    
    # Compute the symmetrically normalized adjacency matrix: A_sym = D^(-1/2) * A * D^(-1/2)
    A_sym_sparse = D_inv_sqrt @ A_sparse @ D_inv_sqrt
    
    # Compute the normalized Laplacian: L_sym = I - A_sym
    L_sym_sparse = identity(n) - A_sym_sparse
    
    # Compute the first k+1 smallest eigenpairs (k+1 because the smallest eigenpair is trivial)
    eigenvals, eigenvecs = eigsh(L_sym_sparse, k=k+1, which='SM')
    
    # Sort eigenpairs in ascending order.
    idx = eigenvals.argsort()
    eigenvals = eigenvals[idx]
    eigenvecs = eigenvecs[:, idx]
    
    # Discard the trivial eigenpair (first eigenpair with eigenvalue close to 0).
    mu_nontriv = eigenvals[1:k+1]
    U_nontriv = eigenvecs[:, 1:k+1]
    
    # Compute scaling factors: scale = (1 - mu) / sqrt(mu)
    scale = (1 - mu_nontriv) / np.sqrt(mu_nontriv)
    
    # Construct the effective resistance embedding:
    # For each node i, its embedding is  e_eff[i] = (1/sqrt(d_i)) * [scale[0]*U_nontriv[i, 0], …, scale[k-1]*U_nontriv[i, k-1]]
    e_eff = d_inv_sqrt[:, None] * (U_nontriv * scale[None, :])
    return e_eff

def effective_resistence(adata, num_neighbors=10, k=10):
    """
    Computes the effective resistance embedding from adata.X using the binary symmetric kNN graph,
    and appends it to the AnnData object as adata.obsm['X_ef'].
    
    Parameters:
        adata (anndata.AnnData): An AnnData object (e.g., from scRNA-seq experiments).
        num_neighbors (int): Number of nearest neighbors to use for constructing the kNN graph.
        k (int): Number of nontrivial eigen-components (embedding dimensions) to retain.
        
    Returns:
        None: The function modifies the AnnData object in-place.
    """
    # Compute the effective resistance embedding using adata.X as the point cloud.
    embedding = compute_effective_resistance_embedding(adata.X, num_neighbors, k)
    # Store the embedding in adata.obsm under the key 'X_ef'
    adata.obsm['X_ef'] = embedding


### --- AnnData Object Compatibility Functions --- ###

def circular(adata, comp = [0,1], alpha = 0.2, recenter = False, mode = 'pca'):

    if mode == 'pca':
        data = adata.obsm['X_pca'][:,comp]
    elif mode == 'ef': # effective resistance
        data = adata.obsm['X_ef'][:,comp]

    # generate the weighted circular coordinates
    delta, mini, cocycle, edges = weighted_circular_coordinate(data, weight_ft = weight_ft_0(k=data.shape[1], alpha = alpha), return_aux = True) # weighted circular coordinates

    # put the above into a dict
    circular = {'delta': delta, 'mini': mini, 'cocycle': cocycle, 'edges': edges, 'harm' : delta @ (mini) - cocycle}

    adata.uns['circular'] = circular

    adata.uns['circular']['delta']

    # add circular coordinates to adata_cc_genes
    adata.obs['coords'] = mini % 1

    # add log counts to adata
    adata.obs["log_counts"] = np.log(adata.X.sum(axis=1)+1)

    if recenter == True:

        # recenter circular coordinates around lowest expression cell
        low = adata.obs['log_counts'].idxmin()
        low_coord = adata[low,].obs['coords']
        adata.obs['coords'] = ( adata.obs['coords'] - low_coord.iloc[0] ) % 1
    
    return adata

def h_recenter(adata):

    delta = adata.uns['circular']['delta']
    mini = adata.uns['circular']['mini']
    cocycle = adata.uns['circular']['cocycle']
    edges = adata.uns['circular']['edges']  

    adata.layers['h_recenter'] = harmonic_recenter(adata.X, delta, mini, cocycle, edges)

    return adata

def spectral(adata):

    X = adata.layers['h_recenter']

    integrals = adata.uns['leadlag']

    eigvals,eigvecs = rotational_plot(integrals,X)

    elbow(eigvals)

    adata.varm['leadlag_pcs'] = eigvecs
    adata.var['gene_phase'] = np.angle(eigvecs[:,0])
    adata.var['gene_amp'] = np.abs(eigvecs[:,0])

    return adata

def leadlag_matrix2(X, edges, harm):
    P = X[edges[:,0], :]
    Q = X[edges[:,1], :]

    # Debug shapes
    print("Shape of P:", P.shape)
    print("Shape of Q:", Q.shape)
    print("Maximum edge index:", np.max(edges))
    print("Shape of X:", X.shape)

    # Attempt to stack P and Q
    try:
        PQ = np.stack([P, Q])
        PQ = np.transpose(PQ, (1, 2, 0))
    except Exception as e:
        print("Error in stacking or transposing:", e)
        # Additional diagnostics or alternative handling here
        return None

    # Rest of the function...
    return PQ


def leadlag_matrix(X, edges, harm):

    # get the P and Q matrices, start and end points of the edges
    P = X[edges[:,0], :]
    Q = X[edges[:,1], :]

    # stack the P and Q matrices
    PQ = np.stack([P, Q])

    # permute dimensions of PQ
    PQ = np.transpose(PQ, (1, 2, 0))

    # calculate det of PQ[:,[i,j],:] FOR ALL i<j without using for loop
    ll = np.zeros((X.shape[1], X.shape[1]))
    for i in tqdm(range(X.shape[1])):
        for j in range(i+1, X.shape[1]):
            ll[i,j] = 0.5 * np.linalg.det(PQ[:,[i,j],:]).T @ harm
            ll[j,i] = -ll[i,j]

    return ll

def leadlag(adata, alignment = True):

    # Recentering the Data
    print("Harmonic Recentering")
    adata = h_recenter(adata)
    
    X = adata.layers['h_recenter']
    edges = adata.uns['circular']['edges']
    harm = adata.uns['circular']['harm']

    print("Calculating Leadlag Matrix") 
    adata.uns['leadlag'] = leadlag_matrix(X, edges, harm)

    print("Calculating Spectral Information")
       # compute the eigenvalues and eigenvectors of the integrals
    eigvals, eigvecs = np.linalg.eig(adata.uns['leadlag'])
    adata.varm['leadlag_pcs'] = eigvecs
    adata.uns['leadlag_eigvals'] = eigvals
    adata.var['gene_phase'] = np.angle(eigvecs[:,0]) % (2 * np.pi)
    adata.var['gene_amp'] = np.abs(eigvecs[:,0])

    if alignment == True:
        print("Aligning Data")
        # align the data to the first gene
        adata = align(adata)


    return adata



def leadlag_old(adata, filter_perc = 0.1):

    edges = adata.uns['circular']['edges'] 
    harm = adata.uns['circular']['harm']

    print("Recentering...")
    adata = h_recenter(adata)

    print("Calculating lead-lag...")
    adata.uns['leadlag'] = angular_integral(edges, adata.layers['h_recenter'], harm, filter_perc)

    print("Calculating spectral information...")
    # compute the eigenvalues and eigenvectors of the integrals
    eigvals, eigvecs = np.linalg.eig(adata.uns['leadlag'])
    adata.varm['leadlag_pcs'] = eigvecs
    adata.uns['leadlag_eigvals'] = eigvals
    adata.var['gene_phase'] = np.angle(eigvecs[:,0])
    adata.var['gene_amp'] = np.abs(eigvecs[:,0])

    return adata

def reverse(adata):

    adata.uns['circular']['harm'] = -adata.uns['circular']['harm']
    adata.obs['coords'] = -adata.obs['coords']%1

    if 'gene_phase' in adata.var:
        phases = np.exp(1j * adata.var['gene_phase'])
        phases = np.conjugate(phases) 
        adata.var['gene_phase'] = np.angle(phases) % (2 * np.pi)
        adata.varm['leadlag_pcs'] = adata.varm['leadlag_pcs'].conj()

        phase_plot(adata, topk=10)
        plot_2d(adata, c = 'coords', mode = 'll')
    
    return adata

# takes an adata object and returns the top k genes by gene_amp sorted by gene_phase
def get_top_genes(adata, k = 10):

    gene_amps = adata.var['gene_amp']

    # find top 10 genes by gene_amp
    top_genes = gene_amps.sort_values(ascending=False).index[:k]

    top_genes = list(top_genes)

    gene_phases = adata.var['gene_phase'] % (2 * np.pi)

    # sort top_genes by their phase
    top_genes = sorted(top_genes, key=lambda x: gene_phases[x])

    return top_genes

import anndata

# fit a lead-lag plane to new data
def fit_leadlag_plane(
    adata_sub: anndata.AnnData,
    adata_full: anndata.AnnData,
    vertical_layer: str = None,
    leadlag_layer: str = None
) -> anndata.AnnData:
    """
    Fits a simple linear model (with real and imaginary parts) to each gene in `adata_full`
    using the first lead-lag principal component from `adata_sub`.
    
    Args:
        adata_sub: An AnnData subset that already contains the first lead-lag PC in .varm['leadlag_pcs'].
        adata_full: The full AnnData object to be modeled and expanded.
        vertical_layer: (Optional) Name of the layer in `adata_full` to fit. If None, uses `adata_full.X`.
        leadlag_layer: (Optional) Name of the layer in `adata_full` from which the lead-lag PC projection is computed. 
                       If None, uses `adata_full.X`.

    Returns:
        A copy of `adata_full` (`expansion`) with various regression metrics and fits saved to .var.
        Also updates .varm['leadlag_pcs'] with the normalized real + imaginary coefficients.
    """
    
    # Select the data for projection onto the lead-lag PC
    if leadlag_layer is not None:
        X_data = adata_full[:, adata_sub.var_names].layers[leadlag_layer]
    else:
        X_data = adata_full[:, adata_sub.var_names].X

    # Retrieve the first leadlag PC from adata_sub and normalize it
    pcs = adata_sub.varm['leadlag_pcs'][:, 0]
    pcs = pcs / np.linalg.norm(pcs)

    # Project full data onto the first leadlag PC
    proj = np.dot(X_data, pcs)
    real = np.real(proj)
    imag = np.imag(proj)

    # Make a copy of the full adata for storing results
    expansion = adata_full.copy()

    # Select the target data (the values to be fitted)
    if vertical_layer is not None:
        targets = expansion.layers[vertical_layer]
    else:
        targets = expansion.X

    # Step 1: Create design matrix (1, real, imag)
    X = np.column_stack((np.ones_like(real), real, imag))  # shape: (n_cells, 3)

    # Step 2: Compute the Moore-Penrose pseudoinverse of X
    X_pinv = np.linalg.pinv(X)  # shape: (3, n_cells)

    # Step 3: Estimate coefficients for all target variables at once
    # Resulting shape: (3, n_genes)
    coefficients = X_pinv @ targets

    # Step 4: Compute predictions
    # Shape: (n_cells, n_genes)
    predictions = X @ coefficients

    # Step 5: Compute residuals
    residuals = targets - predictions

    # Step 6: Compute sum of squared residuals (losses) for each gene
    losses = np.sum(residuals ** 2, axis=0)

    # Step 7: Compute total variance for each target gene
    target_means = np.mean(targets, axis=0)
    total_variance = np.sum((targets - target_means) ** 2, axis=0)

    # Step 8: Compute R^2 for each target
    r_squared = 1 - (losses / total_variance)

    # Step 9: Record R^2 and other fits in the AnnData object
    expansion.var['r_squared'] = r_squared
    expansion.var['r'] = np.sqrt(r_squared)

    expansion.var['real_fit'] = coefficients[1]
    expansion.var['imag_fit'] = coefficients[2]
    expansion.var['const_fit'] = coefficients[0]
    expansion.var['radius_fit'] = coefficients[1]**2 + coefficients[2]**2
    expansion.var['complex_fit'] = coefficients[1] + 1j * coefficients[2]
    expansion.var['loss'] = losses

    # Compute amplitude and phase of each gene
    expansion.var['gene_amp'] = np.sqrt(expansion.var['real_fit']**2 + expansion.var['imag_fit']**2)
    expansion.var['gene_phase'] = np.arctan2(expansion.var['imag_fit'], expansion.var['real_fit'])
    expansion.var['gene_phase'] = expansion.var['gene_phase'] % (2 * np.pi)

    # Normalize the real and imaginary coefficient vectors
    # (Note: This normalizes across genes, so ensure it matches your intention.)
    coefficients[1] = coefficients[1] / np.linalg.norm(coefficients[1])
    coefficients[2] = coefficients[2] / np.linalg.norm(coefficients[2])

    # Store normalized lead-lag PC in varm
    # Here we combine real+imag parts into one complex vector, and expand dims to (n_genes, 1)
    expansion.varm['leadlag_pcs'] = coefficients[1] + 1j * coefficients[2]
    expansion.varm['leadlag_pcs'] = np.expand_dims(expansion.varm['leadlag_pcs'], axis=1)

    # Optional check of shape
    _ = expansion.varm['leadlag_pcs'].shape  # just for confirmation/debugging

    return expansion






##### ADATA PLOTTING FUNCTIONS #####

def phase_plot(adata, genes = None, scale = 1, topk = 10, color = None, size = None):

    if genes != None:
        subset = adata.copy()[:,genes]
    else:
        subset = adata.copy()

    # sort subset by gene_amp
    subset = subset[:,subset.var['gene_amp'].sort_values(ascending=False).index]



    phases = subset.var['gene_phase']
    amps = subset.var['gene_amp'] / (1.5 * subset.var['gene_amp'].max())

    exp = np.exp(1j*phases) * amps

    labels = subset.var_names

    # plot some labelled level sets of the function x^2 + y^2
    x = np.linspace(-1,1,100)
    y = np.linspace(-1,1,100)
    X, Y = np.meshgrid(x,y)
    Z = X**2 + Y**2

    # plot the level sets with a low opacity and a labelling
    plt.contour(X,Y,Z,levels=np.linspace(0,1,10)**2, alpha=0.2, colors = 'black')

    # do the 

    # make the plot square
    plt.gca().set_aspect('equal', adjustable='box')

    # make lines radiating from the origin with a label of their angle
    for i in range(0,360,30):
        plt.plot([0,np.cos(i*np.pi/180)],[0,np.sin(i*np.pi/180)],'k', alpha=0.2)
        plt.text(1.15*np.cos(i*np.pi/180),1.05*np.sin(i*np.pi/180),str(i)+str('°'))


    # plot a black boundary around the circle
    plt.plot(np.cos(np.linspace(0,2*np.pi,100)), np.sin(np.linspace(0,2*np.pi,100)), 'k')

    if color != None:
        # check the type of elements in subset.var[color]
        if type(subset.var[color][0]) == str:
            print('O')
            for t in subset.var[color].unique():
                # find indices of genes in group t
                indices = subset.var[subset.var[color] == t].index

                plt.scatter(exp[indices].values.real, exp[indices].values.imag, s = amps[indices]*200,edgecolors = 'black', alpha = 1, label = t)
        else:
            plt.scatter(exp.values.real, exp.values.imag, s = amps*200, c = subset.var[color], edgecolors = 'black', alpha = 1)




    else:
        # plot the entries of eigenvector 0 on the complex plane with size the modulus of the entry
        plt.scatter(exp.values.real, exp.values.imag, s = amps*200, c = plt.cm.hsv(np.angle(exp.values) % (2*np.pi) / (2 * np.pi)), cmap = 'hsv', edgecolors = 'black', alpha = 1)


    # label the points with the index
    for i in range(min(len(exp), topk)):
                # position of the point
        v = [exp.values.real[i], exp.values.imag[i]]

        v =  v / np.linalg.norm(v)

        # add a random scaling factor to the vector
        v = v * (1 + np.random.rand()*0.5)

        # scale the vector by 0.7
        v = v * 0.6

        # plot the text, colored by the angle of eigvecs[i,0] and with the label labels[i], at position v
        plt.text(v[0], v[1], labels[i], fontsize = 10)

        # draw a line from the point to the text
        plt.plot([exp.values.real[i], v[0]], [exp.values.imag[i], v[1]], alpha = 0.3, color = 'black')



    # remove the axes
    plt.axis('off')

    # make the plot bigger
    plt.gcf().set_size_inches(scale * 10, scale * 10)

    plt.legend(loc = 'upper right')

    if color != None:
        if type(subset.var[color][0]) != str:
            plt.colorbar(label = color)

    plt.show()

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.sparse as sp
import anndata

def plot_heatmap(
    adata: anndata.AnnData,
    coords_key: str = 'coords',
    phase_key: str = 'gene_phase',
    layer: str = None,
    cmap: str = 'viridis',
    figsize: tuple = (10, 6),
    show_gene_labels: bool = True,
    rotate_xticks: int = 90,
    title: str = "Heatmap sorted by circular coord (rows) and gene_phase (columns)"
):
    """
    Plot a heatmap of cells × genes in `adata`, with rows (cells) sorted by
    a circular coordinate (e.g., 'coords') and columns (genes) sorted by a phase variable
    (e.g., 'gene_phase').

    Args:
        adata: The AnnData object containing at least:
            - .obs[coords_key]: A numeric or circular coordinate for each cell
            - .var[phase_key]: A numeric or circular phase for each gene
        coords_key: The key in adata.obs used to sort cells (defaults to 'coords').
        phase_key: The key in adata.var used to sort genes (defaults to 'gene_phase').
        layer: If specified, use adata.layers[layer] for the expression matrix; 
               otherwise use adata.X.
        cmap: Colormap string passed to seaborn.heatmap (e.g., 'viridis', 'magma', etc.).
        figsize: Size of the figure (width, height) in inches.
        show_gene_labels: Whether to show gene names on the x-axis.
        rotate_xticks: Degrees to rotate the x-axis tick labels (e.g., 0, 45, 90).
        title: Title for the heatmap.
    """

    # 1. Determine sorted order of cells by 'coords_key'
    cell_order = np.argsort(adata.obs[coords_key])

    # 2. Determine sorted order of genes by 'phase_key'
    gene_order = np.argsort(adata.var[phase_key])

    # 3. Subset and reorder the data matrix
    #    If 'layer' is provided, use that, otherwise use adata.X
    if layer is not None:
        data_matrix = adata.layers[layer]
    else:
        data_matrix = adata.X

    # Slice rows and columns in sorted order
    data_matrix = data_matrix[cell_order, :][:, gene_order]

    # Convert to dense if it's sparse (caution with large data)
    if sp.issparse(data_matrix):
        data_matrix = data_matrix.toarray()

    # 4. Extract the gene names in the new sorted order
    genes_sorted = adata.var_names[gene_order] if show_gene_labels else False

    # 5. Plot the heatmap
    plt.figure(figsize=figsize)
    ax = sns.heatmap(
        data_matrix,
        cmap=cmap,
        xticklabels=genes_sorted,  # gene names as column labels (or False if not shown)
        yticklabels=False          # often too many cells to label; set to False or subset
    )

    if rotate_xticks != 0 and show_gene_labels:
        plt.xticks(rotation=rotate_xticks)

    plt.title(title)
    plt.xlabel(f"Genes (sorted by {phase_key})")
    plt.ylabel(f"Cells (sorted by {coords_key})")
    plt.tight_layout()
    plt.show()



def phase_plot_old(adata, genes = None, comp = 0, topk = False, scale = 1):

    if genes == None:
        genes = list(adata.var_names)
        new = adata.copy()
    else:
        new = adata.copy()[:, genes]

    
    eigvec = np.array(new.varm['leadlag_pcs'][:,comp])

    circular_contribution_plot(eigvec, labels = genes, scale = scale)

def phase_plot_old(adata, genes = None, comp = 0, topk = False, scale = 1):


    if genes == None:
        if topk != False:
            genes = list(adata.var.sort_values('gene_amp', ascending = False).index[:topk])
            new_adata = adata.copy()
            new_adata.var['ev'] = adata.varm['leadlag_pcs'][:,comp]
            new_adata.var['ev']
        
            # subset the data to only the genes of interest
            new_adata = new_adata[:, genes].copy()

            eigvec = np.array(new_adata.var['ev'])
        else:
            genes = list(adata.var_names)
            eigvec = adata.varm['leadlag_pcs'][:,comp]
    else:
        new_adata = adata.copy()
        new_adata.var['ev'] = adata.varm['leadlag_pcs'][:,comp]
        new_adata.var['ev']
        
        # subset the data to only the genes of interest
        new_adata = new_adata[:, genes].copy()

        eigvec = np.array(new_adata.var['ev'])

    circular_contribution_plot(eigvec, labels = genes, scale = scale)

def leadlag_plot_old(adata, genes = None, labels = None, order = True):

    if genes != None:
        adata = adata[:,genes].copy()

    integrals = adata.uns['leadlag']

    eig = adata.varm['leadlag_pcs'][:,0]

    if genes == None:
        genes = list(adata.var_names)

    plot_leadlag(integrals, genes, eig = eig, order = order)


def leadlag_plot(adata, genes = None, k = 10):
    if genes is None:
        genes = get_top_genes(adata, k = k)
    total_indices = [adata.var_names.get_loc(gene) for gene in genes]
    l = adata.uns['leadlag']
    l = l[total_indices]
    l = l[:, total_indices]
    plt.figure(figsize = (10,10))
    plt.imshow(l, cmap = 'bwr', aspect = 'auto', interpolation='nearest')
    plt.colorbar()
    plt.xticks(ticks = np.arange(0,len(total_indices)), labels = genes, rotation = 90)
    plt.yticks(ticks = np.arange(0,len(total_indices)), labels = genes)

def elbow_plot(adata):

    # assert that the leadlag_eigvals are in adata.uns
    assert 'leadlag_eigvals' in adata.uns, 'leadlag_eigvals not in adata.uns. please run chnt.leadlag'

    eigvals = adata.uns['leadlag_eigvals']

    plt.plot(np.abs(eigvals[::2]), 'o')
    plt.xticks(np.arange(len(eigvals)/2))
    plt.title('Modulus of Complex Eigenvalues')
    plt.show()


def circular_denoise(adata, eig_index = 0):

    X = adata.X
    eigvecs = adata.varm['leadlag_pcs']

    adata.layers['circular_denoised'] = leadlag_denoise(X,eigvecs, eig_index = eig_index)

    return adata

# turn the above into a function
def plot_gene_expression(adata, genes, title = None, polar = False, alpha = 0.5, filepath = False, ax = None):

    remember = False
    
    if ax == None: 
        fig = plt.figure(figsize=(10,5))
        remember = True
        

        if polar:
            ax = fig.add_subplot(1,2,1, polar=True)
        else:
            ax = fig.add_subplot(1,2,1)

        coords = adata.obs['coords'].values

    for i in range(len(genes)):
        if genes[i] in adata.var_names:
            gene_exp = adata[:,genes[i]].X

            if polar:
                ax.scatter(coords * 2 * np.pi, gene_exp, label = genes[i], alpha = alpha)
            else:
                ax.scatter(coords, gene_exp, label = genes[i], alpha = alpha)

    if title != None:
        ax.set_title(title)

    ax.legend()

    # put the legend outside the figure
    ax.legend(bbox_to_anchor=(0.01, 0.99), loc='upper left', borderaxespad=0.)

    # make figure size bigger
    if remember:
        fig.set_size_inches(20, 10)
    fig.show()

    # save the figure
    if filepath != False:
        fig.savefig(filepath + '.png')



# turn the above into a function plot_top_genes which takes in adata, k and returns the above plot
def plot_top_genes(adata, k = 10):

    top_genes = get_top_genes(adata, k = k)

    gene_phases = adata[:, top_genes].var['gene_phase']

    genes = top_genes

    # set up 4 subplots stack ontop of each other
    fig, axs = plt.subplots(len(top_genes), 1, figsize=(10, len(genes)*2))

    # plot gene expression
    for i, gene in enumerate(genes):
        gene_exp = adata[:,genes[i]].X
        # map gene_phase to a hsv color
        color = plt.cm.hsv(gene_phases[gene] / (2 * np.pi))

        

        axs[i].scatter(adata.obs['coords'], gene_exp, label = genes[i], color = color)
        axs[i].set_ylabel('Gene Expression')
        axs[i].legend()

        # color by phase of gene
        

        if i == len(genes) - 1:
            axs[i].set_xlabel('Circular Coordinate')
        

    # add a colorbar to the figure
    fig.colorbar(plt.cm.ScalarMappable(cmap='hsv'), ax=axs, orientation='vertical', label='Gene Phase', shrink = 0.5)

    # make the width of the colorbar small
    plt.show()

def comparision_plot(adata, gene1, gene2, c = 'coords'):
    plt.scatter(adata[:,gene1].X, adata[:,gene2].X, c = adata.obs[c], cmap = 'viridis')
    plt.xlabel(gene1)
    plt.ylabel(gene2)
    plt.suptitle(f'{gene1} vs {gene2}')
    # add colorbar
    plt.colorbar().set_label(c)

    plt.show()

def pc_column_plot(adata, ax, c, comp = [0,1]):

    # add c to title
    ax.set_title(c)

        
    if c in adata.obs.columns:
        # check if the column is categorical
        if adata.obs[c].dtype == 'category':
            
            for iden in adata.obs[c].unique():

                sub_adata = adata[adata.obs[c] == iden]
                ax.scatter(sub_adata.obsm['X_pca'][:,comp[0]], 
                        sub_adata.obsm['X_pca'][:,comp[1]], 
                        label = iden)
                

            #Shrink current axis by 20%
            box = ax.get_position()
            ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

            # Put a legend to the right of the current axis
            ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

            
            ax.set_title(c)
            
        elif c == 'coords':
            ax.scatter(adata.obsm['X_pca'][:,comp[0]], adata.obsm['X_pca'][:,comp[1]], c = list(adata.obs[c]), cmap = 'hsv')
            
            # add a colorbar to the figure
            cbar = plt.colorbar(ax.collections[0], ax = ax)
            cbar.set_label(c)

        else:
            ax.scatter(adata.obsm['X_pca'][:,comp[0]], adata.obsm['X_pca'][:,comp[1]], c = list(adata.obs[c]))
            
            # add a colorbar to the figure
            cbar = plt.colorbar(ax.collections[0], ax = ax)
            cbar.set_label(c)

    elif c in adata.var_names:
        ax.scatter(adata.obsm['X_pca'][:,comp[0]], adata.obsm['X_pca'][:,comp[1]], c = list(adata[:,c].X))
        cbar = plt.colorbar(ax.collections[0], ax = ax)
        cbar.set_label(c)
    
    ax.set_title(c)

    # axis labels
    ax.set_xlabel(f'PC {comp[0]}')
    ax.set_ylabel(f'PC {comp[1]}')

    


# rewrite the pc_column_plot to plot on the LL pcs
def ll_column_plot(adata, ax, c, comp = 0):

    # add c to title
    ax.set_title(c)

    eigvecs = adata.varm['leadlag_pcs']

    # take the real and complex part of the first eigenvector
    re = eigvecs[:,2*comp].real
    im = eigvecs[:,2*comp].imag

    # project the data onto the real and imaginary parts of the first eigenvector
    proj_re = adata.X @ re
    proj_im = adata.X @ im

    if c in adata.obs.columns:
        # check if the column is categorical
        if adata.obs[c].dtype == 'category':
            
            for iden in adata.obs[c].unique():

                sub_adata = adata[adata.obs[c] == iden]
                # project the data onto the real and imaginary parts of the first eigenvector
                proj_re_iden = sub_adata.X @ re
                proj_im_iden = sub_adata.X @ im
                ax.scatter(proj_re_iden, 
                        proj_im_iden, 
                        label = iden)
                
            ax.legend()
            # put legend in top right

            #Shrink current axis by 20%
            box = ax.get_position()
            ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

            # Put a legend to the right of the current axis
            ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

            
            ax.set_title(c)
            # add a colorbar

        elif 'coords' in c:
            ax.scatter(proj_re, proj_im, c = list(adata.obs[c]), cmap = 'hsv')
            
            # add a colorbar to the figure
            cbar = plt.colorbar(ax.collections[0], ax = ax)
            cbar.set_label(c)
            ax.set_xlabel('LL PCA Real')
            ax.set_ylabel('LL PCA Imaginary')
            ax.set_title(c)

            
        else:
            ax.scatter(proj_re, proj_im, c = list(adata.obs[c]))
            
            # add a colorbar to the figure
            cbar = plt.colorbar(ax.collections[0], ax = ax)
            cbar.set_label(c)
            ax.set_xlabel('LL PCA Real')
            ax.set_ylabel('LL PCA Imaginary')
            ax.set_title(c)

    # c is a gene
    elif c in adata.var_names:
        
        ax.scatter(proj_re, proj_im, c = list(adata[:, c].X), cmap = 'viridis')
        ax.set_xlabel('LL PCA Real')
        ax.set_ylabel('LL PCA Imaginary')
        ax.set_title(c)
        cbar = plt.colorbar(ax.collections[0], ax = ax)
        cbar.set_label(c)

def plot_2d(adata, c, mode = 'll', comp = None, scale = 1):

    # if c is not a list make it a list
    if not isinstance(c, list):
        c = [c]

    # if mode is ll make sure that leadlag_pcs is in adata.varm
    if mode == 'll':
        if 'leadlag_pcs' not in adata.varm.keys():
            raise ValueError('leadlag_pcs not in adata.varm, please run chnt.leadlag()')
        
    # if mode is pca make sure that X_pca is in adata.obsm
    if mode == 'pca':
        if 'X_pca' not in adata.obsm.keys():
            raise ValueError('PCA not computed')

    # intialize the figure with len(c) subplots, and a size which is a function of len(c)
    fig, ax = plt.subplots(1, len(c), figsize = (scale*8*(len(c)), scale*6))

    a = len(c)

    for i, c in enumerate(c):
        if mode == 'll':
            if comp is None:
                comp = 0

            if a == 1:
                ll_column_plot(adata, ax, c, comp)
            elif a > 1:
                ll_column_plot(adata, ax[i], c, comp)
        elif mode == 'pca':
            if comp is None:
                comp = [0,1]
            
            if a == 1:
                pc_column_plot(adata, ax, c, comp)
            elif a > 1:
                pc_column_plot(adata, ax[i], c, comp)
    

    plt.show()



def scatter3D(adata, color = None, comp = [0,1,2], title = False, color_continuous_scale = 'Viridis', mode = 'pca'):

    # check length of combo is 3
    if len(comp) != 3:
        raise ValueError('combo must be a list of length 3')
    
    # check pca is computed
    if mode == 'pca':
        if 'X_pca' not in adata.obsm.keys():
            raise ValueError('PCA not computed')

    elif mode == 'ef':
        if 'X_ef' not in adata.obsm.keys():
            raise ValueError('Effective Resistance not computed')
    
    # check color is in adata.obs
    if color is not None:

        if color not in adata.var_names:
            if color not in adata.obs.columns:
                raise ValueError('color not in adata.obs or adata.var_names, please select one of the following: ' + str(adata.obs.columns))

    # load the best pca projection
    if mode == 'pca':
        data = adata.obsm['X_pca'][:,comp]
    elif mode == 'ef':
        data = adata.obsm['X_ef'][:,comp]

    # make a dataframe of the data and phases
    dummy_df = pd.DataFrame(data)

    # exact the color and save to df
    if color is not None:
        if color in adata.obs.columns:
            dummy_df['color'] = list(adata.obs[color])
        elif color in adata.var_names:
            dummy_df['color'] = list(adata[:,color].X[:,0])

    # make a 3d scatter plot of the data using plotly express
    
    if color is not None:
        fig = px.scatter_3d(dummy_df, x=0, y=1, z=2, color = 'color', color_continuous_scale=color_continuous_scale)
    else:
        fig = px.scatter_3d(dummy_df, x=0, y=1, z=2)

    # make plotly figure square
    fig.update_layout(scene_aspectmode='cube')

    # add a legend to the figure specifying which color corresponds to which phase
    fig.update_layout(legend=dict(
        title = color,
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))
    fig.update_layout(showlegend=True)

    # make the points in the legend larger
    fig.update_layout(legend=dict(
        itemsizing='constant'
    ))

    # make the markers in the smaller, and give them a thin black  outline
    fig.update_traces(marker=dict(size=4, line=dict(width=1, color='DarkSlateGrey')))


    # set the title centering it at the top of the plot
    if title != False:
        fig.update_layout(title=dict(
            text=title,
            xref="paper",
            x=0.5,
            yref="paper",
            y=1.0,
            font=dict(
                size=24,
                color="#7f7f7f"
            )   
        ))

    # make figure height larger
    fig.update_layout(height=800)

    # make figure width smaller
    fig.update_layout(width=1000)

    fig.show()

def leadlag_table(adata, k = 10):
    """
    Create a table of the top k genes by leadlag score
    """
    leadlag = adata.uns['leadlag']
    idx = np.argpartition(leadlag, -k, axis=None)[-k:]

    idx = idx[np.argsort(-leadlag.flat[idx])]
    idx = np.unravel_index(idx, leadlag.shape)

    idx

    gene_names = adata.var_names

    # store them in a dataframe
    df = pd.DataFrame({
        'Leadin': gene_names[idx[0]],
        'Laggin': gene_names[idx[1]],
        'Leadlag Coefficient': leadlag[idx]
    })

    print(df)

def plot_3d_scatter_ll_pcs_two_conditions(
    adata_cond1,
    adata_cond2,
    adata_pcs,
    genes,
    condition_label_1='Condition 1',
    condition_label_2='Condition 2',
    pc_index=0,
    vertical_layer='pre_magic',
    leadlag_layer=None,
    camera_eye=(1.5, -1.5, 0.75),
    title_texts=None
):
    """
    Plots 3D scatter subplots for each gene in `genes`,
    displaying the real (x) and imaginary (y) components of
    the chosen lead-lag PC projection vs. gene expression (z-axis)
    for two different conditions in a single figure (with 2 subplots).

    Parameters
    ----------
    adata_cond1 : AnnData
        AnnData object for the first condition.
    adata_cond2 : AnnData
        AnnData object for the second condition.
    adata_pcs : AnnData
        AnnData object containing the 'leadlag_pcs' array in `adata_pcs.varm['leadlag_pcs']`.
        Also used for referencing `adata_pcs.var_names` if needed.
    genes : list of str
        List of gene names to plot.
    condition_label_1 : str, optional
        Label to display for the first condition in the plot legend/subplot title.
    condition_label_2 : str, optional
        Label to display for the second condition in the plot legend/subplot title.
    pc_index : int, optional
        Index of the lead-lag PC to use (default is 0 for the first PC).
    vertical_layer : str, optional
        Name of the layer in adata_cond1 / adata_cond2 to use
        as the main expression matrix (default 'pre_magic').
        If None, uses the existing X.
    leadlag_layer : str, optional
        Name of the layer for the lead-lag transformations, if any.
        If None, uses the existing X for that purpose.
    camera_eye : tuple(float, float, float), optional
        A 3-tuple specifying (x, y, z) for the 3D camera viewpoint (default (1.5, -1.5, 0.75)).
    title_texts : list of str or None, optional
        A list of custom titles, one for each gene. If None, each figure's title is just the gene name.

    Returns
    -------
    figs : list
        A list of Plotly figure objects (one per gene).
    """

    figs = []

    # We'll use all genes in adata_pcs.var_names for the lead-lag projection
    ll_genes = adata_pcs.var_names

    # If custom titles are supplied, ensure they match the number of genes
    if title_texts is not None and len(title_texts) != len(genes):
        raise ValueError("Length of title_texts must match length of genes.")

    for i, gene in enumerate(genes):
        # Copy the original AnnData objects so we can safely modify X
        adata1 = adata_cond1.copy()
        adata2 = adata_cond2.copy()

        adata1m = adata_cond1.copy()
        adata2m = adata_cond2.copy()

        # Switch the X matrix to the specified vertical_layer, if given
        if vertical_layer is not None:
            adata1.X = adata1.layers[vertical_layer]
            adata2.X = adata2.layers[vertical_layer]

        # Switch the X matrix to the specified leadlag_layer for lead/lag, if given
        if leadlag_layer is not None:
            adata1m.X = adata1m.layers[leadlag_layer]
            adata2m.X = adata2m.layers[leadlag_layer]

        # We'll copy again for taking gene expression
        adata1_expr = adata1.copy()
        adata2_expr = adata2.copy()

        # Subset to the lead-lag genes
        adata1m = adata1m[:, ll_genes]
        adata2m = adata2m[:, ll_genes]

        # Extract the chosen lead-lag PC (e.g., pc_index=0 for the first PC)
        pcs = adata_pcs.varm['leadlag_pcs'][:, pc_index]
        # Normalize the PC to unit length
        pcs = pcs / np.linalg.norm(pcs)

        # Real/Imag parts for condition 1
        real1 = np.real(np.dot(adata1m.X, pcs))
        imag1 = np.imag(np.dot(adata1m.X, pcs))
        gene_expr1 = adata1_expr[:, gene].X.flatten()

        # Real/Imag parts for condition 2
        real2 = np.real(np.dot(adata2m.X, pcs))
        imag2 = np.imag(np.dot(adata2m.X, pcs))
        gene_expr2 = adata2_expr[:, gene].X.flatten()

        # Determine the shared Z-axis and color range
        z_min = min(gene_expr1.min(), gene_expr2.min())
        z_max = max(gene_expr1.max(), gene_expr2.max())

        color_min = z_min
        color_max = z_max

        # Create subplots
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'scatter3d'}, {'type': 'scatter3d'}]],
            subplot_titles=(condition_label_1, condition_label_2)
        )

        # Subplot 1 (Condition 1)
        fig.add_trace(
            go.Scatter3d(
                x=real1,
                y=imag1,
                z=gene_expr1,
                mode='markers',
                marker=dict(
                    size=4,
                    color=gene_expr1,
                    colorscale='viridis',
                    cmin=float(color_min),
                    cmax=float(color_max),
                    line=dict(width=1, color="DarkSlateGrey")
                ),
                name=condition_label_1
            ),
            row=1, col=1
        )

        # Subplot 2 (Condition 2)
        fig.add_trace(
            go.Scatter3d(
                x=real2,
                y=imag2,
                z=gene_expr2,
                mode='markers',
                marker=dict(
                    size=4,
                    color=gene_expr2,
                    colorscale='viridis',
                    cmin=float(color_min),
                    cmax=float(color_max),
                    line=dict(width=1, color="DarkSlateGrey")
                ),
                name=condition_label_2
            ),
            row=1, col=2
        )

        # Common layout settings
        fig.update_layout(
            scene=dict(
                xaxis_title='LL PCA Real',
                yaxis_title='LL PCA Imaginary',
                zaxis_title=f'{gene} Expression',
                zaxis=dict(range=[z_min, z_max]),
                aspectmode="cube",
                camera=dict(
                    eye=dict(
                        x=camera_eye[0],
                        y=camera_eye[1],
                        z=camera_eye[2]
                    )
                )
            ),
            scene2=dict(
                xaxis_title='LL PCA Real',
                yaxis_title='LL PCA Imaginary',
                zaxis_title=f'{gene} Expression',
                zaxis=dict(range=[z_min, z_max]),
                aspectmode="cube",
                camera=dict(
                    eye=dict(
                        x=camera_eye[0],
                        y=camera_eye[1],
                        z=camera_eye[2]
                    )
                )
            ),
            coloraxis=dict(
                cmin=float(color_min),
                cmax=float(color_max),
                colorscale='viridis',
                colorbar=dict(title=gene)
            ),
            width=1600,
            height=800
        )

        # Determine the plot title for this figure
        if title_texts is not None:
            plot_title = title_texts[i]
        else:
            plot_title = gene

        fig.update_layout(title_text=plot_title)

        figs.append(fig)

    return figs


def plot_3d_scatter_ll_pcs_single_condition(
    adata_cond,
    adata_pcs,
    genes,
    pc_index=0,
    condition_label='Condition',
    vertical_layer='pre_magic',
    leadlag_layer=None,
    camera_eye=(1.5, -1.5, 0.75),
    title_texts=None
):
    """
    Plots a 3D scatter of real (x) and imaginary (y) components of
    a lead-lag PC projection vs. gene expression (z-axis) for a single condition.

    Parameters
    ----------
    adata_cond : AnnData
        AnnData object containing cells for a single condition.
    adata_pcs : AnnData
        AnnData object containing the 'leadlag_pcs' array in `adata_pcs.varm['leadlag_pcs']`.
        Also used for referencing `adata_pcs.var_names` if needed.
    genes : list of str
        List of gene names to plot.
    pc_index : int, optional
        Index of the lead-lag PC to use (default is 0 for the first PC).
    condition_label : str, optional
        Label to display for the condition in the plot legend/title.
    vertical_layer : str, optional
        Name of the layer in `adata_cond` to use for the main expression matrix X.
        If None, uses `adata_cond.X` as-is. Default is 'pre_magic'.
    leadlag_layer : str, optional
        Name of the layer for the lead-lag transformations, if any.
        If None, uses the existing X for that purpose.
    camera_eye : tuple (float, float, float), optional
        A 3-tuple that specifies the (x, y, z) position of the camera eye for the 3D plot viewpoint.
        Default is (1.5, -1.5, 0.75).
    title_texts : list of str or None, optional
        A list of custom titles (same length as `genes`). If None, each figure's title is just the gene name.

    Returns
    -------
    figs : list
        A list of Plotly Figure objects (one per gene).
    """

    figs = []

    # We'll use all genes in adata_pcs.var_names for the lead-lag projection
    ll_genes = adata_pcs.var_names

    # If custom titles are supplied, ensure they match the number of genes
    if title_texts is not None and len(title_texts) != len(genes):
        raise ValueError("Length of title_texts must match length of genes.")

    for i, gene in enumerate(genes):
        # Copy the original AnnData object so we can safely modify X
        adata_expr = adata_cond.copy()  # This will be used for gene expression
        adata_proj = adata_cond.copy()  # This will be used for lead-lag projection

        # Switch the X matrix to the specified vertical_layer, if given
        if vertical_layer is not None:
            adata_expr.X = adata_expr.layers[vertical_layer]

        # Switch the X matrix to the specified leadlag_layer, if given
        if leadlag_layer is not None:
            adata_proj.X = adata_proj.layers[leadlag_layer]

        # Subset to the lead-lag genes for projection
        adata_proj = adata_proj[:, ll_genes]

        # Extract the chosen lead-lag PC (e.g., pc_index=0 for the first PC)
        pcs = adata_pcs.varm['leadlag_pcs'][:, pc_index]

        # Normalize the PC to unit length
        pcs = pcs / np.linalg.norm(pcs)

        # Project onto that PC, then take real/imag
        real_vals = np.real(np.dot(adata_proj.X, pcs))
        imag_vals = np.imag(np.dot(adata_proj.X, pcs))
        gene_expr = adata_expr[:, gene].X.flatten()

        # Determine color range (z-axis range) based on this gene's expression
        z_min = gene_expr.min()
        z_max = gene_expr.max()

        # Create a single 3D scatter plot
        fig = make_subplots(
            rows=1, cols=1,
            specs=[[{'type': 'scatter3d'}]],
            subplot_titles=[condition_label]
        )

        fig.add_trace(
            go.Scatter3d(
                x=real_vals,
                y=imag_vals,
                z=gene_expr,
                mode='markers',
                marker=dict(
                    size=4,
                    color=gene_expr,
                    colorscale='viridis',
                    cmin=float(z_min),
                    cmax=float(z_max),
                    line=dict(width=1, color="DarkSlateGrey")
                ),
                name=condition_label
            ),
            row=1, col=1
        )

        # Update layout
        fig.update_layout(
            scene=dict(
                xaxis_title='LL PCA Real',
                yaxis_title='LL PCA Imaginary',
                zaxis_title=f'{gene} Expression',
                zaxis=dict(range=[z_min, z_max]),
                aspectmode="cube",
                camera=dict(
                    eye=dict(
                        x=camera_eye[0],
                        y=camera_eye[1],
                        z=camera_eye[2]
                    )
                )
            ),
            width=900,
            height=700
        )

        # Determine the plot title:
        # If a custom title was provided, use it. Otherwise default to the gene name.
        if title_texts is not None:
            plot_title = title_texts[i]
        else:
            plot_title = gene

        fig.update_layout(title_text=plot_title)

        figs.append(fig)

    return figs



### --- PERSISTENCE DIAGRAM STATISTICS --- ###

def l_transform(pdgm):
    pratios = [elem[1]/elem[0] for elem in pdgm]
    loglog_ratio = np.log(np.log(pratios))
    corr_factor = np.euler_gamma + np.mean(loglog_ratio)
    l_value = loglog_ratio - corr_factor
    return l_value

def update_data_dict(data_dict, adata, population, gs_size, population_keyword = 'population', do_magic= False):
    sub_adata = adata[adata.obs[population_keyword] == population]
    
    if do_magic:
            sce.pp.magic(sub_adata, name_list='all_genes', knn=5)
            
    gs = random.sample(list(sub_adata.var_names), gs_size)
    pdgm = rng.singlecell.pdiagram_from_anndata(sub_adata, var_names = gs)
    data_dict[population][gs_size].append(pdgm)
    
def pdgm_to_pBS(pdgm):
    """
    Calculate the KS test p-value of the L-transformed persistence diagram against the L-Gumbel distribution.
    """
    pval = ss.ks_1samp(l_transform(pdgm), ss.gumbel_l().cdf).pvalue
    return pval

def pdgm_to_pMY(pdgm):
    """ 
    Calculate the KS test p-value of the persistence diagram against the Pareto distribution.
    """
    pratios = [elem[1]/elem[0] for elem in pdgm]
    alpha = len(pdgm) / sum(np.log(pratios))
    pval = ss.ks_1samp(pdgm.pratios, ss.pareto(b = alpha).cdf).pvalue
    return pval

def pdgm_to_pNorm(pdgm):
    """ 
    Calculate the KS test p-value of the persistence diagram against the Normal distribution.
    """
    pratios = [elem[1]/elem[0] for elem in pdgm]
    mu = np.mean(pratios)
    sd = np.std(pratios)
    pval = ss.ks_1samp(pratios, ss.norm(loc = mu, scale = sd).cdf).pvalue
    return pval

def data_to_pBS(data):
    """
    Calculate the KS test p-value of a point cloud's persistence diagram against the L-Gumbel distribution.
    """
    pdgm = ripser(data, maxdim=1)['dgms'][1]
    pval = pdgm_to_pBS(pdgm)

    return pval

def data_to_pNorm(data):
    """
    Calculate the KS test p-value of a point cloud's persistence diagram against the Normal distribution.
    """
    pdgm = ripser(data, maxdim=1)['dgms'][1]
    pval = pdgm_to_pNorm(pdgm)

    return pval

# rewrite the code in the box above as a function with input adata and combos
def PCA_persistence_info(adata, pca_combos, mode = 'pca'):
    """
    A function to calculate the persistence diagram and assosicated statistics for each combo in combos and store them in a list
    ----------

    Parameters:
        adata (anndata.AnnData): an AnnData object
        pca_combos (list): a list of lists of integers, each list of integers is a combination of PCs

    Returns:
        df (pandas.DataFrame): a pandas dataframe with the following columns:
            combo (list): a list of integers, each integer is a PCA index
            min_adj_pvals (float): the minimum adjusted p-value for the persistence diagram
            minpvals (float): the minimum p-value for the persistence diagram
            ksLGumbel (float): the Kolmogorov-Smirnov statistic for the persistence diagram under the L-transformed LGumbel distribution
            ksNormal (float): the Kolmogorov-Smirnov statistic for the persistence diagram under the L-transformed Normal distribution
            adj_pvals (list): a list of adjusted p-values for each point in the persistence diagram
            pvals (list): a list of p-values for each point in the persistence diagram
            pdgm (list): a list of lists, each list is a point in the persistence diagram
    """

    pds = []
    for combo in pca_combos:
        if mode == 'pca':
            pds.append(ripser(adata.obsm['X_pca'][:,combo])['dgms'][1])
        elif mode == 'ef':
            pds.append(ripser(adata.obsm['X_ef'][:,combo])['dgms'][1])   

    pds_L = []
    ksLGumbel = []
    ksNormal = []

    for p in pds:
        pds_L.append(l_transform(p))
        ksLGumbel.append(pdgm_to_pBS(p))
        ksNormal.append(pdgm_to_pNorm(p))


    pvals = []
    minpvals = []
    adj_pvals = []
    min_adj_pvals = []
    

    for L in pds_L:
        pvals.append(np.exp(-np.exp(L)))
        minpvals.append(np.exp(-np.exp(np.min(L))))
        adj_pvals.append(np.exp(-np.exp(L)) * len(L))
        min_adj_pvals.append(np.min(np.exp(-np.exp((L))) * len(L)))

    df = pd.DataFrame({'combo': pca_combos, 
                       'min_adj_pvals': min_adj_pvals,
                       'minpvals': minpvals,
                       'ksLGumbel': ksLGumbel,
                       'ksNormal': ksNormal,
                       'adj_pvals': adj_pvals, 
                       'pvals': pvals, 
                       'pdgm' : pds})

    df = df.sort_values(by=['min_adj_pvals'])
    return df

# turn the above 3 cells into a single function with inputs adata, gs_collection, random state
# and outputs the df
def circ_enrich(adata, gs_collection, comp = [0,1,2],  k = None, exponent = 2, min_genes = None):
    
    if k != None:
        comp = list(range(k))
    else:
        k = max(comp)+1

    pdgm_ls = []
    pbar = tqdm(gs_collection.items(), total=len(gs_collection))

    if min_genes is None:
        min_genes = k +1

    for gs_name, gs in pbar:
        sub_gs_genes = adata.var_names.intersection(gs)
        sub_adata = adata[:, sub_gs_genes].copy()

        if sub_adata.n_vars < min_genes:
            continue

        sc.tl.pca(sub_adata, n_comps=k)
        diameter = max(distance.pdist(sub_adata.obsm["X_pca"]))
        pdgm_pca = PCA_persistence_info(sub_adata, [comp])
        pdgm_pca["diameter"] = diameter
        pdgm_pca.index = [gs_name]
        pdgm_ls.append(pdgm_pca)

    if len(pdgm_ls) != 0:
        df = pd.concat(pdgm_ls)

    data_dict = {}
    for gs_name, row in df.iterrows():
        pdgm = rng.PDiagram(row.pdgm, diameter=row.diameter, dim=1)
        data_dict[gs_name] = [
            rng.ring_score_from_pdiagram(pdgm, score_type="length", exponent=exponent),
            rng.ring_score_from_pdiagram(pdgm, score_type="diameter", exponent= exponent),
            rng.ring_score_from_pdiagram(pdgm, score_type="ratio", exponent=exponent), 
            rng.ringscore.statistics.min_pvalue_from_pdiagram(pdgm),
            rng.ringscore.statistics.min_pvalue_from_pdiagram(
                pdgm,
                remove_top_n=0,
            ),
        ]

    col_names = [
        "score_length",
        "score_diameter",
        "score_ratio",
        "min_pvalue",
        "min_pvalue_no_top",
    ]

    ring_score_df = pd.DataFrame(data_dict, index=col_names).T

    df = df.merge(ring_score_df, left_index=True, right_index=True)

    return df

def filter_cells_by_density_iterative(adata, n_iter=3, n_pcs=3, bandwidth=0.5,
                                        lower_percentile=10, upper_percentile=90,
                                        n_neighbors=30, recompute_pca=False):
    """
    Iteratively filters cells in an AnnData object based on the density of their PCA coordinates,
    using a nearest-neighbor approximation for efficiency.

    Parameters:
    -----------
    adata : AnnData
        The annotated data matrix.
    n_iter : int, optional (default: 3)
        Number of iterations to perform density-based filtering.
    n_pcs : int, optional (default: 3)
        Number of principal components to consider for density estimation.
    bandwidth : float, optional (default: 0.5)
        Bandwidth parameter for the Gaussian kernel used in density estimation.
    lower_percentile : float, optional (default: 10)
        Lower percentile threshold to filter out cells with the lowest density.
    upper_percentile : float, optional (default: 90)
        Upper percentile threshold to filter out cells with the highest density.
    n_neighbors : int, optional (default: 30)
        Number of nearest neighbors to use for density estimation.
    recompute_pca : bool, optional (default: False)
        Whether to recompute PCA on the filtered data at each iteration.

    Returns:
    --------
    AnnData
        Filtered AnnData object containing only cells within the specified density range
        after the iterative filtering process.
    """
    import numpy as np
    from sklearn.neighbors import NearestNeighbors
    import scanpy as sc

    # Compute PCA if not already done
    if 'X_pca' not in adata.obsm:
         sc.tl.pca(adata)
    
    # Extract the first `n_pcs` PCA coordinates
    X = adata.obsm['X_pca'][:, :n_pcs]

    for i in range(n_iter):
        # Build the nearest neighbor model and query the n_neighbors for each cell
        nbrs = NearestNeighbors(n_neighbors=n_neighbors, algorithm='auto').fit(X)
        distances, _ = nbrs.kneighbors(X)
        
        # Compute density using only the nearest neighbors.
        # Here, each cell's density is the sum of Gaussian weights of its distances.
        # The Gaussian kernel used is: exp(-0.5 * (distance / bandwidth)**2)
        density = np.sum(np.exp(-0.5 * (distances / bandwidth)**2), axis=1)
        
        # Store density for this iteration in the AnnData object
        adata.obs[f'density_iter_{i+1}'] = density
        
        # Determine density thresholds based on the desired percentiles
        lower_threshold = np.percentile(density, lower_percentile)
        upper_threshold = np.percentile(density, upper_percentile)
        
        # Create a mask for cells whose density falls within the specified range
        keep_idx = (density > lower_threshold) & (density < upper_threshold)
        adata = adata[keep_idx].copy()
        print(f"Iteration {i+1}: {adata.n_obs} cells remain.")
        
        # Update the PCA coordinates for the next iteration:
        if recompute_pca:
            sc.tl.pca(adata, n_comps=n_pcs)
            X = adata.obsm['X_pca'][:, :n_pcs]
        else:
            # If not recomputing PCA, filter the existing PCA coordinate matrix
            X = X[keep_idx]
    
    return adata

# turn the above 3 cells into a single function with inputs adata, gs_collection, random state
# and outputs the df
def circ_enrich_ef(adata, gs_collection, comp = [0,1,2],  k = None, exponent = 2, min_genes= None, n_neighbors = 5):
    

    if k != None:
        comp = list(range(k))
    else:
        k = max(comp)+1

    pdgm_ls = []
    pbar = tqdm(gs_collection.items(), total=len(gs_collection))

    if min_genes is None:
        min_genes = k +1

    for gs_name, gs in pbar:
        sub_gs_genes = adata.var_names.intersection(gs)
        sub_adata = adata[:, sub_gs_genes].copy()

        if sub_adata.n_vars < min_genes:
            continue

        effective_resistence(sub_adata, num_neighbors=n_neighbors, k=k)

        diameter = max(distance.pdist(sub_adata.obsm["X_ef"]))
        pdgm_pca = PCA_persistence_info(sub_adata, [comp], mode = 'ef')
        pdgm_pca["diameter"] = diameter
        pdgm_pca.index = [gs_name]
        pdgm_ls.append(pdgm_pca)

    if len(pdgm_ls) != 0:
        df = pd.concat(pdgm_ls)

    data_dict = {}
    for gs_name, row in df.iterrows():
        pdgm = rng.PDiagram(row.pdgm, diameter=row.diameter, dim=1)
        data_dict[gs_name] = [
            rng.ring_score_from_pdiagram(pdgm, score_type="length", exponent=exponent),
            rng.ring_score_from_pdiagram(pdgm, score_type="diameter", exponent= exponent),
            rng.ring_score_from_pdiagram(pdgm, score_type="ratio", exponent=exponent), 
            rng.ringscore.statistics.min_pvalue_from_pdiagram(pdgm),
            rng.ringscore.statistics.min_pvalue_from_pdiagram(
                pdgm,
                remove_top_n=0,
            ),
        ]

    col_names = [
        "score_length",
        "score_diameter",
        "score_ratio",
        "min_pvalue",
        "min_pvalue_no_top",
    ]

    ring_score_df = pd.DataFrame(data_dict, index=col_names).T

    df = df.merge(ring_score_df, left_index=True, right_index=True)

    return df



# turn the above 3 cells into a single function with inputs adata, gs_collection, random state
# and outputs the df
def circ_enrich_density(adata, gs_collection, comp = [0,1,2],  k = None, exponent = 2, bandwidth=0.3,lower_percentile=5, upper_percentile=100, min_genes= None):
    
    if k != None:
        comp = list(range(k))
    else:
        k = max(comp)+1

    pdgm_ls = []
    pbar = tqdm(gs_collection.items(), total=len(gs_collection))

    if min_genes is None:
        min_genes = k +1

    for gs_name, gs in pbar:
        sub_gs_genes = adata.var_names.intersection(gs)
        sub_adata = adata[:, sub_gs_genes].copy()

        

        if sub_adata.n_vars < min_genes:
            continue

        sc.tl.pca(sub_adata, n_comps=k)

        sub_adata = filter_cells_by_density(sub_adata, n_pcs=k, bandwidth=bandwidth,lower_percentile=lower_percentile, upper_percentile=upper_percentile)

        diameter = max(distance.pdist(sub_adata.obsm["X_pca"]))
        pdgm_pca = PCA_persistence_info(sub_adata, [comp])
        pdgm_pca["diameter"] = diameter
        pdgm_pca.index = [gs_name]
        pdgm_ls.append(pdgm_pca)

    if len(pdgm_ls) != 0:
        df = pd.concat(pdgm_ls)

    data_dict = {}
    for gs_name, row in df.iterrows():
        pdgm = rng.PDiagram(row.pdgm, diameter=row.diameter, dim=1)
        data_dict[gs_name] = [
            rng.ring_score_from_pdiagram(pdgm, score_type="length", exponent=exponent),
            rng.ring_score_from_pdiagram(pdgm, score_type="diameter", exponent= exponent),
            rng.ring_score_from_pdiagram(pdgm, score_type="ratio", exponent=exponent), 
            rng.ringscore.statistics.min_pvalue_from_pdiagram(pdgm),
            rng.ringscore.statistics.min_pvalue_from_pdiagram(
                pdgm,
                remove_top_n=0,
            ),
        ]

    col_names = [
        "score_length",
        "score_diameter",
        "score_ratio",
        "min_pvalue",
        "min_pvalue_no_top",
    ]

    ring_score_df = pd.DataFrame(data_dict, index=col_names).T

    df = df.merge(ring_score_df, left_index=True, right_index=True)

    return df

def ring_score(adata, score_type = 'ratio', exponent = 2, comp = np.arange(5), recompute = False):
    if 'pdgm' not in adata.uns.keys() or recompute:
        adata.uns['pdgm'] = rng.pdiagram(adata.obsm['X_pca'][:, comp])

    return rng.ring_score_from_pdiagram(adata.uns['pdgm'], score_type = score_type, exponent = exponent)


def ring_score_from_adata(sub_adata, comp = [0,1]):
    ripser_result = ripser(
        sub_adata.obsm["X_pca"][:,comp],
        coeff=3,
        do_cocycles=False,
        maxdim=1,
    )
    # Get 1-persistence diagram
    pdgm = ripser_result["dgms"][1]

    return rng.ring_score_from_pdiagram(pdgm, score_type='diameter')



def calculate_pvalue_from_empirical_scores(test_score, empirical_scores):
    ecdf = ss.ecdf(empirical_scores)
    return ecdf.sf.evaluate(test_score)

from statsmodels.distributions.empirical_distribution import ECDF

def calculate_pvalue_from_empirical_scores2(test_score, empirical_scores):
    ecdf = ECDF(empirical_scores)
    return 1-ecdf(test_score)

 
def permutation_pvalue(adata, gs, n_ensemble=2**7, score_type="diameter", n_comps = 3, bandwidth=0.3,lower_percentile=5, upper_percentile=100):
    sub_gs_genes = adata.var_names.intersection(gs)
    sub_adata = adata[:, sub_gs_genes].copy()

    sc.tl.pca(sub_adata, n_comps=n_comps)

    sub_adata = filter_cells_by_density(sub_adata, n_pcs=n_comps, bandwidth=bandwidth,lower_percentile=lower_percentile, upper_percentile=upper_percentile)
    

    test_pdgm = rng.pdiagram_from_point_cloud(sub_adata.obsm["X_pca"])
    test_score = rng.ring_score_from_pdiagram(test_pdgm, score_type=score_type)

    empirical_scores = []

    pbar = tqdm(range(n_ensemble), total=n_ensemble)
    for _ in pbar:
        n_genes = len(sub_gs_genes)

        random_gs_genes = random.sample(list(adata.var_names), n_genes)
        sub_adata = adata[:, random_gs_genes].copy()

        sc.tl.pca(sub_adata, n_comps=3)
        diameter = max(distance.pdist(sub_adata.obsm["X_pca"]))
        pdgm_pca = PCA_persistence_info(sub_adata, [[0, 1, 2]])
        pdgm = rng.PDiagram(pdgm_pca.pdgm[0], diameter=diameter, dim=1)
        score = rng.ring_score_from_pdiagram(pdgm, score_type="diameter")
        empirical_scores.append(score)

    pvalue = calculate_pvalue_from_empirical_scores2(test_score, empirical_scores)

    fig, ax = plt.subplots()

    ax.hist(empirical_scores, bins=20, alpha=0.5, label="empirical")
    ax.axvline(test_score, color="r", label="test")

    # label axes
    ax.set_xlabel("Ring score")
    ax.set_ylabel("Frequency")

    return pvalue, empirical_scores, test_score

def plot_diagram(adata, comp = [0,1,2]):

    # check PCA computed
    if "X_pca" not in adata.obsm:
        sc.tl.pca(adata, n_comps=5)
    
    ripser_result = ripser(
        adata.obsm["X_pca"][:,comp],
        coeff=3,
        do_cocycles=True,
        maxdim=1,
    )
    # Get 1-persistence diagram
    pdgm = ripser_result["dgms"][1]

    # identify the index of the longest interval
    idx = np.argmax(pdgm[:, 1] - pdgm[:, 0])
    max_birth, max_death = pdgm[idx]

    fig, ax = plt.subplots()
    rng.PDiagram(pdgm).plot(ax=ax)
    ax.scatter(max_birth, max_death, 75, "k", "x")
    ax.set_title(f"Max 1D birth = {max_birth:.2f}, death = {max_death:.2f}")


# A helper function for pd_analysis
def intersect(gs, adata):

    out = []

    for elem in gs:

        if elem in adata.var_names:

            out.append(elem)

    return out


# A helper function for pd_anaysis
def subset_adata(gs,adata):
    """
    A function to 

    Parameters 
    ---- 
    """
    I = intersect(gs,adata)

    if len(I) == 0:
        return None

    return adata[:, I].copy()


# rewrite the code in the box above as a function with input adata and combos
def pd_analysis(adata, gene_sets):
    """
    A function to calculate the persistence diagram and assosicated statistics for each combo in combos and store them in a list
    ----------

    Parameters:
        adata (anndata.AnnData): an AnnData object
        gene_sets (Dict): a dictionary of gene sets, each gene set is a list of gene names

    Returns:
        df (pandas.DataFrame): a pandas dataframe with the following columns:
            gs_name (str): the name of the gene set
            gs_genes (list): a list of genes in the gene set
            min_adj_pvals (float): the minimum adjusted p-value for the persistence diagram
            minpvals (float): the minimum p-value for the persistence diagram
            ksLGumbel (float): the Kolmogorov-Smirnov statistic for the persistence diagram under the L-transformed LGumbel distribution
            ksNormal (float): the Kolmogorov-Smirnov statistic for the persistence diagram under the L-transformed Normal distribution
            adj_pvals (list): a list of adjusted p-values for each point in the persistence diagram
            pvals (list): a list of p-values for each point in the persistence diagram
            pdgm (list): a list of lists, each list is a point in the persistence diagram
    """

    # initialize the list of persistence diagrams
    pds = []

    # initialize the list of gene set names and the list of genes in each gene set
    gs_names = []
    gs_genes = [] 

    # loop through each gene set
    for gs_name, gs in gene_sets.items():
        
        # find the intersection of the genes in the gene set and the genes in adata.var_names
        gs = intersect(gs,adata)

        # if the intersection is empty, skip to the next gene set
        if len(gs) == 0:
            continue
        
        # add the name of the gene set to gs_names and the genes in the gene set to gs_genes
        gs_names.append(gs_name)
        gs_genes.append(gs)

        # subset adata by the genes in the gene set
        sub_adata = subset_adata(gs,adata)

        # calculate the persistence diagram for the subset of adata
        pds.append(ripser(sub_adata.X)['dgms'][1])   

    # initialize the list of L-transformed persistence diagrams and the list of p-values for the persistence diagrams under the L-transformed LGumbel and Normal distributions
    pds_L = []
    ksLGumbel = []
    ksNormal = []

    for p in pds:
        pds_L.append(l_transform(p))
        ksLGumbel.append(pdgm_to_pBS(p))
        ksNormal.append(pdgm_to_pNorm(p))


    pvals = []
    minpvals = []
    adj_pvals = []
    min_adj_pvals = []
    

    for L in pds_L:
        pvals.append(np.exp(-np.exp(L)))
        minpvals.append(np.exp(-np.exp(np.max(L))))
        adj_pvals.append(np.exp(-np.exp(L)) * len(L))
        min_adj_pvals.append(np.min(np.exp(-np.exp((L))) * len(L)))

    df = pd.DataFrame({'gs_name': gs_names, 
                       'min_adj_pvals': min_adj_pvals,
                       'minpvals': minpvals,
                       'ksLGumbel': ksLGumbel,
                       'ksNormal': ksNormal,
                       'gs_genes': gs_genes,
                       'adj_pvals': adj_pvals, 
                       'pvals': pvals, 
                       'pdgm' : pds})

    df = df.sort_values(by=['min_adj_pvals'])
    return df
    


### --- PLOTTING PCA DATA --- ###

# a function to list all length 2 and length 3 combinations of integers below n
def get_combos(n):
    """
    A function to list all length 2 and length 3 combinations of integers below n.

    Parameters
    ----------
    n : int
        An integer.

    Returns
    -------
    combos : list
        A list of lists of integers, each list of integers is a combination of integers below n.
    """
    combos = []
    for i in range(0,n-1):
        for j in range(i+1,n):
            combos.append([i,j])
    for i in range(0,n-1):
        for j in range(i+1,n):
            for k in range(j+1,n):
                combos.append([i,j,k])
    return combos

# a function to plot all PCA combos on the same figure as subplots, split into 2d and 2d
def plot_all_PC_combos(adata, combos = None):
    """

    A function to plot all combinations of PCA components on the same figure as subplots.

    Parameters
    ----------
    adata : AnnData
        Annotated data matrix.
    combos : list
        A list of lists of integers, each list of integers is a combination of PCA components to plot.

    Returns
    -------
    None.

    """
    
    # error checking
    assert type(combos) == list
    assert len(combos) == 20
    assert 'X_pca' in adata.obsm.keys(), 'adata must have a PCA embedding in adata.obsm["X_pca"]'

    # if combos is not specified, use all length 2 and 3 combinations of first 5 PCs
    if combos == None:
        combos = get_combos(5)

    # length 2 combos
    two_combos = [elem for elem in combos if len(elem) == 2]

    fig, axs = plt.subplots(5,2, figsize=(8,20))

    # put two_combos into a 4x3 grid
    for i in range(0,5):
        for j in range(0,2):

            axs[i,j].scatter(adata.obsm['X_pca'][:,two_combos[2*i+j][0]], adata.obsm['X_pca'][:,two_combos[2*i+j][1]])
            axs[i,j].set_title(str(two_combos[2*i+j]))

    fig.suptitle("PCA plots for all combinations of 2 genes")
    plt.show()

    # length 3 combos
    three_combos = [elem for elem in combos if len(elem) == 3]

    # make a 5x2 grid of 3d scatterplots for each length 3 combo using matplotlib
    fig = plt.figure(figsize=(8,20))
    for i in range(0,5):
        for j in range(0,2):
            ax = fig.add_subplot(5,2,2*i+j+1, projection='3d')
            ax.scatter(adata.obsm['X_pca'][:,three_combos[2*i+j][0]], adata.obsm['X_pca'][:,three_combos[2*i+j][1]], adata.obsm['X_pca'][:,three_combos[2*i+j][2]])
            ax.set_title(str(three_combos[2*i+j]))

    fig.suptitle("PCA plots for all combinations of 3 genes")
    plt.show()

    return None


# a function to plot the pca projection persistence diagram in a given row of a df
def plot_pca_pd(adata, df, row):
    """
    
    a function to plot the pca projection persistence diagram in a given row of a df

    ----------

    Parameters:
        adata (AnnData): an AnnData object

        df (pandas.DataFrame): a pandas dataframe with the following columns:
            combo (list): a list of integers, each integer is a PCA index
            min_adj_pvals (float): the minimum adjusted p-value for the persistence diagram
            minpvals (float): the minimum p-value for the persistence diagram
            adj_pvals (list): a list of adjusted p-values for each point in the persistence diagram
            pvals (list): a list of p-values for each point in the persistence diagram
            pdgm (list): a list of lists, each list is a point in the persistence diagram
            
        row (int): the row of df to plot

    Returns: 
        a plot of the pca projection persistence diagram in a given row of a df
    """

    fig = plt.figure(figsize=(10,5))

    # add a subplot for the pca projection
    if len(df.iloc[row]['combo']) == 2:
        ax = fig.add_subplot(1,2,1)
        ax.scatter(adata.obsm['X_pca'][:,df.iloc[row]['combo'][0]], adata.obsm['X_pca'][:,df.iloc[row]['combo'][1]])
        ax.set_title(str(df.iloc[row]['combo']))
    else:
        ax = fig.add_subplot(1,2,1, projection='3d')
        ax.scatter(adata.obsm['X_pca'][:,df.iloc[row]['combo'][0]], adata.obsm['X_pca'][:,df.iloc[row]['combo'][1]], adata.obsm['X_pca'][:,df.iloc[row]['combo'][2]])
        ax.set_title(str(df.iloc[row]['combo']))

    # add a subplot for the persistence diagram
    ax = fig.add_subplot(1,2,2)
    ax.scatter(df.iloc[row]['pdgm'][:,0], df.iloc[row]['pdgm'][:,1])

    # set the limits of the plot to be 10% larger than the max value in the persistence diagram
    m =np.max(df.iloc[row]['pdgm'][:,1])
    ax.set_xlim(0,1.1*m)
    ax.set_ylim(0,1.1*m)
    ax.set_aspect('equal', adjustable='box')

    # plot the diagonal
    ax.plot([0, 1], [0, 1], transform=ax.transAxes, ls="--", c=".3")
    ax.set_title("Persistence diagram")

    # add a title to the whole figure
    fig.suptitle("PCA projection and persistence diagram for " + str(df.iloc[row]['combo']) + " with min_adj_pval = " + str(df.iloc[row]['min_adj_pvals']))

    plt.show()

    return None






#### LEGACY LEADLAG 



# a function for turning a chain into a discretized chain
def discretize_chain(chain,d):
    """ 
    A function for turning a chain into a discretized chain

    Parameters
    ----------
    chain : numpy array
        A chain in R^n, represented as a numpy array of shape (p-1,2,n), where p is the number of points in the path.

    d : int
        The number of points in the discretized chain

    Returns
    -------
    d_chain : numpy array
        A discretized chain in R^n, represented as a numpy array of shape (p-1,d,n), where p is the number of points in the path.

    """

    r = chain.shape[0]

    n = chain.shape[2]

    d_chain = torch.zeros((r,d,n))

    t = np.linspace(0,1,d)

    for i in range(d):

        d_chain[:,i,:] = (1-t[i]) * chain[:,0,:] + t[i] * chain[:,1,:] 

    return d_chain


# a function for turning a chain into a cochain data matrix
def gen_CDM(vf,chain, d = 5):
    """
    A function for generating a cochain data matrix from a chain and a vector field

    Parameters
    ----------
    vf : a Pytorch Sequential object
        The vector field to be applied to the chain
    
    chain : a torch tensor of shape (r,2,n)
        The chain to be turned into a cochain data matrix

    d : int
        The number of discrete steps in the discretization of the chain
    
    Returns
    -------
    out : a torch tensor of shape (r,c)
        The cochain data matrix
    """

    
    # discretize the chain
    chain = discretize_chain(chain, d)

    # number of simplicies
    r = chain.shape[0]

    # number of discrete steps
    d = chain.shape[1]

    # dimension of ambient space
    n = chain.shape[2]

    # number of feature-cochains in the cochain data matrix
    c = int(vf[-1].out_features / n)

    # apply the vector field to the discretized chain
    out = vf(chain).reshape((r,d,n,c))

    # calculate the simplex gradients
    simplex_grad = chain[:,1,:] - chain[:,0,:]

    # swap dimensions n and c in out
    out = out.permute(0,1,3,2)

    # calculate the inner product of the vector field and the simplex gradients at each discrete step on each simplex
    inner_prod = torch.matmul(out,simplex_grad.T/(d-1))

    # take diagonal of out3 along axis 0 and 3 (this corresponds to correcting the broadcasted multplication effect)
    inner_prod = torch.diagonal(inner_prod, dim1 = 0, dim2 = 3)

    # permute dimensions 0 and 2 of out4
    inner_prod = inner_prod.permute(2,0,1)

    # apply the trapzoidal rule to the inner product
    cdm = (inner_prod[:,1:,:] + inner_prod[:,0:-1,:])/2
    cdm = cdm.sum(axis = 1)

    return cdm
