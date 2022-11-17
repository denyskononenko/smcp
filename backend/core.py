import os 
import glob
import json
import pickle
import numpy as np 
from numpy.linalg import norm

from pymatgen.core.sites import PeriodicSite
from pymatgen.core.structure import Structure  
from utils import *

_N_MAX_ = 25
# path
dirname = os.path.dirname(__file__)
ionrad_file = os.path.join(dirname, 'ionrad.json')
basis_path = os.path.join(dirname, 'basis/')

# ML Model
file_scalerX = os.path.join(dirname, 'ml/model/scalerX.sav')
file_scalerY = os.path.join(dirname, 'ml/model/scalerY.sav')
file_feat_selector = os.path.join(dirname, 'ml/model/feat_selector.sav')
file_model = os.path.join(dirname, 'ml/model/model.sav')

# bohr radii to angstroms conversion coefficient 
B2A = 0.5291
# read the file with ionic radii of atoms 
with open(ionrad_file, 'r') as f:
    CRYST_ION_RAD = json.load(f)

def get_site_Z(site: PeriodicSite) -> int:
    """Auxilary function to select atomic number of the PeriodicNeighbor."""
    return int(list(site.species.keys())[0].Z)

def get_site_OxN(site: PeriodicSite) -> int:
    """Auxilary function to select oxidation state of the PeriodicNeighbor."""
    return int(site.as_dict()['species'][0]['oxidation_state'])

class CrystalEnvironment:
    def __init__(self, 
                structure: Structure, 
                cu1: PeriodicSite, 
                cu2: PeriodicSite, 
                r_env: float = 4.0, 
                r_cu: float = 2.5,
                r_norm: float = 6.0,
                cryst_ion_rad: dict = CRYST_ION_RAD):
        self.structure = structure
        self.cu1 = cu1
        self.cu2 = cu2 
        self.r_env = r_env
        self.r_cu = r_cu
        self.r_norm = r_norm
        self.cryst_ion_rad = cryst_ion_rad
    
    @property 
    def centroid(self):
        return (self.cu2.coords - self.cu1.coords) / 2
    
    @property
    def cu_cu_dist(self):
        """Return Cu - Cu distance"""
        return norm(self.cu2.coords - self.cu1.coords) 

    @property
    def chem_composition(self):
        """Return chemical composition, aka tuple of sorted species."""
        return tuple(sorted([_[-1] for _ in self.get_atoms()]))

    @timeit
    def get_atoms(self) -> list:
        """
        Constrct crystal environment of given pair of atoms (self.cu1, self.cu2) for given structure.
        The local crystal environemnt includes atoms from the nearest environement of self.cu1 and self.cu2
        and atoms in the sphere with center in the centroid between self.cu1 and self.cu2.
        Returns: list[list]
            ```
            [
            [x, y, z, ionicity_radius, oxidation_number, atomic_number],
            ...
            ]
            ```
        """
        # radius of the sphere with the center in centroid 
        r_sph = max(self.r_env, self.cu_cu_dist / 2 + 0.2)
        # atoms in environment = atoms in central sphere + atoms from nearest environment of the copper
        atoms_in_env = self.structure.get_sites_in_sphere(self.centroid, r_sph) +\
                       self.structure.get_sites_in_sphere(self.cu1.coords, self.r_cu) +\
                       self.structure.get_sites_in_sphere(self.cu2.coords, self.r_cu)
        

        cu_cu_env = [[
                        *((site.coords - self.centroid) / self.r_norm), # normalized x y z with substracted zero 
                        self.cryst_ion_rad[str(get_site_Z(site))][str(get_site_OxN(site))] / self.r_norm, # ionic radius
                        get_site_OxN(site), # oxidation number 
                        get_site_Z(site) # atomic number
                    ] 
                    for site in atoms_in_env]
        # sort by the atomic number 
        cu_cu_env = sorted(cu_cu_env, key=lambda e: e[-1], reverse=True)
        return cu_cu_env

    def __eq__(self, other):
        """
        Override the implementation of the equivalence operation for the local crystal environemnt.
        Local crystal environment are equivalent if:
        (i) Cu1-Cu2 distances are equal
        (ii) Numbers of atoms are equal 
        (iii) Chemical compositions are equal 
        """
        cu_cu_threshold = 0.01 

        if isinstance(other, CrystalEnvironment):
            dist_cu_cu_self  = self.cu_cu_dist
            dist_cu_cu_other = other.cu_cu_dist
            dist_cu_cu_diff  = abs(dist_cu_cu_self - dist_cu_cu_other)
            
            atoms_self  = self.get_atoms() 
            atoms_other = other.get_atoms()

            chemcomp_self  = self.chem_composition
            chemcomp_other = other.chem_composition

            print(f'Dist self: {dist_cu_cu_self}\t dist other: {dist_cu_cu_other}')
            print(f'Chem comp self: {chemcomp_self}, other: {chemcomp_other}')

            if (dist_cu_cu_diff <= cu_cu_threshold) and\
               (len(atoms_self) == len(atoms_other)) and\
               (chemcomp_self == chemcomp_other):
                return True

        return False

