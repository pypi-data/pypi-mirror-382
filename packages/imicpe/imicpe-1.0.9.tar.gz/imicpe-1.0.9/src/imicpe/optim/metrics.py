import numpy as np
import torch

def mse(I,ref):
    return np.round(np.sum((I-ref)**2)/I.size,5)

def snr(I,ref):
    return np.round(10* np.log10(np.sum(ref**2)/np.sum((I-ref)**2)),2)

