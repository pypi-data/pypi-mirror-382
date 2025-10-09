import numpy as np
from scipy import ndimage
#import igl
import scipy.sparse as sp

############################################################
## identity operator
############################################################
def Id(x):
    """Opérateur identité
   
    Args:
        X (numpy.ndarray)               signal 1D ou: image non vectorisée 2D
                                
    Returns: 
        (numpy.ndarray)                  X 
    """
    
    return x


############################################################
## differential forward and backward operators
############################################################
# gradient
def D(x):
    """Calcule le gradient par différences finies à droite.
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
    """Calcule l’adjoint gradient par différences finies à droite.
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
    """Calcule la dérivée seconde d’un signal, ou le laplacien dans le cas d’une image.
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
    """Calcule l’adjoint du laplacien.
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

def generateDiff3D(vert, faces, dtype):
    """
    generateDiff3D       Génère la matrice de différentiation de type DTYPE (ordre 1 ou 2) en 3D
    
    Args:
        VERT (numpy.ndarray)            matrice Nx3 dont la i-ème ligne correspond au vecteur
                                            de coordonnées (X,Y,Z) du i-ème point du maillage
        FACES (numpy.ndarray)           matrice Nx3 dont la i-ème ligne donne les  numéros des
                                            3 points composant un triangle du maillage
        DTYPE(str)                      'gradient', 'laplacian'
    
    Returns:
        (numpy.ndarray)                 matrice 3D de différentiation de type DTYPE
    """
    
    if dtype == 'gradient':
        #matG = igl.grad(vert, faces)
        n = vert.shape[0]
        G = sp.lil_matrix((3 * len(faces), n))
        for f_idx, tri in enumerate(faces):
            i, j, k = tri
            vi, vj, vk = vert[i], vert[j], vert[k]
            # Normale du triangle
            normal = np.cross(vj - vi, vk - vi)
            area = np.linalg.norm(normal) / 2.0
            normal /= np.linalg.norm(normal) if np.linalg.norm(normal) > 0 else 1
            # Gradients barycentriques
            G_f = np.zeros((3, 3))
            G_f[:, 0] = np.cross(normal, vk - vj) / (2 * area)
            G_f[:, 1] = np.cross(normal, vi - vk) / (2 * area)
            G_f[:, 2] = np.cross(normal, vj - vi) / (2 * area)
            # Assignation dans la matrice globale
            for local_idx, global_idx in enumerate(tri):
                G[3 * f_idx: 3 * f_idx + 3, global_idx] = G_f[:, local_idx]
                
        matG = G.tocsc()
        
    elif dtype == 'laplacien':    
        #matG = igl.cotmatrix(vert, faces)
        n = vert.shape[0]
        L = sp.lil_matrix((n, n))
    
        for tri in faces:
            i, j, k = tri
            vi, vj, vk = vert[i], vert[j], vert[k]
        
            # Calcul des arêtes
            e0 = vj - vk
            e1 = vk - vi
            e2 = vi - vj
        
            # Longueurs des arêtes
            l0 = np.linalg.norm(e0)
            l1 = np.linalg.norm(e1)
            l2 = np.linalg.norm(e2)
        
            # Calcul des angles via le produit scalaire
            cot0 = np.dot(-e1, e2) / (l1 * l2)
            cot1 = np.dot(-e2, e0) / (l2 * l0)
            cot2 = np.dot(-e0, e1) / (l0 * l1)
        
            # Construction de la matrice du Laplacien
            L[i, j] += cot2
            L[j, i] += cot2
            L[j, k] += cot0
            L[k, j] += cot0
            L[k, i] += cot1
            L[i, k] += cot1
            L[i, i] -= (cot1 + cot2)
            L[j, j] -= (cot0 + cot2)
            L[k, k] -= (cot0 + cot1)
    
        matG = L.tocsc()
    
    return (matG/np.amax(matG)).toarray()



############################################################
## blurring operators
############################################################
def generatePSF(dim,blurtype,kernelSize):
    """Génère le noyau de convolution d’un flou de dimension DIM, de type BLURTYPE, 
    et de taille KERNELSIZE.
    
    Args:
        DIM (str)                       ’1D’ ou ’2D’
        BLURTYPE (str)                  ’none’, ’gaussian’ ou ’uniform’
        KERNELSIZE (int)                entier impair
                                
    Returns: 
        (numpy.ndarray)                 Noyau de convolution
    
    -> voir les fonctions A(x,h) et At(x,h).
    """

    # compute kernel
    if blurtype == 'none':
        h = np.array([1.])

    elif blurtype == 'gaussian':
        std = kernelSize/6
        x = np.linspace(-(kernelSize-1)/2, (kernelSize-1)/2, kernelSize)
        arg = -x**2/(2*std**2)
        h = np.exp(arg)

    elif blurtype == 'uniform':
        h = np.ones(kernelSize)
    
    # kernel normalization
    h = h/sum(h)

    # return kernel
    if dim == '1D':
        ker = h
    elif dim == '2D':
        ker = np.tensordot(h,h, axes=0)
    
    return ker 