class SpinModel:
    def __init__(self, 
                    structure: Structure, 
                    basis, 
                    scaler_X, 
                    scaler_Y, 
                    feat_selector, 
                    model,
                    r_cu_cu_max: float = 6.0, 
                    scaling: list = [2, 2, 2],
                    nmax: int = _N_MAX_
                    ):
        self.structure = structure
        self.basis  = basis 
        self.scaler_X =  scaler_X
        self.scaler_Y = scaler_Y
        self.feat_selector = feat_selector
        self.model = model
        self.r_cu_cu_max = r_cu_cu_max
        self.scaling = scaling         # scaling coefficients to build the super cell
        self.nmax = nmax               # maximum n for basis of Zernike 3D functions
        self.cu_envs, self.cu_couplings = self.struct2env()

    @property 
    def superstructure(self):
        """Return structure with scaled unit cell."""
        superstructure = self.structure.copy()
        superstructure.make_supercell(scaling_matrix=self.scaling) # make the supercell
        return superstructure

    @property
    def cu_sites(self):
        """Select Cu2+ stes from the upscaled unit cell."""
        cu_sites = [] # list to store Cu2+ sites        
                
        # find Cu2+ sites 
        for site in self.superstructure:
            if get_site_Z(site) == 29 and get_site_OxN(site) == 2:
                cu_sites.append(site)
        print(type(cu_sites[1]))
        return cu_sites

    @property
    def vertices(self):
        """Vertices of the spin model as [[x,y,z], ... ]"""
        return [site.coords.tolist() for site in self.cu_sites]

    @property
    def edges(self):
        """Edges of the spin model."""
        return self.cu_couplings
    
    @property
    def exchanges(self):
        return [self.descr2hop(self.env2descr(env)) for env in self.cu_envs]
    
    @property
    def distances(self):
        return [round(env.cu_cu_dist, 3) for env in self.cu_envs]

    @timeit
    def struct2env(self) -> list:
        """ 
        Select all unique Cu-Cu crystal environments for given structure.
        
        Return:
            (list[CrystalEnvironment], [[(i,j), ...]]) list of crystal environments and couplings
        """
        # make supercell 
        cu_envs = []                      # list for Cu2+ pairs environments
        cu_couplings = []                 # indices of coupled Cu2+ sites for each determined hopping
        cu_pairs_count = 0                # counter of Cu2+ pairs 

        # find Cu2+ pairs 
        for i in range(len(self.cu_sites) - 1):
            for j in range(i + 1, len(self.cu_sites)):
                cu_pairs_count += 1
                cu1, cu2 = self.cu_sites[i], self.cu_sites[j]
                t_env = CrystalEnvironment(self.superstructure, cu1, cu2)
                if (t_env.cu_cu_dist <= self.r_cu_cu_max):
                    if t_env not in cu_envs:
                        cu_envs.append(t_env)
                        cu_couplings.append([(i, j)])
                    else:
                        for l, e in enumerate(cu_envs):
                            if t_env == e:
                                cu_couplings[l].append((i, j))
        
        print(f'Sites in the cell: {len(self.structure)}')
        print(f'Sites in the supercell: {len(self.superstructure)}')
        print(f'# of Cu sites in the supercell: {len(self.cu_sites)}')
        print(f'# of pairs: {cu_pairs_count}')
        print(f'# of unique environemnts: {len(cu_envs)}')
        print(f'Couplings in the supercell:')
        for _ in cu_couplings:
            print(_)

        return cu_envs, cu_couplings
    
    def env2descr(self, env: CrystalEnvironment) -> list:
        """
        Create rotationally-invariant 3D Zernike desriptor for local crystal environment.
        Args:
            env: (CrystalEnvironment) local crystal environment for which to create descriptor
        Return: 
            (dict) rotationally-invariant 3D Zernike descriptor
        """
        dist = env.cu_cu_dist
        env_atoms = env.get_atoms()
        env_atoms = np.array(env_atoms, dtype=np.float32)
        # convert atoms in environment to the 3D image 
        img3d = make_3d_img(env_atoms, ds=0.025)
        # make rotationally invariant Zernike 3D descriptor 
        descr = zernike3d_descriptor_invariant(img3d, self.basis, self.nmax)  # [[n, l, Coeff], ...]

        X = np.array([[dist] + [_[2] for _ in descr]])
        print(f'Predictors: {len(X)}')
        return X
    
    def descr2hop(self, descr: list):
        """Predict the hopping for the given descriptor of the local crystal environment."""
        # min max scale the feature vector 
        X = self.scaler_X.transform(descr)
        # select important features 
        X_new = self.feat_selector.transform(X)
        # predict the hopping, value is scaled from 0 to 1
        Y_pred = self.model.predict(X_new) 
        # inverse transform the predicted value 
        Y_pred = self.scaler_Y.inverse_transform(Y_pred.reshape(-1, 1))
        return Y_pred.flatten()[0]

