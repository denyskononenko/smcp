import os
import time
from flask import Flask, request
from pymatgen.core.structure import Structure  
from core import dir_ensemble, get_basis4prod, SpinModel, validate_cif, get_chemical_formula
from ensemble_ann import EnsembleANN, N_ESTIMATORS

app = Flask(__name__, static_folder='../build', static_url_path='/')

# load basis and model 
model = EnsembleANN([], [], n_estimators=N_ESTIMATORS)
model.load_estimators(dir_ensemble)

basis = get_basis4prod()

__file_dir__ = '/'.join(__file__.split('/')[:-1])
__buffer_dir__ = f'{__file_dir__}/cif'
if not os.path.isdir(__buffer_dir__):
    os.mkdir(__buffer_dir__)
    
UPLOAD_PATH = f"{__buffer_dir__}/temp.cif"
TEST_PATH = f"{__buffer_dir__}/test/"

def get_spin_model_response(cif_file: str, maxR: float) -> dict:
    """
    Make response with spin model description.
    Args:
        cif_file: (str) path of the target cif file 
        maxR: (float) maximal hopping distance, i.e. Cu..Cu distance
    Response specification:
    {
        "formula"  : (str),
        "lattice"  : (list),
        "exchanges": (list),
        "distances": (list),
        "vertices" : (list),
        "edges"    : (list),
        "error"    : (str)
    }
    Args:
        cif_file: (str) path to the cif file 
    Returns:
        (dict) dictionary of responce with spin model description
    """
    response = {
        "formula"  : None,
        "lattice"  : None,
        "exchanges": None,
        "distances": None,
        "vertices" : None,
        "edges"    : None,
        "error"    : None
    }

    check_status, check_message = validate_cif(cif_file)

    response["error"] = check_message
    response["status"] = check_status
    
    if check_status:
        structure = Structure.from_file(cif_file)
        spin_model = SpinModel(structure, basis, model, maxR)
        response["formula"] = get_chemical_formula(cif_file)
        response["lattice"] = structure.lattice.matrix.tolist()
        response["exchanges"] = spin_model.exchanges
        response["distances"] = spin_model.distances
        response["vertices"] = spin_model.vertices
        response["edges"] = spin_model.edges

    print(f'Strcture is valid: {check_status}')
    print(check_message)
    print(response)

    return response


@app.route('/')
def index():
    return app.send_static_file('index.html')

# endpoint for processing of custom cif file
@app.route('/upload', methods=['POST'])
def process_user_spin_model():
    maxR = float(request.form.get('maxR'))
    f = request.files['file']
    f.save(UPLOAD_PATH)

    print(f'maxR: {maxR}')

    response = get_spin_model_response(UPLOAD_PATH, maxR)

    return response

# endpoint for processing of the test structure from database
@app.route('/process_test_cif', methods=['POST'])
def process_test_spin_model():
    maxR = float(request.form.get('maxR'))
    test_cif_id = request.form.get('id')
    test_cif_file = f"{TEST_PATH}{test_cif_id}.cif"

    print(f'maxR: {maxR}')

    response = get_spin_model_response(test_cif_file, maxR)

    return response