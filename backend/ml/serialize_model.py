import os
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

RAND_ST = 26
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

if __name__ == "__main__":
    __file_dir__ = '/'.join(__file__.split('/')[:-1])

    dataset_path = f'{__file_dir__}/envs_r4_h0.005_f0.1+test/'
    print(dataset_path, os.path.isdir(dataset_path))

    # path for serialization of the model
    dir_for_serialized_models = f"{__file_dir__}/model/"

    # check if directory for model serialization exists 
    if not os.path.isdir(dir_for_serialized_models): 
        os.mkdir(dir_for_serialized_models)

    # make the dataset 
    dataset_pd = Dataset(dataset_path).items
    # split dataset into parts with low and large hoppings
    dataset_pd_higt = dataset_pd.loc[dataset_pd['hval'] >= 0.04]
    dataset_pd_lowt = dataset_pd.loc[dataset_pd['hval'] < 0.04]
    # number of dataset items with low hopping 
    n_lowt = dataset_pd_lowt.shape[0]
    # select 25 % of dataset items with low hopping
    indices_to_select_lowt = np.random.choice(np.arange(n_lowt, dtype=int), int(0.05 * n_lowt)).tolist()
    dataset_pd_lowt = dataset_pd_lowt.iloc[indices_to_select_lowt]

    dataset_pd_concat = pd.concat([dataset_pd_lowt, dataset_pd_higt])

    # get numpy entities 
    X = dataset_pd_concat.to_numpy()[:,3:].astype(float)
    Y = dataset_pd_concat.to_numpy()[:,1].astype(float).reshape(-1,1)
    n, p = X.shape

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.80, random_state=RAND_ST)
    
    # model serialization
    print("Model serialization")
    save_gpr(X_train, Y_train, dir_for_serialized_models)


    
    
