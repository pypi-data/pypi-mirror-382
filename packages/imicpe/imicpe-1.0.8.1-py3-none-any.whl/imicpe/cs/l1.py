
import numpy as np
from scipy import ndimage

from .operators import *
from tqdm import tqdm_notebook as tqdm

def l1(opreg,A,At,z,x0,lam):
    """
    l1       Algorithme Forward-Backward pour résoudre le problème
                xhat = argmin  ||Hx-z||_2^2 + lam.||Gx||_1
                        x
    
    en particulier : 
    - le modèle LASSO si G = Id,
    - le modèle TV si G = D (gradient) ou L (laplacien),
   
    Args:
        opreg (string)              nom de l'opérateur G sur lequel opère la contrainte de parcimonie {'id', 'gradient', 'laplacien'}
        A (fonction)    
        At (fonction)
        z
        x0 (numpy.ndarray)
        lam (float)
                                
    Returns: 
        xhat (numpy.ndarray)        solution du problème
        loss (numpy.ndarray)        évolution de la fonction de coût au cours des itérations
    """
    
    print('Running l1 model with ' +opreg+ ' sparsity constraint...\n\t')
    
    ### init ###
    dim = x0.ndim
    if opreg == 'id':
        G = Id
        Gt = Id
    elif opreg == 'gradient':
        G = D
        Gt = Dt
    if opreg == 'laplacien':
        G = L
        Gt = Lt
    
    # operator norms
    lipA = opNorm(A,At,dim,x0)
    lipG = opNorm(G,Gt,dim,x0)   

    # cost functions
    def f(x):           # data fidelity
        return np.sum(x**2)/2

    def R(x):           # regularization
        return np.sum(np.abs(x))
    
    def E(x,lam):       # total cost
        return f(A(x)-z) + lam*R(G(x))

    # proximity operator
    def proxl1(x,gam):
        return x - np.maximum(np.minimum(x,gam*np.ones(x.shape)),-gam*np.ones(x.shape))

    ### Algo ###
    niter       = 1e3;                                  # max number of iterations
    # model hyperparameters
    mu    = 5;                                          # Bregman parameter (in [1,10], should not vary)
    
    # algo hyperparameters
    gamx  = .9/(lipA**2 + mu*lipG**2); #.5e-1;          # gradient descent step (x subproblem)
    gamu  = 1/mu;                                       # proximal descent step (y subproblem)
    
    # initialize variables
    En = np.zeros((int(niter+1),),float) * np.nan
    xn = x0   #np.random.standard_normal((z.shape))
    un = G(xn)                                          # splitting variable
    bn = np.zeros(un.shape,float)                       # Bregman variable
    
    En[0] = E(xn,lam)

    # loop parameters
    k         = 0
    tol       = 1e-10
    stop_crit = En[0]
    
  
    with tqdm(total=niter) as pbar: 
        while (k < niter) and (stop_crit > tol):
            # yn subproblem
            Gxn = G(xn)
            un = proxl1(un - gamu*mu*(un-Gxn-bn/mu) , lam*gamu)
            
            # xn subproblem (relaxed): gradient descent step instead of GS iteration
            xn = xn - gamx*( At(A(xn)-z) - mu*Gt(un-Gxn-bn/mu) )

            # bn subproblem
            bn = bn - mu*(un-G(xn))
            
            # compute loss
            En[k+1] = E(xn,lam)
            
            # update loop parameters
            stop_crit = (En[k] - En[k+1])/En[k]
            k += 1
            pbar.update(1)
    
    pbar.close()
    xhat = xn
    loss = En
    
    return xhat, loss