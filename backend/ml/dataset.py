""" 
Adapter class for the dataset of crystal environments and hoppings. 
"""
import glob
import numpy as np
import pandas as pd 

class Dataset:

    def __init__(self, path, get_h_class=lambda h: 1 * (h > 0.3)):
        self.path = path
        self.dscfiles = glob.glob(f'{self.path}/*/*/*.dat') # descriptors 
        self.envfiles = glob.glob(f'{self.path}/*/*/*.env') # environments
        self.get_h_class = get_h_class

    @property
    def items(self):
        # list of files with descriptors
        files = self.dscfiles
        # read descriptors and assemble the dataset as pandas dataframe
        # dataframe fields
        name = []   # crystal environment name
        dist = []   # Cu..Cu distance
        hval = []   # hopping value
        clas = []   # hopping class
        
        desc_zernike = {f'{int(n)} {int(l)}': [] for n, l, val in Dataset.read_f(files[0])[-1]}   # descriptor with n l being keys

        for f in files:
            # parse the descriptor file name 
            fname = f.rstrip('.dat').split('/')
            tenv_id = fname[-1]      # crystal environment id 
            tstr_id = fname[-3]      # structure id 
            tname   = f'{tstr_id}-{tenv_id}' 
            thval, tdist, tdesc = Dataset.read_f(f) # read descriptor 
            tclas =  self.get_h_class(thval)        # define class label to the hopping 

            for n, l, val in tdesc:
                key = f'{int(n)} {int(l)}'
                desc_zernike[key].append(val)

            name.append(tname)
            dist.append(tdist)
            hval.append(thval)
            clas.append(tclas)
            
        data = {
            'name' : name,
            'hval' : hval,
            'clas' : clas,
            'dist' : dist,
            **desc_zernike,
        }

        df = pd.DataFrame(data=data)

        return df
    
    @staticmethod
    def select_edge_corner(envfile):
        """Select corner sharing cases from the dataset."""
        r0 = 6   # normalization factor for coordinates (in env file coodinates are normalized on this value)
        rc = 2.5 # cutoff distance for Cu - O bond
        cu_pair, oxygens = [], [] # list of copper pairs on distance equal to hopping distance, list of shared oxygens
        # calculate angle between two vectors in degrees
        get_angle = lambda v1, v2: (180 / pi) * arccos(clip(dot(v1, v2) / (norm(v1) * norm(v2)), -1, 1))
        # read environment file
        hval, dist, env = Dataset.read_f(envfile)
        # find the copper atoms distanced on the hoo_dist
        for i in range(len(env) - 1):
            for j in range(i, len(env)):
                a1, a2 = env[i], env[j]
                dij = norm(np.array(a1[:3]) - np.array(a2[:3])) * r0
                if a1[5] == a2[5] == 29 and abs(dij - dist) <= 1e-5:
                    cu_pair.append((i,j))
        # copper atoms
        i1, i2 = cu_pair[0]
        cu1, cu2 = env[i1], env[i2]
        # find the shared oxygen
        for a in env:
            if a[5] == 8:
                da1 = norm(np.array(a[:3]) - np.array(cu1[:3])) * r0 # distance to first copper
                da2 = norm(np.array(a[:3]) - np.array(cu2[:3])) * r0 # distance to second copper
                if da1 <= rc and da2 <= rc: oxygens.append(a)
        
        # corner-sharing case
        if len(oxygens) == 1:
            ox = oxygens[0]
            # vector from Cu1 to O
            v1 = np.array(cu1[:3]) - np.array(ox[:3])
            # vector from Cu2 to O
            v2 = np.array(cu2[:3]) - np.array(ox[:3])
            # Cu1 - O - Cu2 angle 
            alpha = get_angle(v1, v2)
            # Cu1/2 - O distance
            d1, d2 = norm(v1) * r0, norm(v2) * r0
            return [alpha, d1, d2, hval]
        # edge-sharing case
        elif len(oxygens) == 2:
            # for edge-shared cases 
            ox1, ox2 = oxygens[:2]
            
            # vectors from Cu1 - O1, Cu1 - O2
            v11 = np.array(cu1[:3]) - np.array(ox1[:3])
            v12 = np.array(cu1[:3]) - np.array(ox2[:3])
            # vectors from Cu2 - O1, Cu2 - O2
            v21 = np.array(cu2[:3]) - np.array(ox1[:3])
            v22 = np.array(cu2[:3]) - np.array(ox2[:3]) 
            
            # angles 
            alpha1, alpha2 = get_angle(v11, v21), get_angle(v12, v22)
            # distances 
            d11, d12, d21, d22 = norm(v11) * r0, norm(v12) * r0, norm(v21) * r0, norm(v22) * r0

            return [alpha1, alpha2, d11, d12, d21, d22, hval]
        else:
            return []

    @property
    def corner_sharing_items(self):
        """Select corner-sharing items form the dataset."""
        items = []

        for f in self.envfiles:
            td = Dataset.select_edge_corner(f)
            items.append(td)
        return items

    @staticmethod
    def read_f(path) -> tuple:
        """Read descriptor dat or environemnt env file."""
        with open(path, 'r') as f:
            lines = [[float(_) for _ in l.split(' ') if _ != ''] for l in f.readlines()]
            hval = lines[0][0] # hopping value
            dist = lines[0][1] # Cu..Cu distance
            cont = lines[1:]   # descriptor or crystal environemnt
            return hval, dist, cont
    
    @property
    def maxZ(self):
        listZ = []

        # collect all atomic numbers Z in the entire Dataset
        for f in self.envfiles:
            thval, tdist, tenv = Dataset.read_f(f) # read environment
            # tenv = [[x, y, z, ionic_radius, Oxidation_number, Z], ...]
            tZ = np.array(tenv)[:, -1].astype(int)
            listZ += list(set(tZ))
        
        listZ = list(set(listZ))

        return max(listZ)