
import numpy as np
from scipy import ndimage
import pywt


############################################################
## identity operator
############################################################
def Id(x):
    """
    Opérateur identité
   
    Args:
        X (numpy.ndarray)               signal 1D
                                    ou: image non vectorisée 2D
                                
    Returns: 
        (numpy.ndarray)                  X 
    """
    
    return x


############################################################
## differential forward and backward operators
############################################################
# gradient
def D(x):
    """
    Calcule le gradient par différences finies à droite.
    Autrement dit, D(x) calcule le produit matriciel Dx.
   
    Args:
        X (numpy.ndarray)               signal 1D
                                    ou: image non vectorisée 2D
                                
    Returns: 
        (numpy.ndarray)                 Gradient de X 
    """
    
    if x.ndim == 1:
        grad = np.concatenate((x[1:] - x[:-1], [0]))/2.

    elif x.ndim == 2:
        sz = x.shape
        Dx_im = np.concatenate((  x[:,1:] - x[:,:-1] , np.zeros((sz[0],1)) ), axis=1)/ 2.
        Dy_im = np.concatenate((  x[1:,:] - x[:-1,:] , np.zeros((1,sz[1])) ), axis=0)/ 2.
        
        grad = np.array([Dx_im,Dy_im])
    return grad

def Dt(x):
    """
    Calcule l’adjoint gradient par différences finies à droite.
    Autrement dit, Dt(x) calcule le produit matriciel D'x.
   
    Args:
        X (numpy.ndarray)               signal 1D
                                    ou: image non vectorisée 2D
                                
    Returns: 
        (numpy.ndarray)                 Divergence de X 
    """
    
    if x.ndim == 1:
        div = - np.concatenate(([x[0]], x[1:-1] - x[:-2], [-x[-2]])) /2.

    elif x.ndim == 3:
        x1 = x[0]
        x2 = x[1]
        div = - np.concatenate((x1[:,[0]], x1[:,1:-1] - x1[:,:-2], -x1[:,[-2]]), axis=1) /2. \
              - np.concatenate((x2[[0],:], x2[1:-1,:] - x2[:-2,:], -x2[[-2],:]), axis=0) /2.
    return div

# laplacian
def L(x):
    """
    Calcule la dérivée seconde d’un signal, ou le laplacien dans le cas d’une image.
    Autrement dit, L(x) calcule le produit matriciel Lx.
   
    Args:
        X (numpy.ndarray)               signal 1D
                                    ou: image non vectorisée 2D
                                
    Returns: 
        (numpy.ndarray)                 Laplacien de X 
    """
    
    if x.ndim == 1:
        ker = np.array([1, -2, 1])
        #lap = np.convolve(x,ker,'same')
        lap = ndimage.convolve1d(x,ker,mode='nearest')
    elif x.ndim == 2:
        ker = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])    # V4
        #ker = np.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]])    # V8
        lap = ndimage.convolve(x,ker,mode='nearest')
    return lap

def Lt(x):
    """
    Calcule l’adjoint du laplacien.
    Autrement dit, Lt(x) calcule le produit matriciel L'x.
   
    Args:
        X (numpy.ndarray)               signal 1D
                                    ou: image non vectorisée 2D
                                
    Returns: 
        (numpy.ndarray)                 Adjoint du Laplacien de X 
    """
    
    if x.ndim == 1:
        ker = np.array([1, -2, 1])
        #lap = np.correlate(x,ker,'same')
        lap = ndimage.correlate1d(x,ker,mode='nearest')
    elif x.ndim == 2:
        ker = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])    # V4
        #ker = np.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]])    # V8
        lap = ndimage.correlate(x,ker,mode='nearest')
    return lap


############################################################
## Wavelet transforms
############################################################
def fwt(x,wavelet,level):
    """
    Calcule la transformée en ondelettes directe 1D.

    Args:
    x (numpy.ndarray)               signal 1D

    Returns: 
    (numpy.ndarray)                 Vecteur des coefficients de la décomposition en ondelettes de x
    """

    dim = x.ndim

    coeffs = pywt.wavedec(x, wavelet, level=level, mode="periodization")
    coeff_arr, _, _ = pywt.ravel_coeffs(coeffs)
            
    return coeff_arr


