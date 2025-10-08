import polars as pl
import pandas as pd
from scipy.spatial import distance
from scipy.spatial.distance import pdist, squareform

################################################################################

def hamming_dist_matrix(X):
    """
    Calculates the hamming distance matrix for a data matrix `X` using SciPy.

    Parameters (inputs)
    ----------
    X: a pandas/polars DataFrame or a NumPy array. It represents a data matrix.

    Returns (outputs)
    -------
    M: the hamming distance matrix between the rows of X.
    """

    if isinstance(X, pl.DataFrame):
        X = X.to_numpy()
    if isinstance(X, pd.DataFrame):
        X = X.to_numpy()    
            
    # Compute the pairwise distances using pdist and convert to a square form.
    M = squareform(pdist(X, metric='matching'))
    
    return M

################################################################################

def hamming_dist(xi, xr) :
    """
    Calculates the hamming distance between a pair of vectors.

    Parameters (inputs)
    ----------
    xi, xr: a pair of quantitative vectors. They represent a couple of statistical observations.

    Returns (outputs)
    -------
    The hamming distance between the observations `xi` and `xr`.
    """

    if isinstance(xi, (pl.DataFrame, pd.DataFrame)) :
        xi = xi.to_numpy().flatten()
    elif isinstance(xi, (pd.Series, pl.Series)) :
        xi = xi.to_numpy() 
    if isinstance(xr, (pl.DataFrame, pd.DataFrame)) :
        xr = xr.to_numpy().flatten()
    elif isinstance(xr, (pd.Series, pl.Series)) :
        xr = xr.to_numpy() 
        
    return distance.hamming(xi, xr)

################################################################################