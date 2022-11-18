import os
import time
from flask import Flask, request
from pymatgen.core.structure import Structure  
from core import *

app = Flask(__name__)
# load basis and model 
scaler_X, scaler_Y, feat_selector, model = load_ml()
basis = get_basis4prod()

UPLOAD_PATH = os.getcwd() + "/cif/temp.cif"

@app.route('/upload', methods=['POST'])
def get_spin_model():
    f = request.files['file']
    f.save(UPLOAD_PATH)

    response = {
        "lattice"  : None,
        "exchanges": None,
        "distances": None,
        "vertices" : None,
        "edges"    : None,
        "error"    : None
    }

    try:
        structure = Structure.from_file(UPLOAD_PATH)
        spin_model = SpinModel(structure, basis, scaler_X, scaler_Y, feat_selector, model)
        response["lattice"] = structure.lattice.matrix.tolist()
        response["exchanges"] = spin_model.exchanges
        response["distances"] = spin_model.distances
        response["vertices"] = spin_model.vertices
        response["edges"] = spin_model.edges
    except:
        response["error"] = "Error message"
        print("An exception occured")

    print(response)
    return response
