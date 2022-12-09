import os
import time
import numpy as np
from zernike3d import Zernike3D
from utils import timeit

@timeit
def save_basis(path: str, nmax: int = 25, nmin: int = 0, ds: float = 0.025):
    """
    Save basis of Zernike 3D functions as binary .npy files.
    Basis funtion is determined in the unit ball, 
    i.e. x in [-1, 1], y in [-1, 1], z in [-1, 1].

    Args:
        path: (str) path to save the basis 
        nmax: (int) maximal order of the Zernike 3D polynimial in the basis
        nmin: (int) minimal order of the Zernike 3D polynimial in the basis
        ds  : (float) discretization step 
    """
    N = int((2 + ds) // ds + 1)
    img3d = np.zeros((N, N, N)) 

    zen = Zernike3D(img3d)
    print(f"Saving basis nmin={nmin} nmax={nmax}\ngrid size: {img3d.shape}")
    allowed_modes = zen.allowed_modes(nmax, nmin=nmin)
    for n, l, m in allowed_modes[:]:
        t1 = time.time()

        np.save(f'{path}/{n}_{l}_{m}.npy', zen.zfunction_on_grid(n, l, m))
        
        t2 = time.time()
        print(f"{n}, {l}, {m} took {round(t2 - t1, 6)} s")
    
if __name__ == '__main__':
    __file_dir__ = os.getcwd() # '/'.join(__file__.split('/')[:-1])
    basis_path = f'{__file_dir__}/basis_test/'
    
    # check if directory for model serialization exists 
    if not os.path.isdir(basis_path): 
        os.mkdir(basis_path)

    # save the basis 
    save_basis(basis_path)


