
import numpy as np
from scipy import ndimage
import pywt


mat2mask = lambda mat, H, W, M:  np.reshape(mat.T, (H, W, M))

    
def starPattern(N, M):
    """
    starPattern       Génère un masque de taille NxN en étoile (tomographie) correspondant à M mesures.

    Args:
    N (int)                    Taille du masque
    M (int)                    Nombre de mesures

    Returns: 
    Amat (numpy.ndarray)       Matrice d'acquisition
    mask (numpy.ndarray)       Masque 
    """
    

    mask2mat = lambda mask: np.reshape(mask,  (M, N**2))  
     
    H = int(N)
    W = int(N)
    
    n = int(N)
    r = np.linspace(-1, 1, 3*n)*n

    nrho = 2**4
    R = np.round(np.linspace(-n/2, n/2, nrho))#.astype(int)

    ntheta = M//nrho
    T = np.linspace(0, np.pi, ntheta+1, endpoint=False)

    mask = np.zeros((H, W, ntheta, nrho))
    for itt in range(ntheta):
        theta = T[itt]
            
        for itr in range(nrho):
            rho = R[itr]
                
            x = np.round(r*np.cos(theta) + n/2 - rho*np.sin(theta))#.astype(int)
            y = np.round(r*np.sin(theta) + n/2 + rho*np.cos(theta))#.astype(int)

            valid = np.where((x >= 0) & (x < n) & (y >= 0) & (y < n))
            x = x[valid].astype(int)
            y = y[valid].astype(int)

            tmpM = np.zeros((H, W))
            tmpM[y, x] = 1
 
            mask[:, :, itt, itr] = tmpM

    mask = mask.reshape((H, W, M))
    Amat = mask2mat(mask)
        
    return Amat, mask
        
        
def getAcquisitionImage(x,mask):
    _, _, Nmeasures = mask.shape
    
    zim = np.sum(mask * np.tile(x[..., None], (1, 1, Nmeasures)), axis=2)
    zim = zim / np.max(zim)
    
    return zim



# def sub2ind(array_shape, rows, cols):
#     ind = rows*array_shape[1] + cols
#     return ind.astype(int)

# def ind2sub(array_shape, ind):
#     rows = (ind.astype('int') / array_shape[1])
#     cols = (ind.astype('int') % array_shape[1]) # or numpy.mod(ind.astype('int'), array_shape[1])
#     return (int(rows), int(cols))