import numpy as np

def mse(I,ref):
    return np.sum((I-ref)**2)/I.size

def snr(I,ref):
    return 10* np.log10(np.sum(ref**2)/np.sum((I-ref)**2))