def validate_cif(cif_file: str):
    pass

@timeit
def struct2env(structure: Structure, r_max: float) -> list:
    """ 
    Select all unique Cu-Cu crystal environments for given structure.
    Args:
        structure: (Structure) pymatgen structure
        r_max : (float) maximal Cu-Cu distance to consider
    Return:
        (list[dict]) list of dictionaries
        [{'dist': cu-cu dist, 'env': CrystalEnvironment}]
    """
    # make supercell 
    cu_sites = []
    cu_envs = []
    cu_pairs_count = 0
    scaling = [2, 2, 2]
    print(f'Sites in the cell: {len(structure)}')
    structure.make_supercell(scaling_matrix=scaling)
    print(f'Sites in the supercell: {len(structure)}')
    
    # find Cu2+ sites 
    for site in structure:
        if get_site_Z(site) == 29 and get_site_OxN(site) == 2:
            cu_sites.append(site)
    
    # find Cu2+ pairs 
    for i in range(len(cu_sites) - 1):
        for j in range(i + 1, len(cu_sites)):
            cu_pairs_count += 1
            cu1, cu2 = cu_sites[i], cu_sites[j]
            t_env = CrystalEnvironment(structure, cu1, cu2)
            if (t_env.cu_cu_dist <= r_max) and t_env not in cu_envs:
                cu_envs.append(t_env)
    
    print(f'# of Cu sites in the supercell: {len(cu_sites)}')
    print(f'# of pairs: {cu_pairs_count}')
    print(f'# of unique environemnts: {len(cu_envs)}')

    return cu_envs

def env2descr(env: CrystalEnvironment, basis: list) -> list:
    """
    Create rotationally-invariant 3D Zernike desriptor for local crystal environment.
    Args:
        env: (CrystalEnvironment) local crystal environment for which to create descriptor
    Return: 
        (dict) rotationally-invariant 3D Zernike descriptor
    """
    dist = env.cu_cu_dist
    env_atoms = env.get_atoms()
    env_atoms = np.array(env_atoms, dtype=np.float32)

    img3d = make_3d_img(env_atoms, ds=0.025)
    # make rotationally invariant Zernike 3D descriptor 
    descr = zernike3d_descriptor_invariant(img3d, basis, _N_MAX_)  # [[n, l, Coeff], ...]

    X = np.array([[dist] + [_[2] for _ in descr]])
    print(f'Predictors: {len(X)}')
    return X

def load_ml():
    """
    Load ML pipeline which involves MinMax scaling, feature selection and 
    """
    scaler_X = pickle.load(open(file_scalerX, 'rb'))
    scaler_Y = pickle.load(open(file_scalerY, 'rb'))
    feat_selector = pickle.load(open(file_feat_selector, 'rb'))
    loaded_model = pickle.load(open(file_model, 'rb'))
    return scaler_X, scaler_Y, feat_selector, loaded_model

def descr2hop(descr: list) -> float:
    """ 
    Predict hopping for given descriptor.
    Args:
        descr: (dict) descriptor of the given crystal environment
    Return:
        (float) real value of the hopping.
    """
    scaler_X, scaler_Y, feat_selector, loaded_model = load_ml()
    # min max scale the feature vector 
    X = scaler_X.transform(descr)
    
    # select important features 
    X_new = feat_selector.transform(X)
    # predict the hopping, value is scaled from 0 to 1
    Y_pred = loaded_model.predict(X_new) 
    # inverse transform the predicted value 
    Y_pred = scaler_Y.inverse_transform(Y_pred.reshape(-1, 1))
    return Y_pred

if __name__ == "__main__":
    cif_path = '/home/denys/Documents/ifw/smc/data/raw/531.cif'

    struct = Structure.from_file(cif_path)
    scaler_X, scaler_Y, feat_selector, loaded_model = load_ml()
    basis_size = calc_basis_size(_N_MAX_)
    basis = load_basis(basis_path, basis_size)

    test_spin_model = SpinModel(struct, basis, scaler_X, scaler_Y, feat_selector, loaded_model)

    print(test_spin_model.distances)
    print(test_spin_model.exchanges)
    print(test_spin_model.edges)
    print(test_spin_model.edges)

    #envs = struct2env(struct, 6.0)
    #test_env = envs[0]
    #print(envs[0] == envs[0])
    #print(envs[0] == envs[1])
    
    #test_descr = env2descr(test_env, basis)
    #pred_t = descr2hop(test_descr)

    #print(f'Test env dist: {test_env.cu_cu_dist} Ang')
    #print(f'Pred t = {pred_t} eV')
    
    