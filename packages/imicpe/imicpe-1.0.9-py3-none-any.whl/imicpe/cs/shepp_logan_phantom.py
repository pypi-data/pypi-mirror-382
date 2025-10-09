
import numpy as np

from skimage.data import shepp_logan_phantom
from skimage.transform import rescale, resize

def phantom_shepp_logan(N):
    """
    phantom_shepp_logan       Génère le phantom de Shepp-Logan 2D de taille NxN.

    Args:
    N (int)                    Taille du phantom

    Returns: 
    (numpy.ndarray)           Image du phantom
    """
    p = shepp_logan_phantom()
    p = resize(p, (int(N),int(N)), anti_aliasing=False)
    p[p<1e-10] = .1
    
    return p