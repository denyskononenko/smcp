import os
import time
from flask import Flask, request
from pymatgen.core.structure import Structure  
from core import load_ml, get_basis4prod, SpinModel, validate_cif

app = Flask(__name__, static_folder='../build', static_url_path='/')

# load basis and model 
scaler_X, scaler_Y, feat_selector, model = load_ml()
basis = get_basis4prod()

__file_dir__ = '/'.join(__file__.split('/')[:-1])
__buffer_dir__ = f'{__file_dir__}/cif'
if not os.path.isdir(__buffer_dir__):
    os.mkdir(__buffer_dir__)
    
UPLOAD_PATH = f"{__buffer_dir__}/temp.cif"

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/upload', methods=['POST'])
def get_spin_model():
    f = request.files['file']
    f.save(UPLOAD_PATH)

    response = {
        "formula"  : None,
        "lattice"  : None,
        "exchanges": None,
        "distances": None,
        "vertices" : None,
        "edges"    : None,
        "error"    : None
    }

    check_status, check_message = validate_cif(UPLOAD_PATH)

    response["error"] = check_message
    response["status"] = check_status
    
    if check_status:
        structure = Structure.from_file(UPLOAD_PATH)
        spin_model = SpinModel(structure, basis, scaler_X, scaler_Y, feat_selector, model)
        response["formula"] = structure.formula
        response["lattice"] = structure.lattice.matrix.tolist()
        response["exchanges"] = spin_model.exchanges
        response["distances"] = spin_model.distances
        response["vertices"] = spin_model.vertices
        response["edges"] = spin_model.edges

    print(f'Strcture is valid: {check_status}')
    print(check_message)
    print(response)

    return response
