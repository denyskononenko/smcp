import os
import glob
import numpy as np

from time import time
from numba import jit
from numpy.linalg import norm
from zernike3d import Zernike3D
from scipy.spatial import distance

def timeit(foo):
    """Calculate the elapsed time of the function foo"""
    def wrap(*args, **kargs):
        t1 = time()
        res = foo(*args, **kargs)
        t2 = time()
        print(f"function {foo.__name__} took: {round(t2 - t1, 6)} s")
        return res
    return wrap

def calc_basis_size(nmax: int):
    """Calculate size of the basis for given maximal n."""
    return int(sum([0.5 * ((n + 1)**2 + (n + 1)) for n in range(0, nmax + 1)]))

@timeit
def load_basis(basis_path: str, basis_size: int=-1) -> dict:
    """Upload given number of Zernike 3D functions basis."""
    basis = {}
    modes_list = sorted([[int(_) for _ in fname.rstrip('.npy').split('/')[-1].split('_')] for fname in  glob.glob(f'{basis_path}/*.npy')])
    
    for n, l, m in modes_list[:basis_size]:
        basis[(n, l, m)] = np.load(f'{basis_path}/{n}_{l}_{m}.npy')

    print(f"Length of the basis: {len(basis)}")
    return basis

@timeit
@jit(nopython=True, parallel=True)
def make_3d_img(atoms, ds: float=0.025) -> np.array:
    """
    Make 3D image from the list of atoms from crystal environment.
    Args:
        atoms: (list) contains the following atom information
        
        ```
        x y z ionicity_radius oxidation_number atomic_number
        ...
        ```
    Returns:
        (np.array) crystal environment on the mesh in form of numpy array.
    """
    smpl = np.arange(-1, 1 + ds, ds)
    N = smpl.shape[0]
    grid = np.zeros((N, N, N)) 

    for xi, yi, zi, ri, oi, atom_zi in atoms:
        for i, x in enumerate(smpl):
            for j, y in enumerate(smpl):
                for k, z in enumerate(smpl):
                    if (x - xi)**2 + (y - yi)**2 + (z - zi)**2 <= ri**2:
                        grid[i,j,k] = oi
    return grid

@timeit
def zernike3d_descriptor(img: np.array, basis: dict, nmax: int) -> list:
    """Construct Zernike 3D descriptor."""
    res = []
    # normalization factor is number of voxels in the unit sphere
    norm_factor = np.count_nonzero(np.real(basis[(0,0,0)]))

    for n in range(nmax + 1):
        for l in range(n + 1):
            if (n - l) % 2 == 0:
                for m in range(-l, l + 1):
                    Z = np.real(basis[(n,l,m)])
                    C = np.sum(Z * img) / norm_factor
                    res.append([n, l, m, C])
    return res

@timeit
def zernike3d_descriptor_invariant(img: np.array, basis: dict, nmax: int) -> list:
    """
    Construct rotationally invariant Zernike 3D descriptor.
    Args:
        img  : (np.array) target 3D image
        basis: (dict) dictionary of Zernike 3D functions wiht key n, l, m
        nmax : (int) maximal order of Zernike 3D function
    Returns:
        (list) descriptor of the img: n, l, descriptor_component_value
    """
    # normalization factor is number of voxels in the unit sphere
    norm_factor = np.count_nonzero(np.real(basis[(0,0,0)]))
    # agregate all m harmonics with n,l into vector
    # calculate norm of the vector to get the invariant descriptor of 3D image 
    descriptor_ri = []
    for n in range(nmax + 1):
        for l in range(n + 1):
            if (n - l) % 2 == 0:
                Cms = []
                for m in range(-l, l + 1):
                    Z = np.real(basis[(n,l,m)])
                    C = np.sum(Z * img) / norm_factor
                    Cms.append(C)
                descriptor_ri.append((n, l, norm(Cms)))
    
    return descriptor_ri

if __name__ == "__main__":
    n_max = 25
    basis_size = calc_basis_size(n_max)
    basis_path = 'basis/'
    basis = load_basis(basis_path, basis_size)

    test_env = [
        [-0.625718, -0.044363, -0.146979, 0.210000, -2, 8],
        [-0.062056, -0.091179, -0.383175, 0.210000, -2, 8],
        [-0.301820, -0.385205, -0.293569, 0.193333, 2, 80],
        [-0.049217, -0.089279, 0.413931, 0.210000, -2, 8]
    ]
    # sort atoms by ionicity radius
    test_env = sorted(test_env, key=lambda e: e[3], reverse=True)
    test_env = np.array(test_env, dtype=np.float32)
    print(test_env)
    print(type(test_env))

    img3d = make_3d_img(test_env, ds=0.025)
    # make rotationally invariant Zernike 3D descriptor 
    descr = zernike3d_descriptor_invariant(img3d, basis, n_max)