def A(x,psf):
    """Permet de flouter l’image X par un flou de noyau PSF.
    Autrement dit, A(x,h) calcule le produit de convolution h*x, ou de manière équivalente, calcule
    le produit matriciel Hx.

    Args:
        X (numpy.ndarray)               signal 1D
                                    ou: image non vectorisée 2D
        PSF (numpy.ndarray)             doit être générée à partir de la fonction generatePSF

    Returns:
        (numpy.ndarray)                 Convolution de X par le noyau PSF
    """
    
    if x.ndim == 1:
        b = np.convolve(x,psf,'same')
    elif x.ndim == 2:
        b = ndimage.convolve(x,psf,mode='nearest')

    return b

def At(x,psf):
    """Permet de flouter l’image X par un flou de noyau la transposée de PSF.
    Autrement dit, A(x,h) calcule le produit de convolution h'*x, ou de manière équivalente, calcule
    le produit matriciel H'x.

    Args:
        X (numpy.ndarray)               signal 1D
                                    ou: image non vectorisée 2D
        PSF (numpy.ndarray)             doit être générée à partir de la fonction generatePSF

    Returns:
        (numpy.ndarray)                 Correlation de X par le noyau PSF
    """
    
    if x.ndim == 1:
        b = np.correlate(x,psf,'same')
    elif x.ndim == 2:
        b = ndimage.correlate(x,psf,mode='nearest')

    return b



############################################################
## TP3 - cartoon + texture decomposition operators (only 2D)
############################################################
def S(x):
    """Convolue X avec un noyau KER.
   
    Args:
        X (numpy.ndarray)               image non vectorisée 2D
                                
    Returns: 
        (numpy.ndarray)                 Convolution de X par le noyau KER
    """
    
    h,w = x.shape
    
    ox = np.linspace(-w/2+1/2, w/2-1/2, w)
    oy = np.linspace(-h/2+1/2, h/2-1/2, h)
    X,Y = np.meshgrid(ox, oy)
    dist  = np.sqrt(X**2/w**2 + Y**2/h**2);         # anisotropic distance
    n  = 5
    fc = 1/3                                        # in [0,1] since dist is normalized
    ker  = 1./(1 + (dist/fc)**(2*n))

    imf = np.real(np.fft.ifft2(np.fft.ifftshift(ker*np.fft.fftshift(np.fft.fft2(x)))))

    return imf

def St(x):   
    """Corrèle X avec un noyau KER.
   
    Args:
        X (numpy.ndarray)               image non vectorisée 2D
                                
    Returns: 
        (numpy.ndarray)                 Correlation de X par le noyau KER
    """
    
    h,w = x.shape
    
    ox = np.linspace(-w/2+1/2, w/2-1/2, w)
    oy = np.linspace(-h/2+1/2, h/2-1/2, h)
    X,Y = np.meshgrid(ox, oy)
    dist  = np.sqrt(X**2/w**2 + Y**2/h**2);         # anisotropic distance
    n  = 5
    fc = 1/3                                        # in [0,1] since dist is normalized
    ker  = 1./(1 + (dist/fc)**(2*n))

    imf = np.real(np.fft.ifft2(np.fft.ifftshift(np.conj(ker)*np.fft.fftshift(np.fft.fft2(x)))))

    return imf



############################################################
## Operator and matrix norm
############################################################
def opNorm(op,opt,dim):
    """Calcule la norme de l'opérateur OP, dont 
    l'opérateur transposé est OPT, en dimension DIM

    Args:
        OP (function)                   opérateur direct
        OPT (function)                  opérateur adjoint
        DIM (str)                       '1D', '2D'
        
    Returns:
        (float)                         norme de l'opérateur OP
    """
    
    def T(x):
        return opt(op(x))

    if dim == '1D':  
        xn = np.random.standard_normal((64))
    elif dim == '2D':
        xn = np.random.standard_normal((64,64))

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
    """Calcule la norme de la matrice M

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