import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.utils import resample

KFOLDS = 6
DROPOUT_RATE = 0.05
LEARN_RATE = 0.001
NUM_FEATURES = 183

class EnsembleANN:
    def __init__(self, X, Y, n_estimators=100):
        self.n_estimators = n_estimators
        self.X = X
        self.Y = Y
        self.models = []
        self.histories = []

    @staticmethod
    def apply_bn_and_dropout(x):
        return layers.Dropout(DROPOUT_RATE)(layers.BatchNormalization()(x))

    @staticmethod
    def make_ann():
        # ANN for prediction of hooping
        input = keras.Input(shape=(NUM_FEATURES,))
        x = layers.Dense(128, activation='relu')(input)
        x = EnsembleANN.apply_bn_and_dropout(x)
        x = layers.Dense(64, activation='relu')(x)
        x = EnsembleANN.apply_bn_and_dropout(x)
        x = layers.Dense(32, activation='relu')(x)
        x = EnsembleANN.apply_bn_and_dropout(x)
        x = layers.Dense(16, activation='relu')(x)
        x = EnsembleANN.apply_bn_and_dropout(x)
        out = layers.Dense(1, name="affinity")(x)
        ann = keras.Model(input, out, name="t_predictor")
        ann.summary()
        return ann
    
    def train_ensamble(self):
        for _ in range(self.n_estimators):
            train_ix = resample(list(range(len(self.X))))
            X_train, Y_train = self.X[train_ix], self.Y[train_ix]

            t_ann = EnsembleANN.make_ann()
            t_ann.compile(
                optimizer=keras.optimizers.legacy.Adam(LEARN_RATE), 
                loss=keras.losses.MeanSquaredError())
            t_hist = t_ann.fit(
                X_train, 
                Y_train, 
                epochs=2000, 
                batch_size=256,
                verbose=0
            ) 
            
            self.models.append(t_ann)
            self.histories.append(t_hist)
    
    def predict(self, X):
        n = X.shape[0]
        models_pred = np.zeros((n, self.n_estimators))
        
        for i, model in enumerate(self.models):
            y_pred = np.abs(model.predict(X))
            models_pred[:, i] = y_pred[:, 0]
        
        return models_pred
    
    def save_estimators(self, path_to_save):
        for i, model in enumerate(self.models):
            model.save(f'{path_to_save}/{i}.keras')

    def load_estimators(self, path_to_load):
        if len(self.models) == 0:
            for i in range(self.n_estimators):
                # load model 
                t_model = keras.models.load_model(f'{path_to_load}/{i}.keras')
                self.models.append(t_model)
        else:
            print('Estimators are trained already.')