def iwt(x,wavelet,level):
    """
    Calcule la transformée en ondelettes inverse 1D.

    Args:
    x (numpy.ndarray)               Vecteur des coefficients d'ondelettes                
    wavelet (string)                Nom de l'ondelette mère (voir la librairie pywt)     
    level (int)                     Niveau de décompisition                                     

    Returns: 
    (numpy.ndarray)                 Signal correspondant aux coefficients d'ondelettes donnés par x
    """

    J = level
    N = len(x)
    _, coeffs_slices, coeffs_shapes = pywt.ravel_coeffs(pywt.wavedec(np.ones(N), wavelet=wavelet, level=J, mode='periodization'))
    
    if coeffs_shapes is None:
        # compute coeffs size at each level
        sizes = [N // (2**j) for j in range(J, 0, -1)] + [N // (2**J)]

        # coefficients splitting
        start = 0
        coeffs = []
        for size in reversed(sizes):
            coeffs.append(x[start:start + size])
            start += size
    else:
        coeffs = pywt.unravel_coeffs(x, coeffs_slices, coeffs_shapes, output_format='wavedec')

    # reconstruct corresponding signal
    signal = pywt.waverec(coeffs, wavelet, mode="periodization")
            
    return signal


def fwt2(x,wavelet,level):
    """
    Calcule la transformée en ondelettes directe 2D.

    Args:
    x (numpy.ndarray)               image NON vectorisée 2D        
    wavelet (string)                Nom de l'ondelette mère (voir la librairie pywt)     
    level (int)                     Niveau de décompisition                    

    Returns: 
    (numpy.ndarray)                 Vecteur des coefficients de la décomposition en ondelettes de x
    """

    coeffs = pywt.wavedec2(x, wavelet, level=level, mode="periodization")
    coeff_arr, _, _ = pywt.ravel_coeffs(coeffs)

    return coeff_arr

def iwt2(x,wavelet,level):
    """
    Calcule la transformée en ondelettes inverse 2D.

    Args:
    x (numpy.ndarray)               Vecteur des coefficients d'ondelettes            
    wavelet (string)                Nom de l'ondelette mère (voir la librairie pywt)     
    level (int)                     Niveau de décompisition                                                          

    Returns: 
    (numpy.ndarray)                 Image correspondante aux coefficients d'ondelettes donnés par x
    """

    J = level
    N = len(x)

    _, coeffs_slices, coeffs_shapes = pywt.ravel_coeffs(pywt.wavedec2(np.ones((int(np.sqrt(N)),int(np.sqrt(N)))), wavelet=wavelet, level=J, mode='periodization'))
    
    coeffs = pywt.unravel_coeffs(x, coeffs_slices, coeffs_shapes,
                                      output_format='wavedec2')
    
    # reconstruct corresponding signal
    image = pywt.waverec2(coeffs, wavelet, mode="periodization")

    return image


############################################################
## Operator and matrix norm
############################################################
def opNorm(op,opt,dim,xn):
    """
    Calcule la norme de l'opérateur OP, dont 
    l'opérateur transposé est OPT, en dimension DIM

    Args:
        OP (function)                   opérateur direct
        OPT (function)                  opérateur adjoint
        DIM (int)                       1 or 2
        
    Returns:
        (float)                         norme de l'opérateur OP
    """
    
    def T(x):
        return opt(op(x))

    # match dim:
    #     case 1:  
    #         xn = np.random.standard_normal((64))
    #     case 2:
    #         xn = np.random.standard_normal((64,64))

    xnn = xn

    n = np.zeros((1000,),float)
    n[1] = 1
    tol  = 1e-4
    rhon = n[1]+2*tol

    k = 1
    while abs(n[k]-rhon)/n[k] >= tol:
        xn  = T(xnn)
        xnn = T(xn)

        rhon   = n[k]
        n[k+1] = np.sum(xnn**2)/np.sum(xn**2)
   
        k = k+1

    N = n[k-1] + 1e-16
    return 1.01* N**(.25)              # sqrt(L) gives |||T|||=|||D'D||| ie |||D|||^2


def matNorm(M):
    """
    Calcule la norme de la matrice M

    Args:
        M (numpy.ndarray)               matrice dont on souhaite calculer la norme
        
    Returns:
        (float)                         norme de la matrice M
    """
    
    def T(x):
        return np.dot(M.T, np.dot(M,x))

    xn = np.random.standard_normal((M.shape[1]))
    xnn = xn

    n = np.zeros((1000,),float)
    n[1] = 1
    tol  = 1e-4
    rhon = n[1]+2*tol

    k = 1
    while abs(n[k]-rhon)/n[k] >= tol:
        xn  = T(xnn)
        xnn = T(xn)

        rhon   = n[k]
        n[k+1] = np.sum(xnn**2)/np.sum(xn**2)
   
        k = k+1

    N = n[k-1] + 1e-16
    return 1.01* N**(.25)              # sqrt(L) gives |||T|||=|||D'D||| ie |||D|||^2