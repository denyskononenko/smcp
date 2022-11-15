# math
import numpy as np
from scipy.special import sph_harm
from math import factorial as fact
from math import pi, sqrt, sin, cos, atan2
from numpy.linalg import norm

# plotting
import matplotlib.pyplot as plt

def binomial(n, k): return fact(n)  / (fact(k) * fact(n - k))

class Zernike3D:
    def __init__(self, IMG3D: np.array):
        self.IMG3D = IMG3D

    def radial(self, n: int, l: int) -> ():
        """Radial Zernike polynomials normalized for 3D case for given order n, l."""
        # normalization factor
        Q = lambda k, l, nu: ((-1)**(k + nu) / 4**k) *\
                             sqrt((2 * l + 4 * k + 3) / 3) *\
                             (binomial(2 * k, k) * binomial(k, nu) * binomial(2 * (k + l + nu) + 1, 2 * k) / binomial(k + l + nu, k))
        if (n - l) % 2 != 0: 
            return lambda r: 0
        else:
            return lambda r: sum([Q((n - l) / 2, l, nu) * r**(2 * nu + l) for nu in range((n - l) // 2 + 1)]) 
    
    def zfunction(self, n: int, l: int, m: int) -> ():
        """Zernike 3D function of given order n, l, m."""
        # check parameters validity
        # init radial part
        R = self.radial(abs(n), abs(l))
        # 3D Zernike function
        def Z(x, y, z) -> ():
            if x**2 + y**2 + z**2 > 1:
                return 0
            else:
                r = sqrt(x**2 + y**2 + z**2)
                theta = atan2(sqrt(x**2 + y**2), z)
                phi = atan2(y, x)
                return  R(r) * sph_harm(m, l, phi, theta)
        return Z

    def zfunction_on_grid(self, n: int, l: int, m: int) -> np.array:
        """Calculate 3D Zernike function on the grid with shape of the given 3D image."""
        # discretization parameters
        max_x, max_y, max_z = self.IMG3D.shape[:3]
        dx, dy, dz = 2 / (max_x - 1), 2 / (max_y - 1), 2 / (max_z - 1)
        x, y, z = np.arange(-1, 1 + dx, dx), np.arange(-1, 1 + dy, dy), np.arange(-1, 1 + dz, dz) 
        Z = self.zfunction(n, l, m)
        Z_on_grid = np.array([[[np.real(Z(xi, yi, zi)) for xi in x] for yi in y] for zi in z])
        return Z_on_grid
    
    def allowed_modes(self, nmax: int, nmin: int=0) -> list:
        """Generate list of (n, l, m) allowed modes for given maximum order of n: nmax."""
        return [(n, l, m) for n in range(nmin, nmax + 1) for l in range(nmax + 1) for m in range(-l, l+1) if (n - l) % 2 == 0 and n >= l]

    def descriptor(self, nmax: int) -> list:
        """Zernike 3D descriptor vector of given order for 3D image."""
        # determine the Zernike functions on the grid of the given 3D image
        vector = []
        # calculate the normalization factor: number of pixels in the unit sphere, i.e. mode 0,0,0
        norm_factor = np.count_nonzero(np.real(self.zfunction_on_grid(0,0,0)))
        # calculate allowed modes for given n
        allowed_modes = self.allowed_modes(nmax)
        
        for ni, li, mi in allowed_modes:
            # calculation of the 3D Zernike function on the grid 
            A = self.zfunction_on_grid(ni, li, mi) # <- most computationally comlex part
            component = np.sum(A * self.IMG3D) / norm_factor
            vector.append((ni, li, mi, component))
        return vector

    def invariant_descriptor(self, nmax: int) -> list:
        """Rotationally invariant Zernike 3D descriptor."""
        # agregate all m harmonics with n,l into vector
        # calculate norm of the vector to get the invariant descriptor of 3D image 
        descriptor = self.descriptor(nmax)
        descriptor_ri = [ [descriptor[0][0], descriptor[0][1], [descriptor[0][3]]] ]
        # assemble vectors [[n,l, A], ...], where A composed of Znlm with m = [-l, l]
        for n, l, m, Z in descriptor[1:]:
            prev_n, prev_l = descriptor_ri[-1][:2]
            if n == prev_n and l == prev_l:
                descriptor_ri[-1][2] += [Z]
            else:
                descriptor_ri.append([n, l, [Z]])
        # calculate norm of A vectors 
        descriptor_ri_norm = [(n, l, norm(Z)) for n, l, Z in descriptor_ri]
        return descriptor_ri_norm

    def reconstruct(self, descriptor: list) -> np.array:
        """Reconstruct given 3D image from descriptor composed of Zernike 3D moments."""
        res = np.zeros(self.IMG3D.shape[:3])

        for n, l, m, coeff in descriptor:
            res += coeff * self.zfunction_on_grid(n, l, m)
        return res
        
    def plot_radial(self, n: int, l: int):
        """Plot radial Zernike polynom of order n."""
        R = self.radial(n, l)
        x = np.arange(0, 1, 0.01)
        y = np.array([R(r) for r in x])

        plt.figure(dpi=100)
        plt.plot(x, y)
        plt.xlim(0, 1.1)
        plt.ylabel(f'$R_{n}^{l}(r)$')
        plt.xlabel('r')
        plt.show()

    def plot_zfunction_slice(self, n: int, l: int, m: int, lattitude: int=1):
        """Plot 3D Zernike moment slice at the level lattitude * grid_step."""
        Z = self.zfunction(n, l, m)
        d = 0.01
        x = np.concatenate([np.arange(-1, -d, d), np.arange(d, 1 + d, d)])
        cut_const_z = np.array([[np.real(Z(xi, yi, lattitude * d)) for xi in x] for yi in x])
        cut_const_x = np.array([[np.real(Z(lattitude * d, yi, zi)) for zi in x] for yi in x])

        plt.figure(dpi=100)
        plt.subplot(1,2,1)
        plt.imshow(cut_const_z, cmap='rainbow')
        plt.tick_params(top=False, bottom=False, left=False, right=False, labelleft=False, labelbottom=False)
        plt.title('xy')

        plt.subplot(1,2,2)
        plt.imshow(cut_const_x, cmap='rainbow')
        plt.tick_params(top=False, bottom=False, left=False, right=False, labelleft=False, labelbottom=False)
        plt.title('zy')
        plt.show()
