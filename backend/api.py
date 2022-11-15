import os
import time
from flask import Flask, request

app = Flask(__name__)

UPLOAD_PATH = os.getcwd() + "/cif/temp.cif"

@app.route('/upload', methods=['POST'])
def get_spin_model():
    f = request.files['file']
    f.save(UPLOAD_PATH)

    response = {
        "lattice"  : [[1,0,0], [0,1,0], [0,0,1]],
        "exchanges": [0.5, 0.05],
        "vertices" : [[2, 2, 0], [2, 3, 0], [2, 4, 0], [2, 2, 1], [2, 3, 1], [2, 4, 1]],
        "edges"    : [[[0, 1], [1, 2], [3, 4], [4, 5]], [[0, 3], [1, 4], [2, 5]]]
    }
    print(response)
    return response
