import os
import sys
sys.path.append('..')
import glob
import numpy as np 
import pandas as pd
import pickle
#plotting 
import matplotlib.pyplot as plt 
# gaussian process
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern
# utils 
from sklearn.feature_selection import SelectFromModel
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
# dataset
from dataset import Dataset
# metrics
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
# deep ensemble mode
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.utils import resample
from ensemble_ann import EnsembleANN

RAND_ST = 26
N_ESTIMATORS = 100
__file_path__ = os.getcwd()

def save_gpr(X, Y, path):
    """
    Save ML pipeline with Gaussian Process Regression for production.
    """
    scaler_X = MinMaxScaler().fit(X)
    scaler_Y = MinMaxScaler().fit(Y)
    X = scaler_X.transform(X)
    Y = scaler_Y.transform(Y)
    # export scalers
    pickle.dump(scaler_X, open(f'{path}/scalerX.sav', 'wb'))
    pickle.dump(scaler_Y, open(f'{path}/scalerY.sav', 'wb'))

    rfr = RandomForestRegressor(
        warm_start=True, 
        oob_score=True, 
        n_estimators=300, 
        max_features='sqrt',
        random_state=RAND_ST
        )
    # select features 
    feat_selector = SelectFromModel(rfr, threshold=0.005).fit(X, Y.flatten())
    X_new = feat_selector.transform(X)
    # export feature selector
    pickle.dump(feat_selector, open(f'{path}/feat_selector.sav', 'wb'))

    n, p = X_new.shape
    
    # build predictive model
    kernel =  ConstantKernel(1.0, (1e-36, 1e36)) + Matern(length_scale=[1] * p, length_scale_bounds=(1e-36, 1e36), nu=2.0)
    model = GaussianProcessRegressor(
        kernel=kernel,
        alpha=0.005, 
        n_restarts_optimizer=500,
        random_state=RAND_ST
        )

    print("Fit the model")
    model.fit(X_new, Y.ravel())

    print("Exporting the model")
    # export model 
    pickle.dump(model, open(f'{path}/model.sav', 'wb'))

def save_ensemble_ann(X, Y, path):
    """Save Ensemble ANN"""
    ensemble_ann = EnsembleANN(X, Y, n_estimators=N_ESTIMATORS)
    ensemble_ann.train_ensamble()
    ensemble_ann.save_estimators(path)

if __name__ == "__main__":
    __file_dir__ = '/'.join(__file__.split('/')[:-1])

    dataset_path = f'{__file_dir__}/envs_r4_f0.1_Hopt/'
    print(dataset_path, os.path.isdir(dataset_path))

    # path for serialization of the model
    dir_for_serialized_models = f"{__file_dir__}/model/ensemble_ann/"

    # check if directory for model serialization exists 
    if not os.path.isdir(dir_for_serialized_models): 
        os.mkdir(dir_for_serialized_models)

    # make the dataset 
    dataset_pd = Dataset(dataset_path).items
    X_total = dataset_pd.to_numpy()[:,3:].astype(float)
    Y_total = dataset_pd.to_numpy()[:,1].astype(float).reshape(-1,1)

    print(f'X shape: {X_total.shape}, Y shape: {Y_total.shape}')

    # train and serialize the ML model 
    print("Model training and serialization")
    #save_gpr(X_train, Y_train, dir_for_serialized_models)
    save_ensemble_ann(X_total, Y_total, dir_for_serialized_models)

    
    
